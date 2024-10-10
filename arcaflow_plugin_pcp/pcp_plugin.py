#!/usr/bin/env python3.9

import json
import csv
import shutil
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from time import sleep
from datetime import datetime
import typing
from threading import Event
from arcaflow_plugin_sdk import plugin, predefined_schemas
from pcp_schema import (
    PcpInputParams,
    post_process_params_schema,
    PostProcessParams,
    PerfOutput,
    Error,
)


def run_oneshot_cmd(command_list):
    try:
        cmd_out = subprocess.check_output(
            command_list,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as err:
        return "error", Error(
            f"{err.cmd[0]} failed with return code {err.returncode}:\n{err.output}"
        )
    return "completed", cmd_out


class StartPcpStep:
    exit = Event()
    finished_early = False

    @plugin.signal_handler(
        id=predefined_schemas.cancel_signal_schema.id,
        name=predefined_schemas.cancel_signal_schema.display.name,
        description=predefined_schemas.cancel_signal_schema.display.description,
        icon=predefined_schemas.cancel_signal_schema.display.icon,
    )
    def cancel_step(self, _input: predefined_schemas.cancelInput):
        # First, let it know that this is the reason it's exiting.
        self.finished_early = True
        # Now signal to exit.
        self.exit.set()

    @plugin.step_with_signals(
        id="run-pcp",
        name="Run PCP",
        description=(
            "Runs the PCP data collection and then processes the results into a "
            "machine-readable format"
        ),
        outputs={"success": PerfOutput, "error": Error},
        signal_handler_method_names=["cancel_step"],
        signal_emitters=[],
        step_object_constructor=lambda: StartPcpStep(),
    )
    def run_pcp(
        self,
        params: PcpInputParams,
    ) -> typing.Tuple[str, typing.Union[PerfOutput, Error]]:

        # Start the PCMD daemon
        pcmd_cmd = [
            "/usr/libexec/pcp/lib/pmcd",
            "start",
        ]

        pcmd_return = run_oneshot_cmd(pcmd_cmd)
        if "error" in pcmd_return[0]:
            return pcmd_return

        # pmlogger_cfg_path = Path(tempfile.gettempdir(), "pmlogger.conf")
        # Create the pmlogger.conf file from the user-provided contents or
        # a default file with the generator command
        if params.pmlogger_conf:
            print("Using provided pmlogger configuration file")
            Path("pmlogger.conf").write_text(params.pmlogger_conf)
        else:
            print("Generating default pmlogger configuration file")
            pmlogconf_cmd = [
                "/usr/bin/pmlogconf",
                "pmlogger.conf",
            ]

            pmlogconf_return = run_oneshot_cmd(pmlogconf_cmd)
            if "error" in pmlogconf_return[0]:
                return pmlogconf_return

        # with tempfile.TemporaryDirectory() as tmp_pcp:
        # Create the pmrep.conf file from the user-provided contents or
        # point to the system configuration directory
        tmp_pcp = Path(tempfile.mkdtemp(), "pcp_plugin")
        pmrep_path = Path(params.pmrep_conf_path)
        pcp_path = pmrep_path.parent
        shutil.copytree(pcp_path, tmp_pcp)
        pmrep_conf_tmppath = tmp_pcp.joinpath("pmrep", "pmrep.conf")
        plugin_pmrep_path = params.pmrep_conf_path
        if params.pmrep_conf:
            params.pmrep_conf_path = "pmrep.conf"
            print("Using provided pmrep configuration file")
            # Path(params.pmrep_conf_path).write_text(params.pmrep_conf)
            pmrep_conf_tmppath.write_text(params.pmrep_conf)
            plugin_pmrep_path = pmrep_conf_tmppath
        else:
            print(f"Using default {params.pmrep_conf_path} configuration directory")

        # Start pmlogger to collect metrics
        pmlogger_cmd = [
            "/usr/bin/pmlogger",
            "-c",
            "pmlogger.conf",
            "-t",
            str(params.pmlogger_interval),
            "pmlogger-out",
        ]

        try:
            print("Gathering data... Use Ctrl-C to stop.")
            subprocess.Popen(
                pmlogger_cmd,
                text=True,
            )

            # Block here, waiting on the cancel signal
            self.exit.wait(params.timeout)

        except subprocess.CalledProcessError as err:
            return "error", Error(
                f"{err.cmd[0]} failed with return code {err.returncode}:\n{err.output}"
            )

        # Secondary block interrupt is via the KeyboardInterrupt exception.
        # This enables running the plugin stand-alone without a workflow.
        except (KeyboardInterrupt, SystemExit):
            print("\nReceived keyboard interrupt; Stopping data collection.\n")

        # Check the pmlogger output file
        try:
            if os.stat("pmlogger-out.0").st_size == 0:
                return "error", Error(
                    "The pmlogger output file is empty; Unable to process results."
                )
        except FileNotFoundError:
            return "error", Error(
                "The pmlogger output file was not found; Unable to process results."
            )

        post_process_params = {
            "pmlogger_metrics": params.pmlogger_metrics,
            "pmlogger_interval": params.pmlogger_interval,
            "pmrep_conf_path": str(plugin_pmrep_path),
            "generate_csv": params.generate_csv,
            "flatten": params.flatten,
            "archive_path": ".",
        }

        return post_process(
            params=post_process_params_schema.unserialize(post_process_params),
            run_id="post-process",
        )


@plugin.step(
    id="post-process",
    name="Post-Process PCP Archive",
    description="Processes an existing PCP archive into a machine-readable format",
    outputs={"success": PerfOutput, "error": Error},
)
def post_process(
    params: PostProcessParams,
) -> typing.Tuple[str, typing.Union[PerfOutput, Error]]:

    # Parse metrics from input
    metrics = params.pmlogger_metrics.split()

    pcp2_flags = [
        "-a",
        params.archive_path,
        "-t",
        str(params.pmlogger_interval),
        "-f",
        # pmrep doesn't accept %z for the timezone,
        # so we'll get it explicitly via datetime
        f"%FT%T.%f{str(datetime.now().astimezone())[-6:]}",
        "-c",
        params.pmrep_conf_path,
        "-P",
        "6",
    ]

    # Initialized pcp2json command
    pcp2json_cmd = [
        "/usr/bin/pcp2json",
        "-E",
    ]

    pcp2json_cmd.extend(pcp2_flags)

    # The list of metrics to collect is appended to the pcp2json command
    pcp2json_cmd.extend(metrics)

    print(f"Reporting metrics for: {params.pmlogger_metrics}")

    if params.flatten or params.generate_csv:
        # Initialize (optional) pcp2csv command
        pcp2csv_cmd = [
            "/usr/bin/pcp2csv",
            "-l",
            ",",
        ]

        pcp2csv_cmd.extend(pcp2_flags)
        pcp2csv_cmd.extend(metrics)

    max_attempts = 2
    pcp2csv_status = ""
    pcp2json_status = ""
    # Here we give an additional chance to run the pcp2json conversion.
    # This covers the situation where pmlogger is cancelled before a
    # params.pmlogger_interval time has passed, which can cause pcp2json
    # to fail.
    for _attempt in range(max_attempts):
        if params.flatten or params.generate_csv:
            pcp2csv_status, pcp2csv_return = run_oneshot_cmd(pcp2csv_cmd)
            if "error" in pcp2csv_status:
                if params.flatten:
                    # If the pcp2csv command fails, we first attempt to retry.
                    print(
                        f"{pcp2csv_return} "
                        f"Retrying in {params.pmlogger_interval} seconds...\n"
                    )
                    sleep(params.pmlogger_interval)
                    continue
                print(pcp2csv_return + "; continuing")

        if params.flatten:
            reader = csv.DictReader(pcp2csv_return.splitlines())
            pcp_metrics_list = list(reader)

        else:
            pcp2json_status, pcp2json_return = run_oneshot_cmd(pcp2json_cmd)
            if "error" in pcp2json_status:
                # If the pcp2json command fails, we first attempt to retry.
                print(
                    f"{pcp2json_return} "
                    f"Retrying in {params.pmlogger_interval} seconds...\n"
                )
                sleep(params.pmlogger_interval)
                continue
            pcp_out_json = json.loads(pcp2json_return.strip().split("\n", 2)[2])
            pcp_metrics_list = pcp_out_json["@pcp"]["@hosts"][0]["@metrics"]

        if params.generate_csv:
            # Send the CSV format to stdout, if requested
            print(pcp2csv_return)

        # If pcp2json or pcp2csv completes without an exception, we return success.
        return "success", PerfOutput(pcp_metrics_list)

    # Return the appropriate error condition after max_retries
    if "error" in pcp2json_status:
        return (pcp2json_status, pcp2json_return)
    if "error" in pcp2csv_status:
        return (pcp2csv_status, pcp2csv_return)

    # Since the above for loop should always return either success or error,
    # and should never come to its natural end, if we get here, something
    # unexpected went wrong.
    return "error", Error("Unexpected failure attempting to process pmlogger output")


if __name__ == "__main__":
    sys.exit(
        plugin.run(
            plugin.build_schema(
                StartPcpStep.run_pcp,
                post_process,
            )
        )
    )

#!/usr/bin/env python3.9

import json
import csv
import subprocess
import sys
from time import sleep
import typing
from threading import Event
from arcaflow_plugin_sdk import plugin, predefined_schemas
from pcp_schema import (
    PcpInputParams,
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
    except subprocess.CalledProcessError as error:
        return "error", Error(
            "{} failed with return code {}:\n{}".format(
                error.cmd[0], error.returncode, error.output
            )
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
        id="start-pcp",
        name="Start PCP",
        description="Start the PCP data logging tools",
        outputs={"success": PerfOutput, "error": Error},
        signal_handler_method_names=["cancel_step"],
        signal_emitters=[],
        step_object_constructor=lambda: StartPcpStep(),
    )
    def start_pcp(
        self,
        params: PcpInputParams,
    ) -> typing.Tuple[str, typing.Union[PerfOutput, Error]]:
        # Parse metrics from input
        metrics = params.pmlogger_metrics.split()

        # Start the PCMD daemon
        pcmd_cmd = [
            "/usr/libexec/pcp/lib/pmcd",
            "start",
        ]

        pcmd_return = run_oneshot_cmd(pcmd_cmd)
        if "error" in pcmd_return[0]:
            return pcmd_return

        # Create the pmlogger.conf file
        if params.pmlogger_conf:
            print("Using provided pmlogger configuration file")
            f = open("pmlogger.conf", "w")
            f.write(params.pmlogger_conf)
            f.close
        else:
            print("Generating default pmlogger configuration file")
            pmlogconf_cmd = [
                "/usr/bin/pmlogconf",
                "pmlogger.conf",
            ]

            pmlogconf_return = run_oneshot_cmd(pmlogconf_cmd)
            if "error" in pmlogconf_return[0]:
                return pmlogconf_return

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

        except subprocess.CalledProcessError as error:
            return "error", Error(
                "{} failed with return code {}:\n{}".format(
                    error.cmd[0], error.returncode, error.output
                )
            )

        # Secondary block interrupt is via the KeyboardInterrupt exception.
        # This enables running the plugin stand-alone without a workflow.
        except (KeyboardInterrupt, SystemExit):
            print("\nReceived keyboard interrupt; Stopping data collection.\n")
            pass

        pcp2_flags = [
            "-a",
            "pmlogger-out",
            "-f",
            "%FT%T.%f",
            "-c",
            "/etc/pcp/pmrep",
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

        max_retries = 1
        pcp2csv_return = ("", "")
        pcp2json_return = ("", "")
        # Here we give max_retries chances to run the pcp2json conversion.
        # This covers the situation where pmlogger is cancelled before a
        # params.pmlogger_interval time has passed, which can cause pcp2json
        # to fail.
        for _attempt in range(max_retries):
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

        else:
            # Return the appropriate error condition after max_retries
            if "error" in pcp2json_status:
                return pcp2json_return
            elif "error" in pcp2csv_status:
                return pcp2csv_return

            # Since the above for loop should always return either success or error,
            # and should never come to its natural end, if we get here, something
            # unexpected went wrong.
            return "error", Error(
                "Unknown failure attempting to process pmlogger output"
            )


if __name__ == "__main__":
    sys.exit(
        plugin.run(
            plugin.build_schema(
                StartPcpStep.start_pcp,
            )
        )
    )

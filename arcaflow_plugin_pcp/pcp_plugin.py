#!/usr/bin/env python3.9

import json
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

        try:
            subprocess.check_output(
                pcmd_cmd,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            return "error", Error(
                "{} failed with return code {}:\n{}".format(
                    error.cmd[0], error.returncode, error.output
                )
            )

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

            try:
                subprocess.check_output(
                    pmlogconf_cmd,
                    text=True,
                )
            except subprocess.CalledProcessError as error:
                return "error", Error(
                    "{} failed with return code {}:\n{}".format(
                        error.cmd[0], error.returncode, error.output
                    )
                )

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

        print(f"pcp2json command: {pcp2json_cmd}")

        print(f"Reporting metrics for: {params.pmlogger_metrics}")

        max_retries = 1
        retries = 0
        # Here we give max_retries chances to run the pcp2json conversion.
        # This covers the situation where pmlogger is cancelled before a
        # params.pmlogger_interval time has passed, which can cause pcp2json
        # to fail.
        while retries <= max_retries:
            try:
                pcp_out = (
                    (
                        subprocess.check_output(
                            pcp2json_cmd,
                            text=True,
                            stderr=subprocess.STDOUT,
                        )
                    )
                    .strip()
                    .split("\n", 2)[2]
                )
                pcp_out_json = json.loads(pcp_out)

            except subprocess.CalledProcessError as error:
                # If the pcp2json command fails, we first attempt to retry.
                if retries < max_retries:
                    retries += 1
                    print(
                        f"{error.output} "
                        f"Retrying in {params.pmlogger_interval} seconds..."
                    )
                    sleep(params.pmlogger_interval)
                    continue
                # After max_retries, if there is still an exception in
                # the pcp2json command, we return an error.
                else:
                    return "error", Error(
                        "{} failed with return code {}:\n{}".format(
                            error.cmd[0], error.returncode, error.output
                        )
                    )

            if params.generate_csv:

                # Initialize (optional) pcp2csv command
                pcp2csv_cmd = [
                    "/usr/bin/pcp2csv",
                ]

                pcp2csv_cmd.extend(pcp2_flags)
                pcp2csv_cmd.extend(metrics)
                
                try:
                    csv_out = subprocess.check_output(
                        pcp2csv_cmd,
                        text=True,
                        stderr=subprocess.STDOUT,
                    )
                    print(csv_out)
                except subprocess.CalledProcessError as error:
                    print(
                        "{} failed with return code {}:\n{}".format(
                            error.cmd[0], error.returncode, error.output
                        )
                    )

            # If pcp2json completes without an exception, we return success.
            pcp_metrics_list = pcp_out_json["@pcp"]["@hosts"][0]["@metrics"]
            return "success", PerfOutput(pcp_metrics_list)

        # Since the above while loop should always return either success or error,
        # and should never come to its natural end, if we get here, something
        # unexpected went wrong.
        return "error", Error("Unknown failure attempting to process pmlogger output")


if __name__ == "__main__":
    sys.exit(
        plugin.run(
            plugin.build_schema(
                StartPcpStep.start_pcp,
            )
        )
    )

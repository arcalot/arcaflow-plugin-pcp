#!/usr/bin/env python3.9

import json
import subprocess
import sys
import typing
from threading import Event, Thread
import signal
from arcaflow_plugin_sdk import plugin, predefined_schemas
from pcp_schema import (
    PcpInputParams,
    PerfOutput,
    Error,
    interval_output_schema,
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

        # Start the collectl daemon
        collectl_cmd = [
            "/usr/bin/collectl",
            "-D",
        ]

        try:
            subprocess.check_output(
                collectl_cmd,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            return "error", Error(
                "{} failed with return code {}:\n{}".format(
                    error.cmd[0], error.returncode, error.output
                )
            )

        # Start SAR collection in the background
        sar_cmd = [
            "/usr/lib64/sa/sa1",
            "1",
        ]

        try:
            subprocess.Popen(
                sar_cmd,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            return "error", Error(
                "{} failed with return code {}:\n{}".format(
                    error.cmd[0], error.returncode, error.output
                )
            )

        # Create the pmlogger.conf file
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

        # Start pmlogger
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
            pmlogger_result = subprocess.Popen(
                pmlogger_cmd,
                text=True,
            )

            # Block waiting on the cancel signal
            self.exit.wait()

            # When the cancel signal is received, terminate pmlogger and continue
            pmlogger_result.terminate()

        except subprocess.CalledProcessError as error:
            return "error", Error(
                "{} failed with return code {}:\n{}".format(
                    error.cmd[0], error.returncode, error.output
                )
            )
        
        except (KeyboardInterrupt, SystemExit):
            print('\nReceived keyboard interrupt; Stopping data collection.\n')
            self.exit.set()

        # Reference command:
        # pcp2json -a _pcp/${PTS_FILENAME} -t 1s -c pts/pcp2json.conf \
        # :sar :sar-b :sar-r :collectl-sn -E | tail -n+3 > ${PTS_FILENAME}.json

        # Convert output to json
        pcp2json_cmd = [
            "/usr/bin/pcp2json",
            "-a",
            "pmlogger-out",
            "-t",
            "1s",
            "-c",
            "fixtures/pcp2json.conf",
            "-E",
            ":sar",
            ":sar-b",
            ":sar-r",
            ":collectl-sn",
        ]

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
            return "error", Error(
                "{} failed with return code {}:\n{}".format(
                    error.cmd[0], error.returncode, error.output
                )
            )
        pcp_metrics_list = pcp_out_json["@pcp"]["@hosts"][0]["@metrics"]
        return "success", PerfOutput(
            interval_output_schema.unserialize(pcp_metrics_list)
        )


if __name__ == "__main__":
    sys.exit(
        plugin.run(
            plugin.build_schema(
                StartPcpStep.start_pcp,
            )
        )
    )

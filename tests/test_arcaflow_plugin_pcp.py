#!/usr/bin/env python3.9

import unittest
from pathlib import Path
import pcp_plugin

from arcaflow_plugin_sdk import plugin


class PCPTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            pcp_plugin.PcpInputParams(
                pmlogger_interval=1.0,
                timeout=5,
                pmlogger_metrics="mem.util.used",
                pmrep_conf_path="/example",
            )
        )

        plugin.test_object_serialization(
            pcp_plugin.PostProcessParams(
                pmlogger_interval=0.5,
                pmlogger_metrics=":sar-B",
                pmrep_conf_path="/EXAMPLE",
                generate_csv=False,
                flatten=True,
                archive_path="./example.com",
            )
        )

        # Normal output
        plugin.test_object_serialization(
            pcp_plugin.PerfOutput(
                pcp_output=[
                    {
                        "@interval": "0",
                        "@timestamp": "2023-11-10T10:12:13.531775Z",
                        "kernel": {
                            "all": {
                                "load": {
                                    "@instances": [
                                        {"name": "1 minute", "value": 1.3},
                                        {"name": "5 minute", "value": 1.33},
                                        {"name": "15 minute", "value": 1.38},
                                    ]
                                }
                            }
                        },
                        "mem": {
                            "util": {"used": {"@unit": "Kbyte", "value": 15401408}}
                        },
                    },
                    {
                        "@interval": "1",
                        "@timestamp": "2023-11-10T10:12:14.027241Z",
                        "disk": {
                            "all": {
                                "read": {"@unit": "count/s", "value": 14},
                                "write": {"@unit": "count/s", "value": 263.993},
                            }
                        },
                        "kernel": {
                            "all": {
                                "cpu": {
                                    "sys": {"@unit": "ms/s", "value": 439.988},
                                    "user": {"@unit": "ms/s", "value": 759.979},
                                },
                                "load": {
                                    "@instances": [
                                        {"name": "1 minute", "value": 1.3},
                                        {"name": "5 minute", "value": 1.33},
                                        {"name": "15 minute", "value": 1.38},
                                    ]
                                },
                            }
                        },
                        "mem": {
                            "util": {"used": {"@unit": "Kbyte", "value": 15464512}}
                        },
                    },
                ]
            )
        )

        # Flattened output
        plugin.test_object_serialization(
            pcp_plugin.PerfOutput(
                pcp_output=[
                    {
                        "Time": "2024-01-17T17:36:49.989464",
                        "kernel.all.load-1 minute": "",
                        "kernel.all.load-5 minute": "",
                        "kernel.all.load-15 minute": "",
                        "mem.util.used": "",
                        "mem.util.free": "",
                        "mem.util.shared": "",
                        "mem.util.bufmem": "",
                        "mem.util.cached": "",
                        "mem.util.other": "",
                        "mem.util.swapCached": "",
                        "mem.util.active": "",
                        "mem.util.inactive": "",
                    },
                    {
                        "Time": "2024-01-17T17:36:50.989464",
                        "kernel.all.load-1 minute": "0.600000",
                        "kernel.all.load-5 minute": "0.520000",
                        "kernel.all.load-15 minute": "0.550000",
                        "mem.util.used": "30313328",
                        "mem.util.free": "2045216",
                        "mem.util.shared": "",
                        "mem.util.bufmem": "256",
                        "mem.util.cached": "18092256",
                        "mem.util.other": "12220816",
                        "mem.util.swapCached": "144",
                        "mem.util.active": "12740016",
                        "mem.util.inactive": "10679792",
                    },
                ]
            )
        )

        plugin.test_object_serialization(pcp_plugin.Error(error="This is an error"))

    def test_functional_full(self):
        tests = [
            {
                # Standard
            },
            {
                # Flatten
                "flatten": True
            },
            {
                # User-provided pmlogger config
                "pmlogger_conf": Path("tests/pmlogger.conf").read_text()
            },
            {
                # User-provided pmrep config
                "pmrep_conf": Path("tests/pmrep.conf").read_text()
            },
        ]

        for test in tests:
            with self.subTest(test=test):
                input = pcp_plugin.PcpInputParams(
                    pmlogger_interval=1.0,
                    pmlogger_metrics="kernel.all.cpu.user mem.util.used",
                    timeout=3,
                    **test,
                )

                output_id, output_data = pcp_plugin.StartPcpStep.start_pcp(
                    params=input, run_id="ci_pcp"
                )

                self.assertEqual("success", output_id)
                plugin.test_object_serialization(
                    pcp_plugin.PerfOutput(output_data.pcp_output),
                    fail=lambda _: self.fail("Output failed schema validation"),
                )

    def test_functional_post(self):
        input = pcp_plugin.PostProcessParams(
            pmlogger_interval=1.0,
            pmlogger_metrics="kernel.all.cpu.user mem.util.used",
            flatten=True,
            archive_path="tests/pmlogger-out",
        )

        output_id, output_data = pcp_plugin.post_process(
            params=input, run_id="ci_pcp_post"
        )

        self.assertEqual("success", output_id)
        self.assertEqual(31787216, int(output_data.pcp_output[1]["mem.util.used"]))


if __name__ == "__main__":
    unittest.main()

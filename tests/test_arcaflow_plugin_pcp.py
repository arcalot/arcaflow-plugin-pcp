#!/usr/bin/env python3.9

import unittest
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
            )
        )

        plugin.test_object_serialization(
            pcp_plugin.PerfOutput(
                pcp_output=[
                    {
                        "@interval": "0",
                        "@timestamp": "2023-11-09 14:39:05",
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
                        "@timestamp": "2023-11-09 14:39:05",
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

        plugin.test_object_serialization(pcp_plugin.Error(error="This is an error"))

    def test_functional(self):
        input = pcp_plugin.PcpInputParams(
            pmlogger_interval=1.0,
            pmlogger_metrics="kernel.all.cpu.user mem.util.used",
            timeout=5,
        )

        output_id, output_data = pcp_plugin.StartPcpStep.start_pcp(
            params=input, run_id="ci_pcp"
        )

        print(f"==>> output_id is {output_id}")
        print(f"==>> output_data is {output_data}")

        self.assertEqual("success", output_id)
        self.assertIsInstance(output_data.pcp_output, list)


if __name__ == "__main__":
    unittest.main()

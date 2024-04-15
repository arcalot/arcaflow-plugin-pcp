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

    def test_functional(self):
        input = pcp_plugin.PcpInputParams(
            pmlogger_interval=1.0,
            pmlogger_metrics="kernel.all.cpu.user mem.util.used",
            timeout=3,
        )

        output_id, output_data = pcp_plugin.StartPcpStep.start_pcp(
            params=input, run_id="ci_pcp"
        )

        print(f"==>> output_id is {output_id}")
        print(f"==>> output_data is {output_data}")

        self.assertEqual("success", output_id)
        self.assertIsInstance(output_data.pcp_output, list)

    def test_functional_flat(self):
        input = pcp_plugin.PcpInputParams(
            pmlogger_interval=1.0,
            pmlogger_metrics="kernel.all.cpu.user mem.util.used",
            timeout=3,
            flatten=True,
        )

        output_id, output_data = pcp_plugin.StartPcpStep.start_pcp(
            params=input, run_id="ci_pcp"
        )

        print(f"==>> output_id is {output_id}")
        print(f"==>> output_data is {output_data}")

        self.assertEqual("success", output_id)
        self.assertIsInstance(output_data.pcp_output, list)
    
    def test_functional_user_pmlogger_conf(self):
        f = open("tests/pmlogger.conf", "r")
        pmlogger_conf = f.read()
        input = pcp_plugin.PcpInputParams(
            pmlogger_interval=1.0,
            pmlogger_metrics="kernel.all.cpu.user mem.util.used",
            timeout=3,
            pmlogger_conf=pmlogger_conf
        )

        output_id, output_data = pcp_plugin.StartPcpStep.start_pcp(
            params=input, run_id="ci_pcp"
        )

        print(f"==>> output_id is {output_id}")
        print(f"==>> output_data is {output_data}")

        self.assertEqual("success", output_id)
        self.assertIsInstance(output_data.pcp_output, list)
    
    def test_functional_user_pmrep_conf(self):
        f = open("tests/pmrep.conf", "r")
        pmrep_conf = f.read()
        input = pcp_plugin.PcpInputParams(
            pmlogger_interval=1.0,
            pmlogger_metrics="kernel.all.cpu.user mem.util.used",
            timeout=3,
            pmrep_conf=pmrep_conf
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

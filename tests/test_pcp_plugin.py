#!/usr/bin/env python3.9

import unittest
import pcp_plugin
from arcaflow_plugin_sdk import plugin
from pcp_schema import (
    interval_output_schema,
)


class PCPTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            pcp_plugin.InputParams(
                pmlogger_interval=1,
                run_duration=10,
            )
        )

        plugin.test_object_serialization(
            pcp_plugin.PerfOutput(
                [
                    {
                        "@interval": "0",
                        "@timestamp": "2022-12-14T13:12:11.894567Z",
                        "commit": {
                            "value": 171.008
                        },
                    },{
                        "@interval": "1",
                        "@timestamp": "2022-12-14T13:12:12.901382Z",
                    },
                ]
            )
        )

        plugin.test_object_serialization(
            pcp_plugin.Error(error="This is an error")
        )

    def test_functional(self):
        input = pcp_plugin.InputParams(
            pmlogger_interval=1,
            run_duration=2,
        )

        output_id, output_data = pcp_plugin.start_pcp(input)

        print(f"==>> output_id is {output_id}")
        print(f"==>> output_data is {output_data}")

        self.assertEqual("success", output_id)
        self.assertIsInstance(output_data.pcp_output, list)


if __name__ == "__main__":
    unittest.main()

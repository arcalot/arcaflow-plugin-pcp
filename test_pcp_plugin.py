#!/usr/bin/env python3.9
import unittest
import pcp_plugin
from arcaflow_plugin_sdk import plugin


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
                {
                    "foo": "bar",
                }
            )
        )

        plugin.test_object_serialization(pcp_plugin.Error(error="This is an error"))

    def test_functional(self):
        input = pcp_plugin.InputParams(
            pmlogger_interval=1,
            run_duration=2,
        )

        output_id, output_data = pcp_plugin.start_pcp(input)

        # The example plugin always returns an error:
        self.assertEqual("success", output_id)
        self.assertIsInstance(output_data.pcp_output, dict)


if __name__ == "__main__":
    unittest.main()

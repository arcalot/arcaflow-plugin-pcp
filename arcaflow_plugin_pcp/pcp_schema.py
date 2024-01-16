import typing
from dataclasses import dataclass
from arcaflow_plugin_sdk import plugin, schema


@dataclass
class PcpInputParams:
    pmlogger_metrics: typing.Annotated[
        typing.Optional[str],
        schema.name("pmlogger metrics to report"),
        schema.description(
            "The pmrep-compatible metrics values to report as a"
            " space-separated string."
        ),
    ] = (
        "kernel.cpu.util kernel.all.load mem.util.used disk.all.read disk.all.write"
    )
    pmlogger_interval: typing.Annotated[
        typing.Optional[float],
        schema.units(schema.UNIT_TIME),
        schema.name("pmlogger logging interval"),
        schema.description(
            "The logging interval in seconds (float) used by pmlogger"
            " for data collection"
        ),
    ] = 1.0
    timeout: typing.Annotated[
        typing.Optional[int],
        schema.name("pmlogger timeout seconds"),
        schema.description(
            "Timeout in seconds after which to cancel the pmlogger collection"
        ),
    ] = None
    pmlogger_conf: typing.Annotated[
        typing.Optional[str],
        schema.name("pmlogger configuration file"),
        schema.description(
            "Complete configuration file content for pmlogger as a multi-line string."
            " If no config file is provided, a default one will be generated."
        ),
    ] = None
    generate_csv: typing.Annotated[
        typing.Optional[bool],
        schema.name("generate CSV output"),
        schema.description(
            "Generates the data payload also in CSV format. This output goes to "
            "the debug_logs, or to stderr if the --debug flag is used."
        ),
    ] = False


@dataclass
class PerfOutput:
    pcp_output: typing.Annotated[
        typing.List[typing.Any],
        schema.name("PCP output list"),
        schema.description("List of of performance data in intervals from PCP"),
    ]


perf_output_schema = plugin.build_object_schema(PerfOutput)


@dataclass
class Error:
    error: str

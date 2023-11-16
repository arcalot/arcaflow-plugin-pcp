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
            "kernel.all.cpu.user kernel.all.cpu.sys kernel.all.load"
            " mem.util.used disk.all.read disk.all.write"
        )
    process_pmlogger_only: typing.Annotated[
        typing.Optional[bool],
        schema.name("only process pmlogger output to json"),
        schema.description(
            "If set, the plugin performs no data collection and instead"
            " only processes the user-provided pmlogger output into the"
            " JSON format. Requires 'pmlogger_file_path'"
        ),
    ] = False
    pmlogger_file_path: typing.Annotated[
        typing.Optional[str],
        schema.required_if(process_pmlogger_only),
        schema.name("file path to pmlogger output"),
        schema.description(
            "The file path for the user-provided pmlogger output for"
            " processing into JSON format. Requires 'process_pmlogger_only."
        ),
    ] = None
    pmlogger_interval: typing.Annotated[
        typing.Optional[float],
        schema.units(schema.UNIT_TIME),
        schema.name("pmlogger logging interval"),
        schema.description(
            "The logging interval in seconds (float) used by pmlogger"
            " for data collection"
        ),
    ] = None
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

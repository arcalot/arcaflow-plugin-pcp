import typing
from dataclasses import dataclass
from arcaflow_plugin_sdk import plugin, schema


@dataclass
class PcpInputParams:
    pmlogger_interval: typing.Annotated[
        typing.Optional[int],
        schema.name("pmlogger logging interval"),
        schema.description(
            "The logging interval in seconds used by " "pmlogger for data collection"
        ),
    ] = None


@dataclass
class IntervalOutput:
    interval: typing.Annotated[
        int,
        schema.id("@interval"),
        schema.name("Interval ID"),
        schema.description("The interval ID as reported by PCP"),
    ]
    timestamp: typing.Annotated[
        str,
        schema.id("@timestamp"),
        schema.name("Interval timestamp"),
        schema.description("The timestamp of the reported interval"),
    ]
    commit: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("commit"),
        schema.description("The commit for the interval"),
    ] = None
    disk: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("disk"),
        schema.description("The disk structure for the interval"),
    ] = None
    kbin: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("kbin"),
        schema.description("The KB in value for the interval"),
    ] = None
    kbout: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("kbout"),
        schema.description("The KB out value for the interval"),
    ] = None
    kernel: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("kernel"),
        schema.description("The kernel CPU structure for the interval"),
    ] = None
    mem: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("mem"),
        schema.description("The memory structure for the interval"),
    ] = None
    memused: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("memused"),
        schema.description("The memory used value for the interval"),
    ] = None
    pktin: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("pktin"),
        schema.description("The packets in for the interval"),
    ] = None
    pktout: typing.Annotated[
        typing.Optional[typing.Dict[str, typing.Any]],
        schema.name("pktout"),
        schema.description("The packets out for the interval"),
    ] = None


interval_output_schema = schema.ListType(plugin.build_object_schema(IntervalOutput))


@dataclass
class PerfOutput:
    pcp_output: typing.Annotated[
        typing.List[IntervalOutput],
        schema.name("PCP output list"),
        schema.description("Performance data from PCP provided in a list format"),
    ]


@dataclass
class Error:
    error: str

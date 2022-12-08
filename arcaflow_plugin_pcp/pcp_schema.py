import typing
from dataclasses import dataclass
from arcaflow_plugin_sdk import schema


@dataclass
class InputParams:
    run_duration: typing.Annotated[
        int,
        schema.name("run duration"),
        schema.description(
            "Time in seconds that the PCP plugin runs before being forceably stopped"
        ),
    ]
    pmlogger_interval: typing.Annotated[
        typing.Optional[int],
        schema.name("pmlogger logging interval"),
        schema.description(
            "The logging interval in seconds used by "
            "pmlogger for data collection"
        ),
    ] = None


@dataclass
class PerfOutput:
    pcp_output: typing.Annotated[
        typing.Dict[str, typing.Any],
        schema.name("PCP output dictionary"),
        schema.description(
            "Performance data from PCP provided in a " "JSON dictionary format"
        ),
    ]


@dataclass
class Error:
    error: str

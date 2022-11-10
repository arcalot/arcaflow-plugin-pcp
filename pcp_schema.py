import typing
from dataclasses import dataclass, field

@dataclass
class InputParams:
    run_duration: int
    pmlogger_interval: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "pmlogger logging interval",
            "description": ("The logging interval in seconds used by "
                            "pmlogger for data collection"),
        },
    )

@dataclass
class StartOutput:
    pass

@dataclass
class PerfOutput:
    pcp_output: typing.Dict[str, typing.Any] = field(
        metadata={
            "name": "PCP output dictionary",
            "description": ("Performance data from PCP provided in a "
                            "JSON dictionary format"),
        },
    )

@dataclass
class Error:
    error: str

#!/usr/bin/env python3

import typing
from dataclasses import dataclass
from dataclasses import field

@dataclass
class InputParams:
    pmlogger-interval: typing.Optional[int] = field(
        default=None,
        metadata={
            "name": "pmlogger logging interval",
            "description": ("The logging interval in seconds used by "
                            "pmlogger for data collection"),
        },
    )

@dataclass
class StartOutput:
    start: str

@dataclass
class PerfOutput:
    pcp-output: typing.Dict[str, typing.Any] = field(
        metadata={
            "name": "PCP output dictionary",
            "description": ("Performance data from PCP provided in a "
                            "JSON dictionary format"),
        },
    )

@dataclass
class Error:
    error: str

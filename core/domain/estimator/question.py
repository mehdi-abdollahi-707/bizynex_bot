"""An estimator question and its answer options.

Each option carries a `score` in [0.0, 1.0]: how much *that specific
answer* pushes the project toward the expensive/slow end of its service's
range, relative to the other options for the same question. The
calculator averages scores across all answered questions to get an
overall complexity ratio — see `calculator.py`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerOption:
    key: str
    label_fa: str
    score: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be within [0.0, 1.0], got {self.score}")


@dataclass(frozen=True)
class EstimatorQuestion:
    key: str
    prompt_fa: str
    options: tuple[AnswerOption, ...]

    def __post_init__(self) -> None:
        if not self.options:
            raise ValueError(f"question '{self.key}' has no options")
        keys = [option.key for option in self.options]
        if len(keys) != len(set(keys)):
            raise ValueError(f"question '{self.key}' has duplicate option keys: {keys}")

    def option_by_key(self, key: str) -> AnswerOption:
        for option in self.options:
            if option.key == key:
                return option
        raise KeyError(f"'{key}' is not a valid option for question '{self.key}'")

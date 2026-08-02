"""FSM states for the project estimator flow.

A single `answering` state, not one state per question — each service has
a different number of questions, so progress (which question, answers so
far) is tracked in FSM *data* (`service_type`, `question_index`,
`answers`) rather than in the state name itself.
"""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class EstimatorFlow(StatesGroup):
    answering = State()

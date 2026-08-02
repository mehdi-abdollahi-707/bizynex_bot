"""FSM states for the project request form — one state per field.

Unlike the estimator (variable question count per service), this form
has a fixed, known set of 7 fields, so an explicit state per field reads
more clearly than an index into a generic list. Sequencing between
fields, and the "editing a single field from the summary" detour, is
handled by `apps.bot.handlers.request_form._proceed`.
"""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class RequestFormFlow(StatesGroup):
    full_name = State()
    phone_number = State()
    company_name = State()
    project_description = State()
    proposed_budget = State()
    desired_timeline = State()
    attachment = State()
    confirm = State()

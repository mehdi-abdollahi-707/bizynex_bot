"""Typed callback_data payloads shared by every keyboard in the bot."""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class NavCallback(CallbackData, prefix="nav"):
    """Identifies which registered page (`apps.bot.pages.registry.PAGES`) to show."""

    target: str


class EstimatorStartCallback(CallbackData, prefix="est_start"):
    """Begins the estimator FSM flow for one service."""

    service: str


class EstimatorAnswerCallback(CallbackData, prefix="est_ans"):
    """A chosen option for a configurator question.

    Carries `question` (not just `option`) so the handler can detect and
    ignore a stale button press from a question the flow has already
    moved past — e.g. a double-tap on an old inline keyboard.
    """

    question: str
    option: str


class EstimatorBackCallback(CallbackData, prefix="est_back"):
    """Steps back one question in the active estimator flow."""


class RequestFormStartCallback(CallbackData, prefix="req_start"):
    """Begins the project request form, linked to the estimation it followed."""

    estimation_id: int


class RequestFormSkipCallback(CallbackData, prefix="req_skip"):
    """Skips the current optional field (نام شرکت or فایل). The active FSM
    state alone identifies which field — no field needed here."""


class RequestFormConfirmCallback(CallbackData, prefix="req_confirm"):
    """One of the three summary-screen actions."""

    action: str  # "submit" | "edit" | "cancel"


class RequestFormEditFieldCallback(CallbackData, prefix="req_edit_field"):
    """Chosen from the edit menu: which field to re-collect, or "__cancel__"
    to return to the summary unchanged."""

    field: str

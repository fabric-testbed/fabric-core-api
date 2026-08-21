"""Regression tests: the SSH key expiry schedule must survive worker recycling.

`GET /start` used to launch a `threading.Thread` inside one of the eight uWSGI
worker processes. `core-api.ini` sets `max-requests = 5000`, so uWSGI recycled
that worker and destroyed the thread with it -- no error, no log line, no
restart -- while `task_timeout_tracker.value` still read 'running', which made
`GET /start` answer "Task Monitor Already Running" forever. Found on all three
tiers in August 2026: production ran the check exactly once after being started
and then not again for four days, across 22 worker respawns.

The schedule now lives in the uWSGI master, which `max-requests` never recycles,
and `/start` is gone. These tests pin the two halves that are testable without
uWSGI: the debounce that decides whether a fire actually runs, and the absence
of the thread machinery from `__main__`. The mechanism itself -- master cron
surviving worker respawn -- is verified against a real uWSGI build; see the PR.

Standard-library unittest only, so it runs on Python 3.12 alongside the other
1.x regression tests::

    PYTHONPATH=server python server/swagger_server/test/test_ske_schedule.py
"""

import ast
import os
import pathlib
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# comanage_utils creates its client at import time.
os.environ.setdefault("COMANAGE_API_URL", "http://example.invalid")
os.environ.setdefault("COMANAGE_API_USER", "test-user")
os.environ.setdefault("COMANAGE_API_PASS", "test-pass")
os.environ.setdefault("COMANAGE_API_CO_ID", "1")
os.environ.setdefault("COMANAGE_API_CO_NAME", "test-co")
os.environ.setdefault("COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID", "1")
os.environ.setdefault("CORE_API_DEFAULT_FACILITY", "FABRIC")
os.environ.setdefault("COU_ID_PROJECTS", "1")
os.environ.setdefault("COU_NAME_JUPYTERHUB", "JupyterHub")
os.environ.setdefault("COU_NAME_FACILITY_OPERATORS", "facility-operators")
os.environ.setdefault("PROJECTS_RENEWAL_PERIOD_IN_DAYS", "365")
os.environ.setdefault("SKE_NAME", "ssh_key_expiry")

from flask import Flask  # noqa: E402

from swagger_server.response_code import task_monitor  # noqa: E402

_APP = Flask(__name__)

SKE_TIMEOUT = 86400


def _tracker(age_seconds, timeout=SKE_TIMEOUT, aware=True):
    """A stand-in for the ssh_key_expiry TaskTimeoutTracker row."""
    now = datetime.now(timezone.utc)
    last_updated = now - timedelta(seconds=age_seconds)
    if not aware:
        last_updated = last_updated.replace(tzinfo=None)
    return SimpleNamespace(
        name="ssh_key_expiry",
        value="running",
        last_updated=last_updated,
        timeout_in_seconds=timeout,
    )


def _run_with(tracker):
    """Drive run_ssh_key_expiry_if_due against a fixed tracker row."""
    with patch.object(task_monitor, "TaskTimeoutTracker") as model:
        model.query.filter_by.return_value.one_or_none.return_value = tracker
        with patch.object(task_monitor, "ssh_key_expiry_check", MagicMock()) as check:
            ran = task_monitor.run_ssh_key_expiry_if_due(_APP)
    return ran, check


class TestDailyFireIsNotSkipped(unittest.TestCase):
    """The debounce must not swallow the scheduled daily run."""

    def test_a_fire_just_under_the_full_timeout_still_runs(self):
        # last_updated records when the PREVIOUS run STARTED, so a 06:00 fire
        # sits a fraction of a second inside an 86400s window. Gating on the
        # full timeout would skip the day, every day, and silently.
        ran, check = _run_with(_tracker(age_seconds=SKE_TIMEOUT - 5))
        self.assertTrue(ran)
        check.assert_called_once()

    def test_a_full_day_later_runs(self):
        ran, check = _run_with(_tracker(age_seconds=SKE_TIMEOUT + 60))
        self.assertTrue(ran)
        check.assert_called_once()

    def test_debounce_is_half_the_configured_timeout(self):
        self.assertEqual(task_monitor.debounce_seconds(_tracker(0)), SKE_TIMEOUT // 2)
        self.assertEqual(task_monitor.debounce_seconds(_tracker(0, timeout=2)), 1)
        # never zero: a zero debounce would let a reload loop re-send mail
        self.assertEqual(task_monitor.debounce_seconds(_tracker(0, timeout=1)), 1)


class TestSecondTriggerInTheSameDayIsSuppressed(unittest.TestCase):
    """A second fire hours after the first must not re-send notifications."""

    def test_a_run_minutes_ago_is_skipped(self):
        ran, check = _run_with(_tracker(age_seconds=600))
        self.assertFalse(ran)
        check.assert_not_called()

    def test_a_run_just_inside_the_debounce_is_skipped(self):
        ran, check = _run_with(_tracker(age_seconds=(SKE_TIMEOUT // 2) - 5))
        self.assertFalse(ran)
        check.assert_not_called()


class TestDegradedInputs(unittest.TestCase):
    def test_missing_tracker_row_is_skipped_not_raised(self):
        ran, check = _run_with(None)
        self.assertFalse(ran)
        check.assert_not_called()

    def test_naive_last_updated_is_treated_as_utc(self):
        # DateTime(timezone=True) normally yields aware values; a naive one must
        # not crash the scheduled run with a tz-comparison TypeError.
        ran, check = _run_with(_tracker(age_seconds=SKE_TIMEOUT, aware=False))
        self.assertTrue(ran)
        check.assert_called_once()


class TestThreadMachineryIsGone(unittest.TestCase):
    """`__main__` must not reintroduce the per-worker thread or /start.

    Source-level assertions: importing __main__ builds the Connexion app, which
    is far heavier than what this pins.
    """

    @classmethod
    def setUpClass(cls):
        cls.source = (
            pathlib.Path(__file__).resolve().parents[1] / "__main__.py"
        ).read_text()
        cls.tree = ast.parse(cls.source)

    def test_threading_is_not_imported(self):
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertNotIn("threading", imported)
        self.assertNotIn("time", imported)

    def test_no_start_or_stop_route_is_registered(self):
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                for arg in decorator.args:
                    if isinstance(arg, ast.Constant) and arg.value in ("/start", "/stop"):
                        self.fail("{0} route is registered by {1}".format(arg.value, node.name))

    def test_cron_registration_is_guarded_for_non_uwsgi_environments(self):
        guarded = False
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Try):
                continue
            imports_decorators = any(
                isinstance(child, ast.ImportFrom) and child.module == "uwsgidecorators"
                for child in ast.walk(node)
            )
            handles_import_error = any(
                isinstance(handler.type, ast.Name) and handler.type.id == "ImportError"
                for handler in node.handlers
            )
            if imports_decorators and handles_import_error:
                guarded = True
        self.assertTrue(guarded, "uwsgidecorators import must tolerate non-uWSGI environments")

    def test_the_cron_handler_goes_through_the_debounce(self):
        # Firing ssh_key_expiry_check() directly would re-send notifications on
        # any second fire; the handler must call the gated runner.
        self.assertIn("run_ssh_key_expiry_if_due(app)", self.source)
        self.assertNotIn("check_sshkey_expiry_and_email(app)", self.source)


if __name__ == "__main__":
    unittest.main()

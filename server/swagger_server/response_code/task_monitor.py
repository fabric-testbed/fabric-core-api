import os
from datetime import datetime, timezone

from swagger_server.database.models.tasktracker import TaskTimeoutTracker
from swagger_server.response_code.sshkeys_utils import ssh_key_expiry_check


# ssh key expiry (ske)
def check_sshkey_expiry_and_email(app):
    """Run the SSH key expiry check unconditionally, inside an app context."""
    with app.app_context():
        print("Checking SSH key expiry...")
        ssh_key_expiry_check()


def debounce_seconds(ske) -> int:
    """Minimum gap between two SSH key expiry runs.

    Half the configured timeout, NOT the full window: ``last_updated`` records
    when the previous run *started*, so a once-a-day schedule lands a fraction
    of a second inside an 86400s window and would skip the day entirely.
    """
    return max(int(ske.timeout_in_seconds) // 2, 1)


def run_ssh_key_expiry_if_due(app) -> bool:
    """Run the SSH key expiry check unless it already ran recently.

    Cadence belongs to the uWSGI master cron (see ``__main__``); this debounce
    only stops a second trigger in the same day -- a reload landing on the cron
    minute, or a manual invocation -- from re-sending notifications that have
    already gone out. Returns True when the check actually ran.
    """
    with app.app_context():
        ske_name = os.getenv('SKE_NAME')
        ske = TaskTimeoutTracker.query.filter_by(name=ske_name).one_or_none()
        if not ske:
            print("SSH key expiry: no '{0}' tracker row found; skipping".format(ske_name))
            return False
        last_updated = ske.last_updated
        if last_updated.tzinfo is None:
            last_updated = last_updated.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - last_updated).total_seconds()
        debounce = debounce_seconds(ske)
        if age < debounce:
            print("SSH key expiry: ran {0:.0f}s ago (< {1}s); skipping".format(age, debounce))
            return False
        print("Checking SSH key expiry...")
        ssh_key_expiry_check()
        return True

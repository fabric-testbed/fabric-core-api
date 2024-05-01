import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.tasktracker import TaskTimeoutTracker


def init_task_timeout_tracker():
    """
    Initialize/Update the TaskTimeoutTracker table
    - author_refresh_check
    - public_signing_key
    - token_revocation_list
    """
    try:
        now = datetime.now(timezone.utc)
        # core_api_metrics
        cam = TaskTimeoutTracker.query.filter_by(name=os.getenv('CAM_NAME')).one_or_none()
        print(cam)
        if not cam:
            stmt = insert(db.Table('task_timeout_tracker')).values(
                description=os.getenv('CAM_DESCRIPTION'),
                id=1,
                last_updated=(now - timedelta(seconds=(int(os.getenv('CAM_TIMEOUT_IN_SECONDS')) + 1))),
                name=os.getenv('CAM_NAME'),
                timeout_in_seconds=int(os.getenv('CAM_TIMEOUT_IN_SECONDS')),
                uuid=str(uuid4()),
                value=None,
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
            db.session.commit()
            consoleLogger.info(
                "CREATE: entry in 'task_timeout_tracker' table for name: {0}".format(os.getenv('CAM_NAME')))
        else:
            cam.description = os.getenv('CAM_DESCRIPTION')
            cam.name = os.getenv('CAM_NAME')
            cam.timeout_in_seconds = os.getenv('CAM_TIMEOUT_IN_SECONDS')
            db.session.commit()
        # public_signing_key
        psk = TaskTimeoutTracker.query.filter_by(name=os.getenv('PSK_NAME')).one_or_none()
        print(psk)
        if not psk:
            stmt = insert(db.Table('task_timeout_tracker')).values(
                description=os.getenv('PSK_DESCRIPTION'),
                id=2,
                last_updated=(now - timedelta(seconds=(int(os.getenv('PSK_TIMEOUT_IN_SECONDS')) + 1))),
                name=os.getenv('PSK_NAME'),
                timeout_in_seconds=int(os.getenv('PSK_TIMEOUT_IN_SECONDS')),
                uuid=str(uuid4()),
                value=None,
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
            db.session.commit()
            consoleLogger.info(
                "CREATE: entry in 'task_timeout_tracker' table for name: {0}".format(os.getenv('PSK_NAME')))
        else:
            psk.description = os.getenv('PSK_DESCRIPTION')
            psk.name = os.getenv('PSK_NAME')
            psk.timeout_in_seconds = os.getenv('PSK_TIMEOUT_IN_SECONDS')
            db.session.commit()
        # token_revocation_list
        trl = TaskTimeoutTracker.query.filter_by(name=os.getenv('TRL_NAME')).one_or_none()
        print(trl)
        if not trl:
            stmt = insert(db.Table('task_timeout_tracker')).values(
                description=os.getenv('TRL_DESCRIPTION'),
                id=3,
                last_updated=(now - timedelta(seconds=(int(os.getenv('TRL_TIMEOUT_IN_SECONDS')) + 1))),
                name=os.getenv('TRL_NAME'),
                timeout_in_seconds=int(os.getenv('TRL_TIMEOUT_IN_SECONDS')),
                uuid=str(uuid4()),
                value=None,
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
            db.session.commit()
            consoleLogger.info(
                "CREATE: entry in 'task_timeout_tracker' table for name: {0}".format(os.getenv('TRL_NAME')))
        else:
            trl.description = os.getenv('TRL_DESCRIPTION')
            trl.name = os.getenv('TRL_NAME')
            trl.timeout_in_seconds = os.getenv('TRL_TIMEOUT_IN_SECONDS')
            db.session.commit()
        reset_serial_sequence(db_table='task_timeout_tracker', seq_value=3)
    except Exception as exc:
        consoleLogger.error(exc)


def reset_serial_sequence(db_table: str, seq_value: int):
    try:
        stmt = text('SELECT setval(pg_get_serial_sequence(\'{0}\',\'id\'),{1});'.format(db_table, str(seq_value)))
        db.session.execute(stmt)
        db.session.commit()
        consoleLogger.info('  - Table: {0}, sequence_id: {1}'.format(db_table, str(seq_value)))
    except Exception as exc:
        consoleLogger.error(exc)


if __name__ == '__main__':
    app.app_context().push()

    #  public | task_timeout_tracker      | table | postgres
    consoleLogger.info('restore task_timeout_tracker table')
    init_task_timeout_tracker()

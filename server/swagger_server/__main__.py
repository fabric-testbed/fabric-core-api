#!/usr/bin/env python3
import os
import threading
from time import sleep

import connexion
from connexion.exceptions import BadRequestProblem, Forbidden, Unauthorized, ValidationError
from flask_migrate import Migrate

from swagger_server import encoder
from swagger_server.database.db import db
from swagger_server.response_code.cors_response import cors_400, cors_401, cors_403
from swagger_server.response_code.task_monitor import check_sshkey_expiry_and_email

"""
---------------------------------------------------------------------------------
BEGIN: Imports needed for alembic and flask using multiple model definition files
---------------------------------------------------------------------------------
"""
from swagger_server.database.models.announcements import FabricAnnouncements
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin, TrackingMixin
from swagger_server.database.models.people import EmailAddresses, Organizations, FabricGroups, FabricPeople, \
    FabricRoles
from swagger_server.database.models.preferences import FabricPreferences
from swagger_server.database.models.profiles import FabricProfilesPeople, FabricProfilesProjects, \
    ProfilesPersonalPages, ProfilesKeywords, ProfilesOtherIdentities, ProfilesReferences
from swagger_server.database.models.projects import FabricProjects, ProjectsTags
from swagger_server.database.models.storage import FabricStorage, StorageSites
from swagger_server.database.models.tasktracker import TaskTimeoutTracker
from swagger_server.database.models.core_api_metrics import CoreApiMetrics
from swagger_server.database.models.quotas import FabricQuotas
"""
-------------------------------------------------------------------------------
END: Imports needed for alembic and flask using multiple model definition files
-------------------------------------------------------------------------------
"""


def flask_bad_request(exception):
    return cors_400(details='Validation error or other malformed request type: {0}'.format(exception))


def flask_unauthorized(exception):
    return cors_401(details='Not authorized to access this endpoint: {0}'.format(exception))


def flask_forbidden(exception):
    return cors_403(details='Forbidden to access this endpoint: {0}'.format(exception))


def main():
    connex_app = connexion.App(__name__, specification_dir='./swagger/')
    connex_app.app.json_encoder = encoder.JSONEncoder
    connex_app.add_api('swagger.yaml', arguments={'title': 'FABRIC Core API'}, pythonic_params=True)
    connex_app.add_error_handler(BadRequestProblem, flask_bad_request)
    connex_app.add_error_handler(ValidationError, flask_bad_request)
    connex_app.add_error_handler(Unauthorized, flask_unauthorized)
    connex_app.add_error_handler(Forbidden, flask_forbidden)

    app = connex_app.app

    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
        os.getenv('POSTGRES_USER'),
        os.getenv('POSTGRES_PASSWORD'),
        os.getenv('POSTGRES_SERVER'),
        os.getenv('POSTGRES_PORT'),
        os.getenv('POSTGRES_DB')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True

    db.init_app(app)
    migrate = Migrate(app, db)

    logger = app.logger
    logger.info("Starting FABRIC Core API")

    return app


app = main()

thread_event = threading.Event()


def ske_task_monitor(app, cooldown: int = 86400):
    while thread_event.is_set():
        # check SSH key expiry and send emails as needed
        check_sshkey_expiry_and_email(app)
        print(' - Sleeping for {} seconds...'.format(str(cooldown)))
        sleep(int(cooldown))


@app.before_first_request
def create_tables():
    db.create_all()


@app.route("/start", methods=["GET"])
def start_task_monitor():
    """
    Start the task monitor
    - only starts once on the condition of value != 'running'
    - needs to be manually set back to None when a new version is deployed or service is restarted
      to restart the timer thread
    """
    try:
        ske = TaskTimeoutTracker.query.filter_by(name=os.getenv('SKE_NAME')).first()
        if str(ske.value).casefold() != 'running':
            thread_event.set()
            thread = threading.Thread(target=ske_task_monitor, args=(app, ske.timeout_in_seconds))
            thread.start()
            ske.value = 'running'
            db.session.commit()
            return "Task Monitor Started"
        else:
            return "Task Monitor Already Running"
    except Exception as error:
        return str(error)


# TODO: remove /stop on production deployment
# @app.route("/stop", methods=["GET"])
# def stop_task_monitor():
#     try:
#         ske = TaskTimeoutTracker.query.filter_by(name=os.getenv('SKE_NAME')).first()
#         if str(ske.value).casefold() == 'running':
#             thread_event.clear()
#             ske.value = None
#             db.session.commit()
#             return "Task Monitor Stopped"
#         else:
#             return "Task Monitor Already Stopped"
#     except Exception as error:
#         return str(error)


if __name__ == '__main__':
    app = main()
    app.run(port=6000, debug=True)

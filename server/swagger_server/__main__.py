#!/usr/bin/env python3
import atexit
import os
import threading

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
INTERVAL = 5  # Seconds

# Shared data structures accessible to both threads and Flask routes
shared_data = {}
data_lock = threading.Lock()

# Timer handler
timer_task = threading.Timer(0, lambda x: None, ())


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

    def terminate_timer():
        global timer_task
        timer_task.cancel()

    def background_process():
        global shared_data
        global timer_task
        with data_lock:
            check_sshkey_expiry_and_email(app=app)

        # Schedule the next execution
        timer_task = threading.Timer(10, background_process)
        timer_task.start()

    def initialize_task():
        global timer_task
        timer_task = threading.Timer(10, background_process)
        timer_task.daemon = True
        timer_task.start()

    # Start the background process
    initialize_task()
    atexit.register(terminate_timer)

    return app


app = main()


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    app = main()
    app.run(port=6000, debug=True)

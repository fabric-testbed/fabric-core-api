#!/usr/bin/env python3
import os

import connexion
from connexion.exceptions import BadRequestProblem, Forbidden, Unauthorized, ValidationError
from flask_migrate import Migrate

from swagger_server import encoder
from swagger_server.database.db import db
from swagger_server.response_code.cors_response import cors_400, cors_401, cors_403, problem_detail
from swagger_server.response_code.task_monitor import run_ssh_key_expiry_if_due

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
    return cors_400(
        details='Validation error or other malformed request type: {0}'.format(problem_detail(exception)))


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


@app.before_first_request
def create_tables():
    db.create_all()


def ske_cron_handler(signum=None):
    """uWSGI cron entry point for the SSH key expiry notifications."""
    try:
        run_ssh_key_expiry_if_due(app)
    except Exception as error:
        app.logger.error('ssh_key_expiry: scheduled run failed: {0}'.format(error))


# SSH key expiry notifications are scheduled by the uWSGI MASTER process and
# dispatched to a live worker.
#
# The previous implementation started a threading.Thread inside whichever worker
# served GET /start. uWSGI recycles workers at max-requests (see core-api.ini), so
# that thread was destroyed along with its process -- silently, with no error and
# no restart -- while the tracker row still read 'running', which made GET /start
# refuse to start a replacement. Production lost the task within days of every
# start, deploy or no deploy. The master is never recycled, so the schedule cannot
# be lost, and there is nothing left to reset by hand after a redeploy.
#
# SKE_CRON_HOUR / SKE_CRON_MINUTE follow uWSGI cron semantics, where -1 is a
# wildcard; the defaults fire once a day at 06:00 in the container's timezone.
# Outside uWSGI (local `flask run`, unit tests) the import fails and no schedule
# is registered.
try:
    from uwsgidecorators import cron as uwsgi_cron
except ImportError:
    pass
else:
    uwsgi_cron(
        int(os.getenv('SKE_CRON_MINUTE', '0')),
        int(os.getenv('SKE_CRON_HOUR', '6')),
        -1, -1, -1
    )(ske_cron_handler)


if __name__ == '__main__':
    app = main()
    app.run(port=6000, debug=os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true'))

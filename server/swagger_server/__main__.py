#!/usr/bin/env python3
import os

import connexion
from connexion.exceptions import BadRequestProblem, Unauthorized, Forbidden, ValidationError
from flask_migrate import Migrate

from swagger_server import encoder
from swagger_server.database.db import db
from swagger_server.response_code.cors_response import cors_400, cors_401, cors_403

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


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    logger.info("Starting FABRIC Core API")
    app.run(port=5000, debug=True)

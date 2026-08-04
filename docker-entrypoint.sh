#!/usr/bin/env bash
#
# Entry point for the Core API container.
#
# Notes for one-time DB bootstrap (run from inside the container):
#   source .env && python -m flask db init
#   python -m flask db migrate
#   python -m flask db upgrade
#
# Restore / sync DB from COmanage:
#   python -m server.swagger_server.backup.utils.db_restore
#   python -m server.swagger_server.backup.utils.db_version_updates
#   python -m server.swagger_server.database.utils.init_task_tracker

set -e

if [[ "$1" == 'run_server' ]]; then
    source .env

    # Inject the deployment's external server URL into the OpenAPI spec
    if [[ -n "${CORE_API_SERVER_URL}" ]]; then
        sed -i '/servers:/!b;n;c- url: '"${CORE_API_SERVER_URL}"'/' \
            /code/server/swagger_server/swagger/swagger.yaml
    fi

    # The venv is populated at image build time via `uv sync` (see Dockerfile).
    exec uwsgi --virtualenv /code/.venv --ini server/core-api.ini
else
    exec "$@"
fi

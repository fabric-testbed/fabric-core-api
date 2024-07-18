#!/usr/bin/env bash

### Initialize and Restore DB ###
# docker exec api-flask-server /bin/bash -c \
#   "source .env; source .venv/bin/activate; server/swagger_server/database/utils/init_and_restore_db.sh"

pwd

python -m flask db init
python -m flask db migrate
python -m flask db upgrade

python -m server.swagger_server.database.utils.init_task_tracker
python -m server.swagger_server.backup.utils.db_restore
python -m server.swagger_server.backup.utils.db_version_updates

exit 0;
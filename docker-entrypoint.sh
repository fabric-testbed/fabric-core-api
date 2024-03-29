#!/usr/bin/env bash
# NOTE: database must be manually setup the first time
#    source .env && source .ven/bin/activate
#    python -m flask db init
#    python -m flask db migrate
#    python -m flask db upgrade
# NOTE: load / verify database against COmanage or restore from backup
#    python -m server.swagger_server.backup.utils.db_restore

if [[ "$1" == 'run_server' ]]; then
    # setup virtual environment
    source .env
    pip install -U pip
    pip install virtualenv
    virtualenv -p /usr/local/bin/python .venv
    source .venv/bin/activate
    pip install -r requirements.txt

    # update swagger.yaml file
    if [[ ! -z ${CORE_API_SERVER_URL} ]]; then
        sed -i '/servers:/!b;n;c- url: '${CORE_API_SERVER_URL}'/' /code/server/swagger_server/swagger/swagger.yaml
    fi

    # run the server
    uwsgi --virtualenv ./.venv --ini server/core-api.ini
else
    exec "$@"
fi

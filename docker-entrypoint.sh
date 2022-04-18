#!/usr/bin/env bash

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

    # setup database
    python -m flask db init
    python -m flask db migrate
    python -m flask db upgrade

    # load / verify database against COmanage
    # TODO: db_load and db_verify scripts

    # run the server
    uwsgi --virtualenv ./.venv --ini server/core-api.ini
else
    exec "$@"
fi

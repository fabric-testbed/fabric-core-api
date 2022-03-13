# FABRIC Core API

Python (Flask) based ReSTful API for FABRIC Core Services based on COmanage registry contents

- User Information Service (UIS)
- Project Registry (PR)

**DISCLAIMER: The code herein may not be up to date nor compliant with the most recent package and/or security notices. The frequency at which this code is reviewed and updated is based solely on the lifecycle of the project for which it was written to support, and is not actively maintained outside of that scope. Use at your own risk.**

## Table of Contents

TODO

## Configuration

Copy the `env.template` file as `.env` and populate according to your environment

```ini
# Configuration

### Core API
export CORE_API_SERVER_URL=http://127.0.0.1:5000
export CORE_API_CO_USER_IDENTIFIER=registryid
export CORE_API_DEFAULT_LIMIT=5
export CORE_API_MAX_LIMIT=20
export CORE_API_JSON_RESPONSE_INDENT=2
export CORE_API_DEFAULT_FACILITY=FABRIC

### COmanage API User
export COMANAGE_API_USER=co_123.api-user-name
export COMANAGE_API_PASS=xxxx-xxxx-xxxx-xxxx
export COMANAGE_API_CO_NAME=RegistryName
export COMANAGE_API_CO_ID=123
export COMANAGE_API_URL=https://FQDN_OF_REGISTRY
export COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID=123

### COmanage COU IDs
export COU_ID_FACILITY_OPERATORS=100
export COU_ID_PROJECT_LEADS=101
export COU_ID_PROJECTS=102
export COU_ID_ACTIVE_USERS=103
export COU_ID_APPROVAL_COMMITTEE=104
export COU_ID_JUPYTERHUB=105

### Postgres
export POSTGRES_SERVER=127.0.0.1
export POSTGRES_PORT=5432
export POSTGRES_PASSWORD=postgres
export POSTGRES_USER=postgres
export POSTGRES_DB=postgres
export PGDATA=/var/lib/postgresql/data/pg_data
export PGDATA_HOST=./data

### Python Path
export PYTHONPATH=$(pwd)/server:${PYTHONPATH}

### Flask
export FLASK_APP=swagger_server.__main__:app

### Nginx
```

## Usage

### Local Development

Flask is run on host while database is run in Docker

1. Set up Python virtual environment

    ```console
    virtualenv -p /usr/local/bin/python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Set the environment variables and pull the images

    ```console
    source .env
    docker-compose pull
    ```

3. Bring up database

    ```console
    docker-compose up -d database
    ```

    Populate database
    
    ```console
    python -m flask db init
    python -m flask db migrate
    python -m flask db upgrade
    python -m server.swagger_server.database.db_load
    ```

4. Run core-api Flask application

    ```console
    python -m server.swagger_server
    ```


## References

- Connexion: [https://connexion.readthedocs.io/en/stable/](https://connexion.readthedocs.io/en/stable/)
- Flask: [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
- Flask SQLAlchemy: [https://flask-sqlalchemy.palletsprojects.com](https://flask-sqlalchemy.palletsprojects.com)
- Flask Migrate: [https://flask-migrate.readthedocs.io/en/latest/](https://flask-migrate.readthedocs.io/en/latest/)
- OpenAPI Specification: [https://swagger.io/specification/](https://swagger.io/specification/)
- Swagger: [https://swagger.io](https://swagger.io)


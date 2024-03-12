# FABRIC Core API

Python (Flask) based ReSTful API for FABRIC Core Services based on COmanage registry contents

- User Information Service (UIS)
- Project Registry (PR)

**DISCLAIMER: The code herein may not be up to date nor compliant with the most recent package and/or security notices. The frequency at which this code is reviewed and updated is based solely on the lifecycle of the project for which it was written to support, and is not actively maintained outside of that scope. Use at your own risk.**

## Table of Contents

- [API documentation](./docs/README.md)
- [Configuration](#config)
- [Usage](#usage)
- [References](#references)

## <a name="config"></a>Configuration

Copy the `env.template` file as `.env` and populate according to your environment

```ini
# Configuration

### Core API
export CORE_API_DEPLOYMENT_TIER=alpha
export CORE_API_SERVER_URL=https://127.0.0.1:8443  # local deployment
#export CORE_API_SERVER_URL=http://127.0.0.1:6000  # docker deployment
export CORE_API_CO_USER_IDENTIFIER=registryid
export CORE_API_USER_UPDATE_FREQUENCY_IN_SECONDS=60
export CORE_API_DEFAULT_LIMIT=5
export CORE_API_MAX_LIMIT=20
export CORE_API_JSON_RESPONSE_INDENT=2
export CORE_API_DEFAULT_FACILITY=FABRIC
export CORE_API_401_UNAUTHORIZED_TEXT="Please Log in (or Sign up) on the FABRIC Portal"

### Announcements
export MAX_ACTIVE_CAROUSEL_ITEMS=10

# Task Timeout Interval
export PSK_DESCRIPTION='Public Signing Key'
export PSK_NAME='public_signing_key'
export PSK_TIMEOUT_IN_SECONDS=86400
export TRL_DESCRIPTION='Token Revocation List'
export TRL_NAME='token_revocation_list'
export TRL_TIMEOUT_IN_SECONDS=300

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
export COU_ID_PORTAL_ADMINS=106
export COU_NAME_FACILITY_OPERATORS=facility-operators
export COU_NAME_PROJECT_LEADS=project-leads
export COU_NAME_PROJECTS=projects
export COU_NAME_ACTIVE_USERS=fabric-active-users
export COU_NAME_APPROVAL_COMMITTEE=approval-committee
export COU_NAME_JUPYTERHUB=Jupyterhub
export COU_NAME_PORTAL_ADMINS=portal-admins

### Vouch Proxy
export VOUCH_COOKIE_NAME=COOKIE_NAME
export VOUCH_JWT_SECRET="xxxx-xxxx-xxxx-xxxx"

### Postgres
export POSTGRES_SERVER=127.0.0.1  # local development
#export POSTGRES_SERVER=database  # docker deployment
export POSTGRES_PORT=5432
export POSTGRES_PASSWORD=xxxx-xxxx-xxxx-xxxx
export POSTGRES_USER=postgres
export POSTGRES_DB=postgres
export PGDATA=/var/lib/postgresql/data/pg_data
export PGDATA_HOST=./data

### SSH Keys
export SSH_KEY_ALGORITHM="ecdsa" # "rsa" or "ecdsa"
export SSH_BASTION_KEY_VALIDITY_DAYS=5
export SSH_SLIVER_KEY_VALIDITY_DAYS=10
export SSH_GARBAGE_COLLECT_AFTER_DAYS=10
# for bastion host to have a shared secret when calling /bastionkeys
export SSH_KEY_SECRET="xxxx-xxxx-xxxx-xxxx"
export SSH_KEY_QTY_LIMIT=5

### Python Path
export PYTHONPATH=$(pwd)/server:${PYTHONPATH}

### Flask
export FLASK_APP=swagger_server.__main__:app

### Nginx
export NGINX_ACCESS_CONTROL_ALLOW_ORIGIN="https://127.0.0.1:8443"

### Projects
export PROJECTS_RENEWAL_PERIOD_IN_DAYS=365

### Ansible
export ANSIBLE_AUTHORIZATION_TOKEN='AnsibleAuthorizationToken'

### FABRIC
export FABRIC_CORE_API=https://COREAPI
export FABRIC_CREDENTIAL_MANAGER=https://CREDENTIALMANAGER
```

## <a name="usage"></a>Usage

### Local Development

Flask is run on host while database is run in Docker

1. Set up Python virtual environment

    ```console
    virtualenv -p <PATH_TO_PYTHON3> venv
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


## <a name="references"></a>References

- Connexion: [https://connexion.readthedocs.io/en/stable/](https://connexion.readthedocs.io/en/stable/)
- Flask: [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
- Flask SQLAlchemy: [https://flask-sqlalchemy.palletsprojects.com](https://flask-sqlalchemy.palletsprojects.com)
- Flask Migrate: [https://flask-migrate.readthedocs.io/en/latest/](https://flask-migrate.readthedocs.io/en/latest/)
- OpenAPI Specification: [https://swagger.io/specification/](https://swagger.io/specification/)
- Swagger: [https://swagger.io](https://swagger.io)


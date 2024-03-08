# Backup and Restore database

Commands used relate to full docker based deployment

## Backup 

### `db_export.py` script

The `db_export.py` file defines a full model backup for all database tables for the version it has been specified for and should be used for periodic backups.

At times the data model may change in anticipation of a new release. When this happens the updated `db_export.py` file should be pushed to the running container prior to backup.

```
docker cp server/swagger_server/backup/utils/db_export.py api-flask-server:/code/server/swagger_server/backup/utils/db_export.py
```

### run script from the container

Exec onto the running container

```
docker exec -ti api-flask-server /bin/bash
```

Run the backup script which saves database tables as json file

```
source .env
source .venv/bin/activate
python -m server.swagger_server.backup.utils.db_export
exit
```

Copy the backup files to the local filesystem

```
docker cp api-flask-server:/code/server/swagger_server/backup/data .
```

A copy of the `data` directory will now be locally available.

## Restore

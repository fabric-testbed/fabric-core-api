# v1.4.1 to v1.4.2 migration

Prior to deploying v1.4.2 the updated DB export script should be used to preserve the v1.4.1 data as JSON files

## Export DB

Using [beta-3.fabric-testbed.net]() as an example.

Checkout the updated v1.4.2 code files but do not build a new image yet

```console
git fetch origin -p
git stash
git checkout main
git pull
git checkout v1.4.2
git stash pop
```
Copy the DB export script and backup files to the running v1.4.1 container

```console 
docker cp server/swagger_server/backup api-flask-server:/code/server/swagger_server/
docker cp server/swagger_server/response_code/core_api_utils.py api-flask-server:/code/server/swagger_server/response_code/
```

Run the export script from within the `api-flask-server` container

```console
docker exec -ti api-flask-server /bin/bash
```

```console
root@5afd7339dcdd:/code# source .env
root@5afd7339dcdd:/code# source .venv/bin/activate
(.venv) root@5afd7339dcdd:/code# python -m server.swagger_server.backup.utils.db_export
2023-02-17 20:04:47,408 [INFO] Exporter for API version 1.4.0
2023-02-17 20:04:47,408 [INFO] dump alembic_version table
2023-02-17 20:04:47,438 [INFO] dump announcements table
2023-02-17 20:04:47,504 [INFO] dump groups table
2023-02-17 20:04:47,520 [INFO] dump people table
2023-02-17 20:04:47,886 [INFO] dump people_email_addresses table
2023-02-17 20:04:47,891 [INFO] dump people_organizations table
2023-02-17 20:04:47,896 [INFO] dump people_roles table
2023-02-17 20:04:47,905 [INFO] dump preferences table
2023-02-17 20:04:48,062 [INFO] dump profiles_keywords table
2023-02-17 20:04:48,066 [INFO] dump profiles_other_identities table
2023-02-17 20:04:48,069 [INFO] dump profiles_people table
2023-02-17 20:04:48,288 [INFO] dump profiles_personal_pages table
2023-02-17 20:04:48,290 [INFO] dump profiles_projects table
2023-02-17 20:04:48,338 [INFO] dump profiles_references table
2023-02-17 20:04:48,340 [INFO] dump projects table
2023-02-17 20:04:48,412 [INFO] dump projects_creators table
2023-02-17 20:04:48,413 [INFO] dump projects_members table
2023-02-17 20:04:48,414 [INFO] dump projects_owners table
2023-02-17 20:04:48,415 [INFO] dump projects_tags table
2023-02-17 20:04:48,418 [INFO] dump sshkeys table
2023-02-17 20:04:48,455 [INFO] dump testbed_info table
```

Verify the contents of the export

```console
(.venv) root@5afd7339dcdd:/code# ls -lh /code/server/swagger_server/backup/data/
total 680K
-rw-r--r-- 1 root root   78 Feb 17 20:04 alembic_version-v1.4.0.json
-rw-r--r-- 1 root root   25 Feb 17 20:04 announcements-v1.4.0.json
-rw-r--r-- 1 root root  15K Feb 17 20:04 groups-v1.4.0.json
-rw-r--r-- 1 root root  68K Feb 17 20:04 people-v1.4.0.json
-rw-r--r-- 1 root root  22K Feb 17 20:04 people_email_addresses-v1.4.0.json
-rw-r--r-- 1 root root 9.0K Feb 17 20:04 people_organizations-v1.4.0.json
-rw-r--r-- 1 root root  72K Feb 17 20:04 people_roles-v1.4.0.json
-rw-r--r-- 1 root root 309K Feb 17 20:04 preferences-v1.4.0.json
-rw-r--r-- 1 root root   29 Feb 17 20:04 profiles_keywords-v1.4.0.json
-rw-r--r-- 1 root root   37 Feb 17 20:04 profiles_other_identities-v1.4.0.json
-rw-r--r-- 1 root root  31K Feb 17 20:04 profiles_people-v1.4.0.json
-rw-r--r-- 1 root root   35 Feb 17 20:04 profiles_personal_pages-v1.4.0.json
-rw-r--r-- 1 root root 6.3K Feb 17 20:04 profiles_projects-v1.4.0.json
-rw-r--r-- 1 root root   31 Feb 17 20:04 profiles_references-v1.4.0.json
-rw-r--r-- 1 root root  14K Feb 17 20:04 projects-v1.4.0.json
-rw-r--r-- 1 root root  859 Feb 17 20:04 projects_creators-v1.4.0.json
-rw-r--r-- 1 root root 3.5K Feb 17 20:04 projects_members-v1.4.0.json
-rw-r--r-- 1 root root 1.4K Feb 17 20:04 projects_owners-v1.4.0.json
-rw-r--r-- 1 root root 6.4K Feb 17 20:04 projects_tags-v1.4.0.json
-rw-r--r-- 1 root root  71K Feb 17 20:04 sshkeys-v1.4.0.json
-rw-r--r-- 1 root root  585 Feb 17 20:04 testbed_info-v1.4.0.json
(.venv) root@5afd7339dcdd:/code# exit
exit
```

Copy the JSON files to the host to be picked up by the next build of the container

```console
cd server/swagger_server/backup/
docker cp api-flask-server:/code/server/swagger_server/backup/data .
```

Verify the contents (match timestamp and file size from above)

```console
$ ls -lh data/
total 680K
-rw-r--r-- 1 nrig-service nrig-service   78 Feb 17 20:04 alembic_version-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service   25 Feb 17 20:04 announcements-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service  15K Feb 17 20:04 groups-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service  22K Feb 17 20:04 people_email_addresses-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service 9.0K Feb 17 20:04 people_organizations-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service  72K Feb 17 20:04 people_roles-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service  68K Feb 17 20:04 people-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service 309K Feb 17 20:04 preferences-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service   29 Feb 17 20:04 profiles_keywords-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service   37 Feb 17 20:04 profiles_other_identities-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service  31K Feb 17 20:04 profiles_people-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service   35 Feb 17 20:04 profiles_personal_pages-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service 6.3K Feb 17 20:04 profiles_projects-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service   31 Feb 17 20:04 profiles_references-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service  859 Feb 17 20:04 projects_creators-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service 3.5K Feb 17 20:04 projects_members-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service 1.4K Feb 17 20:04 projects_owners-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service 6.4K Feb 17 20:04 projects_tags-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service  14K Feb 17 20:04 projects-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service   71K Feb 17 20:04 sshkeys-v1.4.0.json
-rw-r--r-- 1 nrig-service nrig-service  585 Feb 17 20:04 testbed_info-v1.4.0.json
```

## Backup DB

It is also worth getting a traditional database back up file using `pg_dump` in the event that something goes wrong during the deployment of the new code. This provides a safe way to roll-back to the original database.

Dump the database from the `api-database` container using `pg_dump`

```console
docker exec -u postgres api-database /bin/bash -c "pg_dump postgres > /tmp/core_api_backup_$(date +'%m-%d-%Y')"
```

Verify that the backup was created and save to local host (date and size should match)

```console
$ docker exec -u postgres api-database ls -lh /tmp
total 232K
-rw-r--r-- 1 postgres postgres 231K Feb 19 14:32 core_api_backup_02-19-2023

$ docker cp api-database:/tmp/core_api_backup_$(date +'%m-%d-%Y') .
$ ls -lh ./core_api_backup_$(date +'%m-%d-%Y')
-rw-r--r-- 1 nrig-service nrig-service 231K Feb 19 14:32 ./core_api_backup_02-19-2023
```

## Deploy v1.4.2

Stop and remove existing containers (easiest to start as the `root` user)

```console
$ cd /home/nrig-service/fabric-core-api/helper_scripts/
$ ./reset-to-clean.sh
[INFO] stop and remove docker containers
/usr/local/lib/python3.6/site-packages/paramiko/transport.py:33: CryptographyDeprecationWarning: Python 3.6 is no longer supported by the Python core team. Therefore, support for it is deprecated in cryptography and will be removed in a future release.
  from cryptography.hazmat.backends import default_backend
Stopping api-flask-server ... done
Stopping api-nginx        ... done
Stopping api-database     ... done
Stopping api-vouch-proxy  ... done
/usr/local/lib/python3.6/site-packages/paramiko/transport.py:33: CryptographyDeprecationWarning: Python 3.6 is no longer supported by the Python core team. Therefore, support for it is deprecated in cryptography and will be removed in a future release.
  from cryptography.hazmat.backends import default_backend
Going to remove api-flask-server, api-nginx, api-database, api-vouch-proxy
Removing api-flask-server ... done
Removing api-nginx        ... done
Removing api-database     ... done
Removing api-vouch-proxy  ... done
[INFO] remove directory: data/pg_data
[INFO] remove directory: migrations
[INFO] restore directory: migrations
[INFO] completed - check files prior to use
### remove the previous database files after they've been backed up ###
$ rm -rf /opt/data/beta/services/coreapi/postgres/pg_data
$ su - nrig-service
```

as the `nrig-service` user

```console
cd fabric-core-api/
git status
git checkout server/swagger_server/logging.ini
git status
git fetch origin -p
git stash
git checkout main
git pull
git checkout v1.4.2
it stash pop
vim server/swagger_server/logging.ini
docker-compose pull
docker system prune
docker-compose build
docker-compose up -d
```

## Restore DB

Run the restore script from the newly deployed `api-flask-server` container

```console
docker exec api-flask-server -ti /bin/bash
```

```console
root@3a4624cc7d51:/code# source .env
root@3a4624cc7d51:/code# source .venv/bin/activate
(.venv) root@3a4624cc7d51:/code# python -m flask db init
  Creating directory /code/migrations/versions ...  done
  Generating /code/migrations/README ...  done
  Generating /code/migrations/alembic.ini ...  done
  Generating /code/migrations/env.py ...  done
  Generating /code/migrations/script.py.mako ...  done
  Please edit configuration/connection/logging settings in '/code/migrations/alembic.ini' before proceeding.
(.venv) root@3a4624cc7d51:/code# python -m flask db migrate -m "initial migration v1.4.2"
INFO  [alembic.env] No changes in schema detected.
(.venv) root@3a4624cc7d51:/code# python -m flask db upgrade
(.venv) root@3a4624cc7d51:/code# python -m server.swagger_server.backup.utils.db_restore
2023-02-19 14:52:46,205 [INFO] Restorer for API version 1.4.0
2023-02-19 14:52:46,205 [INFO] restore announcements table
2023-02-19 14:52:46,240 [INFO]   - Table: announcements, sequence_id: 1
2023-02-19 14:52:46,240 [INFO] restore groups table
2023-02-19 14:52:46,306 [INFO]   - Table: groups, sequence_id: 56
2023-02-19 14:52:46,306 [INFO] restore people_organizations table
2023-02-19 14:52:46,356 [INFO]   - Table: people_organizations, sequence_id: 69
2023-02-19 14:52:46,356 [INFO] restore people table
2023-02-19 14:52:46,497 [INFO]   - Table: people, sequence_id: 67
2023-02-19 14:52:46,497 [INFO] restore people_email_addresses table
2023-02-19 14:52:46,613 [INFO]   - Table: people_email_addresses, sequence_id: 149
2023-02-19 14:52:46,613 [INFO] restore people_roles table
2023-02-19 14:52:46,878 [INFO]   - Table: people_roles, sequence_id: 266
2023-02-19 14:52:46,878 [INFO] restore profiles_people table
2023-02-19 14:52:46,960 [INFO]   - Table: profiles_people, sequence_id: 67
2023-02-19 14:52:46,960 [INFO] restore profiles_other_identities table
2023-02-19 14:52:46,961 [INFO]   - Table: profiles_other_identities, sequence_id: 1
2023-02-19 14:52:46,962 [INFO] restore profiles_personal_pages table
2023-02-19 14:52:46,963 [INFO]   - Table: profiles_personal_pages, sequence_id: 1
2023-02-19 14:52:46,963 [INFO] restore projects table
2023-02-19 14:52:46,994 [INFO]   - Table: projects, sequence_id: 17
2023-02-19 14:52:46,994 [INFO] restore profiles_projects table
2023-02-19 14:52:47,015 [INFO]   - Table: profiles_projects, sequence_id: 17
2023-02-19 14:52:47,015 [INFO] restore profiles_keywords table
2023-02-19 14:52:47,017 [INFO]   - Table: profiles_keywords, sequence_id: 1
2023-02-19 14:52:47,017 [INFO] restore profiles_references table
2023-02-19 14:52:47,018 [INFO]   - Table: profiles_references, sequence_id: 1
2023-02-19 14:52:47,018 [INFO] restore projects_creators table
2023-02-19 14:52:47,033 [INFO] restore projects_members table
2023-02-19 14:52:47,071 [INFO] restore projects_owners table
2023-02-19 14:52:47,091 [INFO] restore projects_tags table
2023-02-19 14:52:47,144 [INFO]   - Table: projects_tags, sequence_id: 161
2023-02-19 14:52:47,144 [INFO] restore preferences table
2023-02-19 14:52:48,410 [INFO]   - Table: preferences, sequence_id: 1057
2023-02-19 14:52:48,410 [INFO] restore sshkeys table
2023-02-19 14:52:48,576 [INFO]   - Table: sshkeys, sequence_id: 91
2023-02-19 14:52:48,577 [INFO] restore testbed_info table
2023-02-19 14:52:48,589 [INFO]   - Table: testbed_info, sequence_id: 2
2023-02-19 14:52:48,589 [INFO] verify project expiry
2023-02-19 14:52:48,682 [INFO] Project: 0be3a5c6-fe9e-41a4-89b6-b6f7ffaa58a8 set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,695 [INFO] Project: 386c1875-b642-4675-bb37-30cbf348b522 set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,711 [INFO] Project: 68503663-9f33-4eb7-b4a4-6f4a6db7abfa set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,725 [INFO] Project: 75bb6177-4166-48ec-aaac-b771f54bc7e7 set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,739 [INFO] Project: 7a1ffe53-1945-4934-93c5-ef6df39b45ac set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,748 [INFO] Project: 937bbd15-1379-4e20-b24f-fa658352eaa0 set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,758 [INFO] Project: 9cb82df2-0559-4011-bb46-1cd03ee3ed63 set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,767 [INFO] Project: ab130149-3298-4446-826a-fe1b4a3fdd82 set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,777 [INFO] Project: ade3a7dd-9488-40f9-8fc6-967de0eea735 set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,790 [INFO] Project: b83d391d-5b74-40a6-8790-872183eb0cee set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,801 [INFO] Project: b9847fa1-13ef-49f9-9e07-ae6ad06cda3f set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,810 [INFO] Project: e8e3ebc2-4cad-4a80-9f17-a516c158b07a set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,819 [INFO] Project: f87459b8-3cb9-47f8-b91c-ccbcb79268fc set expiry: 2024-02-19 14:52:48.665618+00:00
2023-02-19 14:52:48,830 [INFO] Project: fb07edb4-6609-477e-a320-4b19dcf4826c set expiry: 2024-02-19 14:52:48.665618+00:00
(.venv) root@3a4624cc7d51:/code# exit
```

Verify contents from api UI as well as portal

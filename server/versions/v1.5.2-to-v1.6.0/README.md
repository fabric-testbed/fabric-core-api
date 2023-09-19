# v1.5.2 to v1.6.0 migration

Prior to deploying v1.6.0 the updated DB export script should be used to preserve the v1.5.2 data as JSON files

## Export DB

Using [beta-3.fabric-testbed.net]() as an example.

Checkout the updated v1.6.0 code files but do not build a new image yet

```console
git fetch origin -p
git stash
git checkout main
git pull
git checkout v1.6.0
git stash pop   
```
Copy the DB export script to the running v1.5.2 container

```console 
docker cp server/swagger_server/backup/utils/db_export.py api-flask-server:/code/server/swagger_server/backup/utils/db_export.py
```

Run the export script from within the `api-flask-server` container

```console
docker exec -ti api-flask-server /bin/bash
```

```console
root@7d16f14c8e4a:/code# source .env
root@7d16f14c8e4a:/code# source .venv/bin/activate
(.venv) root@7d16f14c8e4a:/code# python -m server.swagger_server.backup.utils.db_export
2023-09-19 19:17:48,428 [INFO] Exporter for API version 1.5.2
2023-09-19 19:17:48,428 [INFO] dump alembic_version table
2023-09-19 19:17:48,476 [INFO] dump announcements table
Unknown string format: None
Unknown string format: None
2023-09-19 19:17:48,541 [INFO] dump groups table
2023-09-19 19:17:48,555 [INFO] dump people table
2023-09-19 19:17:48,818 [INFO] dump people_email_addresses table
2023-09-19 19:17:48,822 [INFO] dump people_organizations table
2023-09-19 19:17:48,825 [INFO] dump people_roles table
2023-09-19 19:17:48,831 [INFO] dump preferences table
2023-09-19 19:17:48,952 [INFO] dump profiles_keywords table
2023-09-19 19:17:48,955 [INFO] dump profiles_other_identities table
2023-09-19 19:17:48,957 [INFO] dump profiles_people table
2023-09-19 19:17:49,085 [INFO] dump profiles_personal_pages table
2023-09-19 19:17:49,087 [INFO] dump profiles_projects table
2023-09-19 19:17:49,129 [INFO] dump profiles_references table
2023-09-19 19:17:49,130 [INFO] dump projects table
2023-09-19 19:17:49,257 [INFO] dump projects_creators table
2023-09-19 19:17:49,258 [INFO] dump projects_members table
2023-09-19 19:17:49,259 [INFO] dump projects_owners table
2023-09-19 19:17:49,260 [INFO] dump projects_storage table
2023-09-19 19:17:49,260 [INFO] dump projects_tags table
2023-09-19 19:17:49,262 [INFO] dump sshkeys table
2023-09-19 19:17:49,296 [INFO] dump storage table
2023-09-19 19:17:49,301 [INFO] dump storage_sites table
2023-09-19 19:17:49,302 [INFO] dump task_timeout_tracker table
2023-09-19 19:17:49,305 [INFO] dump testbed_info table
2023-09-19 19:17:49,308 [INFO] dump token_holders table
2023-09-19 19:17:49,308 [INFO] dump user_org_affiliations table
2023-09-19 19:17:49,312 [INFO] dump user_subject_identifiers table
```

Verify the contents of the export

```console
(.venv) root@7d16f14c8e4a:/code# ls -lh /code/server/swagger_server/backup/data/
total 788K
-rw-r--r-- 1 root root   78 Sep 19 19:17 alembic_version-v1.5.2.json
-rw-r--r-- 1 root root 3.6K Sep 19 19:17 announcements-v1.5.2.json
-rw-r--r-- 1 root root  19K Sep 19 19:17 groups-v1.5.2.json
-rw-r--r-- 1 root root  82K Sep 19 19:17 people-v1.5.2.json
-rw-r--r-- 1 root root  25K Sep 19 19:17 people_email_addresses-v1.5.2.json
-rw-r--r-- 1 root root  11K Sep 19 19:17 people_organizations-v1.5.2.json
-rw-r--r-- 1 root root  75K Sep 19 19:17 people_roles-v1.5.2.json
-rw-r--r-- 1 root root 334K Sep 19 19:17 preferences-v1.5.2.json
-rw-r--r-- 1 root root   29 Sep 19 19:17 profiles_keywords-v1.5.2.json
-rw-r--r-- 1 root root   37 Sep 19 19:17 profiles_other_identities-v1.5.2.json
-rw-r--r-- 1 root root  33K Sep 19 19:17 profiles_people-v1.5.2.json
-rw-r--r-- 1 root root   35 Sep 19 19:17 profiles_personal_pages-v1.5.2.json
-rw-r--r-- 1 root root 6.4K Sep 19 19:17 profiles_projects-v1.5.2.json
-rw-r--r-- 1 root root   31 Sep 19 19:17 profiles_references-v1.5.2.json
-rw-r--r-- 1 root root  16K Sep 19 19:17 projects-v1.5.2.json
-rw-r--r-- 1 root root  861 Sep 19 19:17 projects_creators-v1.5.2.json
-rw-r--r-- 1 root root 3.5K Sep 19 19:17 projects_members-v1.5.2.json
-rw-r--r-- 1 root root 1.5K Sep 19 19:17 projects_owners-v1.5.2.json
-rw-r--r-- 1 root root   91 Sep 19 19:17 projects_storage-v1.5.2.json
-rw-r--r-- 1 root root 5.1K Sep 19 19:17 projects_tags-v1.5.2.json
-rw-r--r-- 1 root root  83K Sep 19 19:17 sshkeys-v1.5.2.json
-rw-r--r-- 1 root root  586 Sep 19 19:17 storage-v1.5.2.json
-rw-r--r-- 1 root root  174 Sep 19 19:17 storage_sites-v1.5.2.json
-rw-r--r-- 1 root root 1.6K Sep 19 19:17 task_timeout_tracker-v1.5.2.json
-rw-r--r-- 1 root root  585 Sep 19 19:17 testbed_info-v1.5.2.json
-rw-r--r-- 1 root root  145 Sep 19 19:17 token_holders-v1.5.2.json
-rw-r--r-- 1 root root 7.1K Sep 19 19:17 user_org_affiliations-v1.5.2.json
-rw-r--r-- 1 root root 8.2K Sep 19 19:17 user_subject_identifiers-v1.5.2.json
(.venv) root@7d16f14c8e4a:/code# exit
exit
```

Copy the JSON files to the host to be picked up by the next build of the container

```console
cd server/swagger_server/backup/data
docker cp api-flask-server:/code/server/swagger_server/backup/data .
cd ./data
mv *.json ../
cd ../
rm -rf data
```

Verify the contents (match timestamp and file size from above)

```console
[nrig-service@beta-3 data]$ ls -lh .
total 788K
-rw-r--r-- 1 nrig-service nrig-service   78 Sep 19 19:17 alembic_version-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 3.6K Sep 19 19:17 announcements-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  19K Sep 19 19:17 groups-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  25K Sep 19 19:17 people_email_addresses-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  11K Sep 19 19:17 people_organizations-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  75K Sep 19 19:17 people_roles-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  82K Sep 19 19:17 people-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 334K Sep 19 19:17 preferences-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service   29 Sep 19 19:17 profiles_keywords-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service   37 Sep 19 19:17 profiles_other_identities-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  33K Sep 19 19:17 profiles_people-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service   35 Sep 19 19:17 profiles_personal_pages-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 6.4K Sep 19 19:17 profiles_projects-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service   31 Sep 19 19:17 profiles_references-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  861 Sep 19 19:17 projects_creators-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 3.5K Sep 19 19:17 projects_members-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 1.5K Sep 19 19:17 projects_owners-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service   91 Sep 19 19:17 projects_storage-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 5.1K Sep 19 19:17 projects_tags-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  16K Sep 19 19:17 projects-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  83K Sep 19 19:17 sshkeys-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  174 Sep 19 19:17 storage_sites-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  586 Sep 19 19:17 storage-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 1.6K Sep 19 19:17 task_timeout_tracker-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  585 Sep 19 19:17 testbed_info-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service  145 Sep 19 19:17 token_holders-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 7.1K Sep 19 19:17 user_org_affiliations-v1.5.2.json
-rw-r--r-- 1 nrig-service nrig-service 8.2K Sep 19 19:17 user_subject_identifiers-v1.5.2.json
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
total 280K
-rw-r--r-- 1 postgres postgres 279K Sep 19 19:31 core_api_backup_09-19-2023

$ docker cp api-database:/tmp/core_api_backup_$(date +'%m-%d-%Y') .
Successfully copied 287kB to /home/nrig-service/fabric-core-api/server/swagger_server/backup/data/.

$ ls -lh ./core_api_backup_$(date +'%m-%d-%Y')
-rw-r--r-- 1 nrig-service nrig-service 279K Sep 19 19:31 ./core_api_backup_09-19-2023
```

## Deploy v1.6.0

Stop and remove existing containers (easiest to start as the `root` user)

```console
[root@beta-3 ~]# cd /home/nrig-service/fabric-core-api/helper_scripts/
[root@beta-3 helper_scripts]# ./reset-to-clean.sh
[INFO] stop and remove docker containers
WARN[0000] The "PYTHONPATH" variable is not set. Defaulting to a blank string.
WARN[0000] The "PYTHONPATH" variable is not set. Defaulting to a blank string.
[+] Stopping 4/4
 ✔ Container api-flask-server  Stopped                                                                                                10.2s
 ✔ Container api-vouch-proxy   Stopped                                                                                                 0.1s
 ✔ Container api-database      Stopped                                                                                                 0.3s
 ✔ Container api-nginx         Stopped                                                                                                 0.3s
WARN[0000] The "PYTHONPATH" variable is not set. Defaulting to a blank string.
WARN[0000] The "PYTHONPATH" variable is not set. Defaulting to a blank string.
Going to remove api-flask-server, api-vouch-proxy, api-nginx, api-database
[+] Removing 4/4
 ✔ Container api-database      Removed                                                                                                 0.0s
 ✔ Container api-flask-server  Removed                                                                                                 0.3s
 ✔ Container api-vouch-proxy   Removed                                                                                                 0.0s
 ✔ Container api-nginx         Removed                                                                                                 0.0s
[INFO] remove directory: data/pg_data
[INFO] remove directory: migrations
[INFO] restore directory: migrations
[INFO] completed - check files prior to use
### remove the previous database files after they've been backed up ###
[root@beta-3 helper_scripts]# rm -rf /opt/data/beta/services/coreapi/postgres/pg_data
[root@beta-3 helper_scripts]# su - nrig-service
```

as the `nrig-service` user

```console
cd fabric-core-api/

docker compose pull
docker compose build
docker compose up -d
docker compose stop nginx
```

## Restore DB

Run the restore script from the newly deployed `api-flask-server` container

```console
docker exec -ti api-flask-server /bin/bash
```

```
root@2f9e3d6bf454:/code# source .env
root@2f9e3d6bf454:/code# source .venv/bin/activate
(.venv) root@2f9e3d6bf454:/code# python -m flask db init
  Creating directory '/code/migrations/versions' ...  done
  Generating /code/migrations/README ...  done
  Generating /code/migrations/alembic.ini ...  done
  Generating /code/migrations/env.py ...  done
  Generating /code/migrations/script.py.mako ...  done
  Please edit configuration/connection/logging settings in '/code/migrations/alembic.ini' before proceeding.
(.venv) root@2f9e3d6bf454:/code# python -m flask db migrate
  Generating /code/migrations/versions/1053473ccfa9_.py ...  done
(.venv) root@2f9e3d6bf454:/code# python -m flask db 
upgrade

(.venv) root@2f9e3d6bf454:/code# python -m server.swagger_server.backup.utils.db_restore
2023-09-19 19:38:10,182 [INFO] Restore data from API version 1.5.2
...
(.venv) root@2f9e3d6bf454:/code# exit
exit
```

Restart the Nginx server

```
docker compose restart nginx
```

Verify contents from api UI as well as portal

---

### Restore db from pg_dump file

```
docker exec -u postgres api-database sh -c "psql -U postgres -d postgres < /tmp/core_api_backup_09-19-2023;"
```


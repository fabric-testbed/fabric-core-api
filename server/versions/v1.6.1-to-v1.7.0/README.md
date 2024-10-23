# v1.6.1 to v1.7.0 migration

Prior to deploying v1.7.10 the updated DB export script should be used to preserve the v1.6.1 data as JSON files

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
Copy the DB export script to the running v1.6.1 container

```console 
docker cp server/swagger_server/backup/utils/db_export.py api-flask-server:/code/server/swagger_server/backup/utils/db_export.py
```

Run the export script from within the `api-flask-server` container

```console
docker exec -ti api-flask-server /bin/bash
```

```console
root@338053d458ff:/code# source .env
root@338053d458ff:/code# source .venv/bin/activate
(.venv) root@338053d458ff:/code# python -m server.swagger_server.backup.utils.db_export
2023-10-25 16:35:37,306 [INFO] Exporter for API version 1.6.0
2023-10-25 16:35:37,306 [INFO] dump alembic_version table
2023-10-25 16:35:37,374 [INFO] dump announcements table
Unknown string format: None
Unknown string format: None
2023-10-25 16:35:37,442 [INFO] dump groups table
2023-10-25 16:35:37,457 [INFO] dump people table
2023-10-25 16:35:37,760 [INFO] dump people_email_addresses table
2023-10-25 16:35:37,764 [INFO] dump people_organizations table
2023-10-25 16:35:37,767 [INFO] dump people_roles table
2023-10-25 16:35:37,782 [INFO] dump preferences table
2023-10-25 16:35:37,915 [INFO] dump profiles_keywords table
2023-10-25 16:35:37,918 [INFO] dump profiles_other_identities table
2023-10-25 16:35:37,921 [INFO] dump profiles_people table
2023-10-25 16:35:38,065 [INFO] dump profiles_personal_pages table
2023-10-25 16:35:38,067 [INFO] dump profiles_projects table
2023-10-25 16:35:38,108 [INFO] dump profiles_references table
2023-10-25 16:35:38,109 [INFO] dump projects table
2023-10-25 16:35:38,207 [INFO] dump projects_creators table
2023-10-25 16:35:38,207 [INFO] dump projects_members table
2023-10-25 16:35:38,208 [INFO] dump projects_owners table
2023-10-25 16:35:38,209 [INFO] dump projects_storage table
2023-10-25 16:35:38,210 [INFO] dump projects_tags table
2023-10-25 16:35:38,212 [INFO] dump sshkeys table
2023-10-25 16:35:38,248 [INFO] dump storage table
2023-10-25 16:35:38,253 [INFO] dump storage_sites table
2023-10-25 16:35:38,254 [INFO] dump task_timeout_tracker table
2023-10-25 16:35:38,257 [INFO] dump testbed_info table
2023-10-25 16:35:38,261 [INFO] dump token_holders table
2023-10-25 16:35:38,261 [INFO] dump user_org_affiliations table
2023-10-25 16:35:38,265 [INFO] dump user_subject_identifiers table
```

Verify the contents of the export

```console
(.venv) root@338053d458ff:/code# ls -lh /code/server/swagger_server/backup/data/
total 816K
-rw-r--r-- 1 root root   78 Oct 25 16:35 alembic_version-v1.6.0.json
-rw-r--r-- 1 root root 3.6K Oct 25 16:35 announcements-v1.6.0.json
-rw-r--r-- 1 root root  22K Oct 25 16:35 groups-v1.6.0.json
-rw-r--r-- 1 root root  81K Oct 25 16:35 people-v1.6.0.json
-rw-r--r-- 1 root root  25K Oct 25 16:35 people_email_addresses-v1.6.0.json
-rw-r--r-- 1 root root  11K Oct 25 16:35 people_organizations-v1.6.0.json
-rw-r--r-- 1 root root  82K Oct 25 16:35 people_roles-v1.6.0.json
-rw-r--r-- 1 root root 339K Oct 25 16:35 preferences-v1.6.0.json
-rw-r--r-- 1 root root   29 Oct 25 16:35 profiles_keywords-v1.6.0.json
-rw-r--r-- 1 root root   37 Oct 25 16:35 profiles_other_identities-v1.6.0.json
-rw-r--r-- 1 root root  33K Oct 25 16:35 profiles_people-v1.6.0.json
-rw-r--r-- 1 root root   35 Oct 25 16:35 profiles_personal_pages-v1.6.0.json
-rw-r--r-- 1 root root 7.3K Oct 25 16:35 profiles_projects-v1.6.0.json
-rw-r--r-- 1 root root   31 Oct 25 16:35 profiles_references-v1.6.0.json
-rw-r--r-- 1 root root  18K Oct 25 16:35 projects-v1.6.0.json
-rw-r--r-- 1 root root  980 Oct 25 16:35 projects_creators-v1.6.0.json
-rw-r--r-- 1 root root 4.4K Oct 25 16:35 projects_members-v1.6.0.json
-rw-r--r-- 1 root root 1.8K Oct 25 16:35 projects_owners-v1.6.0.json
-rw-r--r-- 1 root root   91 Oct 25 16:35 projects_storage-v1.6.0.json
-rw-r--r-- 1 root root 5.1K Oct 25 16:35 projects_tags-v1.6.0.json
-rw-r--r-- 1 root root  86K Oct 25 16:35 sshkeys-v1.6.0.json
-rw-r--r-- 1 root root  586 Oct 25 16:35 storage-v1.6.0.json
-rw-r--r-- 1 root root  174 Oct 25 16:35 storage_sites-v1.6.0.json
-rw-r--r-- 1 root root 1.6K Oct 25 16:35 task_timeout_tracker-v1.6.0.json
-rw-r--r-- 1 root root  585 Oct 25 16:35 testbed_info-v1.6.0.json
-rw-r--r-- 1 root root  145 Oct 25 16:35 token_holders-v1.6.0.json
-rw-r--r-- 1 root root 7.0K Oct 25 16:35 user_org_affiliations-v1.6.0.json
-rw-r--r-- 1 root root 8.1K Oct 25 16:35 user_subject_identifiers-v1.6.0.json
(.venv) root@338053d458ff:/code# exit
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
total 816K
-rw-r--r-- 1 nrig-service nrig-service   78 Oct 25 16:35 alembic_version-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 3.6K Oct 25 16:35 announcements-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  22K Oct 25 16:35 groups-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  25K Oct 25 16:35 people_email_addresses-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  11K Oct 25 16:35 people_organizations-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  82K Oct 25 16:35 people_roles-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  81K Oct 25 16:35 people-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 339K Oct 25 16:35 preferences-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service   29 Oct 25 16:35 profiles_keywords-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service   37 Oct 25 16:35 profiles_other_identities-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  33K Oct 25 16:35 profiles_people-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service   35 Oct 25 16:35 profiles_personal_pages-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 7.3K Oct 25 16:35 profiles_projects-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service   31 Oct 25 16:35 profiles_references-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  980 Oct 25 16:35 projects_creators-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 4.4K Oct 25 16:35 projects_members-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 1.8K Oct 25 16:35 projects_owners-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service   91 Oct 25 16:35 projects_storage-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 5.1K Oct 25 16:35 projects_tags-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  18K Oct 25 16:35 projects-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  86K Oct 25 16:35 sshkeys-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  174 Oct 25 16:35 storage_sites-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  586 Oct 25 16:35 storage-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 1.6K Oct 25 16:35 task_timeout_tracker-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  585 Oct 25 16:35 testbed_info-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service  145 Oct 25 16:35 token_holders-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 7.0K Oct 25 16:35 user_org_affiliations-v1.6.0.json
-rw-r--r-- 1 nrig-service nrig-service 8.1K Oct 25 16:35 user_subject_identifiers-v1.6.0.json
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
total 288K
-rw-r--r-- 1 postgres postgres 285K Oct 25 16:48 core_api_backup_10-25-2023

$ docker cp api-database:/tmp/core_api_backup_$(date +'%m-%d-%Y') .
Successfully copied 293kB to /home/nrig-service/.

$ ls -lh ./core_api_backup_$(date +'%m-%d-%Y')
-rw-r--r-- 1 nrig-service nrig-service 285K Oct 25 16:48 ./core_api_backup_10-25-2023
```

## Deploy v1.6.1

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
 ✔ Container api-database      Stopped                                                                                                 0.2s
 ✔ Container api-nginx         Stopped                                                                                                 0.2s
WARN[0000] The "PYTHONPATH" variable is not set. Defaulting to a blank string.
WARN[0000] The "PYTHONPATH" variable is not set. Defaulting to a blank string.
Going to remove api-flask-server, api-nginx, api-database, api-vouch-proxy
[+] Removing 4/4
 ✔ Container api-vouch-proxy   Removed                                                                                                 0.0s
 ✔ Container api-nginx         Removed                                                                                                 0.0s
 ✔ Container api-database      Removed                                                                                                 0.0s
 ✔ Container api-flask-server  Removed                                                                                                 0.3s
[INFO] remove directory: data/pg_data
[INFO] remove directory: migrations
[INFO] restore directory: migrations
[INFO] completed - check files prior to use

### remove the previous database files after they've been backed up ###
[root@beta-3 helper_scripts]# rm -rf /opt/data/beta/services/coreapi/postgres/pg_data
[root@beta-3 helper_scripts]# su - nrig-service
```

as the `nrig-service` user

### update the .env file

Add a new entry for max active carousel items

```
### Announcements
export MAX_ACTIVE_CAROUSEL_ITEMS=10
```

### deploy containers

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
### initialize the database
root@f7e3da4ee35c:/code# source .env
root@f7e3da4ee35c:/code# source .venv/bin/activate
(.venv) root@f7e3da4ee35c:/code# python -m flask db init
  Creating directory '/code/migrations/versions' ...  done
  Generating /code/migrations/README ...  done
  Generating /code/migrations/alembic.ini ...  done
  Generating /code/migrations/env.py ...  done
  Generating /code/migrations/script.py.mako ...  done
  Please edit configuration/connection/logging settings in '/code/migrations/alembic.ini' before proceeding.
(.venv) root@f7e3da4ee35c:/code# python -m flask db migrate
  Generating /code/migrations/versions/3d62f58e79c7_.py ...  done
(.venv) root@f7e3da4ee35c:/code# python -m flask db upgrade

### restore prior data files
(.venv) root@f7e3da4ee35c:/code# python -m server.swagger_server.backup.utils.db_restore
2023-10-25 17:13:14,862 [INFO] Restore data from API version 1.6.0
...
(.venv) root@f7e3da4ee35c:/code# exit
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
docker exec -u postgres api-database sh -c "psql -U postgres -d postgres < /tmp/core_api_backup_10-25-2023;"
```


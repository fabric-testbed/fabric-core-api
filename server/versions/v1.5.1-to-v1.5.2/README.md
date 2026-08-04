# v1.5.1 to v1.5.2 migration

Prior to deploying v1.5.2 the updated DB export script should be used to preserve the v1.5.1 data as JSON files

## Export DB

Using [beta-3.fabric-testbed.net]() as an example.

Checkout the updated v1.5.2 code files but do not build a new image yet

```console
git fetch origin -p
git stash
git checkout main
git pull
git checkout v1.5.2
git stash pop   
```
Copy the DB export script to the running v1.5.1 container

```console 
docker cp server/swagger_server/backup/utils/db_export.py api-flask-server:/code/server/swagger_server/backup/utils/db_export.py
```

Run the export script from within the `api-flask-server` container

```console
docker exec -ti api-flask-server /bin/bash
```

```console
root@53bb06d262d6:/code/server/swagger_server/backup/data# cd /code/
root@53bb06d262d6:/code# ls
docker-entrypoint.sh  logs  migrations	requirements.txt  server
root@53bb06d262d6:/code# source .env
root@53bb06d262d6:/code# source .venv/bin/activate
(.venv) root@53bb06d262d6:/code# python -m server.swagger_server.backup.utils.db_export
2023-07-19 19:07:16,855 [INFO] Exporter for API version 1.5.1
2023-07-19 19:07:16,855 [INFO] dump alembic_version table
2023-07-19 19:07:16,881 [INFO] dump announcements table
2023-07-19 19:07:16,941 [INFO] dump groups table
2023-07-19 19:07:16,954 [INFO] dump people table
2023-07-19 19:07:17,305 [INFO] dump people_email_addresses table
2023-07-19 19:07:17,309 [INFO] dump people_organizations table
2023-07-19 19:07:17,314 [INFO] dump people_roles table
2023-07-19 19:07:17,356 [INFO] dump preferences table
2023-07-19 19:07:17,489 [INFO] dump profiles_keywords table
2023-07-19 19:07:17,495 [INFO] dump profiles_other_identities table
2023-07-19 19:07:17,498 [INFO] dump profiles_people table
2023-07-19 19:07:17,674 [INFO] dump profiles_personal_pages table
2023-07-19 19:07:17,675 [INFO] dump profiles_projects table
2023-07-19 19:07:17,715 [INFO] dump profiles_references table
2023-07-19 19:07:17,716 [INFO] dump projects table
2023-07-19 19:07:17,790 [INFO] dump projects_creators table
2023-07-19 19:07:17,791 [INFO] dump projects_members table
2023-07-19 19:07:17,792 [INFO] dump projects_owners table
2023-07-19 19:07:17,792 [INFO] dump projects_storage table
2023-07-19 19:07:17,793 [INFO] dump projects_tags table
2023-07-19 19:07:17,795 [INFO] dump sshkeys table
2023-07-19 19:07:17,826 [INFO] dump storage table
2023-07-19 19:07:17,832 [INFO] dump storage_sites table
2023-07-19 19:07:17,833 [INFO] dump testbed_info table
2023-07-19 19:07:17,836 [INFO] dump token_holders table
2023-07-19 19:07:17,837 [INFO] dump user_org_affiliations table
2023-07-19 19:07:17,841 [INFO] dump user_subject_identifiers table
```

Verify the contents of the export

```console
(.venv) root@53bb06d262d6:/code# ls -lh /code/server/swagger_server/backup/data/
total 780K
-rw-r--r-- 1 root root   78 Jul 19 19:07 alembic_version-v1.5.1.json
-rw-r--r-- 1 root root   25 Jul 19 19:07 announcements-v1.5.1.json
-rw-r--r-- 1 root root  15K Jul 19 19:07 groups-v1.5.1.json
-rw-r--r-- 1 root root  83K Jul 19 19:07 people-v1.5.1.json
-rw-r--r-- 1 root root  25K Jul 19 19:07 people_email_addresses-v1.5.1.json
-rw-r--r-- 1 root root  11K Jul 19 19:07 people_organizations-v1.5.1.json
-rw-r--r-- 1 root root  75K Jul 19 19:07 people_roles-v1.5.1.json
-rw-r--r-- 1 root root 337K Jul 19 19:07 preferences-v1.5.1.json
-rw-r--r-- 1 root root   29 Jul 19 19:07 profiles_keywords-v1.5.1.json
-rw-r--r-- 1 root root   37 Jul 19 19:07 profiles_other_identities-v1.5.1.json
-rw-r--r-- 1 root root  34K Jul 19 19:07 profiles_people-v1.5.1.json
-rw-r--r-- 1 root root   35 Jul 19 19:07 profiles_personal_pages-v1.5.1.json
-rw-r--r-- 1 root root 6.4K Jul 19 19:07 profiles_projects-v1.5.1.json
-rw-r--r-- 1 root root   31 Jul 19 19:07 profiles_references-v1.5.1.json
-rw-r--r-- 1 root root  15K Jul 19 19:07 projects-v1.5.1.json
-rw-r--r-- 1 root root  861 Jul 19 19:07 projects_creators-v1.5.1.json
-rw-r--r-- 1 root root 3.5K Jul 19 19:07 projects_members-v1.5.1.json
-rw-r--r-- 1 root root 1.5K Jul 19 19:07 projects_owners-v1.5.1.json
-rw-r--r-- 1 root root   91 Jul 19 19:07 projects_storage-v1.5.1.json
-rw-r--r-- 1 root root 5.0K Jul 19 19:07 projects_tags-v1.5.1.json
-rw-r--r-- 1 root root  79K Jul 19 19:07 sshkeys-v1.5.1.json
-rw-r--r-- 1 root root  586 Jul 19 19:07 storage-v1.5.1.json
-rw-r--r-- 1 root root  174 Jul 19 19:07 storage_sites-v1.5.1.json
-rw-r--r-- 1 root root  585 Jul 19 19:07 testbed_info-v1.5.1.json
-rw-r--r-- 1 root root   25 Jul 19 19:07 token_holders-v1.5.1.json
-rw-r--r-- 1 root root 7.2K Jul 19 19:07 user_org_affiliations-v1.5.1.json
-rw-r--r-- 1 root root 8.3K Jul 19 19:07 user_subject_identifiers-v1.5.1.json
(.venv) root@53bb06d262d6:/code# exit
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
total 780K
-rw-r--r-- 1 nrig-service nrig-service   78 Jul 19 19:07 alembic_version-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service   25 Jul 19 19:07 announcements-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  15K Jul 19 19:07 groups-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  25K Jul 19 19:07 people_email_addresses-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  11K Jul 19 19:07 people_organizations-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  75K Jul 19 19:07 people_roles-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  83K Jul 19 19:07 people-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service 337K Jul 19 19:07 preferences-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service   29 Jul 19 19:07 profiles_keywords-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service   37 Jul 19 19:07 profiles_other_identities-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  34K Jul 19 19:07 profiles_people-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service   35 Jul 19 19:07 profiles_personal_pages-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service 6.4K Jul 19 19:07 profiles_projects-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service   31 Jul 19 19:07 profiles_references-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  861 Jul 19 19:07 projects_creators-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service 3.5K Jul 19 19:07 projects_members-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service 1.5K Jul 19 19:07 projects_owners-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service   91 Jul 19 19:07 projects_storage-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service 5.0K Jul 19 19:07 projects_tags-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  15K Jul 19 19:07 projects-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  79K Jul 19 19:07 sshkeys-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  174 Jul 19 19:07 storage_sites-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  586 Jul 19 19:07 storage-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service  585 Jul 19 19:07 testbed_info-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service   25 Jul 19 19:07 token_holders-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service 7.2K Jul 19 19:07 user_org_affiliations-v1.5.1.json
-rw-r--r-- 1 nrig-service nrig-service 8.3K Jul 19 19:07 user_subject_identifiers-v1.5.1.json
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
total 272K
-rw-r--r-- 1 postgres postgres 270K Jul 19 17:47 core_api_backup_07-19-2023

$ docker cp api-database:/tmp/core_api_backup_$(date +'%m-%d-%Y') .
$ ls -lh ./core_api_backup_$(date +'%m-%d-%Y')
-rw-r--r-- 1 nrig-service nrig-service 270K Jul 19 17:47 ./core_api_backup_07-19-2023
```

## Deploy v1.5.2

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

docker-compose pull
docker-compose build
docker-compose up -d
```

## Restore DB

Run the restore script from the newly deployed `api-flask-server` container

```console
docker exec -ti api-flask-server /bin/bash
```

```
root@6d02801246af:/code# source .env
root@6d02801246af:/code# source .venv/bin/activate
(.venv) root@6d02801246af:/code# python -m flask db init
  Creating directory /code/migrations/versions ...  done
  Generating /code/migrations/README ...  done
  Generating /code/migrations/alembic.ini ...  done
  Generating /code/migrations/env.py ...  done
  Generating /code/migrations/script.py.mako ...  done
  Please edit configuration/connection/logging settings in '/code/migrations/alembic.ini' before proceeding.
(.venv) root@6d02801246af:/code# python -m flask db migrate
  Generating /code/migrations/versions/ec97d03f3564_.py ...  done
(.venv) root@6d02801246af:/code# python -m flask db upgrade
(.venv) root@43f87c6b3cd1:/code# python -m server.swagger_server.backup.utils.db_restore
...
```

Verify contents from api UI as well as portal

---

### Restore db from pg_dump file

```
docker exec -u postgres api-database sh -c "psql -U postgres -d postgres < /tmp/core_api_backup_07-19-2023;"
```


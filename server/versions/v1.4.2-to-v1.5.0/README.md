# v1.4.2 to v1.5.0 migration

Prior to deploying v1.5.0 the updated DB export script should be used to preserve the v1.4.2 data as JSON files

## Check bastion login related to having a bastion key

This is a database call to ensure that what is on the system is not perturbed by the data model updates to the user model

```
export QUERY="select distinct people.id, people.display_name, people.oidc_claim_email, people.oidc_claim_sub, sshkeys.fabric_key_type, people.bastion_login 
from people join sshkeys on people.id = sshkeys.people_id 
where sshkeys.fabric_key_type = 'bastion'
order by people.id;"

docker exec -u postgres api-database psql -c ${QUERY}
```

## Export DB

Using [beta-3.fabric-testbed.net]() as an example.

Checkout the updated v1.5.0 code files but do not build a new image yet

```console
git fetch origin -p
git stash
git checkout main
git pull
git checkout v1.5.0
git stash pop   
```
Copy the DB export script to the running v1.4.2 container

```console 
docker cp server/swagger_server/backup/utils/db_export.py api-flask-server:/code/server/swagger_server/backup/db_export.py
```

Run the export script from within the `api-flask-server` container

```console
docker exec -ti api-flask-server /bin/bash
```

```console
root@0e895a6adaf2:/code# source .env
root@0e895a6adaf2:/code# source .venv/bin/activate
(.venv) root@0e895a6adaf2:/code# python -m server.swagger_server.backup.utils.db_export
2023-05-02 19:56:07,601 [INFO] Exporter for API version 1.4.2
2023-05-02 19:56:07,601 [INFO] dump alembic_version table
2023-05-02 19:56:07,640 [INFO] dump announcements table
2023-05-02 19:56:07,715 [INFO] dump groups table
2023-05-02 19:56:07,731 [INFO] dump people table
2023-05-02 19:56:08,099 [INFO] dump people_email_addresses table
2023-05-02 19:56:08,103 [INFO] dump people_organizations table
2023-05-02 19:56:08,108 [INFO] dump people_roles table
2023-05-02 19:56:08,117 [INFO] dump preferences table
2023-05-02 19:56:08,312 [INFO] dump profiles_keywords table
2023-05-02 19:56:08,316 [INFO] dump profiles_other_identities table
2023-05-02 19:56:08,319 [INFO] dump profiles_people table
2023-05-02 19:56:08,501 [INFO] dump profiles_personal_pages table
2023-05-02 19:56:08,503 [INFO] dump profiles_projects table
2023-05-02 19:56:08,547 [INFO] dump profiles_references table
2023-05-02 19:56:08,549 [INFO] dump projects table
2023-05-02 19:56:08,623 [INFO] dump projects_creators table
2023-05-02 19:56:08,624 [INFO] dump projects_members table
2023-05-02 19:56:08,625 [INFO] dump projects_owners table
2023-05-02 19:56:08,626 [INFO] dump projects_tags table
2023-05-02 19:56:08,628 [INFO] dump sshkeys table
2023-05-02 19:56:08,666 [INFO] dump testbed_info table
```

Verify the contents of the export

```console
(.venv) root@0e895a6adaf2:/code# ls -lh /code/server/swagger_server/backup/data/
total 684K
-rw-r--r-- 1 root root   78 May  2 19:56 alembic_version-v1.4.2.json
-rw-r--r-- 1 root root   25 May  2 19:56 announcements-v1.4.2.json
-rw-r--r-- 1 root root  15K May  2 19:56 groups-v1.4.2.json
-rw-r--r-- 1 root root  68K May  2 19:56 people-v1.4.2.json
-rw-r--r-- 1 root root  22K May  2 19:56 people_email_addresses-v1.4.2.json
-rw-r--r-- 1 root root 9.0K May  2 19:56 people_organizations-v1.4.2.json
-rw-r--r-- 1 root root  72K May  2 19:56 people_roles-v1.4.2.json
-rw-r--r-- 1 root root 312K May  2 19:56 preferences-v1.4.2.json
-rw-r--r-- 1 root root   29 May  2 19:56 profiles_keywords-v1.4.2.json
-rw-r--r-- 1 root root   37 May  2 19:56 profiles_other_identities-v1.4.2.json
-rw-r--r-- 1 root root  31K May  2 19:56 profiles_people-v1.4.2.json
-rw-r--r-- 1 root root   35 May  2 19:56 profiles_personal_pages-v1.4.2.json
-rw-r--r-- 1 root root 6.4K May  2 19:56 profiles_projects-v1.4.2.json
-rw-r--r-- 1 root root   31 May  2 19:56 profiles_references-v1.4.2.json
-rw-r--r-- 1 root root  13K May  2 19:56 projects-v1.4.2.json
-rw-r--r-- 1 root root  861 May  2 19:56 projects_creators-v1.4.2.json
-rw-r--r-- 1 root root 3.5K May  2 19:56 projects_members-v1.4.2.json
-rw-r--r-- 1 root root 1.5K May  2 19:56 projects_owners-v1.4.2.json
-rw-r--r-- 1 root root 4.8K May  2 19:56 projects_tags-v1.4.2.json
-rw-r--r-- 1 root root  72K May  2 19:56 sshkeys-v1.4.2.json
-rw-r--r-- 1 root root  585 May  2 19:56 testbed_info-v1.4.2.json
(.venv) root@0e895a6adaf2:/code# exit
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
$ ls -lh ./data/
total 680K
-rw-r--r-- 1 nrig-service nrig-service   78 May  2 19:56 alembic_version-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service   25 May  2 19:56 announcements-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  15K May  2 19:56 groups-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  22K May  2 19:56 people_email_addresses-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service 9.0K May  2 19:56 people_organizations-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  72K May  2 19:56 people_roles-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  68K May  2 19:56 people-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service 312K May  2 19:56 preferences-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service   29 May  2 19:56 profiles_keywords-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service   37 May  2 19:56 profiles_other_identities-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  31K May  2 19:56 profiles_people-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service   35 May  2 19:56 profiles_personal_pages-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service 6.4K May  2 19:56 profiles_projects-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service   31 May  2 19:56 profiles_references-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  861 May  2 19:56 projects_creators-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service 3.5K May  2 19:56 projects_members-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service 1.5K May  2 19:56 projects_owners-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service 4.8K May  2 19:56 projects_tags-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  13K May  2 19:56 projects-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  72K May  2 19:56 sshkeys-v1.4.2.json
-rw-r--r-- 1 nrig-service nrig-service  585 May  2 19:56 testbed_info-v1.4.2.json
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
total 240K
-rw-r--r-- 1 postgres postgres 238K May  2 20:04 core_api_backup_05-02-2023

$ docker cp api-database:/tmp/core_api_backup_$(date +'%m-%d-%Y') .
$ ls -lh ./core_api_backup_$(date +'%m-%d-%Y')
-rw-r--r-- 1 nrig-service nrig-service 238K May  2 20:04 ./core_api_backup_05-02-2023
```

Create JSON files for tables that didn't have any data to output (e.g. FABRIC Storage related tables)

```
projects_storage-v1.4.2.json
storage-v1.4.2.json
storage_sites-v1.4.2.json
```

## Deploy v1.5.0

Stop and remove existing containers (easiest to start as the `root` user)

```console
$ cd /home/nrig-service/fabric-core-api/helper_scripts/
$ ./reset-to-clean.sh
[INFO] stop and remove docker containers
/usr/local/lib/python3.6/site-packages/paramiko/transport.py:33: CryptographyDeprecationWarning: Python 3.6 is no longer supported by the Python core team. Therefore, support for it is deprecated in cryptography and will be removed in a future release.
  from cryptography.hazmat.backends import default_backend
Stopping api-flask-server ... done
Stopping api-database     ... done
Stopping api-vouch-proxy  ... done
Stopping api-nginx        ... done
/usr/local/lib/python3.6/site-packages/paramiko/transport.py:33: CryptographyDeprecationWarning: Python 3.6 is no longer supported by the Python core team. Therefore, support for it is deprecated in cryptography and will be removed in a future release.
  from cryptography.hazmat.backends import default_backend
Going to remove api-flask-server, api-database, api-vouch-proxy, api-nginx
Removing api-flask-server ... done
Removing api-database     ... done
Removing api-vouch-proxy  ... done
Removing api-nginx        ... done
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
2023-05-02 20:20:43,999 [INFO] Restorer for API version 1.4.2
2023-05-02 20:20:43,999 [INFO] restore announcements table
2023-05-02 20:20:44,023 [INFO]   - Table: announcements, sequence_id: 1
2023-05-02 20:20:44,023 [INFO] restore groups table
2023-05-02 20:20:44,081 [INFO]   - Table: groups, sequence_id: 60
2023-05-02 20:20:44,081 [INFO] restore people_organizations table
2023-05-02 20:20:44,126 [INFO]   - Table: people_organizations, sequence_id: 69
2023-05-02 20:20:44,126 [INFO] restore people table
2023-05-02 20:20:44,256 [INFO]   - Table: people, sequence_id: 67
2023-05-02 20:20:44,256 [INFO] restore people_email_addresses table
2023-05-02 20:20:44,359 [INFO]   - Table: people_email_addresses, sequence_id: 149
2023-05-02 20:20:44,359 [INFO] restore people_roles table
2023-05-02 20:20:44,575 [INFO]   - Table: people_roles, sequence_id: 272
2023-05-02 20:20:44,575 [INFO] restore profiles_people table
2023-05-02 20:20:44,652 [INFO]   - Table: profiles_people, sequence_id: 67
2023-05-02 20:20:44,652 [INFO] restore profiles_other_identities table
2023-05-02 20:20:44,654 [INFO]   - Table: profiles_other_identities, sequence_id: 1
2023-05-02 20:20:44,654 [INFO] restore profiles_personal_pages table
2023-05-02 20:20:44,657 [INFO]   - Table: profiles_personal_pages, sequence_id: 1
2023-05-02 20:20:44,657 [INFO] restore projects table
2023-05-02 20:20:44,682 [INFO]   - Table: projects, sequence_id: 19
2023-05-02 20:20:44,682 [INFO] restore profiles_projects table
2023-05-02 20:20:44,701 [INFO]   - Table: profiles_projects, sequence_id: 19
2023-05-02 20:20:44,701 [INFO] restore profiles_keywords table
2023-05-02 20:20:44,703 [INFO]   - Table: profiles_keywords, sequence_id: 1
2023-05-02 20:20:44,704 [INFO] restore profiles_references table
2023-05-02 20:20:44,706 [INFO]   - Table: profiles_references, sequence_id: 1
2023-05-02 20:20:44,706 [INFO] restore projects_creators table
2023-05-02 20:20:44,715 [INFO] restore projects_members table
2023-05-02 20:20:44,747 [INFO] restore projects_owners table
2023-05-02 20:20:44,763 [INFO] restore projects_tags table
2023-05-02 20:20:44,800 [INFO]   - Table: projects_tags, sequence_id: 161
2023-05-02 20:20:44,800 [INFO] restore preferences table
2023-05-02 20:20:46,012 [INFO]   - Table: preferences, sequence_id: 1074
2023-05-02 20:20:46,013 [INFO] restore sshkeys table
2023-05-02 20:20:46,153 [INFO]   - Table: sshkeys, sequence_id: 93
2023-05-02 20:20:46,154 [INFO] restore storage table
2023-05-02 20:20:46,156 [INFO]   - Table: storage, sequence_id: 1
2023-05-02 20:20:46,156 [INFO] restore storage_sites table
2023-05-02 20:20:46,158 [INFO]   - Table: storage_sites, sequence_id: 1
2023-05-02 20:20:46,158 [INFO] restore projects_storage table
2023-05-02 20:20:46,159 [INFO] restore testbed_info table
2023-05-02 20:20:46,165 [INFO]   - Table: testbed_info, sequence_id: 2
2023-05-02 20:20:46,165 [INFO] verify project expiry
2023-05-02 20:20:46,289 [INFO] Project: 0be3a5c6-fe9e-41a4-89b6-b6f7ffaa58a8 set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,304 [INFO] Project: 68503663-9f33-4eb7-b4a4-6f4a6db7abfa set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,318 [INFO] Project: 75bb6177-4166-48ec-aaac-b771f54bc7e7 set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,332 [INFO] Project: 7a1ffe53-1945-4934-93c5-ef6df39b45ac set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,346 [INFO] Project: 937bbd15-1379-4e20-b24f-fa658352eaa0 set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,364 [INFO] Project: 9cb82df2-0559-4011-bb46-1cd03ee3ed63 set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,382 [INFO] Project: ab130149-3298-4446-826a-fe1b4a3fdd82 set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,407 [INFO] Project: ade3a7dd-9488-40f9-8fc6-967de0eea735 set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,421 [INFO] Project: b83d391d-5b74-40a6-8790-872183eb0cee set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,435 [INFO] Project: b9847fa1-13ef-49f9-9e07-ae6ad06cda3f set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,448 [INFO] Project: e8e3ebc2-4cad-4a80-9f17-a516c158b07a set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,460 [INFO] Project: f87459b8-3cb9-47f8-b91c-ccbcb79268fc set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,473 [INFO] Project: fb07edb4-6609-477e-a320-4b19dcf4826c set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,484 [INFO] Project: 689bd0e4-1bcd-472a-a500-b0fae3ca5884 set expiry: 2024-05-01 20:20:46.269296+00:00
2023-05-02 20:20:46,485 [INFO] add Bastion login and GECOS to user
2023-05-02 20:20:46,494 [INFO]   - User: 1, bastion_login: user1_123456, gecos: User One,,,,user1@gmail.com
...
2023-05-02 20:20:46,760 [INFO]   - User: 66, bastion_login: user66_654321, gecos: User SixtySix,,,,user66@lbl.gov
2023-05-02 20:20:46,761 [INFO] update User Subject Identities
2023-05-02 20:20:47,083 [INFO]   - User: 1, sub: ['http://cilogon.org/serverT/users/123456']
...
2023-05-02 20:20:54,858 [INFO]   - User: 66, sub: ['http://cilogon.org/serverE/users/654321']
2023-05-02 20:20:54,859 [INFO] update User Org Affiliations
2023-05-02 20:20:55,122 [WARNING] [NEEDS REVIEW] org_identity_id = 3296
2023-05-02 20:20:55,143 [INFO]   - User: 1, affiliation: ['University of Wisconsin-Madison']
...
2023-05-02 20:21:04,121 [INFO]   - User: 66, affiliation: ['Lawrence Berkeley National Laboratory']
```

Verify contents from api UI as well as portal

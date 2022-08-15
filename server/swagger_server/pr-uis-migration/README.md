# PR and UIS migration to fabric-core-api

FABRIC Core API (core-api) is intended to be a replacement for two existing services

- Project Registry (PR)
- User Information Service (UIS)

Core-api will also extend these services by including preference and profile information for Users and Projects, as well as other new features.

In an effort to preserve prior data a migration must take place between existing services running in FABRIC v1.2 (PR and UIS) and the new core-api service that will run in v1.3.

Documentation written using Alpha Tier infrastructure

- PR: `alpha-1.fabric-testbed.net`
- UIS: `alpha-5.fabric-testbed.net`
- core-api: `alpha-6.fabric-testbed.net`

## Order of operations

- [Maintenance period](#maintenance)
- [Snapshot existing data from PR and UIS](#snapshot)
- [Copy snapshot data to core-api](#copy)
- [Deploy fabric-core-api and allow it to self-populate based on COmanage data](#deploy)
- [Run fabric-core-api migration script](#migrate)
- [Verify migrated data](#verify)

## <a name="maintenance"></a>Maintenance period

It should take less than an hour to perform the migration of PR and UIS to core-api, but arranging for a two hour downtime is preferred.

Maintenance should be denoted in the FABRIC forum at least one week ahead of time

## <a name="snapshot"></a>Snapshot existing data

During the maintenance period both PR and UIS will be unavailable to users such that data remains in a steady state

Data migration scripts have been added to both PR and UIS repositories and are executed as described below:

- Ref PR: See `server/swagger_server/scripts/db_export.py` in [project-registry](https://github.com/fabric-testbed/project-registry)
- Ref UIS: See `server/swagger_server/scripts/db_export.py` in [UserInformationService](https://github.com/fabric-testbed/UserInformationService)

### project-registry (PR)

```
PR to fabric-core-api migration
- People   - table: fabric_people
- Projects - table: fabric_projects
- Tags     - table: tags

$ docker exec -u postgres pr-database psql -c "\dt;"
              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | comanage_cous   | table | postgres
 public | fabric_people   | table | postgres
 public | fabric_projects | table | postgres
 public | fabric_roles    | table | postgres
 public | project_members | table | postgres
 public | project_owners  | table | postgres
 public | tags            | table | postgres
 public | version         | table | postgres
```

Generate JSON migration files from running PR instance

Example using: `alpha-1.fabric-testbed.net`

#### from the `pr-flask-server` container run the export script

```
docker exec -ti pr-flask-server /bin/bash
```

Generate JSON output files

```
source .env
source .venv/bin/activate
python -m server.swagger_server.scripts.db_export
exit
```

#### from the host copy the files from the `pr-flask-server` container

```
docker cp pr-flask-server:/code/pr_people.json ./pr_people.json
docker cp pr-flask-server:/code/pr_projects.json ./pr_projects.json
docker cp pr-flask-server:/code/pr_tags.json ./pr_tags.json
```

#### sample data

`pr_people.json`

```json
{
  "pr_people": [
    {
      "id": 1,
      "uuid": "593dd0d3-cedb-4bc6-9522-a945da0a8a8e",
      "oidc_claim_sub": "http://cilogon.org/serverA/users/242181",
      "co_person_id": 1522,
      "co_id": 26,
      "co_status": "Active",
      "name": "Michael Stealey",
      "email": "stealey@unc.edu"
    },
    ...
  ]
}  
```

`pr_projects.json`

```json
{
  "pr_projects": [
    {
      "id": 1,
      "uuid": "0103c245-0284-4a35-8e3e-8cb0d9178595",
      "name": "Test Project for Tags",
      "description": "Test Project for Tags",
      "facility": "FABRIC",
      "created_by": "69f9b1a6-c3c3-4c53-8693-21c63e771c78",
      "created_time": "2022-05-11 17:19:00+00:00",
      "modified": "2022-08-12 18:53:43.347147+00:00"
    },
    ...
  ]
}  
```

`pr_tags.json`

```json
{
  "pr_tags": [
    {
      "id": 1,
      "projects_id": 5,
      "tag": "VM.NoLimitRAM"
    },
    ...
  ]
}  
```

### UserInformationService (UIS)

```
UIS to fabric-core-api migration
- People  - table: fabric_people
- SshKeys - table: fabric_sshkeys

$ docker exec -u postgres uis-database psql -c '\dt;'
             List of relations
 Schema |      Name      | Type  |  Owner
--------+----------------+-------+----------
 public | author_ids     | table | postgres
 public | fabric_papers  | table | postgres
 public | fabric_people  | table | postgres
 public | fabric_sshkeys | table | postgres
 public | papers_authors | table | postgres
 public | version        | table | postgres
```

Generate JSON migration files from running UIS instance

#### from the `uis-api-server` container run the export script

```
docker exec -ti uis-api-server /bin/bash
```

Generate JSON output files

```
source venv/bin/activate
python -m swagger_server.scripts.db_export
exit
```

#### from the host copy the files from the `uis-api-server` container

```
docker cp uis-api-server:/code/uis_people.json ./uis_people.json
docker cp uis-api-server:/code/uis_sshkeys.json ./uis_sshkeys.json
```

#### sample data

`uis_people.json`

```json
{
  "uis_people": [
    {
      "id": 2,
      "registered_on": "2021-08-31 20:12:00.590417+00:00",
      "uuid": "593dd0d3-cedb-4bc6-9522-a945da0a8a8e",
      "oidc_claim_sub": "http://cilogon.org/serverA/users/242181",
      "name": "Michael Stealey ",
      "email": "stealey@unc.edu",
      "eppn": "stealey@unc.edu",
      "bastion_login": "stealey_0000242181",
      "co_person_id": 1522
    },
    ...
  ]
}  
```

`uis_sshkeys.json`

```json
{
  "uis_sshkeys": [
    {
      "id": 166,
      "key_uuid": "8cdc786e-7047-483b-9a43-c436322703d1",
      "comment": "stealey_sliver",
      "description": "my sliver key",
      "ssh_key_type": "ssh-rsa",
      "fabric_key_type": "sliver",
      "fingerprint": "MD5:1f:b8:e6:22:c5:10:68:61:42:15:6c:24:86:62:ec:77",
      "created_on": "2022-08-14 20:55:23.016631+00:00",
      "expires_on": "2022-08-21 20:55:23.016631+00:00",
      "active": true,
      "deactivation_reason": null,
      "deactivated_on": null,
      "owner_uuid": "593dd0d3-cedb-4bc6-9522-a945da0a8a8e",
      "public_key": "AAAAB3NzaC1yc2EAAAADAQABAAABgQCf26...iTEDXrWTN3E2mq2dFPTQpMxt7GzVO6OM5yAVFSls=",
      "comanage_key_id": "151"
    },
    ...
  ]
}  
```

## <a name="copy"></a>Copy snapshot data to core-api

Output files from PR and UIS need to be copied into the fabric-core-api repository at `server/swagger_server/pr-uis-migration/data`

```console
$ ls -1 server/swagger_server/pr-uis-migration/data
pr_people.json    # from PR
pr_projects.json  # from PR
pr_tags.json      # from PR
uis_people.json   # from UIS
uis_sshkeys.json  # from UIS
```

## <a name="deploy"></a>Deploy fabric-core-api and allow it to self-populate based on COmanage data

See deployment docs for production in: [fabric-core-api](https://github.com/fabric-testbed/fabric-core-api)

### fabric-core-api (core-api)

## <a name="migrate"></a>Run fabric-core-api migration script

### fabric-core-api (core-api)


## <a name="verify"></a>Verify migrated data

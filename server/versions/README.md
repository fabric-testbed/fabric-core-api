# Versions

Version changelog and migration information

## Table of Contents

- [v1.4.2](#v142) - released TBD
- [v1.4.1](#v141) - released 02/07/2023
- [v1.4.0](#v140) - released 01/23/2023
- [v1.3.0](#v130) - released 08/29/2022

### <a name="v142"></a>v1.4.2

Deployed on: TBD

- Add site storage endpoints:
  - [/storage]() - GET, POST
  - [/storage/sites]() - GET
  - [/storage/{uuid}]() - GET, PATCH, DELETE
- Add `is_locked` and `expires_on` to FabricProjects model
- Add [/projects/{uuid}/expires-on]() API endpoint
- Add more robust DB export and restore scripts
- [migration details](./v1.4.1-to-v1.4.2/README.md)

### <a name="v141"></a>v1.4.1

Deployed on: 02/07/2023

- Hotfix for bastion response that are missing `bastion_login` attribute
- No change to database

### <a name="v140"></a>v1.4.0

Deployed on: 01/23/2023

- No change to database

### <a name="v130"></a>v1.3.0

Deployed on: 08/29/2022

- Initial deployment of fabric-core-api
- [migration details](./pr-uis-to-v1.3.0/README.md)

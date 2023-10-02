# Versions

Version changelog and migration information

## Table of Contents

- [v1.6.1](#v161) - released TBD
- [v1.6.0](#v160) - released 09/21/2023
- [v1.5.2](#v152) - released 09/06/2023
- [v1.4.2](#v142) - released 03/16/2023
- [v1.4.1](#v141) - released 02/07/2023
- [v1.4.0](#v140) - released 01/23/2023
- [v1.3.0](#v130) - released 08/29/2022

### <a name="v161"></a>v1.6.1

Deployed on: TBD

### <a name="v160"></a>v1.6.0

Deployed on: 09/21/2023

- long lived tokens model updates and endpoints
- check cookie user validation endpoint
- reframe user model to not rely on `email` claim alone, but also function using `sub` claim when email not provided
- export and reload scripts
- add `exact_match` parameter to `/people` and `/projects` searches (default is False)
- misc bug fixes

### <a name="v152"></a>v1.5.2

Deployed on: 09/06/2023

- if `email` is found as a claim, use it
- if `email` is not found, pull in user `sub` claim and interrogate COmanage API for CoPerson by Identifier until either an email is found, or account creation fails 
- if an email is not found in COmanage (which should never be the case) an account cannot be created for the user - individual consultation at that time (lets hope we don’t see this)

### <a name="v150"></a>v1.5.0

Deployed on: 08/17/2023

### <a name="v142"></a>v1.4.2

Deployed on: 03/16/2023

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

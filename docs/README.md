# FABRIC Core API

## Table of Contents

- [API endpoints](#endpoints)
    - People: [Overview](#people), [Details](./core-api-people.md)
    - Projects: [Overview](#projects), [Details](./core-api-projects.md)

- [Pagination](./core-api-pagination.md)
- [HTTP Status Codes](./core-api-status-codes.md)


## <a name="endpoints"></a>API endpoints

### <a name="people"></a>People

GET `/people`

- params: `search`, `limit`, `offset`

GET `/people/preferences`

- params: `search`

GET `/people/profile/otheridentiy-types`

- params: `search`

GET `/people/profile/personalpage-types`

- params: `search`

GET `/people/profile/preferences`

- params: `search`

GET `/people/{uuid}`

- params: `uuid`, `as_self`

PATCH `/people/{uuid}`

- params: `uuid`
- body: `email`, `name`, `preferences`

PATCH `/people/{uuid}/profile`

- params: `uuid`
- body: `bio`, `cv`, `job`, `other_identities`, `personal_pages`, `preferences`, `pronouns`, `website`

### <a name="projects"></a>Projects

GET `/projects`

- params: `search`, `limit`, `offset`

POST `/projects`

GET `/projects/preferences`

GET `/projects/profile/preferences`

GET `/projects/tags`

DELETE `/projects/{uuid}`

GET `/projects/{uuid}`

PATCH `/projects/{uuid}`

PATCH `/projects/{uuid}/personnel`

PATCH `/projects/{uuid}/profile`

PATCH `/projects/{uuid}/tags`

### Publications

GET `/publications`

POST `/publications`

GET `/publications/classifications-terms`

DELETE `/publications/{uuid}`

GET `/publications/{uuid}`

PATCH `/publications/{uuid}`

### SSH Keys

GET `/bastionkeys`

GET `/sshkeys`

POST `/sshkeys`

PUT `/sshkeys`

DELETE `/sshkeys/{uuid}`

GET `/sshkeys/{uuid}`

### Updates

GET `/updates`

POST `/updates`

DELETE `/updates/{uuid}`

GET `/updates/{uuid}`

PATCH `/updates/{uuid}`

### Version

GET `/version`

### Who am I

GET `/whoami`

# API documentation

Python (Flask) based ReSTful API for FABRIC Core Services based on COmanage registry contents

## Table of Contents

API endpoints

- [/announcements](./announcements.md) - API endpoint (release 1.3)
- [/check-cookie](./check-cookie.md) - API endpoint (release 1.6)
- [/core-api-metrics](./core-api-metrics.md) - API endpoint (release 1.7)
- [/people](./people.md) - API endpoint (release 1.0)
- [/projects](./projects.md) - API endpoint (release 1.0)
- [/sshkeys](./sshkeys.md) - API endpoint (release 1.3)
- [/storage](./storage.md) - API endpoint (release 1.4)
- [/testbed-info](./testbed-info.md) - API endpoint (release 1.4)
- [/version](./version.md) - API endpoint (release 1.0)
- [/whoami](./whoami.md) - API endpoint (release 1.0)

Response/Request Formatting

- Response: [paginated - list for multiple items](./pagination.md)
- Response: [singleton - details for one item](./singleton.md)
- Information: [http status codes](./status-codes.md)

## Overview

### announcements
FABRIC Facility & Maintenance Announcements

- GET: `/announcements`
- POST: `/announcements`
- GET: `/announcements`
- PATCH: `/announcements`
- DELETE: `/announcements`

### check-cookie
Check OIDC authentication cookie claims

- GET: `/check-cookie`

### core-api-metrics
Core API metrics data

- GET: `/core-api-metrics/overview`

### people
FABRIC People

- GET: `/people`
- GET: `/people/{uuid}`
- PATCH: `/people/{uuid}`
- PATCH: `/people/{uuid}/profile`
- GET: `/people/preferences`
- GET: `/people/profile/otheridentity-types`
- GET: `/people/profile/preferences`
- GET: `/people/profile/personalpage-types`

### projects
FABRIC Projects

- GET: `/projects`
- POST: `/projects`
- GET: `/projects/communities`
- GET: `/projects/funding-agencies`
- GET: `/projects/funding-directorates`
- GET: `/projects/preferences`
- GET: `/projects/profile/preferences`
- GET: `/projects/project-types`
- GET: `/projects/tags`
- GET: `/projects/{uuid}`
- DELETE: `/projects/{uuid}`
- PATCH: `/projects/{uuid}`
- PATCH: `/projects/{uuid}/communities`
- PATCH: `/projects/{uuid}/expires-on`
- PATCH: `/projects/{uuid}/personnel` *deprecated
- PATCH: `/projects/{uuid}/profile`
- PATCH: `/projects/{uuid}/project-creators`
- PATCH: `/projects/{uuid}/project-funding`
- PATCH: `/projects/{uuid}/project-members`
- PATCH: `/projects/{uuid}/project-owners`
- PATCH: `/projects/{uuid}/tags`
- PATCH: `/projects/{uuid}/token-holders`
- PATCH: `/projects/{uuid}/topics`

### publications
FABRIC Publications (release TBD)

- GET: `/publications`
- POST: `/publications`
- GET: `/publications/{uuid}`
- PATCH: `/publications/{uuid}`
- DELETE: `/publications/{uuid}`
- GET: `/publications/classification-terms`

### sshkeys
FABRIC Public SSH Keys

- GET: `/bastionkeys`
- GET: `/sshkeys`
- POST: `/sshkeys`
- PUT: `/sshkeys`
- GET: `/sshkeys/{uuid}`
- DELETE: `/sshkeys/{uuid}`

### storage
FABRIC Site Storage

- GET: `/storage`
- POST: `/storage`
- GET: `/storage/sites`
- GET: `/storage/{uuid}`
- PATCH: `/storage/{uuid}`
- DELETE: `/storage{uuid}`

### testbed-info
FABRIC Testbed Information

- GET: `/testbed-info`
- POST: `/testbed-info`

### version
Core API Version

- GET: `/version`

### whoami
Who am I authenticated as

- GET: `/whomai`

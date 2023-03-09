# Storage

Allow core-api to store information about allocated storage volumes. Volumes are created on specific sites for specific projects. Any user in the project should be able to see available volumes and use them. Volumes have a size and an expiration date.

Requests for storage are handled via Jira tickets, using which the operations team can create the required volumes at each site. For a given request all volumes across indicated sites have the same name and size.

## API Endpoints

FABRIC Storage Allocations

### `/storage`

- GET - retrieve list of storage allocations
  - param: `project_uuid` - optional search by project UUID
  - param: `offset` - number of items to skip before starting to collect the result set
  - param: `limit` - maximum number of results to return per page (1 or more
  - authz: `facility-operators` can list all storage allocations
  - authz: all others can list storage allocations associated to projects they are creator/owner/member of
- POST - create a new storage allocation
  - data: `expires_on` as string (required)
  - data: `project_uuid` as string (required)
  - data: `requested_by_uuid` as string (required)
  - data: `site_list` as array of string (optional)
  - data: `volume_name` as string (required)
  - data: `volume_size_gb` as integer (optional)
  - authz: `facility-operators` - only role allowed to create storage
  - authz: `Authorization: Bearer $TOKEN` in the request header

### `/storage/site-list`

- GET - retrieve list of valid FABRIC site short-names
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users

### `/storage/{uuid}`

- GET - retrieve details about a single storage allocation
  - authz: `facility-operators` see all storage allocations
  - authz: `Authorization: Bearer $TOKEN` in the request header
  - authz: all others see storage allocations associated to projects they are creator/owner/member of
- PATCH - update an existing storage allocation
  - data: `active` as boolean (optional)
  - data: `expires_on` as string (optional)
  - data: `site_list` as array of string (optional)
  - data: `volume_name` as string (optional)
  - data: `volume_size_gb` as integer (optional)
  - authz: `facility-operators` - only role allowed to update storage
  - authz: `Authorization: Bearer $TOKEN` in the request header
- DELETE - remove an existing storage allocation
  - authz: `facility-operators` - only role allowed to delete storage
  - authz: `Authorization: Bearer $TOKEN` in the request header

## Response and Request formats

### GET response as list or detail

```
{ 
    "active": <boolean>,
    "created_on": "<string>",
    "expires_on": "<string>",
    "project_name": "<string>",
    "project_uuid": "<string>",
    "requested_by_uuid": "<string>",
    "site_list": [ "<string>", ... ],
    "uuid": "<string>",
    "volume_name": "<string>", 
    "volume_size_gb": <integer>
}
```

### GET response as part of /projects/{uuid}

```
project_storage: [
    { 
        "active": <boolean>,
        "expires_on": "<string>",
        "site_list": [ "<string>", ... ],
        "uuid": "<string>",
        "volume_name": "<string>", 
        "volume_size_gb": <integer>
    },
    ...
]
```

### POST request body

```
{ 
    "expires_on": "<string>",         <-- required - Date/Time
    "project_uuid": "<string>",       <-- required - Project UUID
    "requested_by_uuid": "<string>",  <-- required - Person UUID
    "site_list": [ "<string>", ... ], <-- optional - controlled vocabulary (see /storage/site-list)
    "volume_name": "<string>",        <-- required - min 5 chars
    "volume_size_gb": <integer>       <-- optional - integer only
}
```

### PATCH request body

```
{ 
    "active": <boolean>,              <-- optional
    "expires_on": "<string>",         <-- optional
    "site_list": [ "<string>", ... ], <-- optional
    "volume_name": "<string>",        <-- optional
    "volume_size_gb": <integer>       <-- optional
}
```

## Authorization Bearer Token

To enable programmatic Ansible interaction a Bearer token in the request header is allowed as a valid means of authorization. For example.

```sh
curl -X 'POST' ${API_URL}'/storage' \
  -H 'Authorization: Bearer '${TOKEN} \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d ${data}
```

The following endpoints accept Bearer Tokens:

- POST `/storage`
- GET `/storage/{uuid}`
- PATCH `/storage/{uuid}`
- DELETE `/storage/{uuid}`

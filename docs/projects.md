# Projects

When a project is created it also triggers the remote creation of four COUs in COmanage (API call to COmanage registry)

- COU: `uuid-pc` - group to associate project creator to
- COU: `uuid-pm` - group to associate project members to
- COU: `uuid-po` - group to associate project owners to
- COU: `uuid-tk` - group to associate project long lived token holders to

The notation `uuid` from above is a universal unique identifier (e.g. `990d8a8b-7e50-4d13-a3be-0f133ffa8653`) - all COUs for the same project would have the same `uuid` value which matches the core-api `uuid` for the project object.

Personnel endpoints are additive, subtractive, or "WYSIWYG" in nature 

 - Operation `add`: The API will attempt to add all valid user UUIDs to existing creators/members/owners/token-holders
 - Operation `remove`: The API will attempt to remove all valid user UUIDs from existing creators/members/owners/token-holders
 - Operation `batch`: The API will attempt to modify the data object to exactly match the data provided by the `api_user` for creators/members/owners/token-holders in a "WYSIWG" way

For example:

- POST request including the following for `project_members` will create the project with those three users as members (user-1, user-2 and user-3)

```json
"project_members": [
    "uuid-1",
    "uuid-2",
    "uuid-3"
]
```

- a subsequent PATCH request (`operation=batch`) including the following for `project_members` will update the project to only have those two users as members (user-1 and user-4)

```json
"project_members": [
    "uuid-1",
    "uuid-4"
]
```

- a subsequent PATCH request (`operation=batch`) including the following for `project_members` will update the project to have zero members

```json
"project_members": []
```

## API Endpoints

FABRIC Projects

### `/projects`

- GET - retrieve list of projects
    - param: `search` - optional search, 3 or more characters. 
        - free-text search term
        - comma separated terms convert to search array for communities, topics, and type searches
  - param: `search_set` - optional search set parameter
        - `communities` - search over project communities
        - `description` - search over project name, description, and uuid (default)
        - `topics` - search over project topics
        - `type` - search over project type
  - param: `exact_match` - boolean flag that when true will only return exact matches found for a search query (default is false)
  - param: `offset` - number of items to skip before starting to collect the result set
  - param: `limit` - maximum number of results to return per page (1 or more)
  - param: `person_uuid` - return only projects where `person_uuid` is a project creator/owner/member (private projects are enforced by the calling user permissions)
  - param: `sort_by` - attribute to sort results by - `created_time`, `modified_time`, `name`
  - param: `order_by` - attribute to order results by - `asc`, `desc` 
  - authz: open to all authenticated users - results vary by role or membership
  - response type: paginated `projects`
- POST - create a new project
  - data: `description` as string (required)
  - data: `is_public` as boolean (required)
  - data: `name` as string (required)
  - data: `project_members` as array of string (optional)
  - data: `project_owners` as array of string (optional)
  - authz: `project-leads` - only role allowed to create a new project
  - response type: singleton `projects.details`

### `/projects/communities`

- GET - retrieve list of valid FABRIC community options
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `projects.communities`

### `/projects/funding-agencies`

- GET - retrieve list of valid funding agencies
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `projects.funding_agencies`

### `/projects/funding-directorates`

- GET - retrieve list of valid funding directorates (NSF)
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `projects.funding_directorates`

### `/projects/preferences`

- GET - retrieve list of valid FABRIC project preference types
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `projects.preferences`

### `/projects/profile/preferences`

- GET - retrieve list of valid FABRIC project profile preference types
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `projects.profile.preferences`

### `/projects/project-types`

- GET - retrieve list of valid FABRIC project types
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `projects.project_types`

### `/projects/tags`

- GET - retrieve list of valid FABRIC project permission tags
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `projects.tags`

### `/projects/{uuid}`

- GET - retrieve details about a single project
  - authz: open to all authenticated users - public projects and projects they are creator/member/owner of 
  - authz: `facility-operators` see all projects
  - response type: singleton `projects.details`
- PATCH - update an existing project
  - data: `description` as string (optional)
  - data: `is_public` as boolean (optional)
  - data: `name` as string (optional)
  - data: `preferences.show_profile` as boolean (optional)
  - data: `preferences.show_project_members` as boolean (optional)
  - data: `preferences.show_project_owners` as boolean (optional)
  - data: `preferences.show_publications` as boolean (optional)
  - authz: project creator/owner can update their project
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`
- DELETE - remove an existing project
  - authz: project creator/owner can remove their project
  - authz: `facility-operators` can remove any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/communities`

- PATCH - update an existing project communities
  - data: `communities` as array of string (optional)
  - authz: project creator/owner can update their project
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/expires-on`

- PATCH - update an existing project expires on date
  - data: `expires_on` as a string date / datetime
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/personnel`

- PATCH: Deprecated

### `/projects/{uuid}/profile`

- PATCH - update an existing project profile
  - data: `award_information` as string (optional - 5 or more characters
  - data: `goals` as string (optional)
  - data: `keywords` as array of string (optional)
  - data: `notebooks` as array of uuid as string (optional)
  - data: `preferences.show_award_information` as boolean (optional)
  - data: `preferences.show_goals` as boolean (optional)
  - data: `preferences.show_keywords` as boolean (optional)
  - data: `preferences.show_notebooks` as boolean (optional)
  - data: `preferences.show_project_status` as boolean (optional)
  - data: `preferences.show_purpose` as boolean (optional)
  - data: `preferences.show_references` as boolean (optional)
  - data: `project_status` as string (optional)
  - data: `purpose` as string (optional)
  - data: `references` as array of references (optional)
  - authz: project creator/owner can update their project
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/project-creators`

- PATCH - update existing project creator personnel
  - parameter: `operation` as string in {`add`, `remove`, `batch`} (default is `add`)
  - data: `project_creators` as array of uuid as string (optional)
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/project-funding`

- PATCH - update an existing project communities
  - data: `project_funding` as array of funding objects (optional)
  - data: `agency` as string, attribute of funding object
  - data: `agency_other` as string, attribute of funding object (optional)
  - data: `award_amount` as string, attribute of funding object (optional)
  - data: `award_number` as string, attribute of funding object (optional)
  - data: `directorate` as string, attribute of funding object (optional)
  - authz: project creator/owner can update their project
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/project-members`

- PATCH - update existing project member personnel
  - parameter: `operation` as string in {`add`, `remove`, `batch`} (default is `add`)
  - data: `project_members` as array of uuid as string (optional)
  - authz: project creator/owner can update their project
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/project-owners`

- PATCH - update existing project owner personnel
  - parameter: `operation` as string in {`add`, `remove`, `batch`} (default is `add`)
  - data: `project_owners` as array of uuid as string (optional)
  - authz: project creator/owner can update their project
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/tags`

- PATCH - update an existing project permission tags
  - data: `tags` as array of string (optional)
  - authz: project creator/owner can update their project
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects{uuid}/token-holders`

- PATCH - update an existing project personnel
  - parameter: `operation` as string in {`add`, `remove`, `batch`} (default is `add`)
  - data: `token-holders` as array of uuid as string (optional)
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

### `/projects/{uuid}/topics`

- PATCH - update an existing project topics list
  - data: `topics` as array of string (optional)
  - authz: project creator/owner can update their project
  - authz: `facility-operators` can update any project
  - response type: 200 OK as `204 no content`

## Response and Request formats

### GET projects response as list

Anonymous User:

```
{
    "communities": [
        "<string>",
      ],
    "description": "<string>",
    "is_public": <boolean>,
    "name": "<string>",
    "project_type": "<string>",
    "topics": [
        "<string>",
    ],
    "uuid": "<string>"
}
```

FABRIC User:

```
{
    "communities": [
        "<string>",
      ],
    "created": "<string>",
    "description": "<string>",
    "facility": "<string>",
    "is_public": <boolean>,
    "memberships": {
        "is_creator": <boolean>,      <-- based on identity of the API user
        "is_member": <boolean>,       <-- based on identity of the API user
        "is_owner": <boolean>,        <-- based on identity of the API user
        "is_token_holder": <boolean>  <-- based on identity of the API user
    },
    "name": "<string>",
    "project_type": "<string>",
    "tags": [
        "<string>",                   <-- shown to facility-operators and project creator/member/owner
    ],             
    "topics": [
        "<string>",
    ],
    "uuid": "<string>"
}
```

### GET projects response as detail - facility-operators and project creator/member/owner

Anonymous User:

```
{
    "active": <boolean>,
    "communities": [
        "<string>",
      ],
    "description": "<string>",
    "is_locked": <boolean>,
    "is_public": <boolean>,
    "name": "<string>",
    "project_funding": [
        "<funding_object>",
    ],
    "project_type": "<string>",
    "topics": [
        "<string>",
    ],
    "uuid": "<string>"
}
```

FABRIC User:

```
{
    "active": <boolean>,
    "communities": [
        "<string>",
      ],
    "created": "<string>",
    "description": "<string>",
    "expires_on": "<string>",
    "facility": "<string>",
    "is_locked": <boolean>,
    "is_public": <boolean>,
    "memberships": {
        "is_creator": <boolean>,      <-- based on identity of the API user
        "is_member": <boolean>,       <-- based on identity of the API user
        "is_owner": <boolean>,        <-- based on identity of the API user
        "is_token_holder": <boolean>  <-- based on identity of the API user
    },
    "modified": "<string>",
    "name": "<string>",
    "project_type": "<string>",
    "preferences": {
        "show_profile": <boolean>,
        "show_project_members": <boolean>,
        "show_project_owners": <boolean>,
        "show_publications": <boolean>
    },
    "profile": {
        "award_information": "<string>",
        "goals": "<string>",
        "preferences": {
            "show_award_information": <boolean>,
            "show_goals": <boolean>,
            "show_keywords": <boolean>,
            "show_notebooks": <boolean>,
            "show_project_status": <boolean>,
            "show_purpose": <boolean>,
            "show_references": <boolean>
        },
        "project_status": "<string>",
        "purpose": "<string>",
        "references": [ ... ]
    },
    "project_creators": [ ... ],
    "project_funding": [
        "<funding_object>",
    ],
    "project_members": [ ... ],
    "project_owners": [ ... ],
    "project_storage": [ ... ],
    "tags": [
        "<string>",                   <-- shown to facility-operators and project creator/member/owner
    ],            
    "topics": [
        "<string>",
    ],
    "uuid": "<string>"
}
```

### POST project request body

```
{
    "description": "<string>", <-- required - 5 or more characters
    "is_public": <boolean>,    <-- required - true/false
    "name": "<string>",        <-- required - 5 or more characters
    "project_members": [       <-- optional - array of uuid as string
        "<string>"
    ],
    "project_owners": [        <-- optional - array of uuid as string
        "<string>"
    ]
}
```

### PATCH project request body

```
{
    "description": "<string>",             <-- optional - 5 or more characters
    "is_public": <boolean>,                <-- optional - true/false
    "name": "<string>",                    <-- optional - 5 or more characters
    "preferences": {
        "show_profile": <boolean>,         <-- optional - true/false
        "show_project_members": <boolean>, <-- optional - true/false
        "show_project_owners": <boolean>,  <-- optional - true/false
        "show_publications": <boolean>     <-- optional - true/false
    },
   "project_type": "<string>"              <-- optional - project_type options
}
```

Valid project `preferences` keys:

```json
"preferences_keys": [
    "show_profile",
    "show_project_members",
    "show_project_owners",
    "show_publications"
]
```

### PATCH project communities request body

```
{
    "communities": [
        "<string>"
    ]
}
```

### PATCH project expires-on request body

```
{
    "expires_on": "<string>" <-- optional - Date/Time
}
```

### PATCH project personnel request body
Deprecated

### PATCH project profile request body

```
{
    "award_information": "<string>",         <-- optional - 5 or more characters
    "goals": "<string>",                     <-- optional - 5 or more characters
    "keywords": [ ... ],                     <-- optional - array of string
    "notebooks": [ ... ],                    <-- optional - array of uuid
    "preferences": {
        "show_award_information": <boolean>, <-- optional - true/false
        "show_goals": <boolean>,             <-- optional - true/false
        "show_keywords": <boolean>,          <-- optional - true/false
        "show_notebooks": <boolean>,         <-- optional - true/false
        "show_project_status": <boolean>,    <-- optional - true/false
        "show_purpose": <boolean>,           <-- optional - true/false
        "show_references": <boolean>         <-- optional - true/false
    },
    "project_status": "<string>",            <-- optional - 5 or more characters
    "purpose": "<string>",                   <-- optional - 5 or more characters
    "references": [ ... ]                    <-- optional - array of references
}
```

Valid `keywords` format:

```json
"keywords": [
    "string",
    "string"
]
```

Valid `notebooks` format - **TODO**:

```json
"notebooks": [ 
    "<string_notebook_uuid>",
    "<string_notebook_uuid>"
]
```

Valid project profile `preferences` keys:

```json
"preferences_keys": [
    "show_award_information",
    "show_goals",
    "show_keywords",
    "show_notebooks",
    "show_project_status",
    "show_purpose",
    "show_references"
]
```

Valid `references` format:

```json
"references": [
    {
        "description": "<string_5_or_more_characters>",
        "url": "<string_as_URL>"
    }
]
```

### PATCH project-creators request body

```
{
    "project_creators": [      <-- optional - array of uuid as string
        "<string>"
    ]
}
```

### PATCH project-funding request body

```
    {
    "project_funding": [       <-- optional - array of funding objects as string
        {
            "agency": "<string>",
            "agency_other": "<string>",
            "award_amount": "<string>",
            "award_number": "<string>",
            "directorate": "<string>"
        }
    ]
}
```

### PATCH project-members request body

```
{
    "project_members": [       <-- optional - array of uuid as string
        "<string>"
    ]
}
```

### PATCH project-owners request body

```
{
    "project_owners": [        <-- optional - array of uuid as string
        "<string>"
    ]
}
```

### PATCH project tags request body

```
{
    "tags": [                  <-- optional - array of project_tags as string
        "<string>"
    ]
}
```

Valid `project_tags`:

```json
"project_tags": [
    "Component.FPGA",
    "Component.GPU",
    "Component.NVME",
    "Component.SmartNIC",
    "Component.Storage",
    "Net.AllFacilityPorts",
    "Net.FABNetv4Ext",
    "Net.FABNetv6Ext",
    "Net.FacilityPort.Chameleon-StarLight",
    "Net.FacilityPort.Chameleon-TACC",
    "Net.FacilityPort.Cloud-Facility-AWS",
    "Net.FacilityPort.Cloud-Facility-Azure",
    "Net.FacilityPort.Cloud-Facility-Azure-Gov",
    "Net.FacilityPort.Cloud-Facility-GCP",
    "Net.FacilityPort.ESnet-StarLight",
    "Net.FacilityPort.Internet2-StarLight",
    "Net.FacilityPort.Utah-Cloudlab-Powder",
    "Net.NoLimitBW",
    "Net.PortMirroring",
    "Slice.Measurements",
    "Slice.Multisite",
    "Slice.NoLimitLifetime",
    "VM.NoLimit",
    "VM.NoLimitCPU",
    "VM.NoLimitDisk",
    "VM.NoLimitRAM"
]
```

### PATCH project token-holders request body

```
{
    "token_holders": [       <-- optional - array of uuid as string
        "<string>"
    ]
}
```

### PATCH project topics request body

```
{
    "topics": [              <-- optional - array of topics as string
        "<string>"
    ]
}
```

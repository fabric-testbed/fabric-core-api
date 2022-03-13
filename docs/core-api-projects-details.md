# Projects

FabricPeople objects are created through a COmananage (CILogon 2.0) enrollment workflow and can only be removed from COmanage directly. As such no `POST` or `DELETE` endpoints have been made available for the FabricPeople object.

Available HTTP methods are:

Method | Endpoint | Operation
:------|:---------|:---------
`GET` | [/people](#people) | get paginated `people` response as authenticated user
`GET` | [/people/{uuid}](#people_one) | get single `people_one` response as authenticated user
`GET` | [/people/{uuid}/self](#people_self) | get single `people_self` response as self
`PATCH` | [/people/{uuid}/self](#people_patch) | add/modify/remove attributes from existing FabricPeople object as self

## GET

### <a name="people"></a>GET: `/people`

Parameters:

- `search`: search term applied on name and email
- `offset`: number of items to skip before starting to collect the result set
- `limit`: maximum number of results to return per page (1 to 20)

Response object: `people`

```json
{
    "data": [
        {
            "created": "string",
            "description": "string",
            "facility": "string",
            "name": "string",
            "uuid": "string"
        }
    ],
    "limit": 0,
    "links": {
        "first": "string",
        "last": "string",
        "next": "string",
        "prev": "string"
    },
    "offset": 0,
    "size": 0,
    "status": 200,
    "type": "people"
}
```

### <a name="people_one"></a>GET: `/people/{uuid}`

Parameters:

- `uuid`: universal unique identifier

Response object: `people_one`

```json
{
    "data": [
        {
        "active": <bool>,
        "created": "string",
        "description": "string",
        "name": "string",
        "facility": "string"
        "modified": "string"
        "tags": [ "string" ]
        "profile": {
            "website": "string"
        },
        "publications": [
            {}
        ],
        "uuid": "string"
        }
    ],
    "size": 1,
    "status": 200,
    "type": "people_one"
}
```

### <a name="people_self"></a>GET: `/people/{uuid}/self`

Parameters:

- `uuid`: universal unique identifier

Response object: `people_self`

```json
{
    "data": [
        {
            "affiliation": "string",
            "email": "string",
            "eppn": "string",
            "name": "string",
            "profile": {
                "bio": "string",
                "cv": "string",
                "job": "string",
                "other_identities": [
                    {
                        "identity": "string",
                        "type": "string"
                    }
                ],
                "professional": [
                    {
                        "url": "string",
                        "type": "string"
                    }
                ],
                "pronouns": "string",
                "social": [
                    {
                        "url": "string",
                        "type": "string"
                    }
                ],
                "website": "string",
                "preferences": {
                    "show_bio": true,
                    "show_cv": true,
                    "show_job": true,
                    "show_other_identities": true,
                    "show_professional": true,
                    "show_pronouns": true,
                    "show_social": true,
                    "show_website": true
                }
            },
            "publications": [
                {}
            ],
            "registered_on": "string",
            "roles": [
                {
                    "name": "string",
                    "description": "string"
                }
            ],
            "sshkeys": [
                {}
            ],
            "uuid": "string",
            "bastion_login": "string",
            "cilogon_email": "string",
            "cilogon_family_name": "string",
            "cilogon_given_name": "string",
            "cilogon_id": "string",
            "cilogon_idp_name": "string",
            "cilogon_name": "string",
            "email_addresses": [
                "string"
            ],
            "fabric_id": "string",
            "preferences": {
                "show_email": true,
                "show_eppn": true,
                "show_profile": true,
                "show_projects": true,
                "show_publications": true,
                "show_roles": true,
                "show_sshkeys": true
            }
        }
    ],
    "size": 1,
    "status": 200,
    "type": "people_self"
}
```

## PATCH

### <a name="people_patch"></a>PATCH: `/people/{uuid}/self?operation=add`

Update existing people object by adding or modifying content only if the `uuid` value maps to the user making the request

- **add**: `profile.other_identities`, `profile.professional` and `profile.social` provided an exact match does not already exist
- **modify**: `email` provided the updated email matches an existing user **EmailAddress** already in the system
- **modify**: all other attributes are modified in place

Parameters:

- `uuid`: universal unique identifier
- `operation`: **add**

Request body (showing all available options):

```json
{
    "name": "string",
    "email": "string",
    "preferences": {
        "show_email": true,
        "show_eppn": true,
        "show_profile": true,
        "show_publications": true,
        "show_roles": true,
        "show_sshkeys": true
    },
    "profile": {
        "bio": "string",
        "cv": "string",
        "job": "string",
        "other_identities": [
            {
                "identity": "string",
                "type": "string"
            }
        ],
        "professional": [
            {
                "url": "string",
                "type": "string"
            }
        ],
        "pronouns": "string",
        "social": [
            {
                "url": "string",
                "type": "string"
            }
        ],
        "website": "string",
        "preferences": {
            "show_bio": true,
            "show_cv": true,
            "show_job": true,
            "show_other_identities": true,
            "show_professional": true,
            "show_pronouns": true,
            "show_social": true,
            "show_website": true
        }
    }
}
```

### PATCH: `/people/{uuid}/self?operation=remove`

Update existing people object by removing content only if the `uuid` value maps to the user making the request

- **remove**: when an exact match is passed as a parameter of the request body the corresponding user attribute is removed

Parameters:

- `uuid`: universal unique identifier
- `operation`: **remove**

Request body (showing all available options):

```json
{
    "profile": {
        "bio": "string",
        "cv": "string",
        "job": "string",
        "other_identities": [
            {
                "identity": "string",
                "type": "string"
            }
        ],
        "professional": [
            {
                "url": "string",
                "type": "string"
            }
        ],
        "pronouns": "string",
        "social": [
            {
                "url": "string",
                "type": "string"
            }
        ],
        "website": "string"
    }
}
```

## Glossary

Request / Response terms

- `name` - display name as seen in all public interfaces
- `email` - preferred email as seen in all public interfaces
- `preferences` - people preference settings
    - `show_email` - show/hide email in all public interfaces
    - `show_eppn` - show/hide eppn in all public interfaces
    - `show_profile` - show/hide profile in all public interfaces
    - `show_publications` - show/hide publications in all public interfaces
    - `show_roles` - show/hide roles in all public interfaces
    - `show_sshkeys` - show/hide sshkeys in all public interfaces
- `profile` - people profile settings
    - `bio` - short bio 
    - `cv` - URL link to a CV or resume (Later it might be nice if this could be stored on the Portal)
    - `job` - Role/job/position
    - `other_identities` - IDs from other identity services such as ORCID, Google Scholar
        - `identity` - unique identity link or name
        - `type` - see below for type options
    - `professional` - Links to professional pages on resources such as LinkedIn, Twitter, Youtube, Github
        - `url` - URL link
        - `type` - see below for type options
    - `pronouns` - personal pronouns used
    - `social` - Links to personal pages on resources such as LinkedIn, Twitter, Youtube, Github
        - `url` - URL link
        - `type` - see below for type options
    - `website` - Link to a personal website
    - `preferences` - profile people preference settings
        - `show_bio` - show/hide bio in all public interfaces
        - `show_cv` - show/hide cv in all public interfaces
        - `show_job` - show/hide job in all public interfaces
        - `show_other_identities` - show/hide other_identities in all public interfaces
        - `show_professional` - show/hide professional in all public interfaces
        - `show_pronouns` - show/hide pronouns in all public interfaces
        - `show_social` - show/hide social in all public interfaces
        - `show_website` - show/hide website in all public interfaces

    

Professional / Social `type` options:

- `bitbucket`:
- `facebook`:
- `github`:
- `gitlab`:
- `instagram`:
- `linkedin`:
- `messenger`:
- `other`:
- `pinterest`:
- `twitter`:
- `youtube`:

Other Identities `type` options:

- `google_scholar`:
- `orcid`:
- `other`:

# People

FabricPeople objects are created through a COmanage (CILogon 2.0) enrollment workflow and can only be removed from COmanage directly. As such no `POST` or `DELETE` endpoints have been made available for the FabricPeople object.

Available HTTP methods are:

Method | Endpoint | Parameters | Operation
:------|:---------|:-----------|:---------
`GET` | [/people](#people) | `limit`, `offset`, `search` | Search for FABRIC People by name or email
`GET` | [/people/preferences](#peopleprefs) | `search` | List of People Preference options
`GET` | [/people/profile/otheridentity-types](#peopleoitypes) | `search` | List of People Profile Other Identity Type options
`GET` | [/people/profile/personalpage-types](#peoplepptypes) | `search` | List of People Profile Personal Page Type options
`GET` | [/people/profile/preferences](#peopleprofileprefs) | `search` | List of People Profile Preference options
`GET` | [/people/{uuid}](#peopleuuidget) | `as_self`, `uuid` | Person details by UUID
`PATCH` | [/people/{uuid}](#peopleuuidpatch) |  `uuid`, `--data` object | Update Person details as Self
`PATCH` | [/people/{uuid}/profile](#peopleuuidprofilepatch) |  `uuid`, `--data` object | Update Person Profile details as Self



## <a name="people"></a>GET: `/people`

Parameters:

- `search`: search term applied on name and email (optional)
- `offset`: number of items to skip before starting to collect the result set, default=0 (optional)
- `limit`: maximum number of results to return per page, default=5, range 1 to 20 (optional)

Response object: `people`

```json
{
  "results": [
    {
      "email": "string",
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
  "total": 0,
  "type": "people"
}
```

Example:

```console
curl -X 'GET' \
  'https://127.0.0.1:8443/people?search=stealey&offset=0&limit=5' \
  -H 'accept: application/json'
  
{
  "limit": 5,
  "links": {
    "first": "https://127.0.0.1:8443/people?search=stealey&offset=0&limit=5",
    "last": "https://127.0.0.1:8443/people?search=stealey&offset=0&limit=5"
  },
  "offset": 0,
  "results": [
    {
      "email": "stealey@unc.edu",
      "name": "Michael Stealey",
      "uuid": "414b7755-ff33-4442-8227-bbcd362ac05b"
    },
    {
      "email": "mjstealey@gmail.com",
      "name": "mj stealey",
      "uuid": "7c62cec1-eca1-464a-a649-6e482e0d6ab7"
    }
  ],
  "size": 2,
  "status": 200,
  "total": 2,
  "type": "people"
}
```

## <a name="peopleprefs"></a>GET: `/people/preferences`

Parameters: 

- `search`: search term applied (optional)

Response object: `people.preferences`

```json
{
  "results": [
    "show_XYZ"
  ],
  "size": 1,
  "status": 200,
  "type": "people.preferences"
}
```

Example: 

```console
curl -X 'GET' \
  'https://127.0.0.1:8443/people/preferences' \
  -H 'accept: application/json'
  
{
  "results": [
    "show_email",
    "show_eppn",
    "show_profile",
    "show_publications",
    "show_roles",
    "show_sshkeys"
  ],
  "size": 6,
  "status": 200,
  "type": "people.preferences"
}
```

## <a name="peopleoitypes"></a>GET: `/people/profile/otheridentity-types`

Parameters: 

- `search`: search term applied (optional)

Response object: `people.profile.otheridentity.types`

```json
{
  "results": [
    "show_XYZ"
  ],
  "size": 1,
  "status": 200,
  "type": "people.profile.otheridentity.types"
}
```

Example: 

```console
curl -X 'GET' \
  'https://127.0.0.1:8443/people/profile/otheridentity-types' \
  -H 'accept: application/json'
  
{
  "results": [
    "google_scholar",
    "orcid",
    "other"
  ],
  "size": 3,
  "status": 200,
  "type": "people.profile.otheridentity.types"
}
```

## <a name="peoplepptypes"></a>GET: `/people/profile/personalpage-types`

Parameters: 

- `search`: search term applied (optional)

Response object: `people.profile.personalpage.types`

```json
{
  "results": [
    "show_XYZ"
  ],
  "size": 1,
  "status": 200,
  "type": "people.profile.personalpage.types"
}
```

Example: 

```console
curl -X 'GET' \
  'https://127.0.0.1:8443/people/profile/personalpage-types' \
  -H 'accept: application/json'
  
{
  "results": [
    "bitbucket",
    "facebook",
    "github",
    "gitlab",
    "google",
    "instagram",
    "linkedin",
    "messenger",
    "other",
    "pinterest",
    "twitter",
    "youtube"
  ],
  "size": 12,
  "status": 200,
  "type": "people.profile.personalpage.types"
}
```

## <a name="peopleprofileprefs"></a>GET: `/people/profile/preferences`

Parameters: 

- `search`: search term applied (optional)

Response object: `people.profile.preferences`

```json
{
  "results": [
    "show_XYZ"
  ],
  "size": 1,
  "status": 200,
  "type": "people.profile.preferences"
}
```

Example: 

```console
curl -X 'GET' \
  'https://127.0.0.1:8443/people/profile/preferences' \
  -H 'accept: application/json'
  
{
  "results": [
    "show_bio",
    "show_cv",
    "show_job",
    "show_other_identities",
    "show_personal_pages",
    "show_pronouns",
    "show_website"
  ],
  "size": 7,
  "status": 200,
  "type": "people.profile.preferences"
}
```

## <a name="peopleuuidget"></a>GET: `/people/{uuid}`

Parameters: 

- `uuid`: universally unique identier of User
- `as_self`: view details as self

Response object: `no_content`

```json
{
  "results": [
    {
      "affiliation": "string",
      "bastion_login": "string",
      "cilogon_email": "string",
      "cilogon_family_name": "string",
      "cilogon_given_name": "string",
      "cilogon_id": "string",
      "cilogon_name": "string",
      "email": "string",
      "email_addresses": [
        "string"
      ],
      "eppn": "string",
      "fabric_id": "string",
      "name": "string",
      "preferences": {
        "show_XYZ": true
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
        "preferences": {
          "show_XYZ": true
        },
        "personal_pages": [
          {
            "url": "string",
            "type": "string"
          }
        ],
        "pronouns": "string",
        "website": "string"
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
      "uuid": "string"
    }
  ],
  "size": 1,
  "status": 200,
  "type": "people.details"
}
```

Example: 

```console
curl -X 'GET' \
  'https://127.0.0.1:8443/people/414b7755-ff33-4442-8227-bbcd362ac05b?as_self=true' \
  -H 'accept: application/json'
  
{
  "results": [
    {
      "affiliation": "University of North Carolina at Chapel Hill",
      "bastion_login": "stealey_0000242181",
      "cilogon_email": "stealey@unc.edu",
      "cilogon_family_name": "Stealey",
      "cilogon_given_name": "Michael",
      "cilogon_id": "http://cilogon.org/serverA/users/242181",
      "cilogon_name": "Michael Stealey",
      "email": "stealey@unc.edu",
      "email_addresses": [
        "stealey@unc.edu"
      ],
      "eppn": "stealey@unc.edu",
      "fabric_id": "FABRIC-alpha1000001",
      "name": "Michael J. Stealey, Sr",
      "preferences": {
        "show_email": true,
        "show_eppn": true,
        "show_profile": true,
        "show_publications": true,
        "show_roles": true,
        "show_sshkeys": true
      },
      "profile": {
        "bio": "my bio",
        "cv": "https://my-cv-on-the-web.com/my-cv",
        "job": "my job",
        "other_identities": [],
        "personal_pages": [],
        "preferences": {
          "show_bio": true,
          "show_cv": true,
          "show_job": true,
          "show_other_identities": true,
          "show_personal_pages": true,
          "show_pronouns": true,
          "show_website": true
        },
        "pronouns": "my pronouns",
        "website": "https://my-personal-website.org/about-me"
      },
      "publications": [],
      "registered_on": "2022-05-13 20:40:42.208565+00:00",
      "roles": [
        {
          "description": "FABRIC Project",
          "name": "8b3a2eae-a0c0-475a-807b-e9af581ce4c0-pm"
        },
        {
          "description": "Development project",
          "name": "a5488d93-7c6b-48ea-9de1-19e216c0519b-pc"
        },
        {
          "description": "Development project",
          "name": "a5488d93-7c6b-48ea-9de1-19e216c0519b-po"
        },
        {
          "description": "FABRIC Approval Committee for CO/COU membership (alpha)",
          "name": "approval-committee "
        },
        {
          "description": "Test Project",
          "name": "c3e4b3ce-ca83-4bd7-ad5b-6ce6423eeb33-pm"
        },
        {
          "description": "Test Project",
          "name": "c3e4b3ce-ca83-4bd7-ad5b-6ce6423eeb33-po"
        },
        {
          "description": "Test Project 03/17",
          "name": "d6818b0e-dd19-4ef2-8eec-7f91a87f4efa-po"
        },
        {
          "description": "api-project",
          "name": "ec8389c8-6129-40aa-a6ee-3a1d80d74f33-pc"
        },
        {
          "description": "api-project",
          "name": "ec8389c8-6129-40aa-a6ee-3a1d80d74f33-pm"
        },
        {
          "description": "api-project",
          "name": "ec8389c8-6129-40aa-a6ee-3a1d80d74f33-po"
        },
        {
          "description": "Active Users of FABRIC - initially set by enrollment workflow",
          "name": "fabric-active-users"
        },
        {
          "description": "Facility Operators for FABRIC",
          "name": "facility-operators"
        },
        {
          "description": "Project Leads for FABRIC",
          "name": "project-leads"
        }
      ],
      "sshkeys": [],
      "uuid": "414b7755-ff33-4442-8227-bbcd362ac05b"
    }
  ],
  "size": 1,
  "status": 200,
  "type": "people.details"
}
```

## <a name="peopleuuidpatch"></a>PATCH: `/people/{uuid}`

Parameters: 

- `uuid`: universally unique identier of User

Request body data:

- `--data`: `email`, `name`, `preferences`

Response object: `no_content`

```json
{
  "results": [
    {
      "message": "No Content",
      "details": "string"
    }
  ],
  "type": "no_content",
  "size": 1,
  "status": 200
}
```

Example: 

```console
curl -X 'PATCH' \
  'https://127.0.0.1:8443/people/414b7755-ff33-4442-8227-bbcd362ac05b' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "stealey@unc.edu",
  "name": "Michael J. Stealey, Sr",
  "preferences": {
    "show_email": true,
    "show_eppn": true,
    "show_profile": true,
    "show_publications": true,
    "show_roles": true,
    "show_sshkeys": true
  }
}'

{
  "results": [
    {
      "details": "User: 'Michael J. Stealey, Sr' has been successfully updated",
      "message": "No Content"
    }
  ],
  "size": 1,
  "status": 200,
  "type": "no_content"
}
```

## <a name="peopleuuidprofilepatch"></a>PATCH: `/people/{uuid}/profile`

Parameters: 

- `uuid`: universally unique identier of User

Request body data:

- `--data`: `bio`, `cv`, `job`, `other_identities`, `preferences`, `personal_pages`, `pronouns`, `website` 

Response object: `no_content`

```json
{
  "results": [
    {
      "message": "No Content",
      "details": "string"
    }
  ],
  "type": "no_content",
  "size": 1,
  "status": 200
}
```

Example: 

```console
curl -X 'PATCH' \
  'https://127.0.0.1:8443/people/414b7755-ff33-4442-8227-bbcd362ac05b/profile' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "bio": "my bio",
  "cv": "https://my-cv-on-the-web.com/my-cv",
  "job": "my job",
  "other_identities": [
    {
      "identity": "my other identity",
      "type": "ORCID"
    }
  ],
  "preferences": {
    "show_bio": true,
    "show_cv": true,
    "show_job": true,
    "show_other_identities": true,
    "show_personal_pages": true,
    "show_pronouns": true,
    "show_website": true
  },
  "personal_pages": [
    {
      "url": "https://github.com/mjstealey?tab=repositories",
      "type": "GitHub"
    }
  ],
  "pronouns": "my pronouns",
  "website": "https://my-personal-website.org/about-me"
}'

{
  "results": [
    {
      "details": "Profile for User: 'Michael J. Stealey, Sr' has been successfully updated",
      "message": "No Content"
    }
  ],
  "size": 1,
  "status": 200,
  "type": "no_content"
}
```


---

Parameters:

- `search`: search term applied on name and email
- `offset`: number of items to skip before starting to collect the result set
- `limit`: maximum number of results to return per page (1 to 20)

Response object: `people`

```json
{
    "data": [
        {
            "email": "string",
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
    "total": 0,
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
            "website": "string"
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

    

Personal Page `type` options:

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

# Response Types


Name | Format | Details
:----|:-------|:-------
`error` | single | [details](#error)
`version` | single | [details](#version)
`whoami` | single | [details](#whoami)
`people` | multiple | [details](#people)
`people_one` | single | [details](#people_one)
`projects` | multiple | [details](#projects)
`projects_one` | single | [details](#projects_one)
`sshkeys` | multiple | [details](#sshkeys)
`sshkeys_one` | single | [details](#sshkeys_one)
`bastionkeys` | multiple | [details](#bastionkeys)
`publications` | multiple | [details](#publications)
`publications_one` | single | [details](#publications_one)
`profile_people` | multiple | [details](#profile_people)
`profile_people_one` | single | [details](#profile_people_one)
`profile_projects` | multiple | [details](#profile_projects)
`profile_projects_one` | single | [details](#profile_projects_one)
**Portal Specific GET calls** |
`whoami` (modified) | single | [details](#whoami_alt)
`people_self` | single | [details](#people_self)
`profile_self` | single | [details](#profile_self)
`projects_self` | multiple | [details](#projects_self)

## <a name="responseformat"></a>Response format

### JSON response (data - single - 200)

```json
{
    "data": [
        { <data_object> }
    ],
    "size": 1,
    "status": 200,
    "type": "<type>"
}
```

### JSON response (data - paginated - 200)

See [Pagination](./core-api-pagination.md) for details

```json
{
    "data": [
        { <data_object> },
        ...
    ],
    "limit": <int>,
    "links": {
        "first": "<string>",
        "last": "<string>",
        "next": "<string>",
        "prev": "<string>",
        "self": "<string>"
    }
    "offset": <int>,
    "size": <int>,
    "status": 200,
    "type": "<type>"
}
```

### JSON response (errors - 4xx, 500)

```json
{
    "errors": [
        {
            "detail": "<string>",
            "message": ("<string>":["Bad Request", "Unauthorized", "Forbidden", "Not Found", "Internal Server Error"])
        }
    ],
    "size": <integer>,
    "status": (<integer>:[400, 401, 403, 404, 500]),
    "type": "error"
}
```

`errors`: an array of error objects

## <a name="responsedetails"></a>Response details

### <a name="error"></a>`error`

```json
{
    "errors": [
        {
            "detail": "<string>",
            "message": ("<string>":["Bad Request", "Unauthorized", "Forbidden", "Not Found", "Internal Server Error"])
        }
    ]
    "type": "error",
    "size": <integer>,
    "status": (<integer>:[400, 401, 403, 404, 500])
}
```


### <a name="version"></a>`version`

```json
{
    "data": [
        {
            "reference": "<string>",
            "version": "<string>"
        }
    ],
    "type": "version",
    "size": 1,
    "status": 200
}
```

### <a name="whoami"></a>`whoami`

```json
{
    "data": [
        {
            "active": <bool>,
            "email": "<string>",
            "enrolled": <bool>,
            "name": "<string>",
            "uuid": "<string>"
        }
    ],
    "type": "whoami",
    "size": 1,
    "status": 200
}
```

### <a name="people"></a>`people`

```json
{
    "data": [ <people>, ... ],
    "limit": <int>,
    "links": {
        "first": "<string>",
        "last": "<string>",
        "next": "<string>",
        "prev": "<string>"
    }
    "offset": <int>,
    "size": <int>,
    "status": 200,
    "type": "people"
}
```

Object: `<people>`

```json
{
    "email": "<string>",
    "name": "<string>",
    "uuid": "<string>"
}
```

### <a name="people_one"></a>`people_one`

```json
{
    "data": [
        {
            "affiliation": "<string>",
            "email": "<string>",
            "eppn": "<string>",
            "name": "<string>",
            "profile": <profile_one>
            "publications": [ <publication>, ... ]
            "registered_on": "<string>",
            "roles": [ <role>, ... ],
            "sshkeys": [ <sshkey>, ... ]
            "uuid": "<string>"
        }
    ],
    "size": 1,
    "status": 200,
    "type": "people_one"
}
```

Object: `<profile_one>`

```json
{
    "bio": "<string>",
    "cv": "<string>",
    "identities": [ <identity> ]
    "job": "<string>",
    "social": [ <social> ]
    "professional": [ <professional> ]
    "pronouns": "<string>",
    "website": "<string>",
}
```


Object: `<role>`

```json
{
    "name": "<string>", 
    "description": "<string>"
}
```
### <a name="people_self"></a>`people_self`

```json
{
    "data": [
        {
            "affiliation": "<string>",
            "bastion_login": "<string>",
            "cilogon_email": "<string>",
            "cilogon_eppn": "<string>",
            "cilogon_family_name": "<string>",
            "cilogon_given_name": "<string>",
            "cilogon_id": "<string>",
            "cilogon_idp_name": "<string>",
            "cilogon_name": "<string>",
            "email_addresses": [ "<string>" ],
            "fabric_id": "<string>",
            "preferences": "<string>",
            "roles": [ "<string>" ],
            "sshkeys": [ <sshkey_object> ],
            "email": "<string>",
            "name": "<string>",
            "profile": { <people_profile_object> }
            "registered_on": "<string>",
            "uuid": "<string>"
        }
    ]
    "type": "people_self",
    "size": 1,
    "status": 200
}
```


### <a name="projects"></a>`projects`

```json
{
    "base": "<string>",
    "limit": <int>,
    "next": "<string>",
    "offset": <int>,
    "prev": "<string>",
    "type": "projects",
    "results": [{<projects_one}, ...],
    "size": <int>,
    "status": 200
}
```

### <a name="projects_one"></a>`projects_one`

```json
{
    "created": "<datetime:utc>",
    "created_by": {<people_one>},
    "description": "<string>",
    "facility": "<string>",
    "is_member": <bool>,
    "modified": "<datetime:utc>",
    "name": "<string>",
    "preferences": [{<preference>}, ...],
    "profile": "<string>",
    "project_members": [{<people_one>}, ...],
    "project_owners": [{<people_one>}, ...],
    "type": "projects_one",
    "status": 200,
    "tags": [{<tag>}, ...],
    "uuid": "<string>"
}
```

### <a name="sshkeys"></a>`sshkeys`

```json
{
    "base": "<string>",
    "limit": <int>,
    "next": "<string>",
    "offset": <int>,
    "prev": "<string>",
    "type": "sshkeys",
    "results": [{<sshkeys_one>}, ...],
    "size": <int>,
    "status": 200
}
```

### <a name="sshkeys_one"></a>`sshkeys_one`

```json
{
    "comment": "<string>",
    "created_on": "<string>",
    "deactivated_on": "<string>",
    "deactivation_reason": "<string>",
    "description": "<string>",
    "expires_on": "<string>",
    "fabric_key_type": "<string>",
    "fingerprint": "<string>",
    "key_uuid": "<string>",
    "public_key": "<string>",
    "type": "sshkeys_one",
    "ssh_key_type": "<string>",
    "status": 200
}
```

### <a name="bastionkeys"></a>`bastionkeys`

```json
{
    "base": "<string>",
    "limit": <int>,
    "next": "<string>",
    "offset": <int>,
    "prev": "<string>",
    "type": "bastionkeys",
    "results": [
        {
            "gecos": "gecos",
            "login": "login",
            "public_openssh": "public_openssh",
            "status": "deactivated"
        }, 
        ...
    ],
    "size": <int>,
    "status": 200
}
```

### <a name="publications"></a>`publications`

### <a name="publications_one"></a>`publications_one`

### <a name="profile_people"></a>`profile_people`

### <a name="profile_people_one"></a>`profile_people_one`

```
- Display name - a name the experimenter chooses to have displayed to other users of the portal  if the name from CI Logon is not preferred
- IDs from other identity services such as ORCID, Google Scholar.
- Links to personal pages on resources such as LinkedIn, Twitter, Youtube, Github.
- Link to a personal website
- The affiliation associated with the email address used to log in will have been obtained via CILogon, but they may wish to list other affiliations.
- Role/job/position
- Short bio
- Link to a CV or resume. (Later it might be nice if this could be stored on the Portal). 
```

```json
{
    "data": [
        {
            "bio": "<string>",
            "cv": "<string>",
            "identities": [ <identity_object> ],
            "job": "<string>",
            "social": [ <social_object> ],
            "preferences": { <preferences_profile_people> },
            "professional": [ <professional_object> ],
            "pronouns": "<string>",
            "publications": [ <publications_object> ],
            "website": "<string>",
        }
    ],
    "type": "profile_people_one",
    "size": 1,
    "status": 200
}
```

### <a name="profile_projects"></a>`profile_projects`

### <a name="profile_projects_one"></a>`profile_projects_one`

```
- Subjects/topics/keywords
- Name (required to create project)
- Description (required to create project)
- Facility (set by default)
- Goals/value statement
- Purpose - class? research? Etc?
- Award number with directorate acronym
- Project owner (name and email) - need to have permission to show email
- Project members (name and email) - need to have permission to show email
- Add works where this project work is discussed/featured.
- Notebooks they want to share.
- Is there a status for a project (e.g., like if it is for a class and the class ends)... we may not need to show this necessarily but we do need to know it. Can this be automated in some way based on a lack of activity?
```

```json
{
    "data": [
        {
            "keywords": ["<string>", ...]
            "goals": "<string>",
            "purpose": "<string>",
            "award_information": {format TBD},
            "references": [{format TBD}, ...],
            "notebooks": [{format TBD}, ...],
            "project_status": {format TBD}
            "is_public": <bool>,
            "uuid": "<string>"
        }
    ],
    "type": "profile_projects_one",
    "size": 1,
    "status": 200
}
```

## Portal Specific - Alternate Response types

### <a name="whoami_alt"></a>`whoami`

```json
{
    "data": [
        {
            "active": <bool>,
            "enrolled": <bool>,
            "uuid": "<string>"
        }
    ]
    "type": "whoami",
    "size": 1,
    "status": 200
}
```

### <a name="profile_self"></a>`profile_self`

```
- Display name - a name the experimenter chooses to have displayed to other users of the portal  if the name from CI Logon is not preferred
- IDs from other identity services such as ORCID, Google Scholar.
- Links to personal pages on resources such as LinkedIn, Twitter, Youtube, Github.
- Link to a personal website
- The affiliation associated with the email address used to log in will have been obtained via CILogon, but they may wish to list other affiliations.
- Role/job/position
- Short bio
- Link to a CV or resume. (Later it might be nice if this could be stored on the Portal). 
```

```json
{
    "data": [
        {
            "affiliation": "<string>",
            "affiliations_other": [{format TBD}, ...],
            "bio": "<string>",
            "email": "<string>",
            "email_addresses": ["<string>", ...],
            "email_openid": "<string>",
            "identities": [{format TBD}, ...],
            "position": "<string>",
            "preferences": [{<preference>}, ...],
            "name": "<string>",
            "name_openid": "<string>",
            "personal_website": "<string>",
            "professional_links": [{format TBD}, ...],
            "pronouns": "<string>",
            "publications": [{format TBD}, ...],
            "social_links": [{format TBD}, ...],
            "uuid": "<string>"
        }
    ]
    "type": "profile_self",
    "size": 1,
    "status": 200
}
```

### <a name="projects_self"></a>`projects_self`

```json
{
    "base": "<string>",
    "limit": <int>,
    "next": "<string>",
    "offset": <int>,
    "prev": "<string>",
    "type": "projects_self",
    "data": [
        {
            "created": "<string>",
            "created_by": {
                "email": "<string>",
                "name": "<string>",
                "uuid": "<string>"
            },
            "description": "<string>",
            "facility": "<string>",
            "is_public": <bool>,
            "name": "<string>",
            "project_creator": <bool>,
            "project_member": <bool>,
            "project_owner": <bool>,
            "uuid": "<string>"
        },
        ...
    ],
    "size": <int>,
    "status": 200
}
```

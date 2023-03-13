# People

People can only be added to FABRIC by registering through the COmanage enrollment workflow. They cannot be added directly from the API.

## API Endpoints

FABRIC People

### `/people`

- GET - retrieve list of people
  - param: `search` - optional search, 3 or more characters - matches on `name`, `email` or `people_uuid`
  - param: `offset` - number of items to skip before starting to collect the result set
  - param: `limit` - maximum number of results to return per page (1 or more)
  - authz: open to all authenticated users
  - response type: paginated `people`

### `/people/{uuid}`

- GET - retrieve details about a single person
  - param: `as_self` - optional search boolean - default `false`
  - authz: open to all authenticated users
  - response type: singleton `people.details`
- PATCH - update an existing person
  - data: `email` as string (optional)
  - data: `name` as string (optional)
  - data: `preferences.show_email` as boolean (optional)
  - data: `preferences.show_eppn` as boolean (optional)
  - data: `preferences.show_profile` as boolean (optional)
  - data: `preferences.show_publications` as boolean (optional)
  - data: `preferences.show_roles` as boolean (optional)
  - data: `preferences.show_sshkeys` as boolean (optional) 
  - authz: open to authenticated user as self
  - response type: 200 OK as `204 no content`

### `/people/{uuid}/profile`

- PATCH - update an existing person profile
  - data: `bio` as string (optional)
  - data: `cv` as string (optional)
  - data: `job` as string (optional)
  - data: `other_identities.identity` as string (optional)
  - data: `other_identities.type` as string (optional)
  - data: `personal_pages.type` as string (optional)
  - data: `personal_pages.url` as string (optional)
  - data: `preferences.show_bio` as boolean (optional)
  - data: `preferences.show_cv` as boolean (optional)
  - data: `preferences.show_job` as boolean (optional)
  - data: `preferences.show_other_identities` as boolean (optional)
  - data: `preferences.show_personal_pages` as boolean (optional)
  - data: `preferences.show_pronouns` as boolean (optional)
  - data: `preferences.show_website` as boolean (optional)
  - data: `pronouns` as string (optional)
  - data: `website` as string (optional)
  - authz: open to authenticated user as self
  - response type: 200 OK as `204 no content`

### `/people/preferences`

- GET - retrieve list of valid FABRIC people preference types
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `people.preferences`

### `/people/profile/otheridentity-types`

- GET - retrieve list of valid FABRIC people profile other identity types
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `people.profile.otheridentity.types`

### `/people/profile/preferences`

- GET - retrieve list of valid FABRIC people profile preference types
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `people.profile.preferences`

### `/people/profile/personalpage-types`

- GET - retrieve list of valid FABRIC people profile personal page types
  - param: `search` - optional text search, 3 or more characters
  - authz: open to all authenticated users
  - response type: singleton `people.profile.personalpage.types`

## Response and Request formats

### GET response as list

```
{
    "email": "<string>", <-- based on preference "show_email"
    "name": "<string>",
    "uuid": "<string>"
}
```

### GET response as detail - as self

```
{
    "affiliation": "<string>",
    "bastion_login": "<string>",
    "cilogon_email": "<string>",
    "cilogon_family_name": "<string>",
    "cilogon_given_name": "<string>",
    "cilogon_id": "<string>",
    "cilogon_name": "<string>",
    "email": "<string>",
    "email_addresses": [ ... ],
    "eppn": "<string>",
    "fabric_id": "<string>",
    "name": "<string>",
    "preferences": {
        "show_email": <boolean>,
        "show_eppn": <boolean>,
        "show_profile": <boolean>,
        "show_publications": <boolean>,
        "show_roles": <boolean>,
        "show_sshkeys": <boolean>
    },
    "profile": {
        "bio": "<string>",
        "cv": "<string>",
        "job": "<string>",
        "other_identities": [ ... ],
        "personal_pages": [ ... ],
        "preferences": {
            "show_bio": <boolean>,
            "show_cv": <boolean>,
            "show_job": <boolean>,
            "show_other_identities": <boolean>,
            "show_personal_pages": <boolean>,
            "show_pronouns": <boolean>,
            "show_website": <boolean>
        },
        "pronouns": "<string>",
        "website": "<string>"
    },
    "publications": [ ... ],
    "registered_on": "<string>",
    "roles": [ ... ],
    "sshkeys": [ ... ],
    "uuid": "<string>"
}
```

### GET response as detail - as other users

```
{
    "affiliation": "<string>",
    "email": "<string>",             <-- based on preference "show_email"
    "eppn": "<string>",              <-- based on preference "show_eppn"
    "name": "<string>",
    "profile": {                     <-- based on preference "show_profile"
        "bio": "<string>",           <-- based on preference "show_bio"
        "cv": "<string>",            <-- based on preference "show_cv"
        "job": "<string>",           <-- based on preference "show_job"
        "other_identities": [ ... ], <-- based on preference "show_ other_identities"
        "personal_pages": [ ... ],   <-- based on preference "show_personal_pages"
        "pronouns": "<string>",      <-- based on preference "show_pronouns"
        "website": "<string>"        <-- based on preference "show_website"
    },
    "publications": [ ... ],         <-- based on preference "show_publications"
    "registered_on": "<string>",
    "roles": [ ... ],                <-- based on preference "show_roles"
    "sshkeys": [ ... ],              <-- based on preference "show_sshkeys"
    "uuid": "<string>"
}
```

### PATCH people request body

```
{
    "email": "<string>",                <-- optional - match existing entry in "email_addresses"
    "name": "<string>",                 <-- optional - 5 or more characters
    "preferences": {
        "show_email": <boolean>,        <-- optional - true/false
        "show_eppn": <boolean>,         <-- optional - true/false
        "show_profile": <boolean>,      <-- optional - true/false
        "show_publications": <boolean>, <-- optional - true/false
        "show_roles": <boolean>,        <-- optional - true/false
        "show_sshkeys": <boolean>       <-- optional - true/false
    }
}
```

Valid people `preferences` keys:

```json
"preferences_keys": [
    "show_email",
    "show_eppn",
    "show_profile",
    "show_publications",
    "show_roles",
    "show_sshkeys"
]
```

### PATCH people profile request body

```
{
    "bio": "<string>",                      <-- optional - 5 or more characters
    "cv": "<string>",                       <-- optional - URL format
    "job": "<string>",                      <-- optional - 5 or more characters
    "other_identities": [ ... ],            <-- optional - array of other_identities
    "personal_pages": [ ... ],              <-- optional - array of personal_pages
    "preferences": {
        "show_bio": <boolean>,              <-- optional - true/false
        "show_cv": <boolean>,               <-- optional - true/false
        "show_job": <boolean>,              <-- optional - true/false
        "show_other_identities": <boolean>, <-- optional - true/false
        "show_personal_pages": <boolean>,   <-- optional - true/false
        "show_pronouns": <boolean>,         <-- optional - true/false
        "show_website": <boolean>           <-- optional - true/false
    },
    "pronouns": "<string>",                 <-- optional - 5 or more characters
    "website": "<string>"                   <-- optional - URL format
}
```

Valid `other_identities ` format:

```json
"other_identities": [
    {
        "identity": "<string_5_or_more_characters>",
        "type": "<string_otheridentity_types>"
    }
]
```

Valid `string_otheridentity_types ` values:

```json
"string_otheridentity_types": [
    "google_scholar",
    "orcid",
    "other"
]
```

Valid `personal_pages` format: 

```json
"personal_pages": [
    {
        "type": "<string_personalpage_types>",
        "url": "<string_as_URL>"
    }
]
```

Valid `string_personalpage_types ` values:

```json
"string_personalpage_types": [
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
]
```

Valid people profile `preferences` keys:

```json
"preferences_keys": [
    "show_bio",
    "show_cv",
    "show_job",
    "show_other_identities",
    "show_personal_pages",
    "show_pronouns",
    "show_website"
]
```

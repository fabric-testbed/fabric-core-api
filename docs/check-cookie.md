# Check Cookie

When a user authenticates using OIDC through CILogon a [set of claims](https://www.cilogon.org/oidc#h.p_PEQXL8QUjsQm) are returned to the relying party application based on scope.

The resultant claims are then used to uniquely identify a user within FABRIC and determine which tasks they can perform. Authorization (or permissions) are stored in COmanage and reflected within FABRIC.

The `/check-cookie` endpoint has been added to make is easy for the user to convey what claims are known about them and assist in debugging any user related authentication issues.

## API Endpoints

Check Cookie

### `/check-cookie`

- GET - retrieve details about user cookie attributes

## Response formats

### GET response (anonymous)

```json
{
  "cookie_attributes": {},
  "cookie_name": "COOKIE_NOT_FOUND",
  "fabric_attributes": {}
}
```

### GET response (authenticated) 

```json
{
  "cookie_attributes": {
    "email": "CLAIM_NOT_FOUND",
    "family_name": "CLAIM_NOT_FOUND",
    "given_name": "CLAIM_NOT_FOUND",
    "name": "CLAIM_NOT_FOUND",
    "sub": "http://cilogon.org/serverA/users/242181"
  },
  "cookie_name": "fabric-service-alpha",
  "fabric_attributes": {
    "affiliation": [
      "University of North Carolina at Chapel Hill"
    ],
    "roles": [
      "10582cb1-ee10-4b8c-8d61-ffc4688be0d6-pc",
      "10582cb1-ee10-4b8c-8d61-ffc4688be0d6-po",
      "10582cb1-ee10-4b8c-8d61-ffc4688be0d6-tk",
      "1af8e23d-5fa8-46fc-be94-21609abbadd0-pc",
      "1af8e23d-5fa8-46fc-be94-21609abbadd0-po",
      "88c74e11-9324-42e1-83fa-97dc742919b6-pm",
      "8b3a2eae-a0c0-475a-807b-e9af581ce4c0-pm",
      "8b3a2eae-a0c0-475a-807b-e9af581ce4c0-tk",
      "a5488d93-7c6b-48ea-9de1-19e216c0519b-pc",
      "a5488d93-7c6b-48ea-9de1-19e216c0519b-po",
      "approval-committee ",
      "d74993c8-e3b5-451c-977f-c7cc544f176f-pc",
      "d74993c8-e3b5-451c-977f-c7cc544f176f-po",
      "ec8389c8-6129-40aa-a6ee-3a1d80d74f33-pc",
      "fabric-active-users",
      "facility-operators",
      "Jupyterhub",
      "long-lived-tokens",
      "portal-admins",
      "project-leads"
    ],
    "sub": [
      "http://cilogon.org/serverA/users/242181"
    ],
    "uuid": "593dd0d3-cedb-4bc6-9522-a945da0a8a8e"
  }
}
```

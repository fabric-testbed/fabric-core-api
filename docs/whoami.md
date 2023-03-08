# Who Am I

Who am I - information taken from the user authentication cookie as related to their status within FABRIC

- `active` - active in FABRIC (`active-fabric-users` COU)
- `email` - preferred email used by user
- `enrolled` - enrolled in FABRIC (registered in COmanage)
- `name` - display name used by user
- `uuid` - unique universal identifier from People
- `vouch_expiry` - vouch session cookie expiration time

## API Endpoints

Who am I authenticated as?

### `/whoami`

- GET - retrieve details about authenticated user
  - authz: open to all

## Response and Request formats

### GET response as detail

Authenticated users

```
{
    "active": <boolean>,
    "email": "<string>",
    "enrolled": <boolean>,
    "name": "<string>",
    "uuid": "<string>",
    "vouch_expiry": <integer>
}
```

Unauthenticated users - full response shown for clarity

```
{
  "errors": [
    {
      "details": "Login required: Please Log in (or Sign up) on the FABRIC Portal",
      "message": "Unauthorized"
    }
  ],
  "size": 1,
  "status": 401,
  "type": "error"
}
```

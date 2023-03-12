# SSH Keys

Allow authenticated users to create or put pubic SSH keys into core-api

- Format is RSA or ECDSA
- Only **public** keys are stored in core-api
- Generated **private** key data is displayed to the user once and then is destroyed

Allow bastion hosts to search for `active`, `deactivated`, or `expired` bastion keys

- Uses shared secret between bastion host and core-api
- Response based on `since_date` formatted as UTC

## API Endpoints

FABRIC Public SSH Keys

### `/bastionkeys`

- GET - retrieve list of public bastion keys that have been created/disabled/expired since a specific date/time
  - param: `secret` - required shared secret between bastion hosts and core-api
  - param: `since_time` - required Date/Time
  - authz: open to all users with the shared secret

### `sshkeys`

- GET - retrieve list of SSH keys
  - param: `person_uuid` - required - uuid of person to search by
  - authz: open to all authenticated users
- POST - create a new SSH public/private key pair
  - authz: open to all authenticated users
- PUT - add an existing SSH public key
  - authz: open to all authenticated users

### `sshkeys/{uuid}`

- GET - retrieve details about a single SSH key
  - authz: open to all authenticated users
- DELETE - remove an existing SSH key
  - authz: open to all authenticated users

## Response and Request formats

### GET response - bastionkeys

```json
{
    "gecos": "<string>",
    "login": "<string>",
    "public_openssh": "<string>",
    "status": "<string>"
}
```

### GET response - sshkeys - list and detail

```json
{
    "comment": "<string>",
    "created_on": "<string>",
    "deactivated_on": "<string>",
    "deactivated_reason": "<string>",
    "description": "<string>",
    "expires_on": "<string>",
    "fabric_key_type": "<string>",
    "fingerprint": "<string>",
    "public_key": "<string>",
    "ssh_key_type": "<string>",
    "uuid": "<string>"
}
```

### GET response - sshkeys - response from POST

The response following a successful POST call will contain both the **public** and **private** keys of the newly created SSH key pair. 

- This is the only time that the **private** key will be shown
- **private** keys are not saved within core-api

```json
{
    "private_openssh": "<string>",
    "public_openssh": "<string>"
}
```

### POST request - sshkeys

```
{
    "comment": "<string>",     <-- required - 5-100 chars, regex pattern: '^[\w\-.@()]+$'
    "description": "<string>", <-- required - 5-255 chars, regex pattern: '^[\w\s\-.,@('')/]+$'
    "keytype": "<string>"      <-- required - "sliver", "bastion"
}
```

### PATCH request - sshkeys

```
{
    "description": "<string>",   <-- required - 5-255 chars, regex pattern: '^[\w\s\-.,@('')/]+$'
    "keytype": "<string>",       <-- required - "sliver", "bastion"
    "public_openssh": "<string>" <-- required - public key of type RSA or ECDSA
}
```

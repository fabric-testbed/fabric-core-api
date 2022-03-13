# SSH Keys

Functions:

- POST: Create new sshkey: input - keytype, comment, description; output - pub/priv key (SshKeyPair)
- PUT: Add user public key: input - keytype, public_openssh, description; output - no content
- GET: specific key of a given user: input - uuid; output - SshKey
- DELETE: specific key: input - uuid; output - no content
- GET: list of active keys: input - self; output - array of SshKey
- GET: bastionkeys: input - secret, since_date; output - array of BastionKey

## Endpoints

- GET, POST, PUT: `/sshkeys`
- GET, DELETE: `/sshkeys/{uuid}`
- GET: `/bastionkeys`

## Details


```
SshKey:
- key_uuid:
- public_key:
- ssh_key_type:
- comment:
- description:
- fingerprint:
- fabric_key_type: [bastion, sliver]
- created_on:
- expires_on:
- deactivated_on:
- deactivation_reason:
```

```
BastionKey:
- public_openssh:
- login:
- gecos:
- status: [active, deactivated, expired]
```

```
SshKeyPair:
- private_openssh:
- public_openssh:
```

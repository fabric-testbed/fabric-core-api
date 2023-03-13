# Testbed Info

Relay information about the testbed as a JSON object to any user with or without authentication

## API Endpoints

Testbed Information

### `/testbed-info`

- GET - retrieve testbed information details
  - authz: open to all
  - response type: singleton `testbed.info`
- POST - create new testbed information
  - data: `testbed_info` - required - uuid of person to search by
  - authz: `facility-operators` - only role allowed to create new testbed-info
  - response type: singleton `testbed.info`

## Response and Request formats

### GET response 

```json
{
    "testbed_info": {}
}
```

### POST request 

```
{
    "testbed_info": {} <-- any valid JSON
}
```

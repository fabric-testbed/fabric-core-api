# Version

Version information

- reference to the GitHub repository
- version as code release

## API Endpoints

Core API Version

### `/version`

- GET - retrieve details about core-api version
  - authz: open to all
  - response type: singleton `version`

## Response and Request formats

### GET response as detail

```
{
    "reference": "<string>",
    "version": "<string>"
}
```

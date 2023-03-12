# Publications

**_WORK IN PROGRESS_** - release 1.6

## API Endpoints

FABRIC Publications

### `/publications`

- GET - retrieve list of publications
- POST - create a new publication

### `/publications/{uuid}`

- GET - retrieve details about a single publication
- PATCH - update an existing publication
- DELETE - remove an existing publication

### `/publications/classification-terms`

- GET - retrieve list of valid publication classification terms
  - param: `search` - optional text search, 3 or more letters
  - authz: open to all authenticated users

## Response and Request formats

### GET response 

```
{
    ...
}
```

### POST request 

```
{
    ...
}
```

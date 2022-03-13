# Pagination


### Why pagination?

Often when you're making calls to the FABRIC Core REST API there'll be a lot of results to return. For that reason we paginate the results to make sure responses are easier to handle.

Let's say your initial call is asking for all the results for FABRIC projects; the results set could be large with hundreds of entries. That's not a good place to start.

To alleviate this we've built in a default limit on results, but recommend you always explicitly set the `limit` parameter to ensure you know how many results per page you'll get. Don't rely on the defaults as they may be different depending on what parts of the API you're working with, so the response you get might not be what you expected.

## Format

### JSON response (paginated)

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
        "prev": "<string>"
    }
    "offset": <int>,
    "size": <int>,
    "status": 200,
    "total": <int>,
    "type": "<type>"
}
```

**Resposne keys glossary**

- `data` - the document’s “primary data” 
- `data_object` - results defined by `type` (0 or more)
- `limit` - maximum number of results to return per page (1 or more)
- `links` - a links object related to the primary data
- `first` - the first page of data
- `last` - the last page of data
- `next` - the next page of data
- `prev` - the previous page of data
- `offset`- number of items to skip before starting to collect the result set
- `size` - size of the returned results set (1 to limit)
- `status` - HTTP status code (200) - About [HTTP status codes](./core-api-status-codes.md)
- `total` - total number of results found
- `type ` - type of results being returned (see [Response Types](./core-api-resposne-types.md))



## Example

You might need to request all pages in the projects space, but you only want the results 5 at a time.

### Set the limit parameter

The endpoint we're going to hit here to specifically get the pages in that space is `/projects`. Your `GET` would look something like this:

```bash
curl -X GET "https://127.0.0.1:8443/fabric/api/projects?limit=5"
```

```json
{
    "data": [
        { <data_object_0> },
        { <data_object_1> },
        { <data_object_2> },
        { <data_object_3> },
        { <data_object_4> }
    ],
    "limit": 5,
    "links": {
        "first": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=0",
        "last": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=10",
        "next": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=5"
    }
    "offset": 0,
    "size": 5,
    "status": 200,
    "total": 11,
    "type": "projects"
}
```

### GET the next page of results

You can then make a call to return the next page. The offset parameter in the `next` link is 5, so the next page of results will show items 5 through 9. The call will be as follows:

```bash
curl -X GET "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=5"
```

```json
{
    "data": [
        { <data_object_5> },
        { <data_object_6> },
        { <data_object_7> },
        { <data_object_8> },
        { <data_object_9> }
    ],
    "limit": 5,
    "links": {
        "first": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=0",
        "last": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=10",
        "next": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=10",
        "prev": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=0"
    }
    "offset": 5,
    "size": 5,
    "status": 200,
    "total": 11,
    "type": "projects"
}
```

### How do I know if there are more pages?

When the response doesn't contain a link to the next page of results, you know that you've reached the end. Below you'll see the call for the next page of results, and the response which doesn't contain a `next` link.

```bash
curl -X GET "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=10"
```

```json
{
    "data": [
        { <data_object_10> }
    ],
    "limit": 5,
    "links": {
        "first": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=0",
        "last": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=10",
        "prev": "https://127.0.0.1:8443/fabric/api/projects?limit=5&offset=5"
    }
    "offset": 10,
    "size": 1,
    "status": 200,
    "total": 11,
    "type": "projects"
}
```

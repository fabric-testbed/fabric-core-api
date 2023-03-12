# HTTP Status Codes

### Categories

HTTP defines over 40 standard status codes that can be used to convey the results of a client’s request. The status codes are divided into the five categories:

- `1xx`: **Informational** - Communicates transfer protocol-level information
- `2xx`: **Success** -Indicates that the client’s request was accepted successfully.
- `3xx`: **Redirection** - Indicates that the client must take some additional action in order to complete their request.
- `4xx`: **Client Error** - This category of error status codes points the finger at clients.
- `5xx`: **Server Error** - The server takes responsibility for these error status codes.

### Status codes

When you boil it down, there are really only 3 outcomes in the interaction between an app and an API:

- Everything worked
- The application did something wrong
- The API did something wrong

core-api will make use of the following status codes:

- `200`: **OK**
- `400`: **Bad Request**
- `401`: **Unauthorized**
- `403`: **Forbidden**
- `404`: **Not Found**
- `423`: **Locked**
- `500`: **Internal Server Error**

Example of each below:

- **200 (OK) must not be used to communicate errors in the response body**

    Always make proper use of the HTTP response status codes as specified by the rules in this section. In particular, a REST API must not be compromised in an effort to accommodate less sophisticated HTTP clients.
    
    Paginated response:
    
    ```json
    {
        "limit": 5,
        "links": {
            "first": "https://uis.fabric-testbed.net/projects?sort_by=name&order_by=asc&offset=0&limit=5",
            "last": "https://uis.fabric-testbed.net/projects?sort_by=name&order_by=asc&offset=50&limit=5",
            "next": "https://uis.fabric-testbed.net/projects?sort_by=name&order_by=asc&offset=15&limit=5",
            "prev": "https://uis.fabric-testbed.net/projects?sort_by=name&order_by=asc&offset=5&limit=5"
        },
        "offset": 10,
        "results": [
            { "<project_response_object_11>" },
            { "<project_response_object_12>" },
            { "<project_response_object_13>" },
            { "<project_response_object_14>" },
            { "<project_response_object_15>" }
        ],
        "size": 5,
        "status": 200,
        "total": 51,
        "type": "projects"
    }
    ```
    
    Singleton response:
    
    ```json
    {
        "results": [
            { "<project_response_object>" }
        ],
        "size": 1,
        "status": 200,
        "type": "projects.details"
    }
    ```

- **400 (Bad Request) may be used to indicate nonspecific failure**

    400 is the generic client-side error status, used when no other 4xx error code is appropriate. For errors in the 4xx category, the response body may contain a document describing the client’s error (unless the request method was HEAD).
    
    ```json
    {
        "errors": [
            {
                "details": "Projects Preferences: 'show_XYZ' is not a valid preference type",
                "message": "Bad Request"
            }
        ],
        "size": 1,
        "status": 400,
        "type": "error"
    }
    ```

- **401 (Unauthorized) must be used when there is a problem with the client’s credentials**

    A 401 error response indicates that the client tried to operate on a protected resource without providing the proper authorization. It may have provided the wrong credentials or none at all.
    
    ```json
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

- **403 (Forbidden) should be used to forbid access regardless of authorization state**

    A 403 error response indicates that the client’s request is formed correctly, but the REST API refuses to honor it. A 403 response is not a case of insufficient client credentials; that would be 401 (“Unauthorized”). REST APIs use 403 to enforce application-level permissions. For example, a client may be authorized to interact with some, but not all of a REST API’s resources. If the client attempts a resource interaction that is outside of its permitted scope, the REST API should respond with 403.
    
    ```json
    {
        "errors": [
            {
                "details": "User: 'mj stealey' does not have access to this private project",
                "message": "Forbidden"
            }
        ],
        "size": 1,
        "status": 403,
        "type": "error"
    }
    ```

- **404 (Not Found) must be used when a client’s URI cannot be mapped to a resource**

    The 404 error status code indicates that the REST API can’t map the client’s URI to a resource.
    
    ```json
    {
        "errors": [
            {
                "details": "No match for Project with uuid = '386c1875-b642-4675-bb37-30cbf348b52X'",
                "message": "Not Found"
            }
        ],
        "size": 1,
        "status": 404,
        "type": "error"
    }
    ```
    
- **423 (Locked) if the resource is in the process of being modified**

    The resource that is being accessed is locked, it can be read, but not modified until it is unlocked.
    
    ```json
    {
        "errors": [
            {
                "details": "Locked project, uuid = '386c1875-b642-4675-bb37-30cbf348b522', expires_on = '2024-03-09 20:28:25.301034+00:00'",
                "message": "Locked"
            }
        ],
        "size": 1,
        "status": 423,
        "type": "error"
    }
    ```

- **500 (Internal Server Error) should be used to indicate API malfunction 500 is the generic REST API error response.**

    Most web frameworks automatically respond with this response status code whenever they execute some request handler code that raises an exception. A 500 error is never the client’s fault and therefore it is reasonable for the client to retry the exact same request that triggered this response, and hope to get a different response.

    ```json
    {
        "errors": [
            {
                "details": "Oops! something went wrong with projects_uuid_get(): whoops",
                "message": "Internal Server Error"
            }
        ],
        "size": 1,
        "status": 500,
        "type": "error"
    }
```

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

FABRIC core-api will make use of the following status codes:

- `200`: **OK**
- `400`: **Bad Request**
- `401`: **Unauthorized**
- `403`: **Forbidden**
- `404`: **Not Found**
- `500`: **Internal Server Error**

Details below:

- **200 (OK) must not be used to communicate errors in the response body**

    Always make proper use of the HTTP response status codes as specified by the rules in this section. In particular, a REST API must not be compromised in an effort to accommodate less sophisticated HTTP clients.

- **400 (Bad Request) may be used to indicate nonspecific failure**

    400 is the generic client-side error status, used when no other 4xx error code is appropriate. For errors in the 4xx category, the response body may contain a document describing the client’s error (unless the request method was HEAD).

- **401 (Unauthorized) must be used when there is a problem with the client’s credentials**

    A 401 error response indicates that the client tried to operate on a protected resource without providing the proper authorization. It may have provided the wrong credentials or none at all.

- **403 (Forbidden) should be used to forbid access regardless of authorization state**

    A 403 error response indicates that the client’s request is formed correctly, but the REST API refuses to honor it. A 403 response is not a case of insufficient client credentials; that would be 401 (“Unauthorized”). REST APIs use 403 to enforce application-level permissions. For example, a client may be authorized to interact with some, but not all of a REST API’s resources. If the client attempts a resource interaction that is outside of its permitted scope, the REST API should respond with 403.

- **404 (Not Found) must be used when a client’s URI cannot be mapped to a resource**

    The 404 error status code indicates that the REST API can’t map the client’s URI to a resource.

- **500 (Internal Server Error) should be used to indicate API malfunction 500 is the generic REST API error response.**

    Most web frameworks automatically respond with this response status code whenever they execute some request handler code that raises an exception. A 500 error is never the client’s fault and therefore it is reasonable for the client to retry the exact same request that triggered this response, and hope to get a different response.

# Pagination - response list for multiple items


### Why pagination?

Pagination limits the number of results returned in a response to allow or a faster, more robust interaction with core-api.

- The core-api limit is user definable from 1 to 200 results per page
- The default limit is 5

## Format

All paginated responses have a similar format in that they define the following

- `limit` - maximum number of results to return per page (1 or more) as `integer`
- `links` - a links object related to the response "data"
    - `first` - the first page of data as `string`
    - `last` - the last page of data as `string`
    - `next` - the next page of data as `string`
    - `prev` - the previous page of data as `string`
- `offset`- number of items to skip before starting to collect the result set as `integer`
- `results` - the document’s response "data” as `JSON`
- `size` - size of the returned results set (1 to limit) as `integer`
- `status` - HTTP status code (normally 200) as `integer`
- `total` - total number of results found as `integer`
- `type ` - the "type" of results being returned as `string`


### Structure of a paginated response

```json
{
  "limit": 0,
  "links": {
    "first": "<string>",
    "last": "<string>",
    "next": "<string>",
    "prev": "<string>"
  },
  "offset": 0,
  "results": [],
  "size": 0,
  "status": 200,
  "total": 0,
  "type": "<string>"
}
```

### Example paginated response from /projects

As an example, a query was made to the `/projects` endpoint as:

- Note: Some endpoints may include additional parameters beyond `limit` and `offset`

```
curl -X 'GET' \
    'https://uis.fabric-testbed.net/projects?offset=15&limit=2&sort_by=name&order_by=asc' \
    -H 'accept: application/json'
```

With the following response:

```json
{
    "limit": 2,
    "links": {
        "first": "https://uis.fabric-testbed.net/projects?sort_by=name&order_by=asc&offset=0&limit=2",
        "last": "https://uis.fabric-testbed.net/projects?sort_by=name&order_by=asc&offset=50&limit=2",
        "next": "https://uis.fabric-testbed.net/projects?sort_by=name&order_by=asc&offset=17&limit=2",
        "prev": "https://uis.fabric-testbed.net/projects?sort_by=name&order_by=asc&offset=13&limit=2"
    },
    "offset": 15,
    "results": [
        {
            "created": "2022-09-10 22:50:10.404648+00:00",
            "description": "This project will bring young STEM students onto FABRIC to teach about the next Internet and inspire them to dream big!",
            "facility": "FABRIC",
            "is_public": true,
            "memberships": {
                "is_creator": false,
                "is_member": false,
                "is_owner": false
            },
            "name": "FABRIC in the High School",
            "tags": [],
            "uuid": "6fc62ffe-50d2-49ba-b668-aac8878afdab"
        },
        {
            "created": "2021-08-11 18:20:26+00:00",
            "description": "FABRIC Team",
            "facility": "FABRIC",
            "is_public": true,
            "memberships": {
                "is_creator": false,
                "is_member": true,
                "is_owner": true
            },
            "name": "FABRIC Staff",
            "tags": [
                "Component.FPGA",
                "Component.GPU",
                "Component.NVME",
                "Component.SmartNIC",
                "Component.Storage",
                "Net.AllFacilityPorts",
                "Net.NoLimitBW",
                "Net.PortMirroring",
                "Slice.Multisite",
                "Slice.Measurements",
                "VM.NoLimit",
                "VM.NoLimitDisk",
                "VM.NoLimitRAM",
                "VM.NoLimitCPU",
                "Net.FacilityPort.Chameleon-StarLight",
                "Net.FacilityPort.ESnet-StarLight",
                "Net.FacilityPort.Internet2-StarLight",
                "Net.FABNetv4Ext",
                "Net.FABNetv6Ext",
                "Slice.NoLimitLifetime",
                "Net.FacilityPort.Chameleon-TACC",
                "Net.FacilityPort.Cloud-Facility-AWS",
                "Net.FacilityPort.Cloud-Facility-Azure",
                "Net.FacilityPort.Cloud-Facility-Azure-Gov",
                "Net.FacilityPort.Cloud-Facility-GCP",
                "Net.FacilityPort.Utah-Cloudlab-Powder"
            ],
            "uuid": "990d8a8b-7e50-4d13-a3be-0f133ffa8653"
        }
    ],
    "size": 2,
    "status": 200,
    "total": 51,
    "type": "projects"
}
```

## Additional information

### why are there links?

An API is often used to "drive" a UI, and the links for `first`, `last`, `next`, and `prev` are often embedded as "button navigation" of the UI

### how do I `GET` the next page of results?

The next page of results will be defined by the `next` attribute in the `links` section

### how do I know when there are no more pages?

When the response doesn't contain a link to the `next` page of results, you know that you've reached the end

This same concept also applies for `prev` if your response is for the first page of results

### what happens if there are no results?

When no results are found for a given paginated response, the links section will be empty.

Example query:

```
curl -X 'GET' \
    'https://uis.fabric-testbed.net/projects?search=no-results-to-find&offset=0&limit=5&sort_by=name&order_by=asc' \
    -H 'accept: application/json'
```

With the following response:

```json
{
    "limit": 5,
    "links": {},
    "offset": 0,
    "results": [],
    "size": 0,
    "status": 200,
    "total": 0,
    "type": "projects"
}
```

# Singleton - response details for one item

A singleton response provides details about one item. 

- Often much more detailed than items found in a paginated response
- Content can vary depending on user role, item preference settings, memberships, or other affiliation to the requested item


## Format

All singleton responses have a similar format in that they define the following

- `results` - the document’s response "data” as `JSON`
- `size` - size of the returned results set (generally 1) as `integer`
- `status` - HTTP status code (normally 200) as `integer`
- `type ` - the "type" of results being returned as `string`

### Structure of a singleton response

```json
{
    "results": [
        { "<singleton_response_data>" }
    ],
    "size": 1,
    "status": 200,
    "type": "<string>"
}
```

### Example paginated response from /projects

As an example, a query was made to the `/projects/{uuid}` endpoint as:

```
curl -X 'GET' \
    'https://beta-3.fabric-testbed.net/projects/386c1875-b642-4675-bb37-30cbf348b522' \
    -H 'accept: application/json'
```

If a project with the requested uuid is found, then a response would look like the following:

```json
{
    "results": [
        {
            "active": true,
            "created": "2022-03-07 18:24:43.571568+00:00",
            "description": "beta - test project for API work",
            "expires_on": "2024-03-09 23:51:36.449807+00:00",
            "facility": "FABRIC",
            "is_locked": false,
            "is_public": true,
            "memberships": {        
                "is_creator": true,
                "is_member": false,
                "is_owner": true
            },
            "modified": "2023-03-10 23:52:01.029776+00:00",
            "name": "beta - test project",
            "preferences": {
                "show_profile": true,
                "show_project_members": true,
                "show_project_owners": true,
                "show_publications": true
            },
            "profile": {
                "award_information": "award information",
                "goals": "goals",
                "keywords": [
                    "keyword 1",
                    "keyword 2"
                ],
                "notebooks": [],
                "preferences": {
                    "show_award_information": true,
                    "show_goals": true,
                    "show_keywords": true,
                    "show_notebooks": true,
                    "show_project_status": true,
                    "show_purpose": true,
                    "show_references": true
                },
                "project_status": "project status",
                "purpose": "purpose",
                "references": []
            },
            "project_creators": [
                {
                    "email": "stealey@unc.edu",
                    "name": "Michael J. Stealey, Sr",
                    "uuid": "224ca0a4-ef33-400f-9022-8baddd02c208"
                }
            ],
            "project_members": [
                {
                    "email": "ibaldin@renci.org",
                    "name": "Ilya Baldin",
                    "uuid": "a5bab5f3-7725-48e2-aac2-705e553e0766"
                },
                {
                    "email": "mjstealey@gmail.com",
                    "name": "mj stealey",
                    "uuid": "107dd923-05be-4333-ba83-f516ad602f86"
                }
            ],
            "project_owners": [
                {
                    "email": "stealey@unc.edu",
                    "name": "Michael J. Stealey, Sr",
                    "uuid": "224ca0a4-ef33-400f-9022-8baddd02c208"
                }
            ],
            "project_storage": [],
            "publications": [],
            "tags": [
                "Component.FPGA",
                "Component.GPU",
                "Component.NVME",
                "Component.SmartNIC",
                "Component.Storage",
                "Net.AllFacilityPorts",
                "Net.FABNetv4Ext",
                "Net.FABNetv6Ext",
                "Net.FacilityPort.RENC-Chameleon",
                "Net.FacilityPort.RENC-GSU",
                "Net.NoLimitBW",
                "Net.PortMirroring",
                "Slice.Measurements",
                "Slice.Multisite",
                "Slice.NoLimitLifetime",
                "VM.NoLimit",
                "VM.NoLimitCPU",
                "VM.NoLimitDisk",
                "VM.NoLimitRAM"
            ],
            "uuid": "386c1875-b642-4675-bb37-30cbf348b522"
        }
    ],
    "size": 1,
    "status": 200,
    "type": "projects.details"
}
```

If however a project does not exist for the requested uuid, the response would be:

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

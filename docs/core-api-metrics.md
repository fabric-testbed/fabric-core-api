# Core API metrics

Read-only endpoints exposing aggregated user, project, and event-level activity metrics. Useful for facility dashboards, periodic reporting, and per-user / per-project audit trails.

All `/core-api-metrics` endpoints return JSON; aggregate counters are recomputed on a cadence governed by `CAM_TIMEOUT_IN_SECONDS` in `.env` (default `3600`).

## API Endpoints

### `/core-api-metrics/overview`

- GET — high-level user and project counters (cumulative + rolling-window active user counts)
  - authz: open (no authentication required)
  - response type: see [Overview response](#overview-response) below

### `/core-api-metrics/events`

- GET — recent core-api events (audit log of user/project actions)
  - param: `offset` — pagination offset
  - param: `limit` — page size (1 or more)
  - authz: `facility-operators` or `facility-viewers`
  - response type: paginated `core_api_metrics_events`

### `/core-api-metrics/events/people-membership/{uuid}`

- GET — events related to membership changes for a specific person
  - path: `uuid` — person UUID
  - authz: `facility-operators` or `facility-viewers`
  - response type: singleton `core_api_metrics_events_membership`

### `/core-api-metrics/events/projects-membership/{uuid}`

- GET — events related to membership changes for a specific project
  - path: `uuid` — project UUID
  - authz: `facility-operators` or `facility-viewers`
  - response type: singleton `core_api_metrics_events_membership`

### `/core-api-metrics/people`

- GET — list of people with summary metrics (login counts, role activity, etc.)
  - param: `offset` — pagination offset
  - param: `limit` — page size (1 or more)
  - authz: `facility-operators` or `facility-viewers`
  - response type: paginated `core_api_metrics_people`

### `/core-api-metrics/people-details/{uuid}`

- GET — detailed metrics for a single person
  - path: `uuid` — person UUID
  - authz: `facility-operators` or `facility-viewers`
  - response type: singleton `core_api_metrics_people_one`

### `/core-api-metrics/projects`

- GET — list of projects with summary metrics (membership counts, lifecycle state, etc.)
  - authz: `facility-operators` or `facility-viewers`
  - response type: singleton `core_api_metrics_projects`

### `/core-api-metrics/projects-details/{uuid}`

- GET — detailed metrics for a single project
  - path: `uuid` — project UUID
  - authz: `facility-operators` or `facility-viewers`
  - response type: singleton `core_api_metrics_projects_one`

## Response formats

### <a name="overview-response"></a>`/core-api-metrics/overview` response

```
{
    "last_updated": "<string>",
    "projects": {
        "active_cumulative": <integer>,
        "non_active_cumulative": <integer>
    },
    "users": {
        "active_cumulative": <integer>,
        "active_within_180_days": <integer>,
        "active_within_24_hours": <integer>,
        "active_within_30_days": <integer>,
        "active_within_7_days": <integer>,
        "active_within_90_days": <integer>,
        "non_active_cumulative": <integer>
    }
}
```

For the exact shape of the per-person, per-project, and event response schemas, see the OpenAPI spec at [`server/swagger_server/swagger/swagger.yaml`](../server/swagger_server/swagger/swagger.yaml) under `components/schemas/core_api_metrics_*`.

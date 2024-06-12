# Core API metrics

High level overview of Core API User and Project metrics

## API Endpoints

Core API metrics overview

### `/core-api-metrics/overview`

- GET - retrieve high level user and project details

## Response formats

GET response (anonymous/authenticated)

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

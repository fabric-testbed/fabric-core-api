# Announcements

Announcements that are displayed on the portal regarding maintenance or facility updates.

## API Endpoints

FABRIC Facility and Maintenance Announcements

### `/announcements`

- GET - retrieve list of announcements
  - param: `announcement_type` - optional search by announcement type
  - param: `is_active` - optional search by "is active" value
  - param: `search` - optional text search, 3 or more letters
  - param: `offset` - number of items to skip before starting to collect the result set
  - param: `limit` - maximum number of results to return per page (1 or more
  - authz: open to all 
  - response type: paginated `announcements`
- POST - create a new announcement
  - data: `announcement_type` as string (required)
      - `carousel` - required: button, content, is_active, link, sequence, title
      - `facility` - required: content, display_date, is_active, start_date, title 
      - `maintenance` - required: content, end_date, is_active, start_date, title 
      - `news` - required: content, display_date, is_active, link, title 
  - data: `background_image_url` as string
  - data: `button` as string
  - data: `content` as string
  - data: `display_date` as string
  - data: `end_date` as string
  - data: `is_active` as boolean
  - data: `link` as string
  - data: `sequence` as integer
  - data: `start_date` as string
  - data: `title` as string
  - authz: `portal-admins` - only role allowed to create announcements
  - response type: singleton `announcemnts.details`

### `/announcements/{uuid}`

- GET - retrieve details about a single announcement
  - authz: open to all 
  - response type: singleton `announcemnts.details`
- PATCH - update an existing announcement
  - data: `announcement_type` as string (optional)
  - data: `background_image_url` as string (optional)
  - data: `button` as string (optional)
  - data: `content` as string (optional)
  - data: `display_date` as string (optional)
  - data: `end_date` as string (optional)
  - data: `is_active` as boolean (optional)
  - data: `link` as string (optional)
  - data: `sequence` as integer (optional)
  - data: `start_date` as string (optional)
  - data: `title` as string (optional)
  - authz: `portal-admins` - only role allowed to update announcements
  - response type: 200 OK as `204 no content`
- DELETE - remove an existing announcement
  - authz: `portal-admins` - only role allowed to delete announcements
  - response type: 200 OK as `204 no content`

## Response and Request formats

### GET response as list or detail

```
{
    "announcement_type": "<string>",
    "background_image_url": "<string>",
    "button": "<string>",
    "content": "<string>",
    "display_date": "<string>",
    "end_date": "<string>",
    "is_active": <boolean>,
    "link": "<string>",
    "sequence": <integer>,
    "start_date": "<string>",
    "title": "<string>",
    "uuid": "<string>"
}
```


### POST request body

```
{
    "announcement_type": "<string>",     <-- required - "carousel", "facility", "maintenance" or "news" only
    "background_image_url": "<string>",  <-- optional - image url
    "button": "<string>",                <-- optional - button text
    "content": "<string>",               <-- required - announcement body
    "display_date": "<string>",          <-- optional - Date/Time shown as part of announcement
    "end_date": "<string>",              <-- optional - Date/Time
    "is_active": <boolean>,              <-- required - true/false
    "link": "<string>",                  <-- optional - URL
    "sequence": <integer>,               <-- required for "carousel", otherwise optional
    "start_date": "<string>",            <-- required - Date/Time
    "title": "<string>"                  <-- required - announcement title
}
```

### PATCH request body

```
{
    "announcement_type": "<string>",     <-- optional - "carousel", "facility", "maintenance" or "news" only
    "background_image_url": "<string>",  <-- optional
    "button": "<string>",                <-- optional
    "content": "<string>",               <-- optional
    "display_date": "<string>",          <-- optional
    "end_date": "<string>",              <-- optional
    "is_active": <boolean>,              <-- optional - true/false
    "link": "<string>",                  <-- optional
    "sequence": <integer>,               <-- optional
    "start_date": "<string>",            <-- optional
    "title": "<string>"                  <-- optional
}
```

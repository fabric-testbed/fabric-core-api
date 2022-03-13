# Preferences

Preferences are determined after object creation by the owner(s) of the object

### People

a `People` object is **public** by default, but portions of it can be set to **private**.

```json
"preferences": {
    "show_email": <bool>,
    "show_eppn": <bool>,
    "show_profile": <bool>,
    "show_publications": <bool>,
    "show_roles": <bool>,
    "show_sshkeys": <bool>
}
```

Available `preferences`:

- `show_email`: show/hide `email` in all interfaces (default: True)
- `show_eppn`: show/hide `eppn` in all interfaces (default: True)
- `show_profile`: show/hide `profile` in all interfaces (default: True)
- `show_publications`: show/hide `publications` in all interfaces (default: True)
- `show_roles`: show/hide `roles` in all interfaces (default: True)
- `show_sshkeys`: show/hide `sshkeys` in all interfaces (default: True)


### Profile - People

a `Profile - People` object is set to the value of `people.preferences.show_profile` by default, but its contents can be set to **public** or **private** as desired by the owner.

```json
"preferences": {
    "show_bio": <bool>,
    "show_cv": <bool>,
    "show_job": <bool>,
    "show_other_identities": <bool>,
    "show_professional": <bool>,
    "show_pronouns": <bool>,
    "show_social": <bool>,
    "show_website": <bool>
}
```

Available `preferences`:

- `show_bio`: show/hide `bio` in all interfaces (default: True)
- `show_cv`: show/hide `cv` in all interfaces (default: True)
- `show_job`: show/hide `job` in all interfaces (default: True)
- `show_other_identities`: show/hide `other_identities` in all interfaces (default: True)
- `show_professional`: show/hide `professional` in all interfaces (default: True)
- `show_pronouns`: show/hide `pronouns` in all interfaces (default: True)
- `show_social`: show/hide `social` in all interfaces (default: True)
- `show_website`: show/hide `website` in all interfaces (default: True)

### Projects

a `Project` object is **public** by default, but all or portions of it can be set to **private**.

```json
"preferences": {
    "is_public": <bool>,
    "show_profile": <bool>,
    "show_publications": <bool>
}
```

Available `preferences`:

- `is_public`: show/hide Project in all interfaces (default: True)
- `show_profile`: show/hide `profile` in all interfaces (default: True)
- `show_publications`: show/hide `publications` in all interfaces (default: True)


### Profile - Projects

```json
"preferences": {
    "show_award_information": <bool>,
    "show_goals": <bool>,
    "show_keywords": <bool>,
    "show_notebooks": <bool>,
    "show_project_status": <bool>,
    "show_purpose": <bool>,
    "show_references": <bool>
}
```

Available `preferences`:

- `show_award_information `: show/hide `award_information` in all interfaces (default: True)
- `show_goals `: show/hide `goals ` in all interfaces (default: True)
- `show_keywords `: show/hide `keywords ` in all interfaces (default: True)
- `show_notebooks `: show/hide `notebooks ` in all interfaces (default: True)
- `show_project_status `: show/hide `project_status ` in all interfaces (default: True)
- `show_purpose `: show/hide `purpose ` in all interfaces (default: True)
- `show_references `: show/hide `references ` in all interfaces (default: True)

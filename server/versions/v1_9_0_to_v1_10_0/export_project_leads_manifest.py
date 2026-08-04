"""Export the comanage_project_leads_to_purge.json manifest for the current
deployment by querying COmanage directly."""

import json
import os
import sys
from datetime import datetime, timezone

from comanage_api import ComanageApi


def main():
    required = [
        "COMANAGE_API_URL",
        "COMANAGE_API_USER",
        "COMANAGE_API_PASS",
        "COMANAGE_API_CO_ID",
        "COMANAGE_API_CO_NAME",
        "COU_ID_PROJECT_LEADS",
        "COU_NAME_PROJECT_LEADS",
    ]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        sys.exit("Missing env vars: {}".format(", ".join(missing)))

    api = ComanageApi(
        co_api_url=os.getenv("COMANAGE_API_URL"),
        co_api_user=os.getenv("COMANAGE_API_USER"),
        co_api_pass=os.getenv("COMANAGE_API_PASS"),
        co_api_org_id=os.getenv("COMANAGE_API_CO_ID"),
        co_api_org_name=os.getenv("COMANAGE_API_CO_NAME"),
    )

    cou_id = int(os.getenv("COU_ID_PROJECT_LEADS"))
    cou_name = os.getenv("COU_NAME_PROJECT_LEADS")

    roles = api.coperson_roles_view_per_cou(cou_id=cou_id).get("CoPersonRoles", [])

    memberships = []
    for r in roles:
        co_person_id = r.get("Person", {}).get("Id") or r.get("CoPersonId")
        person = api.copeople_view_one(coperson_id=co_person_id).get("CoPeople", [{}])[
            0
        ]
        names = api.names_view_per_person(
            person_type="copersonid", person_id=co_person_id
        ).get("Names", [{}])[0]
        memberships.append(
            {
                "co_person_role_id": r.get("Id"),
                "co_person_id": co_person_id,
                "people_name": "{} {}".format(
                    names.get("Given", ""), names.get("Family", "")
                ).strip(),
                "status": r.get("Status"),
                "affiliation": r.get("Affiliation"),
            }
        )

    out = {
        "description": "Project-leads role memberships to purge from COmanage registry (v1.9.0 -> v1.10.0)",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "cou": {"co_cou_id": cou_id, "name": cou_name},
        "count": len(memberships),
        "memberships": memberships,
    }

    out_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "swagger_server",
        "backup",
        "data",
        "comanage_project_leads_to_purge.json",
    )
    with open(os.path.abspath(out_path), "w") as f:
        json.dump(out, f, indent=2)
    print("Wrote {} memberships to {}".format(len(memberships), out_path))


if __name__ == "__main__":
    main()

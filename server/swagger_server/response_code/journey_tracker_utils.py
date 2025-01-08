from datetime import datetime

from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.people import FabricPeople, Organizations, FabricRoles
from swagger_server.models.journey_tracker_people_one import JourneyTrackerPeopleOne


def journey_tracker_people_by_since_date(since_date: datetime = None, until_date: datetime = None) -> [
    JourneyTrackerPeopleOne]:
    jt_people = []
    results = FabricPeople.query.filter(
        FabricPeople.updated >= since_date,
        FabricPeople.updated <= until_date,
    ).order_by(FabricPeople.updated.desc()).all()
    for res in results:
        try:
            p = JourneyTrackerPeopleOne()
            p.active = res.active
            org = Organizations.query.filter_by(id=res.org_affiliation).one_or_none()
            p.affiliation = org.organization if org else None
            p.deactivated_date = None
            p.email_address = res.preferred_email
            p.fabric_last_seen = str(res.updated)
            roles = FabricRoles.query.filter_by(people_id=res.id).order_by('name').all()
            p.fabric_roles = [r.name for r in roles]
            p.fabric_uuid = res.uuid
            p.name = res.display_name
            jt_people.append(p)
        except Exception as exc:
            consoleLogger.error('journey_tracker_utils.journey_tracker_people_by_since_date: {0}'.format(exc))
    consoleLogger.info('journey_tracker_utils.journey_tracker_people_by_since_date: {0} records returned'.format(len(jt_people)))
    return jt_people

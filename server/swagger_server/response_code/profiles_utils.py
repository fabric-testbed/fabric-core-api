from uuid import uuid4

from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.profiles import FabricProfilesPeople, EnumExternalPageTypes
from swagger_server.models.profile_people import ProfilePeople, ProfilePeopleOtherIdentities, ProfilePeopleProfessional
from swagger_server.response_code.preferences_utils import create_profile_people_preferences

"""
FabricProfilesPeople model (* denotes required)
- bio - short bio
- created - timestamp created (TimestampMixin)
- cv - Link to a CV or resume. (Later it might be nice if this could be stored on the Portal)
- external_pages - external links for social and professional pages
    - professional - Links to professional pages on resources such as LinkedIn, Twitter, Youtube, Github
    - social - Links to personal pages on resources such as LinkedIn, Twitter, Youtube, Github
- id - primary key (BaseMixin)
- identities - IDs from other identity services such as ORCID, Google Scholar
- job - Role/job/position
- modified - timestamp modified (TimestampMixin)
- * people_id - foreignkey link to people table
- preferences - array of preference booleans
- pronouns - personal pronouns used
- uuid - unique universal identifier
- website - Link to a personal website
"""


def create_profile_people(fab_person: FabricPeople = None) -> None:
    fab_profile = FabricProfilesPeople()
    fab_profile.uuid = uuid4()
    fab_profile.people = fab_person
    db.session.add(fab_profile)
    db.session.commit()
    create_profile_people_preferences(fab_profile=fab_profile)


def get_profile_people(profile_people_id: int = None, as_self: bool = False) -> ProfilePeople:
    fab_profile = FabricProfilesPeople.query.filter_by(id=profile_people_id).one_or_none()
    profile_prefs = {p.key: p.value for p in fab_profile.preferences}
    profile_people = ProfilePeople()
    if as_self:
        profile_people.bio = fab_profile.bio
        profile_people.cv = fab_profile.cv
        profile_people.job = fab_profile.job
        profile_people.other_identities = get_profile_other_identities(profile_people=fab_profile)
        profile_people.professional = get_profile_external_pages(
            profile_people=fab_profile, page_type=EnumExternalPageTypes.professional)
        profile_people.pronouns = fab_profile.pronouns
        profile_people.social = get_profile_external_pages(
            profile_people=fab_profile, page_type=EnumExternalPageTypes.social)
        profile_people.website = fab_profile.website
        profile_people.preferences = profile_prefs
    else:
        profile_people.bio = fab_profile.bio if profile_prefs.get('show_bio') else None
        profile_people.cv = fab_profile.cv if profile_prefs.get('show_cv') else None
        profile_people.job = fab_profile.job if profile_prefs.get('show_job') else None
        profile_people.other_identities = get_profile_other_identities(
            profile_people=fab_profile) if profile_prefs.get('show_other_identities') else None
        profile_people.professional = get_profile_external_pages(
            profile_people=fab_profile,
            page_type=EnumExternalPageTypes.professional) if profile_prefs.get('show_professional') else None
        profile_people.pronouns = fab_profile.pronouns if profile_prefs.get('show_pronouns') else None
        profile_people.social = get_profile_external_pages(
            profile_people=fab_profile,
            page_type=EnumExternalPageTypes.social) if profile_prefs.get('show_social') else None
        profile_people.website = fab_profile.website if profile_prefs.get('show_website') else None

    return profile_people


def get_profile_other_identities(profile_people: FabricProfilesPeople = None) -> [ProfilePeopleOtherIdentities]:
    """
    - identity - identity as string
    - profiles_id - foreignkey link to profiles table
    - type - type of other identity
    """
    data = []
    for oi in profile_people.other_identities:
        ppoi = ProfilePeopleOtherIdentities()
        ppoi.identity = oi.identity
        ppoi.type = oi.type
        data.append(ppoi)

    return data


def get_profile_external_pages(profile_people: FabricProfilesPeople = None,
                               page_type: EnumExternalPageTypes = None) -> [ProfilePeopleProfessional]:
    """
    - page_type - type of page as enum
    - profiles_people_id - foreignkey link to profiles_people table
    - url - url as string
    - url_type - type of url
    """
    data = []
    for ep in profile_people.external_pages:
        ppep = ProfilePeopleProfessional()
        ppep.url = ep.url
        ppep.type = ep.url_type
        if ep.page_type == page_type:
            data.append(ppep)

    return data

import logging
from uuid import uuid4

from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.profiles import FabricProfilesPeople, EnumExternalPageTypes, FabricProfilesProjects, \
    ProfilesKeywords, ProfilesReferences
from swagger_server.database.models.projects import FabricProjects
from swagger_server.models.profile_people import ProfilePeople, ProfilePeopleOtherIdentities, ProfilePeopleProfessional
from swagger_server.models.profile_projects import ProfileProjects, ProfileProjectsReferences
from swagger_server.response_code.preferences_utils import create_profile_people_preferences, \
    create_profile_projects_preferences, delete_profile_projects_preferences
from swagger_server.response_code.response_utils import array_difference

logger = logging.getLogger(__name__)

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


def other_identities_to_array(n): return [{'identity': x.identity, 'type': x.type} for x in n]


def external_pages_to_array(n):
    return [{'url': x.url, 'type': x.type} for x in n]


def external_pages_to_array_professional(n):
    return [{'url': x.url, 'type': x.url_type} for x in n if x.page_type == EnumExternalPageTypes.professional]


def external_pages_to_array_social(n):
    return [{'url': x.url, 'type': x.url_type} for x in n if x.page_type == EnumExternalPageTypes.social]


def references_to_array(n): return [{'description': x.description, 'url': x.url} for x in n]


def create_profile_people(fab_person: FabricPeople) -> None:
    fab_profile = FabricProfilesPeople()
    fab_profile.uuid = uuid4()
    fab_profile.people = fab_person
    db.session.add(fab_profile)
    db.session.commit()
    create_profile_people_preferences(fab_profile=fab_profile)


def get_profile_people(profile_people_id: int, as_self: bool = False) -> ProfilePeople:
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


def get_profile_other_identities(profile_people: FabricProfilesPeople) -> [ProfilePeopleOtherIdentities]:
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


def get_profile_external_pages(profile_people: FabricProfilesPeople,
                               page_type: EnumExternalPageTypes) -> [ProfilePeopleProfessional]:
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


def create_profile_projects(fab_project: FabricProjects) -> None:
    fab_profile = FabricProfilesProjects()
    fab_profile.uuid = uuid4()
    fab_profile.projects = fab_project
    db.session.add(fab_profile)
    db.session.commit()
    create_profile_projects_preferences(fab_profile=fab_profile)


def delete_profile_projects(fab_project: FabricProjects) -> None:
    fab_profile = fab_project.profile
    # delete keywords
    update_profiles_projects_keywords(fab_profile=fab_profile, keywords=[])
    # remove notebooks
    # TODO: define notebooks
    # delete preferences
    delete_profile_projects_preferences(fab_profile=fab_profile)
    # delete references
    update_profiles_projects_references(fab_profile=fab_profile, references=[])
    db.session.delete(fab_profile)
    db.session.commit()


def get_profile_projects(profile_projects_id: int, as_owner: bool = False) -> ProfileProjects:
    fab_profile = FabricProfilesProjects.query.filter_by(id=profile_projects_id).one_or_none()
    profile_prefs = {p.key: p.value for p in fab_profile.preferences}
    profile_projects = ProfileProjects()
    if as_owner:
        profile_projects.award_information = fab_profile.award_information
        profile_projects.goals = fab_profile.goals
        profile_projects.keywords = [k.keyword for k in fab_profile.keywords]
        # TODO: define notebooks
        profile_projects.notebooks = []
        profile_projects.preferences = profile_prefs
        profile_projects.project_status = fab_profile.project_status
        profile_projects.purpose = fab_profile.purpose
        profile_projects.references = [{'description': r.description, 'url': r.url} for r in fab_profile.references]
    else:
        profile_projects.award_information = fab_profile.award_information if profile_prefs.get(
            'show_award_information') else None
        profile_projects.goals = fab_profile.goals if profile_prefs.get('show_goals') else None
        profile_projects.keywords = [k.keyword for k in fab_profile.keywords] if profile_prefs.get(
            'show_keywords') else None
        profile_projects.notebooks = [] if profile_prefs.get('show_notebooks') else None
        profile_projects.project_status = fab_profile.project_status if profile_prefs.get(
            'show_project_status') else None
        profile_projects.purpose = fab_profile.purpose if profile_prefs.get('show_purpose') else None
        profile_projects.references = [{'description': r.description, 'url': r.url} for r in
                                       fab_profile.references] if profile_prefs.get('show_references') else None

    return profile_projects


def update_profiles_projects_keywords(fab_profile: FabricProfilesProjects, keywords: [str] = None) -> None:
    kw_orig = [k.keyword for k in fab_profile.keywords]
    kw_new = keywords
    kw_add = array_difference(kw_new, kw_orig)
    kw_remove = array_difference(kw_orig, kw_new)
    # add profiles projects keywords
    for kw in kw_add:
        fab_kw = ProfilesKeywords.query.filter(
            ProfilesKeywords.keyword == kw, ProfilesKeywords.profiles_projects_id == fab_profile.id).one_or_none()
        if not fab_kw:
            fab_kw = ProfilesKeywords()
            fab_kw.profiles_projects_id = fab_profile.id
            fab_kw.keyword = kw
            fab_profile.keywords.append(fab_kw)
            db.session.commit()
    # remove profiles projects keywords
    for kw in kw_remove:
        fab_kw = ProfilesKeywords.query.filter(
            ProfilesKeywords.keyword == kw, ProfilesKeywords.profiles_projects_id == fab_profile.id).one_or_none()
        if fab_kw:
            fab_profile.keywords.remove(fab_kw)
            db.session.delete(fab_kw)
            db.session.commit()


def update_profiles_projects_references(
        fab_profile: FabricProfilesProjects, references: [ProfileProjectsReferences] = None) -> None:
    ref_orig = references_to_array(fab_profile.references)
    ref_new = references_to_array(references)
    ref_add = array_difference(ref_new, ref_orig)
    ref_remove = array_difference(ref_orig, ref_new)
    # add new references
    for ref in ref_add:
        fab_ref = ProfilesReferences.query.filter(
            ProfilesReferences.description == ref.get('description'),
            ProfilesReferences.profiles_projects_id == fab_profile.id,
            ProfilesReferences.url == ref.get('url')
        ).one_or_none()
        if not fab_ref:
            fab_ref = ProfilesReferences()
            fab_ref.description = ref.get('description')
            fab_ref.profiles_projects_id = fab_profile.id
            fab_ref.url = ref.get('url')
            db.session.add(fab_ref)
            db.session.commit()
            logger.info("CREATE: FabricProfilesProjects: uuid={0}, references: '{1}' = '{2}'".format(
                fab_profile.uuid, fab_ref.description, fab_ref.url))
    # # remove old references
    for ref in ref_remove:
        fab_ref = ProfilesReferences.query.filter(
            ProfilesReferences.description == ref.get('description'),
            ProfilesReferences.profiles_projects_id == fab_profile.id,
            ProfilesReferences.url == ref.get('url')
        ).one_or_none()
        if fab_ref:
            logger.info("DELETE: FabricProfilesProjects: uuid={0}, references: '{1}' = '{2}'".format(
                fab_profile.uuid, fab_ref.description, fab_ref.url))
            db.session.delete(fab_ref)
            db.session.commit()

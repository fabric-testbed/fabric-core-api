import logging
import os

from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople, Organizations
from swagger_server.database.models.preferences import FabricPreferences, EnumPreferenceTypes
from swagger_server.database.models.profiles import FabricProfilesPeople, ProfilesOtherIdentities, ProfilesExternalPages
from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.people import People, Person, Status200OkPaginatedLinks  # noqa: E501
from swagger_server.models.people_details import PeopleDetails, PeopleOne  # noqa: E501
from swagger_server.models.people_patch import PeoplePatch
from swagger_server.models.profile_people import ProfilePeople
from swagger_server.models.status200_ok_no_content import Status200OkNoContent, Status200OkNoContentData  # noqa: E501
from swagger_server.response_code import PEOPLE_PREFERENCES, PEOPLE_PROFILE_OTHER_IDENTITY_TYPES, \
    PEOPLE_PROFILE_PREFERENCES, PEOPLE_PROFILE_PROFESSIONAL_TYPES, PEOPLE_PROFILE_SOCIAL_TYPES
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_403, cors_404, cors_500
from swagger_server.response_code.decorators import login_required
from swagger_server.response_code.people_utils import get_person_by_login_claims, get_people_roles
from swagger_server.response_code.preferences_utils import get_people_preferences
from swagger_server.response_code.profiles_utils import get_profile_people
from swagger_server.response_code.response_utils import is_valid_url

logger = logging.getLogger(__name__)

# Constants
_SERVER_URL = os.getenv('CORE_API_SERVER_URL', '')


@login_required
def people_get(search: str = None, offset: int = None, limit: int = None) -> People:  # noqa: E501
    """Search for FABRIC People

    Search for FABRIC People by name or email # noqa: E501

    :param search: search term applied
    :type search: str
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int

    :rtype: People
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # set page to retrieve
        _page = int((offset + limit) / limit)
        # get paginated search results
        if search:
            data_page = FabricPeople.query.filter(
                (FabricPeople.active.is_(True)) &
                (FabricPeople.display_name.ilike("%" + search + "%")) |
                (FabricPeople.preferred_email.ilike("%" + search + "%"))
            ).order_by(FabricPeople.display_name).paginate(page=_page, per_page=limit, error_out=False)
        else:
            data_page = FabricPeople.query.filter(
                FabricPeople.active.is_(True)
            ).order_by(FabricPeople.display_name).paginate(
                page=_page, per_page=limit, error_out=False)
        # set people response
        response = People()
        response.data = []
        for item in data_page.items:
            # get preferences (show_email)
            prefs = get_people_preferences(fab_person=FabricPeople.query.filter_by(uuid=item.uuid).one_or_none())
            # set person attributes
            person = Person()
            person.email = item.preferred_email if prefs.__getattribute__('show_email') else None
            person.name = item.display_name
            person.uuid = item.uuid
            # add person to people data
            response.data.append(person)
        # set links
        response.links = Status200OkPaginatedLinks()
        _URL_OFFSET_LIMIT = '{0}offset={1}&limit={2}'
        base = '{0}/people?'.format(_SERVER_URL) if not search else '{0}/people?search={1}&'.format(_SERVER_URL, search)
        response.links.first = _URL_OFFSET_LIMIT.format(base, 0, limit) if data_page.pages > 0 else None
        response.links.last = _URL_OFFSET_LIMIT.format(base, int((data_page.pages - 1) * limit),
                                                       limit) if data_page.pages > 0 else None
        response.links.next = _URL_OFFSET_LIMIT.format(base, int(offset + limit), limit) if data_page.has_next else None
        response.links.prev = _URL_OFFSET_LIMIT.format(base, int(offset - limit), limit) if data_page.has_prev else None
        # set offset, limit and size
        response.limit = limit
        response.offset = offset
        response.total = data_page.total
        response.size = len(response.data)

        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with people_get(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)


def people_preferences_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Preference options

    List of People Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PREFERENCES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PREFERENCES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PREFERENCES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_preferences_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Preferences.Get()')


def people_profile_otheridentity_types_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Profile Other Identity Type options

    List of People Profile Other Identity Type options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PROFILE_OTHER_IDENTITY_TYPES.search(search) if
                    search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PROFILE_OTHER_IDENTITY_TYPES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PROFILE_OTHER_IDENTITY_TYPES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_profile_otheridentity_types_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Profile.OtherIdentity.Types.Get()')


def people_profile_preferences_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Profile Preference options

    List of People Profile Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PROFILE_PREFERENCES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PROFILE_PREFERENCES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PROFILE_PREFERENCES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_profile_preferences_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Profile.Preferences.Get()')


def people_profile_professionalpage_types_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Profile Professional Page Type options

    List of People Profile Professional Page Type options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PROFILE_PROFESSIONAL_TYPES.search(search) if
                    search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PROFILE_PROFESSIONAL_TYPES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PROFILE_PROFESSIONAL_TYPES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_profile_professionalpage_types_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Profile.Professional.Types.Get()')


def people_profile_socialpage_types_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Profile Social Page Type options

    List of People Profile Social Page Type options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PROFILE_SOCIAL_TYPES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PROFILE_SOCIAL_TYPES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PROFILE_SOCIAL_TYPES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_profile_socialpage_types_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Profile.Social.Types.Get()')


@login_required
def people_uuid_get(uuid, as_self=None) -> PeopleDetails:  # noqa: E501
    """Person details by UUID

    Person details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param as_self: GET object as Self
    :type as_self: bool

    :rtype: PeopleDetails
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # get person by uuid
        fab_person = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
        if not fab_person:
            return cors_404(details="No match for Person with uuid = '{0}'".format(uuid))
        # set PeopleOne object
        people_one = PeopleOne()
        # set required attributes for any uuid
        people_one.affiliation = Organizations.query.filter_by(id=fab_person.org_affiliation).one_or_none().organization
        people_one.name = fab_person.display_name
        people_one.registered_on = str(fab_person.registered_on)
        people_one.uuid = fab_person.uuid
        # set remaining attributes for uuid == self
        if as_self and api_user.uuid == uuid:
            people_one.bastion_login = fab_person.bastion_login
            people_one.cilogon_email = fab_person.oidc_claim_email
            people_one.cilogon_family_name = fab_person.oidc_claim_family_name
            people_one.cilogon_given_name = fab_person.oidc_claim_given_name
            people_one.cilogon_id = fab_person.oidc_claim_sub
            people_one.cilogon_name = fab_person.oidc_claim_name
            people_one.email = fab_person.preferred_email
            people_one.email_addresses = list(set([e.email for e in fab_person.email_addresses]))
            people_one.eppn = fab_person.eppn
            people_one.fabric_id = fab_person.fabric_id
            people_one.preferences = {p.key: p.value for p in fab_person.preferences}
            people_one.profile = get_profile_people(profile_people_id=fab_person.profile.id, as_self=True)
            people_one.publications = []
            people_one.roles = get_people_roles(people_roles=fab_person.roles)
            people_one.sshkeys = []
        # set remaining attributes for uuid != self based on user preference
        else:
            people_prefs = {p.key: p.value for p in fab_person.preferences}
            people_one.email = fab_person.preferred_email if people_prefs.get('show_email') else None
            people_one.eppn = fab_person.eppn if people_prefs.get('show_eppn') else None
            people_one.profile = get_profile_people(profile_people_id=fab_person.profile.id,
                                                    as_self=False) if people_prefs.get('show_profile') else None
            people_one.publications = [] if people_prefs.get('show_publications') else None
            people_one.roles = get_people_roles(people_roles=fab_person.roles) if people_prefs.get(
                'show_roles') else None
            people_one.sshkeys = [] if people_prefs.get('show_sshkeys') else None

        # set people_details response
        response = PeopleDetails()
        response.data = [people_one]
        response.size = len(response.data)
        response.status = 200
        response.type = 'people.details'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with people_uuid_get(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)


@login_required
def people_uuid_patch(uuid, body: PeoplePatch = None) -> Status200OkNoContent:  # noqa: E501
    """Update Person details as Self

    Update Person details as Self # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Person details as self
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # get person by uuid
        fab_person = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
        if not fab_person:
            return cors_404(details="No match for Person with uuid = '{0}'".format(uuid))
        # check that api_user.uuid == fab_person.uuid
        if not api_user.uuid == fab_person.uuid:
            return cors_403(
                details="User: '{0}' is not permitted to update the requested User".format(api_user.display_name))
        # check for name
        try:
            if len(body.name) == 0:
                fab_person.display_name = fab_person.oidc_claim_name
            else:
                fab_person.display_name = body.name
            db.session.commit()
            logger.info('UPDATE: FabricPeople: uuid={0}, name={1}'.format(fab_person.uuid, fab_person.display_name))
        except Exception as exc:
            logger.info("NOP: people_uuid_patch(): 'name' - {0}".format(exc))
        # check for email
        try:
            if len(body.email) == 0:
                fab_person.preferred_email = fab_person.oidc_claim_email
            elif body.email in [e.email for e in fab_person.email_addresses]:
                fab_person.preferred_email = body.email
            else:
                return cors_400(
                    details="Email: '{0}' is not found in User's existing Email Addresses".format(body.email))
            db.session.commit()
            logger.info('UPDATE: FabricPeople: uuid={0}, email={1}'.format(fab_person.uuid, fab_person.preferred_email))
        except Exception as exc:
            logger.info("NOP: people_uuid_patch(): 'email' - {0}".format(exc))
        # check for preferences
        try:
            for key in body.preferences.keys():
                fab_pref = FabricPreferences.query.filter(
                    FabricPreferences.key == key,
                    FabricPreferences.people_id == fab_person.id,
                    FabricPreferences.type == EnumPreferenceTypes.people
                ).one_or_none()
                if not fab_pref:
                    if key in PEOPLE_PREFERENCES.options:
                        fab_pref = FabricPreferences()
                        fab_pref.key = key
                        fab_pref.value = body.get('preferences').get(key)
                        fab_pref.type = EnumPreferenceTypes.people
                        fab_pref.people_id = fab_person.id
                        db.session.add(fab_pref)
                        db.session.commit()
                        fab_person.preferences.append(fab_pref)
                        logger.info("CREATE: FabricPeople: uuid={0}, 'preferences.{1}' = {2}".format(
                            fab_person.uuid, fab_pref.key, fab_pref.value))
                    else:
                        details = "People Preferences: '{0}' is not a valid preference type".format(key)
                        logger.error(details)
                        return cors_400(details=details)
                else:
                    fab_pref.value = body.get('preferences').get(key)
                    db.session.commit()
                    logger.info("UPDATE: FabricPeople: uuid={0}, 'preferences.{1}' = {2}".format(
                        fab_person.uuid, fab_pref.key, fab_pref.value))
        except Exception as exc:
            logger.info("NOP: people_uuid_patch(): 'preferences' - {0}".format(exc))
        # create response
        patch_info = Status200OkNoContentData()
        patch_info.details = "User: '{0}' has been successfully updated".format(fab_person.display_name)
        response = Status200OkNoContent()
        response.data = [patch_info]
        response.size = len(response.data)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with people_uuid_patch(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)


@login_required
def people_uuid_profile_patch(uuid: str, body: ProfilePeople = None):  # noqa: E501
    """Update Person Profile details as Self

    Update Person Profile details as Self # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Person details as self
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # get person by uuid
        fab_person = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
        if not fab_person:
            return cors_404(details="No match for Person with uuid = '{0}'".format(uuid))
        # check that api_user.uuid == fab_person.uuid
        if not api_user.uuid == fab_person.uuid:
            return cors_403(
                details="User: '{0}' is not permitted to update the requested User".format(api_user.display_name))
        fab_profile = FabricProfilesPeople.query.filter_by(id=fab_person.profile.id).one_or_none()
        # check for bio
        try:
            if len(body.bio) == 0:
                fab_profile.bio = None
            else:
                fab_profile.bio = body.bio
            db.session.commit()
            logger.info('UPDATE: FabricProfilesPeople: uuid={0}, bio={1}'.format(fab_profile.uuid, fab_profile.bio))
        except Exception as exc:
            logger.info("NOP: people_uuid_profile_patch(): 'bio' - {0}".format(exc))
        # check for cv
        try:
            if len(body.cv) == 0:
                fab_profile.cv = None
            else:
                if is_valid_url(body.cv):
                    fab_profile.cv = body.cv
                else:
                    details = "CV: '{0}' is not a valid URL".format(body.cv)
                    logger.error(details)
                    return cors_400(details=details)
            db.session.commit()
            logger.info('UPDATE: FabricProfilesPeople: uuid={0}, cv={1}'.format(fab_profile.uuid, fab_profile.cv))
        except Exception as exc:
            logger.info("NOP: people_uuid_profile_patch(): 'cv' - {0}".format(exc))
        # check for job
        try:
            if len(body.job) == 0:
                fab_profile.job = None
            else:
                fab_profile.job = body.job
            db.session.commit()
            logger.info('UPDATE: FabricProfilesPeople: uuid={0}, job={1}'.format(fab_profile.uuid, fab_profile.job))
        except Exception as exc:
            logger.info("NOP: people_uuid_profile_patch(): 'job' - {0}".format(exc))
        # check for other_identities
        try:
            for oi in body.other_identities:
                oi_identity = oi.identity
                oi_type = oi.type
                if oi_type not in PEOPLE_PROFILE_OTHER_IDENTITY_TYPES.options:
                    details = "OtherIdentities: '{0}' is not a valid identity type".format(oi_type)
                    logger.error(details)
                    return cors_400(details=details)
                fab_oi = ProfilesOtherIdentities.query.filter(
                    ProfilesOtherIdentities.identity == oi_identity,
                    ProfilesOtherIdentities.profiles_id == fab_profile.id,
                    ProfilesOtherIdentities.type == oi_type
                ).one_or_none()
                if not fab_oi:
                    fab_oi = ProfilesOtherIdentities()
                    fab_oi.identity = oi_identity
                    fab_oi.profiles_id = fab_profile.id
                    fab_oi.type = oi_type
                    db.session.add(fab_oi)
                    db.session.commit()
                    logger.info("CREATE: FabricProfilesPeople: uuid={0}, 'other_identities.{1}' = {2}".format(
                        fab_person.uuid, oi_type, oi_identity))
        except Exception as exc:
            logger.info("NOP: people_uuid_profile_patch(): 'other_identities' - {0}".format(exc))
        # check for preferences
        try:
            for key in body.preferences.keys():
                fab_pref = FabricPreferences.query.filter(
                    FabricPreferences.key == key,
                    FabricPreferences.profiles_people_id == fab_profile.id,
                    FabricPreferences.type == EnumPreferenceTypes.profiles_people
                ).one_or_none()
                if not fab_pref:
                    if key in PEOPLE_PROFILE_PREFERENCES.options:
                        fab_pref = FabricPreferences()
                        fab_pref.key = key
                        fab_pref.value = body.preferences.get(key)
                        fab_pref.type = EnumPreferenceTypes.profiles_people
                        fab_pref.profiles_people_id = fab_profile.id
                        db.session.add(fab_pref)
                        db.session.commit()
                        fab_profile.preferences.append(fab_pref)
                        logger.info("CREATE: FabricProfilesPeople: uuid={0}, 'preferences.{1}' = {2}".format(
                            fab_person.uuid, fab_pref.key, fab_pref.value))
                    else:
                        details = "People Preferences: '{0}' is not a valid preference type".format(key)
                        logger.error(details)
                        return cors_400(details=details)
                else:
                    fab_pref.value = body.preferences.get(key)
                    db.session.commit()
                    logger.info("UPDATE: FabricProfilesPeople: uuid={0}, 'preferences.{1}' = {2}".format(
                        fab_person.uuid, fab_pref.key, fab_pref.value))
        except Exception as exc:
            logger.info("NOP: people_uuid_profile_patch(): 'preferences' - {0}".format(exc))
        # check for professional pages
        # check for pronouns
        try:
            if len(body.pronouns) == 0:
                fab_profile.pronouns = None
            else:
                fab_profile.pronouns = body.pronouns
            db.session.commit()
            logger.info(
                'UPDATE: FabricProfilesPeople: uuid={0}, bio={1}'.format(fab_profile.uuid, fab_profile.pronouns))
        except Exception as exc:
            logger.info("NOP: people_uuid_profile_patch(): 'pronouns' - {0}".format(exc))
        # check for social
        # check for website
        try:
            if len(body.website) == 0:
                fab_profile.website = None
            else:
                if is_valid_url(body.website):
                    fab_profile.website = body.website
                else:
                    details = "Website: '{0}' is not a valid URL".format(body.website)
                    logger.error(details)
                    return cors_400(details=details)
            db.session.commit()
            logger.info('UPDATE: FabricProfilesPeople: uuid={0}, website={1}'.format(fab_profile.uuid, fab_profile.website))
        except Exception as exc:
            logger.info("NOP: people_uuid_profile_patch(): 'website' - {0}".format(exc))
        # create response
        patch_info = Status200OkNoContentData()
        patch_info.details = "Profile for User: '{0}' has been successfully updated".format(fab_person.display_name)
        response = Status200OkNoContent()
        response.data = [patch_info]
        response.size = len(response.data)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with people_uuid_profile_patch(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)

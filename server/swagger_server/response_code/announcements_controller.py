import os

from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.announcements import EnumAnnouncementTypes, FabricAnnouncements
from swagger_server.models.announcements import AnnouncementOne, Announcements, Status200OkPaginatedLinks  # noqa: E501
from swagger_server.models.announcements_details import AnnouncementsDetails
from swagger_server.models.announcements_patch import AnnouncementsPatch
from swagger_server.models.announcements_post import AnnouncementsPost
from swagger_server.models.status200_ok_no_content import Status200OkNoContent, \
    Status200OkNoContentResults  # noqa: E501
from swagger_server.response_code.announcements_utils import create_fabric_announcement_from_api
from swagger_server.response_code.core_api_utils import normalize_date_to_utc
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_403, cors_404, cors_500
from swagger_server.response_code.decorators import login_required
from swagger_server.response_code.people_utils import get_person_by_login_claims

# Constants
_SERVER_URL = os.getenv('CORE_API_SERVER_URL', '')


# @login_required
def announcements_get(
        announcement_type: str = None, is_active: str = None, search: str = None, offset: int = None, limit: int = None
) -> Announcements:  # noqa: E501
    """Search for FABRIC Announcements

    Search for FABRIC Announcements # noqa: E501

    :param announcement_type: announcement type
    :type announcement_type: str
    :param is_active: is active
    :type is_active: bool
    :param search: search term applied
    :type search: str
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int

    :rtype: Announcements
    """
    try:
        # # get api_user
        # api_user = get_person_by_login_claims()
        # # check api_user active flag and verify portal-admin role
        # if not api_user.active or not api_user.is_portal_admin():
        #     return cors_403(
        #         details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
        #             api_user.display_name, os.getenv('COU_NAME_PORTAL_ADMINS')))
        # set page to retrieve
        _page = int((offset + limit) / limit)
        # get paginated search results
        if announcement_type and type(is_active) == bool and search:
            results_page = FabricAnnouncements.query.filter(
                (FabricAnnouncements.announcement_type == announcement_type) &
                (FabricAnnouncements.is_active.is_(is_active)) &
                (FabricAnnouncements.title.ilike("%" + search + "%"))
            ).order_by(FabricAnnouncements.start_date.desc()).paginate(page=_page, per_page=limit, error_out=False)
        elif announcement_type and type(is_active) == bool:
            results_page = FabricAnnouncements.query.filter(
                (FabricAnnouncements.announcement_type == announcement_type) &
                (FabricAnnouncements.is_active.is_(is_active))
            ).order_by(FabricAnnouncements.start_date.desc()).paginate(page=_page, per_page=limit, error_out=False)
        elif announcement_type and search:
            results_page = FabricAnnouncements.query.filter(
                (FabricAnnouncements.announcement_type == announcement_type) &
                (FabricAnnouncements.title.ilike("%" + search + "%"))
            ).order_by(FabricAnnouncements.start_date.desc()).paginate(page=_page, per_page=limit, error_out=False)
        elif type(is_active) == bool and search:
            results_page = FabricAnnouncements.query.filter(
                (FabricAnnouncements.is_active.is_(is_active)) &
                (FabricAnnouncements.title.ilike("%" + search + "%"))
            ).order_by(FabricAnnouncements.start_date.desc()).paginate(page=_page, per_page=limit, error_out=False)
        elif announcement_type:
            results_page = FabricAnnouncements.query.filter(
                (FabricAnnouncements.announcement_type == announcement_type)
            ).order_by(FabricAnnouncements.start_date.desc()).paginate(page=_page, per_page=limit, error_out=False)
        elif type(is_active) == bool:
            results_page = FabricAnnouncements.query.filter(
                (FabricAnnouncements.is_active.is_(is_active))
            ).order_by(FabricAnnouncements.start_date.desc()).paginate(page=_page, per_page=limit, error_out=False)
        elif search:
            results_page = FabricAnnouncements.query.filter(
                (FabricAnnouncements.title.ilike("%" + search + "%"))
            ).order_by(FabricAnnouncements.start_date.desc()).paginate(page=_page, per_page=limit, error_out=False)
        else:
            results_page = FabricAnnouncements.query.filter(

            ).order_by(FabricAnnouncements.start_date.desc()).paginate(page=_page, per_page=limit, error_out=False)
        # set announcements response
        response = Announcements()
        response.results = []
        for item in results_page.items:
            announcement = AnnouncementOne()
            announcement.announcement_type = item.announcement_type.name
            announcement.button = item.button if item.button else None
            announcement.content = item.content
            announcement.display_date = str(item.display_date) if item.display_date else None
            announcement.end_date = str(item.end_date) if item.end_date else None
            announcement.is_active = item.is_active
            announcement.link = item.link if item.link else None
            announcement.start_date = str(item.start_date)
            announcement.title = item.title
            announcement.uuid = str(item.uuid)
            # add announcement to announcements results
            response.results.append(announcement)
        # # set links
        response.links = Status200OkPaginatedLinks()
        _URL_OFFSET_LIMIT = '{0}offset={1}&limit={2}'
        if announcement_type and type(is_active) == bool and search:
            base = '{0}/announcements?announcement_type={1}&is_active={2}&search={3}&'.format(_SERVER_URL,
                                                                                              announcement_type,
                                                                                              is_active, search)
        elif announcement_type and type(is_active) == bool:
            base = '{0}/announcements?announcement_type={1}&is_active={2}&'.format(_SERVER_URL, announcement_type,
                                                                                   is_active)
        elif announcement_type and search:
            base = '{0}/announcements?announcement_type={1}&search={2}&'.format(_SERVER_URL, announcement_type, search)
        elif type(is_active) == bool and search:
            base = '{0}/announcements?is_active={1}&search={2}&'.format(_SERVER_URL, is_active, search)
        elif announcement_type:
            base = '{0}/announcements?announcement_type={1}&'.format(_SERVER_URL, announcement_type)
        elif type(is_active) == bool:
            base = '{0}/announcements?is_active={1}&'.format(_SERVER_URL, is_active)
        elif search:
            base = '{0}/announcements?search={1}&'.format(_SERVER_URL, search)
        else:
            base = '{0}/announcements?'.format(_SERVER_URL)
        response.links.first = _URL_OFFSET_LIMIT.format(base, 0, limit) if results_page.pages > 0 else None
        response.links.last = _URL_OFFSET_LIMIT.format(base, int((results_page.pages - 1) * limit),
                                                       limit) if results_page.pages > 0 else None
        response.links.next = _URL_OFFSET_LIMIT.format(base, int(offset + limit),
                                                       limit) if results_page.has_next else None
        response.links.prev = _URL_OFFSET_LIMIT.format(base, int(offset - limit),
                                                       limit) if results_page.has_prev else None
        # set offset, limit and size
        response.limit = limit
        response.offset = offset
        response.total = results_page.total
        response.size = len(response.results)
        response.type = 'announcements'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with announcements_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def announcements_post(body: AnnouncementsPost = None) -> AnnouncementsDetails:  # noqa: E501
    """Create a new FABRIC Announcement

    Create a new FABRIC Announcement # noqa: E501

    :param body: Create an announcement
    :type body: dict | bytes

    :rtype: AnnouncementsDetails
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify portal-admin role
        if not api_user.active or not api_user.is_portal_admin():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_PORTAL_ADMINS')))
        # validate announcement_type
        if body.announcement_type in [EnumAnnouncementTypes.facility.name]:
            # required: content, display_date, is_active, start_date, title
            if any(item is None for item in
                   [body.content, body.display_date, body.is_active, body.start_date, body.title]):
                details = \
                    "Announcements POST: missing required value {content, display_date, is_active, start_date, title}"
                consoleLogger.error(details)
                return cors_400(details=details)
        elif body.announcement_type in [EnumAnnouncementTypes.maintenance.name]:
            # required: content, end_date, is_active, start_date, title
            if any(item is None for item in
                   [body.content, body.end_date, body.is_active, body.start_date, body.title]):
                details = \
                    "Announcements POST: missing required value {content, end_date, is_active, start_date, title}"
                consoleLogger.error(details)
                return cors_400(details=details)
        elif body.announcement_type in [EnumAnnouncementTypes.news.name]:
            # required: content, display_date, is_active, link, title
            if any(item is None for item in
                   [body.content, body.display_date, body.is_active, body.link, body.title]):
                details = \
                    "Announcements POST: missing required value {content, display_date, is_active, link, title}"
                consoleLogger.error(details)
                return cors_400(details=details)
        else:
            details = "Announcements POST: '{0}' is not a valid announcement_type".format(body.announcement_type)
            consoleLogger.error(details)
            return cors_400(details=details)
        # validate display_date, end_date, start_date
        if body.display_date and not normalize_date_to_utc(date_str=body.display_date, return_type='str'):
            details = "Announcements POST: '{0}' is not a valid display_date".format(body.display_date)
            consoleLogger.error(details)
            return cors_400(details=details)
        if body.end_date and not normalize_date_to_utc(date_str=body.end_date, return_type='str'):
            details = "Announcements POST: '{0}' is not a valid end_date".format(body.end_date)
            consoleLogger.error(details)
            return cors_400(details=details)
        if body.start_date and not normalize_date_to_utc(date_str=body.start_date, return_type='str'):
            details = "Announcements POST: '{0}' is not a valid start_date".format(body.start_date)
            consoleLogger.error(details)
            return cors_400(details=details)
        # create Announcement
        fab_announcement = create_fabric_announcement_from_api(body=body, creator=api_user)
        db.session.commit()
        return announcements_uuid_get(uuid=str(fab_announcement.uuid))
    except Exception as exc:
        details = 'Oops! something went wrong with announcements_post(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def announcements_uuid_delete(uuid: str):  # noqa: E501
    """Delete Announcement as Portal Admin

    Delete Announcement as Portal Admin # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify portal-admin role
        if not api_user.active or not api_user.is_portal_admin():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_PORTAL_ADMINS')))
        # get Announcement by uuid
        fab_announcement = FabricAnnouncements.query.filter_by(uuid=uuid).one_or_none()
        if not fab_announcement:
            return cors_404(details="No match for Announcement with uuid = '{0}'".format(uuid))
        # delete Announcement
        db.session.delete(fab_announcement)
        db.session.commit()
        details = "Announcement: '{0}' has been successfully deleted".format(str(fab_announcement.uuid))
        consoleLogger.info(details)
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = details
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with announcements_uuid_delete(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


# @login_required
def announcements_uuid_get(uuid: str) -> AnnouncementsDetails:  # noqa: E501
    """Announcement details by UUID

    Announcement details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: AnnouncementsDetails
    """
    try:
        # get Announcement by uuid
        fab_announcement = FabricAnnouncements.query.filter_by(uuid=uuid).one_or_none()
        if not fab_announcement:
            return cors_404(details="No match for Announcement with uuid = '{0}'".format(uuid))
        # set ProjectsOne object
        announcement_one = AnnouncementOne()
        announcement_one.announcement_type = fab_announcement.announcement_type.name
        announcement_one.button = fab_announcement.button if fab_announcement.button else None
        announcement_one.content = fab_announcement.content
        announcement_one.display_date = str(fab_announcement.display_date) if fab_announcement.display_date else None
        announcement_one.end_date = str(fab_announcement.end_date) if fab_announcement.end_date else None
        announcement_one.is_active = fab_announcement.is_active
        announcement_one.link = fab_announcement.link if fab_announcement.link else None
        announcement_one.start_date = str(fab_announcement.start_date)
        announcement_one.title = fab_announcement.title
        announcement_one.uuid = str(fab_announcement.uuid)
        # set announcement_details response
        response = AnnouncementsDetails()
        response.results = [announcement_one]
        response.size = len(response.results)
        response.status = 200
        response.type = 'announcements.details'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with announcements_uuid_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def announcements_uuid_patch(uuid: str, body: AnnouncementsPatch = None) -> Status200OkNoContent:  # noqa: E501
    """Update Announcement details as Portal Admin

    Update Announcement details as Portal Admin # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update an existing announcement
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify portal-admin role
        if not api_user.active or not api_user.is_portal_admin():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_PORTAL_ADMINS')))
        # get Announcement by uuid
        fab_announcement = FabricAnnouncements.query.filter_by(uuid=uuid).one_or_none()
        if not fab_announcement:
            return cors_404(details="No match for Announcement with uuid = '{0}'".format(uuid))
        # check for announcement_type
        try:
            if len(body.announcement_type) != 0:
                if body.announcement_type not in [x.name for x in EnumAnnouncementTypes]:
                    details = \
                        "Announcements PATCH: '{0}' is not a valid announcement_type".format(body.announcement_type)
                    consoleLogger.error(details)
                    return cors_400(details=details)
                fab_announcement.announcement_type = body.announcement_type
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, announcement_type={1}'.format(
                    fab_announcement.uuid, fab_announcement.button))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'announcement_type' - {0}".format(exc))
        # check for button
        try:
            if len(body.button) != 0:
                fab_announcement.button = body.button
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, button={1}'.format(
                    fab_announcement.uuid, fab_announcement.button))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'button' - {0}".format(exc))
        # check for content
        try:
            if len(body.content) != 0:
                fab_announcement.content = body.content
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, content={1}'.format(
                    fab_announcement.uuid, fab_announcement.content))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'content' - {0}".format(exc))
        # check for display_date
        try:
            if len(body.display_date) != 0:
                if body.display_date and not normalize_date_to_utc(date_str=body.display_date, return_type='str'):
                    details = "Announcements PATCH: '{0}' is not a valid display_date".format(body.display_date)
                    consoleLogger.error(details)
                    return cors_400(details=details)
                fab_announcement.display_date = normalize_date_to_utc(date_str=body.display_date)
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, display_date={1}'.format(
                    fab_announcement.uuid, fab_announcement.display_date))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'display_date' - {0}".format(exc))
        # check for end_date
        try:
            if len(body.end_date) != 0:
                if body.end_date and not normalize_date_to_utc(date_str=body.end_date, return_type='str'):
                    details = "Announcements PATCH: '{0}' is not a valid end_date".format(body.end_date)
                    consoleLogger.error(details)
                    return cors_400(details=details)
                fab_announcement.end_date = normalize_date_to_utc(date_str=body.end_date)
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, end_date={1}'.format(
                    fab_announcement.uuid, fab_announcement.end_date))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'end_date' - {0}".format(exc))
        # check for is_active
        try:
            if body.is_active is not None:
                if body.is_active:
                    fab_announcement.is_active = True
                if not body.is_active:
                    fab_announcement.is_active = False
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, is_active={1}'.format(
                    fab_announcement.uuid, fab_announcement.is_active))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'is_active' - {0}".format(exc))
        # check for link
        try:
            if len(body.link) != 0:
                fab_announcement.link = body.link
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, link={1}'.format(
                    fab_announcement.uuid, fab_announcement.link))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'link' - {0}".format(exc))
        # check for start_date
        try:
            if len(body.start_date) != 0:
                if body.start_date and not normalize_date_to_utc(date_str=body.start_date, return_type='str'):
                    details = "Announcements PATCH: '{0}' is not a valid start_date".format(body.start_date)
                    consoleLogger.error(details)
                    return cors_400(details=details)
                fab_announcement.start_date = normalize_date_to_utc(date_str=body.start_date)
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, start_date={1}'.format(
                    fab_announcement.uuid, fab_announcement.start_date))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'start_date' - {0}".format(exc))
        # check for title
        try:
            if len(body.title) != 0:
                fab_announcement.title = body.title
                db.session.commit()
                consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, title={1}'.format(
                    fab_announcement.uuid, fab_announcement.title))
        except Exception as exc:
            consoleLogger.info("NOP: announcements_uuid_patch(): 'title' - {0}".format(exc))
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Announcement: '{0}' has been successfully updated".format(str(fab_announcement.uuid))
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with announcements_uuid_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)

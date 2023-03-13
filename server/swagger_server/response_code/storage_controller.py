import os

from swagger_server.api_logger import consoleLogger, metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople, FabricRoles
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.storage import FabricStorage
from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent, \
    Status200OkNoContentResults  # noqa: E501
from swagger_server.models.status200_ok_paginated import Status200OkPaginatedLinks
from swagger_server.models.storage import Storage  # noqa: E501
from swagger_server.models.storage_many import StorageMany
from swagger_server.models.storage_one import StorageOne
from swagger_server.models.storage_patch import StoragePatch  # noqa: E501
from swagger_server.models.storage_post import StoragePost  # noqa: E501
from swagger_server.response_code import STORAGE_SITES
from swagger_server.response_code.core_api_utils import normalize_date_to_utc
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_403, cors_404, cors_500
from swagger_server.response_code.decorators import login_or_token_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.storage_utils import create_storage_allocation_from_api, update_storage_site_list

# Constants
_SERVER_URL = os.getenv('CORE_API_SERVER_URL', '')


@login_or_token_required
def storage_get(offset: int = None, limit: int = None, project_uuid: str = None) -> StorageMany:  # noqa: E501
    """Get active Storage allocations

    Get active Storage allocations # noqa: E501

    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int
    :param project_uuid: project uuid
    :type project_uuid: str

    :rtype: StorageMany
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # TODO: token access does not have an api_user --> choose first facility-operator
        if not api_user.id:
            fac_op_ids = [r.people_id for r in
                          FabricRoles.query.filter_by(name=os.getenv('COU_NAME_FACILITY_OPERATORS'))]
            api_user = FabricPeople.query.filter_by(id=fac_op_ids[0]).one_or_none()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # set page to retrieve
        _page = int((offset + limit) / limit)
        # get paginated search results
        if project_uuid:
            fab_project = FabricProjects.query.filter_by(uuid=project_uuid).one_or_none()
            if fab_project:
                results_page = FabricStorage.query.filter(
                    FabricStorage.project_id == fab_project.id
                ).order_by(FabricStorage.volume_name).paginate(page=_page, per_page=limit, error_out=False)
            else:
                return cors_404(details="No match for Project with uuid = '{0}'".format(project_uuid))
        else:
            results_page = FabricStorage.query.filter(
                FabricStorage.active.is_(True)
            ).order_by(FabricStorage.volume_name).paginate(
                page=_page, per_page=limit, error_out=False)
        # set people response
        response = StorageMany()
        response.results = []
        for item in results_page.items:
            prj = FabricProjects.query.filter_by(id=item.project_id).one_or_none()
            # check if user has permission
            if prj and (
                    api_user.is_facility_operator() or api_user in prj.project_creators or api_user in prj.project_members or api_user in prj.project_owners):
                # get Storage attributes
                storage = StorageOne()
                storage.active = item.active
                storage.created_on = str(item.created)
                storage.expires_on = str(item.expires_on)
                storage.project_name = prj.name if prj else None
                storage.project_uuid = str(prj.uuid) if prj else None
                storage.site_list = [s.site for s in item.sites]
                storage.uuid = str(item.uuid)
                storage.volume_name = item.volume_name
                storage.volume_size_gb = item.volume_size_gb
                # add storage to storage many results
                response.results.append(storage)
        # set links
        response.links = Status200OkPaginatedLinks()
        _URL_OFFSET_LIMIT = '{0}offset={1}&limit={2}'
        base = '{0}/storage?'.format(_SERVER_URL) if not project_uuid else '{0}/storage?project_uuid={1}&'.format(
            _SERVER_URL, project_uuid)
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
        response.type = 'storage'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with storage_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_or_token_required
def storage_post(body: StoragePost = None) -> Storage:  # noqa: E501
    """Create a Storage allocation

    Create a Storage allocation # noqa: E501

    :param body: Create a Storage allocation
    :type body: dict | bytes
        {
            "expires_on": "<string>",         <-- required
            "project_uuid": "<string>",       <-- required
            "requested_by_uuid": "<string>",  <-- required
            "site_list": [ "<string>", ... ], <-- optional
            "volume_name": "<string>",        <-- required
            "volume_size_gb": <integer>       <-- optional
        }

    :rtype: Storage
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # TODO: token access does not have an api_user --> choose first facility-operator
        if not api_user.id:
            fac_op_ids = [r.people_id for r in
                          FabricRoles.query.filter_by(name=os.getenv('COU_NAME_FACILITY_OPERATORS'))]
            api_user = FabricPeople.query.filter_by(id=fac_op_ids[0]).one_or_none()
        # check api_user active flag and verify project-leads role
        if not api_user.active or not api_user.is_facility_operator():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_FACILITY_OPERATORS')))
        # check project_uuid
        fab_project = FabricProjects.query.filter_by(uuid=body.project_uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for project_uuid with uuid = '{0}'".format(body.project_uuid))
        # check requested_by_uuid
        fab_person = FabricPeople.query.filter_by(uuid=body.requested_by_uuid).one_or_none()
        if not fab_person:
            return cors_404(details="No match for requested_by_uuid= '{0}'".format(body.requested_by_uuid))
        # check expires_on
        expires_on = normalize_date_to_utc(body.expires_on)
        if not expires_on:
            return cors_400(details="Malformed input for expires_on = '{0}'".format(body.expires_on))
        # create Storage allocation
        try:
            fab_storage = create_storage_allocation_from_api(body=body, storage_creator=api_user)
            fab_storage.active = True
            db.session.commit()
        except Exception as exc:
            details = 'Oops! something went wrong with storage_post(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
        return storage_uuid_get(uuid=str(fab_storage.uuid))
    except Exception as exc:
        details = 'Oops! something went wrong with storage_post(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_or_token_required
def storage_sites_get(search: str = None) -> ApiOptions:  # noqa: E501
    """List of Storage site options

    List of Storage site options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [site for site in STORAGE_SITES.search(search) if search.casefold() in site.casefold()]
        else:
            results = STORAGE_SITES.options
        response = ApiOptions()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = STORAGE_SITES.name
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("storage_sites_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with storage_sites_get()')


@login_or_token_required
def storage_uuid_delete(uuid: str) -> Status200OkNoContent:  # noqa: E501
    """Delete Storage allocation by UUID

    Delete Storage allocation by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # TODO: token access does not have an api_user --> choose first facility-operator
        if not api_user.id:
            fac_op_ids = [r.people_id for r in
                          FabricRoles.query.filter_by(name=os.getenv('COU_NAME_FACILITY_OPERATORS'))]
            api_user = FabricPeople.query.filter_by(id=fac_op_ids[0]).one_or_none()
        # check api_user active flag and verify project-leads role
        if not api_user.active or not api_user.is_facility_operator():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_FACILITY_OPERATORS')))
        # get storage allocation by uuid
        fab_storage = FabricStorage.query.filter_by(uuid=uuid).one_or_none()
        if not fab_storage:
            return cors_404(details="No match for Storage allocation with uuid = '{0}'".format(uuid))
        # flush site_list
        update_storage_site_list(fab_storage=fab_storage, site_list=[])
        # remove from project -- project may have already been removed by user
        try:
            fab_project = FabricProjects.query.filter_by(id=fab_storage.project_id).one_or_none()
            fab_project.project_storage.remove(fab_storage)
            db.session.commit()
        except Exception as exc:
            consoleLogger(exc)
        # delete FabricStorage
        details = "Storage: '{0}' has been successfully deleted".format(fab_storage.uuid)
        consoleLogger.info(details)
        db.session.delete(fab_storage)
        db.session.commit()
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = details
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        # metrics log - Storage was deleted:
        log_msg = 'Storage event stg:{0} delete by usr:{1}'.format(
            str(fab_storage.uuid),
            str(api_user.uuid))
        metricsLogger.info(log_msg)
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with storage_uuid_delete(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_or_token_required
def storage_uuid_get(uuid: str) -> Storage:  # noqa: E501
    """Storage allocation details by UUID

    Storage allocation details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Storage
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # TODO: token access does not have an api_user --> choose first facility-operator
        if not api_user.id:
            fac_op_ids = [r.people_id for r in
                          FabricRoles.query.filter_by(name=os.getenv('COU_NAME_FACILITY_OPERATORS'))]
            api_user = FabricPeople.query.filter_by(id=fac_op_ids[0]).one_or_none()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # get storage by uuid
        fab_storage = FabricStorage.query.filter_by(uuid=uuid).one_or_none()
        if not fab_storage:
            return cors_404(details="No match for Storage allocation with uuid = '{0}'".format(uuid))
        # get project by fab_storage.project_id
        fab_project = FabricProjects.query.filter_by(id=fab_storage.project_id).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with project_id = '{0}'".format(fab_storage.project_id))
        # check if user has permission to view storage allocation
        if not (
                api_user.is_facility_operator() or api_user in fab_project.project_creators or api_user in fab_project.project_members or api_user in fab_project.project_owners):
            return cors_403(
                details="User: '{0}' does not have access to this storage allocation".format(api_user.display_name))
        # set ProjectsOne object
        storage_one = StorageOne()
        # set required attributes for any uuid
        storage_one.active = fab_storage.active
        storage_one.created_on = str(fab_storage.created)
        storage_one.expires_on = str(fab_storage.expires_on)
        storage_one.project_name = fab_project.name
        storage_one.project_uuid = str(fab_project.uuid)
        storage_one.requested_by_uuid = str(
            FabricPeople.query.filter_by(id=fab_storage.requested_by_id).one_or_none().uuid)
        storage_one.site_list = [s.site for s in fab_storage.sites]
        storage_one.uuid = str(fab_storage.uuid)
        storage_one.volume_name = fab_storage.volume_name
        storage_one.volume_size_gb = fab_storage.volume_size_gb
        # set project_details response
        response = Storage()
        response.results = [storage_one]
        response.size = len(response.results)
        response.status = 200
        response.type = 'storage.details'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with storage_uuid_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_or_token_required
def storage_uuid_patch(uuid: str, body: StoragePatch = None) -> Status200OkNoContent:  # noqa: E501
    """Update existing Storage allocation

    Update existing Storage allocation # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update an existing Storage allocation
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # TODO: token access does not have an api_user --> choose first facility-operator
        if not api_user.id:
            fac_op_ids = [r.people_id for r in
                          FabricRoles.query.filter_by(name=os.getenv('COU_NAME_FACILITY_OPERATORS'))]
            api_user = FabricPeople.query.filter_by(id=fac_op_ids[0]).one_or_none()
        # check api_user active flag and verify project-leads role
        if not api_user.active or not api_user.is_facility_operator():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_FACILITY_OPERATORS')))
        # get storage allocation by uuid
        fab_storage = FabricStorage.query.filter_by(uuid=uuid).one_or_none()
        if not fab_storage:
            return cors_404(details="No match for Storage allocation with uuid = '{0}'".format(uuid))
        # check for active
        try:
            if body.active is not None:
                if body.active:
                    fab_storage.active = True
                if not body.active:
                    fab_storage.active = False
                db.session.commit()
                consoleLogger.info('UPDATE: FabricStorage: uuid={0}, active={1}'.format(
                    fab_storage.uuid, fab_storage.active))
                # metrics log - Storage active modified:
                log_msg = 'Storage event stg:{0} modify \'active={1}\' by usr:{2}'.format(
                    str(fab_storage.uuid),
                    str(fab_storage.active),
                    str(api_user.uuid))
                metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: storage_uuid_patch(): 'active' - {0}".format(exc))
        # check for expires_on
        try:
            expires_on = normalize_date_to_utc(date_str=body.expires_on)
            if expires_on:
                fab_storage.expires_on = expires_on
                db.session.commit()
                consoleLogger.info('UPDATE: FabricStorage: uuid={0}, expires_on={1}'.format(
                    fab_storage.uuid, str(fab_storage.expires_on)))
                # metrics log - Storage expires_on modified:
                log_msg = 'Storage event stg:{0} modify \'expires_on={1}\' by usr:{2}'.format(
                    str(fab_storage.uuid),
                    str(fab_storage.expires_on),
                    str(api_user.uuid))
                metricsLogger.info(log_msg)
            else:
                consoleLogger.info("NOP: storage_uuid_patch(): 'expires_on'")
        except Exception as exc:
            consoleLogger.info("NOP: storage_uuid_patch(): 'expires_on' - {0}".format(exc))
        # check for site_list
        try:
            if len(body.site_list) == 0:
                body.site_list = []
            update_storage_site_list(fab_storage=fab_storage, site_list=body.site_list)
            db.session.commit()
            consoleLogger.info('UPDATE: FabricStorage: uuid={0}, site_list={1}'.format(
                fab_storage.uuid, str(fab_storage.expires_on)))
            # metrics log - Storage site_list modified:
            log_msg = 'Storage event stg:{0} modify \'site_list={1}\' by usr:{2}'.format(
                str(fab_storage.uuid),
                str([s.site for s in fab_storage.sites]),
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: storage_uuid_patch(): 'site_list' - {0}".format(exc))
        # check for volume_name
        try:
            if len(body.volume_name) != 0:
                fab_storage.volume_name = body.volume_name
                db.session.commit()
            consoleLogger.info('UPDATE: FabricStorage: uuid={0}, volume_name={1}'.format(
                fab_storage.uuid, fab_storage.volume_name))
            # metrics log - Storage volume_name modified:
            log_msg = 'Storage event stg:{0} modify \'volume_name={1}\' by usr:{2}'.format(
                str(fab_storage.uuid),
                fab_storage.volume_name,
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: storage_uuid_patch(): 'volume_name' - {0}".format(exc))
        # check for volume_size_gb
        try:
            if isinstance(body.volume_size_gb, int):
                fab_storage.volume_size_gb = body.volume_size_gb
                db.session.commit()
            consoleLogger.info('UPDATE: FabricStorage: uuid={0}, volume_size_gb={1}'.format(
                fab_storage.uuid, fab_storage.volume_size_gb))
            # metrics log - Storage volume_name modified:
            log_msg = 'Storage event stg:{0} modify \'volume_size_gb={1}\' by usr:{2}'.format(
                str(fab_storage.uuid),
                fab_storage.volume_size_gb,
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: storage_uuid_patch(): 'volume_size_gb' - {0}".format(exc))

        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Storage: '{0}' has been successfully updated".format(str(fab_storage.uuid))
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with storage_uuid_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)

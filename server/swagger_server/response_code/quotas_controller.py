import math
import os
from datetime import datetime, timezone

from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.quotas import EnumResourceTypes, EnumResourceUnits, FabricQuotas
from swagger_server.models.quotas import Quotas  # noqa: E501
from swagger_server.models.quotas_details import QuotasDetails
from swagger_server.models.quotas_one import QuotasOne
from swagger_server.models.quotas_post import QuotasPost  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent, \
    Status200OkNoContentResults  # noqa: E501
from swagger_server.models.status200_ok_paginated import Status200OkPaginatedLinks
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_401, cors_404, cors_500
from swagger_server.response_code.decorators import login_or_token_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.quotas_utils import create_fabric_quota_from_api
from swagger_server.response_code.vouch_utils import IdSourceEnum

# Constants
_SERVER_URL = os.getenv('CORE_API_SERVER_URL', '')


@login_or_token_required
def quotas_get(project_uuid: str = None, offset: int = None, limit: int = None) -> Quotas:  # noqa: E501
    """Get list of Resource Quotas

    Get list of Resource Quotas # noqa: E501

    :param project_uuid: project uuid
    :type project_uuid: str
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int

    :rtype: Quotas
    {
        "created_at": "2024-12-20T15:59:22.559Z",
        "project_uuid": "string",
        "quota_limit": 0,
        "quota_used": 0,
        "resource_type": "string",
        "resource_unit": "string",
        "updated_at": "2024-12-20T15:59:22.559Z",
        "uuid": "string"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator():
        try:
            # set page to retrieve
            _page = int((offset + limit) / limit)
            # get paginated search results
            if project_uuid:
                fab_project = FabricProjects.query.filter_by(uuid=project_uuid).one_or_none()
                if fab_project:
                    results_page = FabricQuotas.query.filter(
                        FabricQuotas.project_uuid == fab_project.uuid
                    ).order_by(FabricQuotas.resource_type.name).paginate(page=_page, per_page=limit, error_out=False)
                else:
                    return cors_404(details="No match for Project with uuid = '{0}'".format(project_uuid))
            else:
                results_page = FabricQuotas.query.filter(
                    FabricQuotas.project_uuid is not None
                ).order_by(
                    FabricQuotas.resource_type.name
                ).paginate(page=_page, per_page=limit, error_out=False)
            # set quotas response
            response = Quotas()
            response.results = []
            for item in results_page.items:
                quota = QuotasOne()
                quota.created_at = str(item.created_at)
                quota.project_uuid = item.project_uuid
                quota.quota_limit = item.quota_limit
                quota.quota_used = item.quota_used
                quota.resource_type = item.resource_type.value
                quota.resource_unit = item.resource_unit.value
                quota.updated_at = str(item.updated_at)
                quota.uuid = item.uuid
                # add quota to quotas response
                response.results.append(quota)
            # set links
            response.links = Status200OkPaginatedLinks()
            _URL_OFFSET_LIMIT = '{0}offset={1}&limit={2}'
            base = '{0}/quotas?'.format(_SERVER_URL) if not project_uuid else '{0}/quotas?project_uuid={1}&'.format(
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
            details = 'Oops! something went wrong with quotas_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric service user or fabric facility operator",
        )


def quotas_post(body: QuotasPost = None):  # noqa: E501
    """Create new Resource Quota

    Create new Resource Quota # noqa: E501

    :param body: Create a new Resource Quota
    :type body: dict | bytes
    {
        "project_uuid": "string",
        "quota_limit": 0,
        "quota_used": 0,
        "resource_type": "string",
        "resource_unit": "string"
    }

    :rtype: Quotas
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator():
        try:
            # validate project_uuid
            if body.project_uuid and len(body.project_uuid) != 0:
                fab_project = FabricProjects.query.filter_by(uuid=body.project_uuid).one_or_none()
                if not fab_project:
                    return cors_404(details="No match for Project with uuid = '{0}'".format(body.project_uuid))
            else:
                details = "Quotas POST: provide a valid project uuid"
                consoleLogger.error(details)
                return cors_400(details=details)
            # validate quota_limit
            if not body.quota_limit and not math.isclose(float(body.quota_limit), 0.0):
                details = "Quotas POST: provide a valid quota limit"
                consoleLogger.error(details)
                return cors_400(details=details)
            # validate quota_used <-- optional - no check needed
            # validate resource_type
            if not body.resource_type or str(body.resource_type).casefold() not in [x.name for x in EnumResourceTypes]:
                details = "Quotas POST: provide a valid resource_type"
                consoleLogger.error(details)
                return cors_400(details=details)
            # validate resource_unit
            if not body.resource_unit or str(body.resource_unit).casefold() not in [x.name for x in EnumResourceUnits]:
                details = "Quotas POST: provide a valid resource_unit"
                consoleLogger.error(details)
                return cors_400(details=details)
            # create Quota
            fab_quota = create_fabric_quota_from_api(body=body)
            db.session.commit()
            return quotas_uuid_get(uuid=str(fab_quota.uuid))
        except Exception as exc:
            details = 'Oops! something went wrong with quotas_post(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric service user or fabric facility operator",
        )


def quotas_uuid_delete(uuid: str):  # noqa: E501
    """Delete single Resource Quota by UUID

    Delete single Resource Quota by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator():
        try:
            # get Quota by uuid
            fab_quota = FabricQuotas.query.filter_by(uuid=uuid).one_or_none()
            if not fab_quota:
                return cors_404(details="No match for Quota with uuid = '{0}'".format(uuid))
            # delete Announcement
            details = "Quota: '{0}' has been successfully deleted".format(str(fab_quota.uuid))
            db.session.delete(fab_quota)
            db.session.commit()
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
            details = 'Oops! something went wrong with quotas_uuid_delete(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric service user or fabric facility operator",
        )


def quotas_uuid_get(uuid: str):  # noqa: E501
    """Get single Resource Quota by UUID

    Get single Resource Quota by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: QuotasDetails
    {
        "created_at": "2024-12-20T15:59:22.559Z",
        "project_uuid": "string",
        "quota_limit": 0,
        "quota_used": 0,
        "resource_type": "string",
        "resource_unit": "string",
        "updated_at": "2024-12-20T15:59:22.559Z",
        "uuid": "string"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator():
        try:
            # get Quotas by uuid
            fab_quota = FabricQuotas.query.filter_by(uuid=uuid).one_or_none()
            if not fab_quota:
                return cors_404(details="No match for Quota with uuid = '{0}'".format(uuid))
            # set QuotasOne object
            quota_one = QuotasOne()
            quota_one.created_at = str(fab_quota.created_at)
            quota_one.project_uuid = fab_quota.project_uuid
            quota_one.quota_limit = fab_quota.quota_limit
            quota_one.quota_used = fab_quota.quota_used
            quota_one.resource_type = fab_quota.resource_type.value
            quota_one.resource_unit = fab_quota.resource_unit.value
            quota_one.updated_at = str(fab_quota.updated_at)
            quota_one.uuid = fab_quota.uuid
            # set quota_details response
            response = QuotasDetails()
            response.results = [quota_one]
            response.size = len(response.results)
            response.status = 200
            response.type = 'quotas.details'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with quotas_uuid_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric service user or fabric facility operator",
        )


def quotas_uuid_put(uuid, body=None):  # noqa: E501
    """Update single Resource Quota by UUID

    Update single Resource Quota by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update a Resource Quota
    :type body: dict | bytes
    {
        "project_uuid": "string",
        "quota_limit": 0,
        "quota_used": 0,
        "resource_type": "string",
        "resource_unit": "string"
    }

    :rtype: Status200OkNoContent
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator():
        try:
            # get Announcement by uuid
            fab_quota = FabricQuotas.query.filter_by(uuid=uuid).one_or_none()
            if not fab_quota:
                return cors_404(details="No match for Quota with uuid = '{0}'".format(uuid))
            fab_quota_modified = False
            # check for project_uuid
            try:
                if len(body.project_uuid) != 0:
                    fab_project = FabricProjects.query.filter_by(uuid=body.project_uuid).one_or_none()
                    if not fab_project:
                        return cors_404(details="No match for Project with uuid = '{0}'".format(body.project_uuid))
                    fab_quota.project_uuid = body.project_uuid
                    fab_quota_modified = True
                    consoleLogger.info('UPDATE: FabricQuotas: uuid={0}, project_uuid={1}'.format(
                        fab_quota.uuid, fab_quota.project_uuid))
            except Exception as exc:
                consoleLogger.info("NOP: quotas_uuid_put(): 'project_uuid' - {0}".format(exc))
            # check for quota_limit
            try:
                if len(body.quota_limit) != 0:
                    fab_quota.quota_limit = body.quota_limit
                    fab_quota_modified = True
                    consoleLogger.info('UPDATE: FabricQuotas: uuid={0}, quota_limit={1}'.format(
                        fab_quota.uuid, fab_quota.quota_limit))
            except Exception as exc:
                consoleLogger.info("NOP: quotas_uuid_put(): 'quota_limit' - {0}".format(exc))
            # check for quota_used
            try:
                if len(body.quota_used) != 0:
                    fab_quota.quota_used = body.quota_used
                    fab_quota_modified = True
                    consoleLogger.info('UPDATE: FabricQuotas: uuid={0}, quota_used={1}'.format(
                        fab_quota.uuid, fab_quota.quota_used))
            except Exception as exc:
                consoleLogger.info("NOP: quotas_uuid_put(): 'quota_used' - {0}".format(exc))
            # check for resource_type
            try:
                if len(body.resource_type) != 0:
                    if str(body.resource_type).casefold() not in [x.name for x in EnumResourceTypes]:
                        details = \
                            "Quotas PUT: '{0}' is not a valid resource_type".format(body.resource_type)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                    fab_quota.resource_type = str(body.resource_type).casefold()
                    fab_quota_modified = True
                    consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, resource_type={1}'.format(
                        fab_quota.uuid, fab_quota.resource_type))
            except Exception as exc:
                consoleLogger.info("NOP: quotas_uuid_put(): 'resource_type' - {0}".format(exc))
            # check for resource_unit
            try:
                if len(body.resource_unit) != 0:
                    if str(body.resource_unit).casefold() not in [x.name for x in EnumResourceUnits]:
                        details = \
                            "Quotas PUT: '{0}' is not a valid resource_unit".format(body.resource_unit)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                    fab_quota.resource_unit = str(body.resource_unit).casefold()
                    fab_quota_modified = True
                    consoleLogger.info('UPDATE: FabricAnnouncements: uuid={0}, resource_unit={1}'.format(
                        fab_quota.uuid, fab_quota.resource_type))
            except Exception as exc:
                consoleLogger.info("NOP: quotas_uuid_put(): 'resource_unit' - {0}".format(exc))
            # save modified quota
            try:
                if fab_quota_modified:
                    fab_quota.updated_at = datetime.now(timezone.utc)
                    db.session.commit()
            except Exception as exc:
                db.session.rollback()
                details = 'Oops! something went wrong with quotas_uuid_put(): {0}'.format(exc)
                consoleLogger.error(details)
                return cors_500(details=details)
            # create response
            patch_info = Status200OkNoContentResults()
            patch_info.details = "Quotas: '{0}' has been successfully updated".format(str(fab_quota.uuid))
            response = Status200OkNoContent()
            response.results = [patch_info]
            response.size = len(response.results)
            response.status = 200
            response.type = 'no_content'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with quotas_uuid_put(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric service user or fabric facility operator",
        )

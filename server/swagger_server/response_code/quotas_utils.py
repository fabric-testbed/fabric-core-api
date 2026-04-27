from datetime import datetime, timezone
from uuid import uuid4

from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.quotas import FabricQuotas
from swagger_server.models.quotas_post import QuotasPost
from swagger_server.response_code.cors_response import cors_500


def create_fabric_quota_from_api(body: QuotasPost) -> FabricQuotas:
    """
    Quotas - Control Framework quotas for projects
    - created_at = UTC datetime
    - id - primary key
    - project_uuid = UUID as string
    - quota_limit = Float
    - quota_used = Float
    - resource_type = one of EnumResourceTypes member names (see
      `database/models/quotas.py`): core, disk, fpga_xilinx_sn1022,
      fpga_xilinx_u280, gpu_a30, gpu_a40, gpu_rtx6000, gpu_tesla_t4,
      nvme_p4510, p4, ram, sharednic_connectx_6, smartnic_connectx_5,
      smartnic_connectx_6, smartnic_connectx_7_100,
      smartnic_connectx_7_400, storage_nas
    - resource_unit = one of EnumResourceUnits member names (currently:
      hours)
    - updated_at = UTC datetime
    - uuid = UUID as string

    {
        "project_uuid": "10c0094a-abaf-4ef9-a532-2be53e2a896b",
        "quota_limit": 1000.0,
        "quota_used": 0.0,
        "resource_type": "core",
        "resource_unit": "hours"
    }
    """
    # create Quota
    now = datetime.now(timezone.utc)
    fab_quota = FabricQuotas()
    fab_quota.created_at = now
    fab_quota.project_uuid = body.project_uuid
    fab_quota.quota_limit = body.quota_limit
    fab_quota.quota_used = body.quota_used if body.quota_used else 0.0
    fab_quota.resource_type = str(body.resource_type).casefold()
    fab_quota.resource_unit = str(body.resource_unit).casefold()
    fab_quota.updated_at = now
    fab_quota.uuid = str(uuid4())
    try:
        db.session.add(fab_quota)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        details = 'Oops! something went wrong with announcements_uuid_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)
    return fab_quota

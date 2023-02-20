from datetime import datetime, timezone
from uuid import uuid4

from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.testbed_info import FabricTestbedInfo
from swagger_server.models.testbed_info import TestbedInfo
from swagger_server.models.testbed_info_post import TestbedInfoPost


def create_fabric_testbed_info_from_api(body: TestbedInfoPost, creator: FabricPeople) -> TestbedInfo:
    """
    TestbedInfo - Read only information regarding testbed state for remote tools (* denotes required)
    - * created - timestamp created (TimestampMixin)
    - * created_by_uuid - string (TrackingMixin)
    - * is_active - boolean
    - * json_data - JSON field data
    - modified - timestamp modified (TimestampMixin)
    - modified_by_uuid - string (TrackingMixin)
    - * uuid - unique universal identifier

    {
        "testbed_info": {<JSON objects>} or [<array of JSON objects>]
    }
    """
    # deactivate prior Testbed Info
    prior_testbed_info = FabricTestbedInfo.query.filter_by(is_active=True).one_or_none()
    if prior_testbed_info:
        prior_testbed_info.is_active = False
    # create new Testbed Info
    now = datetime.now(timezone.utc)
    testbed_info = FabricTestbedInfo()
    testbed_info.created = now
    testbed_info.created_by_uuid = str(creator.uuid)
    testbed_info.is_active = True
    testbed_info.json_data = body.testbed_info
    testbed_info.modified = now
    testbed_info.modified_by_uuid = str(creator.uuid)
    testbed_info.uuid = uuid4()
    db.session.add(testbed_info)
    db.session.commit()

    return testbed_info

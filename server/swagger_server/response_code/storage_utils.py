from datetime import datetime, timezone
from uuid import uuid4

from swagger_server.api_logger import metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.storage import FabricStorage, StorageSites
from swagger_server.models.storage_post import StoragePost
from swagger_server.response_code.core_api_utils import normalize_date_to_utc
from swagger_server.response_code.response_utils import array_difference


def create_storage_allocation_from_api(body: StoragePost, storage_creator: FabricPeople) -> FabricStorage:
    """
    StoragePost - request body
    {
        "expires_on": "<string>",         <-- required
        "project_uuid": "<string>",       <-- required
        "requested_by_uuid": "<string>",  <-- required
        "site_list": [ "<string>", ... ], <-- optional
        "volume_name": "<string>",        <-- required
        "volume_size_gb": <integer>       <-- optional
    }

    FabricStorage - database object
    - active            - boolean
    - created           - datetime
    - created_by_uuid   - string
    - expires_on        - datetime
    - id                - int:pk
    - modified          - datetime
    - modified_by_uuid  - string
    - project_id        - FabricProject FK
    - requested_by      - FabricPeople FK
    - sites             - array of string
    - volume_name       - string
    - volume_size_gb    - int
    """
    # create FabricStorage object
    fab_project = FabricProjects.query.filter_by(uuid=body.project_uuid).one_or_none()
    fab_person = FabricPeople.query.filter_by(uuid=body.requested_by_uuid).one_or_none()
    now = datetime.now(timezone.utc)
    fab_storage = FabricStorage()
    fab_storage.active = False
    fab_storage.created = now
    fab_storage.created_by_uuid = str(storage_creator.uuid)
    fab_storage.expires_on = normalize_date_to_utc(body.expires_on)
    fab_storage.modified = now
    fab_storage.modified_by_uuid = str(storage_creator.uuid)
    fab_storage.project_id = fab_project.id
    fab_storage.requested_by_id = fab_person.id
    fab_storage.uuid = uuid4()
    fab_storage.volume_name = body.volume_name
    fab_storage.volume_size_gb = body.volume_size_gb if body.volume_size_gb else None
    db.session.add(fab_storage)
    db.session.commit()
    # update storage site list
    update_storage_site_list(fab_storage=fab_storage, site_list=body.site_list)
    # add storage to project
    fab_project.project_storage.append(fab_storage)
    db.session.commit()
    # metrics log - Storage allocation was created:
    # 2022-09-06 19:45:56,022 Storage event stg:dead-beef-dead-beef create by usr:dead-beef-dead-beef
    log_msg = 'Storage event stg:{0} create by usr:{1}'.format(str(fab_storage.uuid), str(storage_creator.uuid))
    metricsLogger.info(log_msg)
    # metrics log - Project storage was added:
    # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add storage stg:feed-beef-feed-beef by usr:0000-0000-0000-0002
    log_msg = 'Project event prj:{0} modify-add storage stg:{1} by usr:{2}'.format(str(fab_project.uuid),
                                                                                   str(fab_storage.uuid),
                                                                                   str(storage_creator.uuid))
    metricsLogger.info(log_msg)

    return fab_storage


def update_storage_site_list(fab_storage: FabricStorage = None, site_list: [str] = None) -> None:
    sites_orig = [s.site for s in fab_storage.sites]
    sites_new = site_list
    sites_add = array_difference(sites_new, sites_orig)
    sites_remove = array_difference(sites_orig, sites_new)
    # add storage sites
    for site in sites_add:
        fab_site = StorageSites.query.filter(
            StorageSites.storage_id == fab_storage.id, StorageSites.site == site).one_or_none()
        if not fab_site:
            fab_site = StorageSites()
            fab_site.storage_id = fab_storage.id
            fab_site.site = site
            fab_storage.sites.append(fab_site)
            db.session.commit()
    # remove projects tags
    for site in sites_remove:
        fab_site = StorageSites.query.filter(
            StorageSites.storage_id == fab_storage.id, StorageSites.site == site).one_or_none()
        if fab_site:
            fab_storage.sites.remove(fab_site)
            db.session.delete(fab_site)
            db.session.commit()

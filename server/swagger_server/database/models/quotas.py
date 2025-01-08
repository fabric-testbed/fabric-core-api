import enum

from sqlalchemy import UniqueConstraint

from swagger_server.database.db import db


# Enum for Resource Types
class EnumResourceTypes(enum.Enum):
    core = "Core"
    disk = "Disk"
    fpga = "FPGA"
    gpu = "GPU"
    nvme = "NVME"
    p4 = "P4"
    ram = "RAM"
    sharednic = "SharedNIC"
    smartnic = "SmartNIC"
    storage = "Storage"


# Enum for Resource Units
class EnumResourceUnits(enum.Enum):
    hours = "Hours"


class FabricQuotas(db.Model):
    """
    Quotas - Control Framework quotas for projects
    - created_at = UTC datetime
    - id - primary key
    - project_uuid = UUID as string
    - quota_limit = Float
    - quota_used = Float
    - resource_type = in [p4, core, ram, disk, gpu, smartnic, sharednic, fpga, nvme, storage] as string
    - resource_unit = in [hours, ...] as string
    - updated_at = UTC datetime
    - uuid = UUID as string
    """
    query: db.Query
    __tablename__ = 'quotas'
    __table_args__ = (
    UniqueConstraint('project_uuid', 'resource_type', 'resource_unit', name='project_resource_type_unit'),)
    __allow_unmapped__ = True

    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    project_uuid = db.Column(db.String(), nullable=False)
    quota_limit = db.Column(db.Float, nullable=False)
    quota_used = db.Column(db.Float, nullable=False)
    resource_type = db.Column(db.Enum(EnumResourceTypes), default=EnumResourceTypes.core, nullable=False)
    resource_unit = db.Column(db.Enum(EnumResourceUnits), default=EnumResourceUnits.hours, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)

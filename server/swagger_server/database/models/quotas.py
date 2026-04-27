import enum

from sqlalchemy import UniqueConstraint

from swagger_server.database.db import db


# Enum for Resource Types
class EnumResourceTypes(enum.Enum):
    """
    ['core',
    'disk',
    'fpga_xilinx_sn1022',
    'fpga_xilinx_u280',
    'gpu_a30',
    'gpu_a40',
    'gpu_rtx6000',
    'gpu_tesla_t4',
    'nvme_p4510',
    'p4',
    'ram',
    'sharednic_connectx_6',
    'smartnic_connectx_5',
    'smartnic_connectx_6',
    'smartnic_connectx_7_100',
    'smartnic_connectx_7_400',
    'storage_nas']
    """
    core = "Core"
    disk = "Disk"
    fpga_xilinx_sn1022 = "FPGA XILINX SN1022"
    fpga_xilinx_u280 = "FPGA XILINX U280"
    gpu_a30 = "GPU A30"
    gpu_a40 = "GPU A40"
    gpu_rtx6000 = "GPU RTX6000"
    gpu_tesla_t4 = "GPU TESLA T4"
    nvme_p4510 = "NVME P4510"
    p4 = "P4"
    ram = "RAM"
    sharednic_connectx_6 = "SharedNIC ConnectX 6"
    smartnic_connectx_5 = "SmartNIC ConnectX 5"
    smartnic_connectx_6 = "SmartNIC ConnectX 6"
    smartnic_connectx_7_100 = "SmartNIC ConnectX 7 - 100"
    smartnic_connectx_7_400 = "SmartNIC ConnectX 7 - 400"
    storage_nas = "Storage NAS"


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

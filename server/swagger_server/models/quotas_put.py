# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class QuotasPut(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, project_uuid: str=None, quota_limit: float=None, quota_used: float=None, resource_type: str=None, resource_unit: str=None):  # noqa: E501
        """QuotasPut - a model defined in Swagger

        :param project_uuid: The project_uuid of this QuotasPut.  # noqa: E501
        :type project_uuid: str
        :param quota_limit: The quota_limit of this QuotasPut.  # noqa: E501
        :type quota_limit: float
        :param quota_used: The quota_used of this QuotasPut.  # noqa: E501
        :type quota_used: float
        :param resource_type: The resource_type of this QuotasPut.  # noqa: E501
        :type resource_type: str
        :param resource_unit: The resource_unit of this QuotasPut.  # noqa: E501
        :type resource_unit: str
        """
        self.swagger_types = {
            'project_uuid': str,
            'quota_limit': float,
            'quota_used': float,
            'resource_type': str,
            'resource_unit': str
        }

        self.attribute_map = {
            'project_uuid': 'project_uuid',
            'quota_limit': 'quota_limit',
            'quota_used': 'quota_used',
            'resource_type': 'resource_type',
            'resource_unit': 'resource_unit'
        }
        self._project_uuid = project_uuid
        self._quota_limit = quota_limit
        self._quota_used = quota_used
        self._resource_type = resource_type
        self._resource_unit = resource_unit

    @classmethod
    def from_dict(cls, dikt) -> 'QuotasPut':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The quotas_put of this QuotasPut.  # noqa: E501
        :rtype: QuotasPut
        """
        return util.deserialize_model(dikt, cls)

    @property
    def project_uuid(self) -> str:
        """Gets the project_uuid of this QuotasPut.


        :return: The project_uuid of this QuotasPut.
        :rtype: str
        """
        return self._project_uuid

    @project_uuid.setter
    def project_uuid(self, project_uuid: str):
        """Sets the project_uuid of this QuotasPut.


        :param project_uuid: The project_uuid of this QuotasPut.
        :type project_uuid: str
        """

        self._project_uuid = project_uuid

    @property
    def quota_limit(self) -> float:
        """Gets the quota_limit of this QuotasPut.


        :return: The quota_limit of this QuotasPut.
        :rtype: float
        """
        return self._quota_limit

    @quota_limit.setter
    def quota_limit(self, quota_limit: float):
        """Sets the quota_limit of this QuotasPut.


        :param quota_limit: The quota_limit of this QuotasPut.
        :type quota_limit: float
        """

        self._quota_limit = quota_limit

    @property
    def quota_used(self) -> float:
        """Gets the quota_used of this QuotasPut.


        :return: The quota_used of this QuotasPut.
        :rtype: float
        """
        return self._quota_used

    @quota_used.setter
    def quota_used(self, quota_used: float):
        """Sets the quota_used of this QuotasPut.


        :param quota_used: The quota_used of this QuotasPut.
        :type quota_used: float
        """

        self._quota_used = quota_used

    @property
    def resource_type(self) -> str:
        """Gets the resource_type of this QuotasPut.


        :return: The resource_type of this QuotasPut.
        :rtype: str
        """
        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type: str):
        """Sets the resource_type of this QuotasPut.


        :param resource_type: The resource_type of this QuotasPut.
        :type resource_type: str
        """

        self._resource_type = resource_type

    @property
    def resource_unit(self) -> str:
        """Gets the resource_unit of this QuotasPut.


        :return: The resource_unit of this QuotasPut.
        :rtype: str
        """
        return self._resource_unit

    @resource_unit.setter
    def resource_unit(self, resource_unit: str):
        """Sets the resource_unit of this QuotasPut.


        :param resource_unit: The resource_unit of this QuotasPut.
        :type resource_unit: str
        """

        self._resource_unit = resource_unit
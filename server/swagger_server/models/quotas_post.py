# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class QuotasPost(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, project_uuid: str=None, quota_limit: float=None, quota_used: float=0, resource_type: str=None, resource_unit: str=None):  # noqa: E501
        """QuotasPost - a model defined in Swagger

        :param project_uuid: The project_uuid of this QuotasPost.  # noqa: E501
        :type project_uuid: str
        :param quota_limit: The quota_limit of this QuotasPost.  # noqa: E501
        :type quota_limit: float
        :param quota_used: The quota_used of this QuotasPost.  # noqa: E501
        :type quota_used: float
        :param resource_type: The resource_type of this QuotasPost.  # noqa: E501
        :type resource_type: str
        :param resource_unit: The resource_unit of this QuotasPost.  # noqa: E501
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
    def from_dict(cls, dikt) -> 'QuotasPost':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The quotas_post of this QuotasPost.  # noqa: E501
        :rtype: QuotasPost
        """
        return util.deserialize_model(dikt, cls)

    @property
    def project_uuid(self) -> str:
        """Gets the project_uuid of this QuotasPost.


        :return: The project_uuid of this QuotasPost.
        :rtype: str
        """
        return self._project_uuid

    @project_uuid.setter
    def project_uuid(self, project_uuid: str):
        """Sets the project_uuid of this QuotasPost.


        :param project_uuid: The project_uuid of this QuotasPost.
        :type project_uuid: str
        """
        if project_uuid is None:
            raise ValueError("Invalid value for `project_uuid`, must not be `None`")  # noqa: E501

        self._project_uuid = project_uuid

    @property
    def quota_limit(self) -> float:
        """Gets the quota_limit of this QuotasPost.


        :return: The quota_limit of this QuotasPost.
        :rtype: float
        """
        return self._quota_limit

    @quota_limit.setter
    def quota_limit(self, quota_limit: float):
        """Sets the quota_limit of this QuotasPost.


        :param quota_limit: The quota_limit of this QuotasPost.
        :type quota_limit: float
        """
        if quota_limit is None:
            raise ValueError("Invalid value for `quota_limit`, must not be `None`")  # noqa: E501

        self._quota_limit = quota_limit

    @property
    def quota_used(self) -> float:
        """Gets the quota_used of this QuotasPost.


        :return: The quota_used of this QuotasPost.
        :rtype: float
        """
        return self._quota_used

    @quota_used.setter
    def quota_used(self, quota_used: float):
        """Sets the quota_used of this QuotasPost.


        :param quota_used: The quota_used of this QuotasPost.
        :type quota_used: float
        """

        self._quota_used = quota_used

    @property
    def resource_type(self) -> str:
        """Gets the resource_type of this QuotasPost.


        :return: The resource_type of this QuotasPost.
        :rtype: str
        """
        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type: str):
        """Sets the resource_type of this QuotasPost.


        :param resource_type: The resource_type of this QuotasPost.
        :type resource_type: str
        """
        if resource_type is None:
            raise ValueError("Invalid value for `resource_type`, must not be `None`")  # noqa: E501

        self._resource_type = resource_type

    @property
    def resource_unit(self) -> str:
        """Gets the resource_unit of this QuotasPost.


        :return: The resource_unit of this QuotasPost.
        :rtype: str
        """
        return self._resource_unit

    @resource_unit.setter
    def resource_unit(self, resource_unit: str):
        """Sets the resource_unit of this QuotasPost.


        :param resource_unit: The resource_unit of this QuotasPost.
        :type resource_unit: str
        """
        if resource_unit is None:
            raise ValueError("Invalid value for `resource_unit`, must not be `None`")  # noqa: E501

        self._resource_unit = resource_unit

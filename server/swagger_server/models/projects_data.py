# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.project_membership import ProjectMembership  # noqa: F401,E501
from swagger_server import util


class ProjectsData(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, created: str=None, description: str=None, facility: str=None, is_public: bool=True, memberships: ProjectMembership=None, name: str=None, uuid: str=None):  # noqa: E501
        """ProjectsData - a model defined in Swagger

        :param created: The created of this ProjectsData.  # noqa: E501
        :type created: str
        :param description: The description of this ProjectsData.  # noqa: E501
        :type description: str
        :param facility: The facility of this ProjectsData.  # noqa: E501
        :type facility: str
        :param is_public: The is_public of this ProjectsData.  # noqa: E501
        :type is_public: bool
        :param memberships: The memberships of this ProjectsData.  # noqa: E501
        :type memberships: ProjectMembership
        :param name: The name of this ProjectsData.  # noqa: E501
        :type name: str
        :param uuid: The uuid of this ProjectsData.  # noqa: E501
        :type uuid: str
        """
        self.swagger_types = {
            'created': str,
            'description': str,
            'facility': str,
            'is_public': bool,
            'memberships': ProjectMembership,
            'name': str,
            'uuid': str
        }

        self.attribute_map = {
            'created': 'created',
            'description': 'description',
            'facility': 'facility',
            'is_public': 'is_public',
            'memberships': 'memberships',
            'name': 'name',
            'uuid': 'uuid'
        }
        self._created = created
        self._description = description
        self._facility = facility
        self._is_public = is_public
        self._memberships = memberships
        self._name = name
        self._uuid = uuid

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectsData':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The projects_data of this ProjectsData.  # noqa: E501
        :rtype: ProjectsData
        """
        return util.deserialize_model(dikt, cls)

    @property
    def created(self) -> str:
        """Gets the created of this ProjectsData.


        :return: The created of this ProjectsData.
        :rtype: str
        """
        return self._created

    @created.setter
    def created(self, created: str):
        """Sets the created of this ProjectsData.


        :param created: The created of this ProjectsData.
        :type created: str
        """
        if created is None:
            raise ValueError("Invalid value for `created`, must not be `None`")  # noqa: E501

        self._created = created

    @property
    def description(self) -> str:
        """Gets the description of this ProjectsData.


        :return: The description of this ProjectsData.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this ProjectsData.


        :param description: The description of this ProjectsData.
        :type description: str
        """
        if description is None:
            raise ValueError("Invalid value for `description`, must not be `None`")  # noqa: E501

        self._description = description

    @property
    def facility(self) -> str:
        """Gets the facility of this ProjectsData.


        :return: The facility of this ProjectsData.
        :rtype: str
        """
        return self._facility

    @facility.setter
    def facility(self, facility: str):
        """Sets the facility of this ProjectsData.


        :param facility: The facility of this ProjectsData.
        :type facility: str
        """
        if facility is None:
            raise ValueError("Invalid value for `facility`, must not be `None`")  # noqa: E501

        self._facility = facility

    @property
    def is_public(self) -> bool:
        """Gets the is_public of this ProjectsData.


        :return: The is_public of this ProjectsData.
        :rtype: bool
        """
        return self._is_public

    @is_public.setter
    def is_public(self, is_public: bool):
        """Sets the is_public of this ProjectsData.


        :param is_public: The is_public of this ProjectsData.
        :type is_public: bool
        """
        if is_public is None:
            raise ValueError("Invalid value for `is_public`, must not be `None`")  # noqa: E501

        self._is_public = is_public

    @property
    def memberships(self) -> ProjectMembership:
        """Gets the memberships of this ProjectsData.


        :return: The memberships of this ProjectsData.
        :rtype: ProjectMembership
        """
        return self._memberships

    @memberships.setter
    def memberships(self, memberships: ProjectMembership):
        """Sets the memberships of this ProjectsData.


        :param memberships: The memberships of this ProjectsData.
        :type memberships: ProjectMembership
        """

        self._memberships = memberships

    @property
    def name(self) -> str:
        """Gets the name of this ProjectsData.


        :return: The name of this ProjectsData.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this ProjectsData.


        :param name: The name of this ProjectsData.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def uuid(self) -> str:
        """Gets the uuid of this ProjectsData.


        :return: The uuid of this ProjectsData.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this ProjectsData.


        :param uuid: The uuid of this ProjectsData.
        :type uuid: str
        """
        if uuid is None:
            raise ValueError("Invalid value for `uuid`, must not be `None`")  # noqa: E501

        self._uuid = uuid

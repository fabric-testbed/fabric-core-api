# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.project_membership import ProjectMembership  # noqa: F401,E501
from swagger_server import util


class Project(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, communities: List[str]=None, created: str=None, description: str=None, expires_on: str=None, facility: str=None, is_public: bool=True, memberships: ProjectMembership=None, name: str=None, tags: List[str]=None, project_type: str=None, topics: List[str]=None, uuid: str=None):  # noqa: E501
        """Project - a model defined in Swagger

        :param communities: The communities of this Project.  # noqa: E501
        :type communities: List[str]
        :param created: The created of this Project.  # noqa: E501
        :type created: str
        :param description: The description of this Project.  # noqa: E501
        :type description: str
        :param expires_on: The expires_on of this Project.  # noqa: E501
        :type expires_on: str
        :param facility: The facility of this Project.  # noqa: E501
        :type facility: str
        :param is_public: The is_public of this Project.  # noqa: E501
        :type is_public: bool
        :param memberships: The memberships of this Project.  # noqa: E501
        :type memberships: ProjectMembership
        :param name: The name of this Project.  # noqa: E501
        :type name: str
        :param tags: The tags of this Project.  # noqa: E501
        :type tags: List[str]
        :param project_type: The project_type of this Project.  # noqa: E501
        :type project_type: str
        :param topics: The topics of this Project.  # noqa: E501
        :type topics: List[str]
        :param uuid: The uuid of this Project.  # noqa: E501
        :type uuid: str
        """
        self.swagger_types = {
            'communities': List[str],
            'created': str,
            'description': str,
            'expires_on': str,
            'facility': str,
            'is_public': bool,
            'memberships': ProjectMembership,
            'name': str,
            'tags': List[str],
            'project_type': str,
            'topics': List[str],
            'uuid': str
        }

        self.attribute_map = {
            'communities': 'communities',
            'created': 'created',
            'description': 'description',
            'expires_on': 'expires_on',
            'facility': 'facility',
            'is_public': 'is_public',
            'memberships': 'memberships',
            'name': 'name',
            'tags': 'tags',
            'project_type': 'project_type',
            'topics': 'topics',
            'uuid': 'uuid'
        }
        self._communities = communities
        self._created = created
        self._description = description
        self._expires_on = expires_on
        self._facility = facility
        self._is_public = is_public
        self._memberships = memberships
        self._name = name
        self._tags = tags
        self._project_type = project_type
        self._topics = topics
        self._uuid = uuid

    @classmethod
    def from_dict(cls, dikt) -> 'Project':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The project of this Project.  # noqa: E501
        :rtype: Project
        """
        return util.deserialize_model(dikt, cls)

    @property
    def communities(self) -> List[str]:
        """Gets the communities of this Project.


        :return: The communities of this Project.
        :rtype: List[str]
        """
        return self._communities

    @communities.setter
    def communities(self, communities: List[str]):
        """Sets the communities of this Project.


        :param communities: The communities of this Project.
        :type communities: List[str]
        """

        self._communities = communities

    @property
    def created(self) -> str:
        """Gets the created of this Project.


        :return: The created of this Project.
        :rtype: str
        """
        return self._created

    @created.setter
    def created(self, created: str):
        """Sets the created of this Project.


        :param created: The created of this Project.
        :type created: str
        """
        if created is None:
            raise ValueError("Invalid value for `created`, must not be `None`")  # noqa: E501

        self._created = created

    @property
    def description(self) -> str:
        """Gets the description of this Project.


        :return: The description of this Project.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this Project.


        :param description: The description of this Project.
        :type description: str
        """
        if description is None:
            raise ValueError("Invalid value for `description`, must not be `None`")  # noqa: E501

        self._description = description

    @property
    def expires_on(self) -> str:
        """Gets the expires_on of this Project.


        :return: The expires_on of this Project.
        :rtype: str
        """
        return self._expires_on

    @expires_on.setter
    def expires_on(self, expires_on: str):
        """Sets the expires_on of this Project.


        :param expires_on: The expires_on of this Project.
        :type expires_on: str
        """

        self._expires_on = expires_on

    @property
    def facility(self) -> str:
        """Gets the facility of this Project.


        :return: The facility of this Project.
        :rtype: str
        """
        return self._facility

    @facility.setter
    def facility(self, facility: str):
        """Sets the facility of this Project.


        :param facility: The facility of this Project.
        :type facility: str
        """
        if facility is None:
            raise ValueError("Invalid value for `facility`, must not be `None`")  # noqa: E501

        self._facility = facility

    @property
    def is_public(self) -> bool:
        """Gets the is_public of this Project.


        :return: The is_public of this Project.
        :rtype: bool
        """
        return self._is_public

    @is_public.setter
    def is_public(self, is_public: bool):
        """Sets the is_public of this Project.


        :param is_public: The is_public of this Project.
        :type is_public: bool
        """
        if is_public is None:
            raise ValueError("Invalid value for `is_public`, must not be `None`")  # noqa: E501

        self._is_public = is_public

    @property
    def memberships(self) -> ProjectMembership:
        """Gets the memberships of this Project.


        :return: The memberships of this Project.
        :rtype: ProjectMembership
        """
        return self._memberships

    @memberships.setter
    def memberships(self, memberships: ProjectMembership):
        """Sets the memberships of this Project.


        :param memberships: The memberships of this Project.
        :type memberships: ProjectMembership
        """
        if memberships is None:
            raise ValueError("Invalid value for `memberships`, must not be `None`")  # noqa: E501

        self._memberships = memberships

    @property
    def name(self) -> str:
        """Gets the name of this Project.


        :return: The name of this Project.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Project.


        :param name: The name of this Project.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def tags(self) -> List[str]:
        """Gets the tags of this Project.


        :return: The tags of this Project.
        :rtype: List[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags: List[str]):
        """Sets the tags of this Project.


        :param tags: The tags of this Project.
        :type tags: List[str]
        """

        self._tags = tags

    @property
    def project_type(self) -> str:
        """Gets the project_type of this Project.


        :return: The project_type of this Project.
        :rtype: str
        """
        return self._project_type

    @project_type.setter
    def project_type(self, project_type: str):
        """Sets the project_type of this Project.


        :param project_type: The project_type of this Project.
        :type project_type: str
        """

        self._project_type = project_type

    @property
    def topics(self) -> List[str]:
        """Gets the topics of this Project.


        :return: The topics of this Project.
        :rtype: List[str]
        """
        return self._topics

    @topics.setter
    def topics(self, topics: List[str]):
        """Sets the topics of this Project.


        :param topics: The topics of this Project.
        :type topics: List[str]
        """

        self._topics = topics

    @property
    def uuid(self) -> str:
        """Gets the uuid of this Project.


        :return: The uuid of this Project.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this Project.


        :param uuid: The uuid of this Project.
        :type uuid: str
        """
        if uuid is None:
            raise ValueError("Invalid value for `uuid`, must not be `None`")  # noqa: E501

        self._uuid = uuid

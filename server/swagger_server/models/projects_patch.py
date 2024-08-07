# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.preferences import Preferences  # noqa: F401,E501
from swagger_server import util


class ProjectsPatch(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, description: str=None, is_public: bool=None, name: str=None, preferences: Preferences=None, project_type: str='research'):  # noqa: E501
        """ProjectsPatch - a model defined in Swagger

        :param description: The description of this ProjectsPatch.  # noqa: E501
        :type description: str
        :param is_public: The is_public of this ProjectsPatch.  # noqa: E501
        :type is_public: bool
        :param name: The name of this ProjectsPatch.  # noqa: E501
        :type name: str
        :param preferences: The preferences of this ProjectsPatch.  # noqa: E501
        :type preferences: Preferences
        :param project_type: The project_type of this ProjectsPatch.  # noqa: E501
        :type project_type: str
        """
        self.swagger_types = {
            'description': str,
            'is_public': bool,
            'name': str,
            'preferences': Preferences,
            'project_type': str
        }

        self.attribute_map = {
            'description': 'description',
            'is_public': 'is_public',
            'name': 'name',
            'preferences': 'preferences',
            'project_type': 'project_type'
        }
        self._description = description
        self._is_public = is_public
        self._name = name
        self._preferences = preferences
        self._project_type = project_type

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectsPatch':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The projects_patch of this ProjectsPatch.  # noqa: E501
        :rtype: ProjectsPatch
        """
        return util.deserialize_model(dikt, cls)

    @property
    def description(self) -> str:
        """Gets the description of this ProjectsPatch.


        :return: The description of this ProjectsPatch.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this ProjectsPatch.


        :param description: The description of this ProjectsPatch.
        :type description: str
        """

        self._description = description

    @property
    def is_public(self) -> bool:
        """Gets the is_public of this ProjectsPatch.


        :return: The is_public of this ProjectsPatch.
        :rtype: bool
        """
        return self._is_public

    @is_public.setter
    def is_public(self, is_public: bool):
        """Sets the is_public of this ProjectsPatch.


        :param is_public: The is_public of this ProjectsPatch.
        :type is_public: bool
        """

        self._is_public = is_public

    @property
    def name(self) -> str:
        """Gets the name of this ProjectsPatch.


        :return: The name of this ProjectsPatch.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this ProjectsPatch.


        :param name: The name of this ProjectsPatch.
        :type name: str
        """

        self._name = name

    @property
    def preferences(self) -> Preferences:
        """Gets the preferences of this ProjectsPatch.


        :return: The preferences of this ProjectsPatch.
        :rtype: Preferences
        """
        return self._preferences

    @preferences.setter
    def preferences(self, preferences: Preferences):
        """Sets the preferences of this ProjectsPatch.


        :param preferences: The preferences of this ProjectsPatch.
        :type preferences: Preferences
        """

        self._preferences = preferences

    @property
    def project_type(self) -> str:
        """Gets the project_type of this ProjectsPatch.


        :return: The project_type of this ProjectsPatch.
        :rtype: str
        """
        return self._project_type

    @project_type.setter
    def project_type(self, project_type: str):
        """Sets the project_type of this ProjectsPatch.


        :param project_type: The project_type of this ProjectsPatch.
        :type project_type: str
        """
        allowed_values = ["educational", "industry", "maintenance", "research", "tutorial"]  # noqa: E501
        if project_type not in allowed_values:
            raise ValueError(
                "Invalid value for `project_type` ({0}), must be one of {1}"
                .format(project_type, allowed_values)
            )

        self._project_type = project_type

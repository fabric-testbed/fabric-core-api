# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class WhoamiResults(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, active: bool=False, email: str=None, enrolled: bool=False, name: str=None, uuid: str=None):  # noqa: E501
        """WhoamiResults - a model defined in Swagger

        :param active: The active of this WhoamiResults.  # noqa: E501
        :type active: bool
        :param email: The email of this WhoamiResults.  # noqa: E501
        :type email: str
        :param enrolled: The enrolled of this WhoamiResults.  # noqa: E501
        :type enrolled: bool
        :param name: The name of this WhoamiResults.  # noqa: E501
        :type name: str
        :param uuid: The uuid of this WhoamiResults.  # noqa: E501
        :type uuid: str
        """
        self.swagger_types = {
            'active': bool,
            'email': str,
            'enrolled': bool,
            'name': str,
            'uuid': str
        }

        self.attribute_map = {
            'active': 'active',
            'email': 'email',
            'enrolled': 'enrolled',
            'name': 'name',
            'uuid': 'uuid'
        }
        self._active = active
        self._email = email
        self._enrolled = enrolled
        self._name = name
        self._uuid = uuid

    @classmethod
    def from_dict(cls, dikt) -> 'WhoamiResults':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The whoami_results of this WhoamiResults.  # noqa: E501
        :rtype: WhoamiResults
        """
        return util.deserialize_model(dikt, cls)

    @property
    def active(self) -> bool:
        """Gets the active of this WhoamiResults.


        :return: The active of this WhoamiResults.
        :rtype: bool
        """
        return self._active

    @active.setter
    def active(self, active: bool):
        """Sets the active of this WhoamiResults.


        :param active: The active of this WhoamiResults.
        :type active: bool
        """
        if active is None:
            raise ValueError("Invalid value for `active`, must not be `None`")  # noqa: E501

        self._active = active

    @property
    def email(self) -> str:
        """Gets the email of this WhoamiResults.


        :return: The email of this WhoamiResults.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email: str):
        """Sets the email of this WhoamiResults.


        :param email: The email of this WhoamiResults.
        :type email: str
        """
        if email is None:
            raise ValueError("Invalid value for `email`, must not be `None`")  # noqa: E501

        self._email = email

    @property
    def enrolled(self) -> bool:
        """Gets the enrolled of this WhoamiResults.


        :return: The enrolled of this WhoamiResults.
        :rtype: bool
        """
        return self._enrolled

    @enrolled.setter
    def enrolled(self, enrolled: bool):
        """Sets the enrolled of this WhoamiResults.


        :param enrolled: The enrolled of this WhoamiResults.
        :type enrolled: bool
        """
        if enrolled is None:
            raise ValueError("Invalid value for `enrolled`, must not be `None`")  # noqa: E501

        self._enrolled = enrolled

    @property
    def name(self) -> str:
        """Gets the name of this WhoamiResults.


        :return: The name of this WhoamiResults.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this WhoamiResults.


        :param name: The name of this WhoamiResults.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def uuid(self) -> str:
        """Gets the uuid of this WhoamiResults.


        :return: The uuid of this WhoamiResults.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this WhoamiResults.


        :param uuid: The uuid of this WhoamiResults.
        :type uuid: str
        """
        if uuid is None:
            raise ValueError("Invalid value for `uuid`, must not be `None`")  # noqa: E501

        self._uuid = uuid
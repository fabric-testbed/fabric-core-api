# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.preferences import Preferences  # noqa: F401,E501
from swagger_server import util


class PeoplePatch(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, email: str=None, name: str=None, preferences: Preferences=None, receive_promotional_email: bool=None):  # noqa: E501
        """PeoplePatch - a model defined in Swagger

        :param email: The email of this PeoplePatch.  # noqa: E501
        :type email: str
        :param name: The name of this PeoplePatch.  # noqa: E501
        :type name: str
        :param preferences: The preferences of this PeoplePatch.  # noqa: E501
        :type preferences: Preferences
        :param receive_promotional_email: The receive_promotional_email of this PeoplePatch.  # noqa: E501
        :type receive_promotional_email: bool
        """
        self.swagger_types = {
            'email': str,
            'name': str,
            'preferences': Preferences,
            'receive_promotional_email': bool
        }

        self.attribute_map = {
            'email': 'email',
            'name': 'name',
            'preferences': 'preferences',
            'receive_promotional_email': 'receive_promotional_email'
        }
        self._email = email
        self._name = name
        self._preferences = preferences
        self._receive_promotional_email = receive_promotional_email

    @classmethod
    def from_dict(cls, dikt) -> 'PeoplePatch':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The people_patch of this PeoplePatch.  # noqa: E501
        :rtype: PeoplePatch
        """
        return util.deserialize_model(dikt, cls)

    @property
    def email(self) -> str:
        """Gets the email of this PeoplePatch.


        :return: The email of this PeoplePatch.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email: str):
        """Sets the email of this PeoplePatch.


        :param email: The email of this PeoplePatch.
        :type email: str
        """

        self._email = email

    @property
    def name(self) -> str:
        """Gets the name of this PeoplePatch.


        :return: The name of this PeoplePatch.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this PeoplePatch.


        :param name: The name of this PeoplePatch.
        :type name: str
        """

        self._name = name

    @property
    def preferences(self) -> Preferences:
        """Gets the preferences of this PeoplePatch.


        :return: The preferences of this PeoplePatch.
        :rtype: Preferences
        """
        return self._preferences

    @preferences.setter
    def preferences(self, preferences: Preferences):
        """Sets the preferences of this PeoplePatch.


        :param preferences: The preferences of this PeoplePatch.
        :type preferences: Preferences
        """

        self._preferences = preferences

    @property
    def receive_promotional_email(self) -> bool:
        """Gets the receive_promotional_email of this PeoplePatch.


        :return: The receive_promotional_email of this PeoplePatch.
        :rtype: bool
        """
        return self._receive_promotional_email

    @receive_promotional_email.setter
    def receive_promotional_email(self, receive_promotional_email: bool):
        """Sets the receive_promotional_email of this PeoplePatch.


        :param receive_promotional_email: The receive_promotional_email of this PeoplePatch.
        :type receive_promotional_email: bool
        """

        self._receive_promotional_email = receive_promotional_email

# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class JourneyTrackerPeopleOne(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, active: bool=None, affiliation: str=None, deactivated_date: datetime=None, email_address: str=None, fabric_last_seen: datetime=None, fabric_roles: List[str]=None, fabric_uuid: str=None, name: str=None):  # noqa: E501
        """JourneyTrackerPeopleOne - a model defined in Swagger

        :param active: The active of this JourneyTrackerPeopleOne.  # noqa: E501
        :type active: bool
        :param affiliation: The affiliation of this JourneyTrackerPeopleOne.  # noqa: E501
        :type affiliation: str
        :param deactivated_date: The deactivated_date of this JourneyTrackerPeopleOne.  # noqa: E501
        :type deactivated_date: datetime
        :param email_address: The email_address of this JourneyTrackerPeopleOne.  # noqa: E501
        :type email_address: str
        :param fabric_last_seen: The fabric_last_seen of this JourneyTrackerPeopleOne.  # noqa: E501
        :type fabric_last_seen: datetime
        :param fabric_roles: The fabric_roles of this JourneyTrackerPeopleOne.  # noqa: E501
        :type fabric_roles: List[str]
        :param fabric_uuid: The fabric_uuid of this JourneyTrackerPeopleOne.  # noqa: E501
        :type fabric_uuid: str
        :param name: The name of this JourneyTrackerPeopleOne.  # noqa: E501
        :type name: str
        """
        self.swagger_types = {
            'active': bool,
            'affiliation': str,
            'deactivated_date': datetime,
            'email_address': str,
            'fabric_last_seen': datetime,
            'fabric_roles': List[str],
            'fabric_uuid': str,
            'name': str
        }

        self.attribute_map = {
            'active': 'active',
            'affiliation': 'affiliation',
            'deactivated_date': 'deactivated_date',
            'email_address': 'email_address',
            'fabric_last_seen': 'fabric_last_seen',
            'fabric_roles': 'fabric_roles',
            'fabric_uuid': 'fabric_uuid',
            'name': 'name'
        }
        self._active = active
        self._affiliation = affiliation
        self._deactivated_date = deactivated_date
        self._email_address = email_address
        self._fabric_last_seen = fabric_last_seen
        self._fabric_roles = fabric_roles
        self._fabric_uuid = fabric_uuid
        self._name = name

    @classmethod
    def from_dict(cls, dikt) -> 'JourneyTrackerPeopleOne':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The journey_tracker_people_one of this JourneyTrackerPeopleOne.  # noqa: E501
        :rtype: JourneyTrackerPeopleOne
        """
        return util.deserialize_model(dikt, cls)

    @property
    def active(self) -> bool:
        """Gets the active of this JourneyTrackerPeopleOne.


        :return: The active of this JourneyTrackerPeopleOne.
        :rtype: bool
        """
        return self._active

    @active.setter
    def active(self, active: bool):
        """Sets the active of this JourneyTrackerPeopleOne.


        :param active: The active of this JourneyTrackerPeopleOne.
        :type active: bool
        """

        self._active = active

    @property
    def affiliation(self) -> str:
        """Gets the affiliation of this JourneyTrackerPeopleOne.


        :return: The affiliation of this JourneyTrackerPeopleOne.
        :rtype: str
        """
        return self._affiliation

    @affiliation.setter
    def affiliation(self, affiliation: str):
        """Sets the affiliation of this JourneyTrackerPeopleOne.


        :param affiliation: The affiliation of this JourneyTrackerPeopleOne.
        :type affiliation: str
        """

        self._affiliation = affiliation

    @property
    def deactivated_date(self) -> datetime:
        """Gets the deactivated_date of this JourneyTrackerPeopleOne.


        :return: The deactivated_date of this JourneyTrackerPeopleOne.
        :rtype: datetime
        """
        return self._deactivated_date

    @deactivated_date.setter
    def deactivated_date(self, deactivated_date: datetime):
        """Sets the deactivated_date of this JourneyTrackerPeopleOne.


        :param deactivated_date: The deactivated_date of this JourneyTrackerPeopleOne.
        :type deactivated_date: datetime
        """

        self._deactivated_date = deactivated_date

    @property
    def email_address(self) -> str:
        """Gets the email_address of this JourneyTrackerPeopleOne.


        :return: The email_address of this JourneyTrackerPeopleOne.
        :rtype: str
        """
        return self._email_address

    @email_address.setter
    def email_address(self, email_address: str):
        """Sets the email_address of this JourneyTrackerPeopleOne.


        :param email_address: The email_address of this JourneyTrackerPeopleOne.
        :type email_address: str
        """

        self._email_address = email_address

    @property
    def fabric_last_seen(self) -> datetime:
        """Gets the fabric_last_seen of this JourneyTrackerPeopleOne.


        :return: The fabric_last_seen of this JourneyTrackerPeopleOne.
        :rtype: datetime
        """
        return self._fabric_last_seen

    @fabric_last_seen.setter
    def fabric_last_seen(self, fabric_last_seen: datetime):
        """Sets the fabric_last_seen of this JourneyTrackerPeopleOne.


        :param fabric_last_seen: The fabric_last_seen of this JourneyTrackerPeopleOne.
        :type fabric_last_seen: datetime
        """

        self._fabric_last_seen = fabric_last_seen

    @property
    def fabric_roles(self) -> List[str]:
        """Gets the fabric_roles of this JourneyTrackerPeopleOne.


        :return: The fabric_roles of this JourneyTrackerPeopleOne.
        :rtype: List[str]
        """
        return self._fabric_roles

    @fabric_roles.setter
    def fabric_roles(self, fabric_roles: List[str]):
        """Sets the fabric_roles of this JourneyTrackerPeopleOne.


        :param fabric_roles: The fabric_roles of this JourneyTrackerPeopleOne.
        :type fabric_roles: List[str]
        """

        self._fabric_roles = fabric_roles

    @property
    def fabric_uuid(self) -> str:
        """Gets the fabric_uuid of this JourneyTrackerPeopleOne.


        :return: The fabric_uuid of this JourneyTrackerPeopleOne.
        :rtype: str
        """
        return self._fabric_uuid

    @fabric_uuid.setter
    def fabric_uuid(self, fabric_uuid: str):
        """Sets the fabric_uuid of this JourneyTrackerPeopleOne.


        :param fabric_uuid: The fabric_uuid of this JourneyTrackerPeopleOne.
        :type fabric_uuid: str
        """

        self._fabric_uuid = fabric_uuid

    @property
    def name(self) -> str:
        """Gets the name of this JourneyTrackerPeopleOne.


        :return: The name of this JourneyTrackerPeopleOne.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this JourneyTrackerPeopleOne.


        :param name: The name of this JourneyTrackerPeopleOne.
        :type name: str
        """

        self._name = name
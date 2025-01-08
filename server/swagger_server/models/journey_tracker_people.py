# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.journey_tracker_people_one import JourneyTrackerPeopleOne  # noqa: F401,E501
from swagger_server.models.status200_ok_single import Status200OkSingle  # noqa: F401,E501
from swagger_server import util


class JourneyTrackerPeople(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, results: List[JourneyTrackerPeopleOne]=None, size: int=1, status: int=200, type: str=None):  # noqa: E501
        """JourneyTrackerPeople - a model defined in Swagger

        :param results: The results of this JourneyTrackerPeople.  # noqa: E501
        :type results: List[JourneyTrackerPeopleOne]
        :param size: The size of this JourneyTrackerPeople.  # noqa: E501
        :type size: int
        :param status: The status of this JourneyTrackerPeople.  # noqa: E501
        :type status: int
        :param type: The type of this JourneyTrackerPeople.  # noqa: E501
        :type type: str
        """
        self.swagger_types = {
            'results': List[JourneyTrackerPeopleOne],
            'size': int,
            'status': int,
            'type': str
        }

        self.attribute_map = {
            'results': 'results',
            'size': 'size',
            'status': 'status',
            'type': 'type'
        }
        self._results = results
        self._size = size
        self._status = status
        self._type = type

    @classmethod
    def from_dict(cls, dikt) -> 'JourneyTrackerPeople':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The journey_tracker_people of this JourneyTrackerPeople.  # noqa: E501
        :rtype: JourneyTrackerPeople
        """
        return util.deserialize_model(dikt, cls)

    @property
    def results(self) -> List[JourneyTrackerPeopleOne]:
        """Gets the results of this JourneyTrackerPeople.


        :return: The results of this JourneyTrackerPeople.
        :rtype: List[JourneyTrackerPeopleOne]
        """
        return self._results

    @results.setter
    def results(self, results: List[JourneyTrackerPeopleOne]):
        """Sets the results of this JourneyTrackerPeople.


        :param results: The results of this JourneyTrackerPeople.
        :type results: List[JourneyTrackerPeopleOne]
        """

        self._results = results

    @property
    def size(self) -> int:
        """Gets the size of this JourneyTrackerPeople.


        :return: The size of this JourneyTrackerPeople.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size: int):
        """Sets the size of this JourneyTrackerPeople.


        :param size: The size of this JourneyTrackerPeople.
        :type size: int
        """

        self._size = size

    @property
    def status(self) -> int:
        """Gets the status of this JourneyTrackerPeople.


        :return: The status of this JourneyTrackerPeople.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status: int):
        """Sets the status of this JourneyTrackerPeople.


        :param status: The status of this JourneyTrackerPeople.
        :type status: int
        """

        self._status = status

    @property
    def type(self) -> str:
        """Gets the type of this JourneyTrackerPeople.


        :return: The type of this JourneyTrackerPeople.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this JourneyTrackerPeople.


        :param type: The type of this JourneyTrackerPeople.
        :type type: str
        """

        self._type = type

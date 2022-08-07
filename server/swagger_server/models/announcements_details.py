# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.announcement_one import AnnouncementOne  # noqa: F401,E501
from swagger_server.models.status200_ok_single import Status200OkSingle  # noqa: F401,E501
from swagger_server import util


class AnnouncementsDetails(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, results: List[AnnouncementOne]=None, size: int=1, status: int=200, type: str=None):  # noqa: E501
        """AnnouncementsDetails - a model defined in Swagger

        :param results: The results of this AnnouncementsDetails.  # noqa: E501
        :type results: List[AnnouncementOne]
        :param size: The size of this AnnouncementsDetails.  # noqa: E501
        :type size: int
        :param status: The status of this AnnouncementsDetails.  # noqa: E501
        :type status: int
        :param type: The type of this AnnouncementsDetails.  # noqa: E501
        :type type: str
        """
        self.swagger_types = {
            'results': List[AnnouncementOne],
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
    def from_dict(cls, dikt) -> 'AnnouncementsDetails':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The announcements_details of this AnnouncementsDetails.  # noqa: E501
        :rtype: AnnouncementsDetails
        """
        return util.deserialize_model(dikt, cls)

    @property
    def results(self) -> List[AnnouncementOne]:
        """Gets the results of this AnnouncementsDetails.


        :return: The results of this AnnouncementsDetails.
        :rtype: List[AnnouncementOne]
        """
        return self._results

    @results.setter
    def results(self, results: List[AnnouncementOne]):
        """Sets the results of this AnnouncementsDetails.


        :param results: The results of this AnnouncementsDetails.
        :type results: List[AnnouncementOne]
        """

        self._results = results

    @property
    def size(self) -> int:
        """Gets the size of this AnnouncementsDetails.


        :return: The size of this AnnouncementsDetails.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size: int):
        """Sets the size of this AnnouncementsDetails.


        :param size: The size of this AnnouncementsDetails.
        :type size: int
        """

        self._size = size

    @property
    def status(self) -> int:
        """Gets the status of this AnnouncementsDetails.


        :return: The status of this AnnouncementsDetails.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status: int):
        """Sets the status of this AnnouncementsDetails.


        :param status: The status of this AnnouncementsDetails.
        :type status: int
        """

        self._status = status

    @property
    def type(self) -> str:
        """Gets the type of this AnnouncementsDetails.


        :return: The type of this AnnouncementsDetails.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this AnnouncementsDetails.


        :param type: The type of this AnnouncementsDetails.
        :type type: str
        """

        self._type = type

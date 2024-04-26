# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.service_auth_one import ServiceAuthOne  # noqa: F401,E501
from swagger_server.models.status200_ok_single import Status200OkSingle  # noqa: F401,E501
from swagger_server import util


class ServiceAuthDetails(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, results: List[ServiceAuthOne]=None, size: int=1, status: int=200, type: str=None):  # noqa: E501
        """ServiceAuthDetails - a model defined in Swagger

        :param results: The results of this ServiceAuthDetails.  # noqa: E501
        :type results: List[ServiceAuthOne]
        :param size: The size of this ServiceAuthDetails.  # noqa: E501
        :type size: int
        :param status: The status of this ServiceAuthDetails.  # noqa: E501
        :type status: int
        :param type: The type of this ServiceAuthDetails.  # noqa: E501
        :type type: str
        """
        self.swagger_types = {
            'results': List[ServiceAuthOne],
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
    def from_dict(cls, dikt) -> 'ServiceAuthDetails':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The service_auth_details of this ServiceAuthDetails.  # noqa: E501
        :rtype: ServiceAuthDetails
        """
        return util.deserialize_model(dikt, cls)

    @property
    def results(self) -> List[ServiceAuthOne]:
        """Gets the results of this ServiceAuthDetails.


        :return: The results of this ServiceAuthDetails.
        :rtype: List[ServiceAuthOne]
        """
        return self._results

    @results.setter
    def results(self, results: List[ServiceAuthOne]):
        """Sets the results of this ServiceAuthDetails.


        :param results: The results of this ServiceAuthDetails.
        :type results: List[ServiceAuthOne]
        """

        self._results = results

    @property
    def size(self) -> int:
        """Gets the size of this ServiceAuthDetails.


        :return: The size of this ServiceAuthDetails.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size: int):
        """Sets the size of this ServiceAuthDetails.


        :param size: The size of this ServiceAuthDetails.
        :type size: int
        """

        self._size = size

    @property
    def status(self) -> int:
        """Gets the status of this ServiceAuthDetails.


        :return: The status of this ServiceAuthDetails.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status: int):
        """Sets the status of this ServiceAuthDetails.


        :param status: The status of this ServiceAuthDetails.
        :type status: int
        """

        self._status = status

    @property
    def type(self) -> str:
        """Gets the type of this ServiceAuthDetails.


        :return: The type of this ServiceAuthDetails.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this ServiceAuthDetails.


        :param type: The type of this ServiceAuthDetails.
        :type type: str
        """

        self._type = type
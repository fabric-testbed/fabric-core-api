# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.status200_ok_single import Status200OkSingle  # noqa: F401,E501
from swagger_server import util


class CoreApiMetrics(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, results: List[object]=None, size: int=1, status: int=200, type: str=None):  # noqa: E501
        """CoreApiMetrics - a model defined in Swagger

        :param results: The results of this CoreApiMetrics.  # noqa: E501
        :type results: List[object]
        :param size: The size of this CoreApiMetrics.  # noqa: E501
        :type size: int
        :param status: The status of this CoreApiMetrics.  # noqa: E501
        :type status: int
        :param type: The type of this CoreApiMetrics.  # noqa: E501
        :type type: str
        """
        self.swagger_types = {
            'results': List[object],
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
    def from_dict(cls, dikt) -> 'CoreApiMetrics':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The core_api_metrics of this CoreApiMetrics.  # noqa: E501
        :rtype: CoreApiMetrics
        """
        return util.deserialize_model(dikt, cls)

    @property
    def results(self) -> List[object]:
        """Gets the results of this CoreApiMetrics.


        :return: The results of this CoreApiMetrics.
        :rtype: List[object]
        """
        return self._results

    @results.setter
    def results(self, results: List[object]):
        """Sets the results of this CoreApiMetrics.


        :param results: The results of this CoreApiMetrics.
        :type results: List[object]
        """

        self._results = results

    @property
    def size(self) -> int:
        """Gets the size of this CoreApiMetrics.


        :return: The size of this CoreApiMetrics.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size: int):
        """Sets the size of this CoreApiMetrics.


        :param size: The size of this CoreApiMetrics.
        :type size: int
        """

        self._size = size

    @property
    def status(self) -> int:
        """Gets the status of this CoreApiMetrics.


        :return: The status of this CoreApiMetrics.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status: int):
        """Sets the status of this CoreApiMetrics.


        :param status: The status of this CoreApiMetrics.
        :type status: int
        """

        self._status = status

    @property
    def type(self) -> str:
        """Gets the type of this CoreApiMetrics.


        :return: The type of this CoreApiMetrics.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this CoreApiMetrics.


        :param type: The type of this CoreApiMetrics.
        :type type: str
        """

        self._type = type
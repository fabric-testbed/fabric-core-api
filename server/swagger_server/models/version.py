# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.status200_ok_single import Status200OkSingle  # noqa: F401,E501
from swagger_server.models.version_results import VersionResults  # noqa: F401,E501
from swagger_server import util


class Version(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, results: List[VersionResults]=None, size: int=1, status: int=200, type: str=None):  # noqa: E501
        """Version - a model defined in Swagger

        :param results: The results of this Version.  # noqa: E501
        :type results: List[VersionResults]
        :param size: The size of this Version.  # noqa: E501
        :type size: int
        :param status: The status of this Version.  # noqa: E501
        :type status: int
        :param type: The type of this Version.  # noqa: E501
        :type type: str
        """
        self.swagger_types = {
            'results': List[VersionResults],
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
    def from_dict(cls, dikt) -> 'Version':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The version of this Version.  # noqa: E501
        :rtype: Version
        """
        return util.deserialize_model(dikt, cls)

    @property
    def results(self) -> List[VersionResults]:
        """Gets the results of this Version.


        :return: The results of this Version.
        :rtype: List[VersionResults]
        """
        return self._results

    @results.setter
    def results(self, results: List[VersionResults]):
        """Sets the results of this Version.


        :param results: The results of this Version.
        :type results: List[VersionResults]
        """

        self._results = results

    @property
    def size(self) -> int:
        """Gets the size of this Version.


        :return: The size of this Version.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size: int):
        """Sets the size of this Version.


        :param size: The size of this Version.
        :type size: int
        """

        self._size = size

    @property
    def status(self) -> int:
        """Gets the status of this Version.


        :return: The status of this Version.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status: int):
        """Sets the status of this Version.


        :param status: The status of this Version.
        :type status: int
        """

        self._status = status

    @property
    def type(self) -> str:
        """Gets the type of this Version.


        :return: The type of this Version.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this Version.


        :param type: The type of this Version.
        :type type: str
        """

        self._type = type

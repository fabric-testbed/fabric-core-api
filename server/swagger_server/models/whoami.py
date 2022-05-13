# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.status200_ok_single import Status200OkSingle  # noqa: F401,E501
from swagger_server.models.whoami_results import WhoamiResults  # noqa: F401,E501
from swagger_server import util


class Whoami(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, results: List[WhoamiResults]=None, size: int=1, status: int=200, type: str=None):  # noqa: E501
        """Whoami - a model defined in Swagger

        :param results: The results of this Whoami.  # noqa: E501
        :type results: List[WhoamiResults]
        :param size: The size of this Whoami.  # noqa: E501
        :type size: int
        :param status: The status of this Whoami.  # noqa: E501
        :type status: int
        :param type: The type of this Whoami.  # noqa: E501
        :type type: str
        """
        self.swagger_types = {
            'results': List[WhoamiResults],
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
    def from_dict(cls, dikt) -> 'Whoami':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The whoami of this Whoami.  # noqa: E501
        :rtype: Whoami
        """
        return util.deserialize_model(dikt, cls)

    @property
    def results(self) -> List[WhoamiResults]:
        """Gets the results of this Whoami.


        :return: The results of this Whoami.
        :rtype: List[WhoamiResults]
        """
        return self._results

    @results.setter
    def results(self, results: List[WhoamiResults]):
        """Sets the results of this Whoami.


        :param results: The results of this Whoami.
        :type results: List[WhoamiResults]
        """

        self._results = results

    @property
    def size(self) -> int:
        """Gets the size of this Whoami.


        :return: The size of this Whoami.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size: int):
        """Sets the size of this Whoami.


        :param size: The size of this Whoami.
        :type size: int
        """

        self._size = size

    @property
    def status(self) -> int:
        """Gets the status of this Whoami.


        :return: The status of this Whoami.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status: int):
        """Sets the status of this Whoami.


        :param status: The status of this Whoami.
        :type status: int
        """

        self._status = status

    @property
    def type(self) -> str:
        """Gets the type of this Whoami.


        :return: The type of this Whoami.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this Whoami.


        :param type: The type of this Whoami.
        :type type: str
        """

        self._type = type

# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.status200_ok_paginated import Status200OkPaginated  # noqa: F401,E501
from swagger_server.models.status200_ok_paginated_links import Status200OkPaginatedLinks  # noqa: F401,E501
from swagger_server.models.storage_one import StorageOne  # noqa: F401,E501
from swagger_server import util


class StorageMany(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, results: List[StorageOne]=None, limit: int=None, links: Status200OkPaginatedLinks=None, offset: int=None, size: int=None, status: int=200, total: int=None, type: str=None):  # noqa: E501
        """StorageMany - a model defined in Swagger

        :param results: The results of this StorageMany.  # noqa: E501
        :type results: List[StorageOne]
        :param limit: The limit of this StorageMany.  # noqa: E501
        :type limit: int
        :param links: The links of this StorageMany.  # noqa: E501
        :type links: Status200OkPaginatedLinks
        :param offset: The offset of this StorageMany.  # noqa: E501
        :type offset: int
        :param size: The size of this StorageMany.  # noqa: E501
        :type size: int
        :param status: The status of this StorageMany.  # noqa: E501
        :type status: int
        :param total: The total of this StorageMany.  # noqa: E501
        :type total: int
        :param type: The type of this StorageMany.  # noqa: E501
        :type type: str
        """
        self.swagger_types = {
            'results': List[StorageOne],
            'limit': int,
            'links': Status200OkPaginatedLinks,
            'offset': int,
            'size': int,
            'status': int,
            'total': int,
            'type': str
        }

        self.attribute_map = {
            'results': 'results',
            'limit': 'limit',
            'links': 'links',
            'offset': 'offset',
            'size': 'size',
            'status': 'status',
            'total': 'total',
            'type': 'type'
        }
        self._results = results
        self._limit = limit
        self._links = links
        self._offset = offset
        self._size = size
        self._status = status
        self._total = total
        self._type = type

    @classmethod
    def from_dict(cls, dikt) -> 'StorageMany':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The storage_many of this StorageMany.  # noqa: E501
        :rtype: StorageMany
        """
        return util.deserialize_model(dikt, cls)

    @property
    def results(self) -> List[StorageOne]:
        """Gets the results of this StorageMany.


        :return: The results of this StorageMany.
        :rtype: List[StorageOne]
        """
        return self._results

    @results.setter
    def results(self, results: List[StorageOne]):
        """Sets the results of this StorageMany.


        :param results: The results of this StorageMany.
        :type results: List[StorageOne]
        """

        self._results = results

    @property
    def limit(self) -> int:
        """Gets the limit of this StorageMany.


        :return: The limit of this StorageMany.
        :rtype: int
        """
        return self._limit

    @limit.setter
    def limit(self, limit: int):
        """Sets the limit of this StorageMany.


        :param limit: The limit of this StorageMany.
        :type limit: int
        """

        self._limit = limit

    @property
    def links(self) -> Status200OkPaginatedLinks:
        """Gets the links of this StorageMany.


        :return: The links of this StorageMany.
        :rtype: Status200OkPaginatedLinks
        """
        return self._links

    @links.setter
    def links(self, links: Status200OkPaginatedLinks):
        """Sets the links of this StorageMany.


        :param links: The links of this StorageMany.
        :type links: Status200OkPaginatedLinks
        """

        self._links = links

    @property
    def offset(self) -> int:
        """Gets the offset of this StorageMany.


        :return: The offset of this StorageMany.
        :rtype: int
        """
        return self._offset

    @offset.setter
    def offset(self, offset: int):
        """Sets the offset of this StorageMany.


        :param offset: The offset of this StorageMany.
        :type offset: int
        """

        self._offset = offset

    @property
    def size(self) -> int:
        """Gets the size of this StorageMany.


        :return: The size of this StorageMany.
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size: int):
        """Sets the size of this StorageMany.


        :param size: The size of this StorageMany.
        :type size: int
        """

        self._size = size

    @property
    def status(self) -> int:
        """Gets the status of this StorageMany.


        :return: The status of this StorageMany.
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status: int):
        """Sets the status of this StorageMany.


        :param status: The status of this StorageMany.
        :type status: int
        """

        self._status = status

    @property
    def total(self) -> int:
        """Gets the total of this StorageMany.


        :return: The total of this StorageMany.
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total: int):
        """Sets the total of this StorageMany.


        :param total: The total of this StorageMany.
        :type total: int
        """

        self._total = total

    @property
    def type(self) -> str:
        """Gets the type of this StorageMany.


        :return: The type of this StorageMany.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this StorageMany.


        :param type: The type of this StorageMany.
        :type type: str
        """

        self._type = type

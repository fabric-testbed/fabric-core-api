# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class StoragePatch(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, active: bool=None, expires_on: str=None, site_list: List[str]=None, volume_name: str=None, volume_size_gb: int=None):  # noqa: E501
        """StoragePatch - a model defined in Swagger

        :param active: The active of this StoragePatch.  # noqa: E501
        :type active: bool
        :param expires_on: The expires_on of this StoragePatch.  # noqa: E501
        :type expires_on: str
        :param site_list: The site_list of this StoragePatch.  # noqa: E501
        :type site_list: List[str]
        :param volume_name: The volume_name of this StoragePatch.  # noqa: E501
        :type volume_name: str
        :param volume_size_gb: The volume_size_gb of this StoragePatch.  # noqa: E501
        :type volume_size_gb: int
        """
        self.swagger_types = {
            'active': bool,
            'expires_on': str,
            'site_list': List[str],
            'volume_name': str,
            'volume_size_gb': int
        }

        self.attribute_map = {
            'active': 'active',
            'expires_on': 'expires_on',
            'site_list': 'site_list',
            'volume_name': 'volume_name',
            'volume_size_gb': 'volume_size_gb'
        }
        self._active = active
        self._expires_on = expires_on
        self._site_list = site_list
        self._volume_name = volume_name
        self._volume_size_gb = volume_size_gb

    @classmethod
    def from_dict(cls, dikt) -> 'StoragePatch':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The storage_patch of this StoragePatch.  # noqa: E501
        :rtype: StoragePatch
        """
        return util.deserialize_model(dikt, cls)

    @property
    def active(self) -> bool:
        """Gets the active of this StoragePatch.


        :return: The active of this StoragePatch.
        :rtype: bool
        """
        return self._active

    @active.setter
    def active(self, active: bool):
        """Sets the active of this StoragePatch.


        :param active: The active of this StoragePatch.
        :type active: bool
        """

        self._active = active

    @property
    def expires_on(self) -> str:
        """Gets the expires_on of this StoragePatch.


        :return: The expires_on of this StoragePatch.
        :rtype: str
        """
        return self._expires_on

    @expires_on.setter
    def expires_on(self, expires_on: str):
        """Sets the expires_on of this StoragePatch.


        :param expires_on: The expires_on of this StoragePatch.
        :type expires_on: str
        """

        self._expires_on = expires_on

    @property
    def site_list(self) -> List[str]:
        """Gets the site_list of this StoragePatch.


        :return: The site_list of this StoragePatch.
        :rtype: List[str]
        """
        return self._site_list

    @site_list.setter
    def site_list(self, site_list: List[str]):
        """Sets the site_list of this StoragePatch.


        :param site_list: The site_list of this StoragePatch.
        :type site_list: List[str]
        """

        self._site_list = site_list

    @property
    def volume_name(self) -> str:
        """Gets the volume_name of this StoragePatch.


        :return: The volume_name of this StoragePatch.
        :rtype: str
        """
        return self._volume_name

    @volume_name.setter
    def volume_name(self, volume_name: str):
        """Sets the volume_name of this StoragePatch.


        :param volume_name: The volume_name of this StoragePatch.
        :type volume_name: str
        """

        self._volume_name = volume_name

    @property
    def volume_size_gb(self) -> int:
        """Gets the volume_size_gb of this StoragePatch.


        :return: The volume_size_gb of this StoragePatch.
        :rtype: int
        """
        return self._volume_size_gb

    @volume_size_gb.setter
    def volume_size_gb(self, volume_size_gb: int):
        """Sets the volume_size_gb of this StoragePatch.


        :param volume_size_gb: The volume_size_gb of this StoragePatch.
        :type volume_size_gb: int
        """

        self._volume_size_gb = volume_size_gb

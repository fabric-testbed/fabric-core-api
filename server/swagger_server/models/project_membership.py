# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ProjectMembership(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, is_creator: bool=False, is_member: bool=False, is_owner: bool=False, is_token_holder: bool=False):  # noqa: E501
        """ProjectMembership - a model defined in Swagger

        :param is_creator: The is_creator of this ProjectMembership.  # noqa: E501
        :type is_creator: bool
        :param is_member: The is_member of this ProjectMembership.  # noqa: E501
        :type is_member: bool
        :param is_owner: The is_owner of this ProjectMembership.  # noqa: E501
        :type is_owner: bool
        :param is_token_holder: The is_token_holder of this ProjectMembership.  # noqa: E501
        :type is_token_holder: bool
        """
        self.swagger_types = {
            'is_creator': bool,
            'is_member': bool,
            'is_owner': bool,
            'is_token_holder': bool
        }

        self.attribute_map = {
            'is_creator': 'is_creator',
            'is_member': 'is_member',
            'is_owner': 'is_owner',
            'is_token_holder': 'is_token_holder'
        }
        self._is_creator = is_creator
        self._is_member = is_member
        self._is_owner = is_owner
        self._is_token_holder = is_token_holder

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectMembership':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The project_membership of this ProjectMembership.  # noqa: E501
        :rtype: ProjectMembership
        """
        return util.deserialize_model(dikt, cls)

    @property
    def is_creator(self) -> bool:
        """Gets the is_creator of this ProjectMembership.


        :return: The is_creator of this ProjectMembership.
        :rtype: bool
        """
        return self._is_creator

    @is_creator.setter
    def is_creator(self, is_creator: bool):
        """Sets the is_creator of this ProjectMembership.


        :param is_creator: The is_creator of this ProjectMembership.
        :type is_creator: bool
        """

        self._is_creator = is_creator

    @property
    def is_member(self) -> bool:
        """Gets the is_member of this ProjectMembership.


        :return: The is_member of this ProjectMembership.
        :rtype: bool
        """
        return self._is_member

    @is_member.setter
    def is_member(self, is_member: bool):
        """Sets the is_member of this ProjectMembership.


        :param is_member: The is_member of this ProjectMembership.
        :type is_member: bool
        """

        self._is_member = is_member

    @property
    def is_owner(self) -> bool:
        """Gets the is_owner of this ProjectMembership.


        :return: The is_owner of this ProjectMembership.
        :rtype: bool
        """
        return self._is_owner

    @is_owner.setter
    def is_owner(self, is_owner: bool):
        """Sets the is_owner of this ProjectMembership.


        :param is_owner: The is_owner of this ProjectMembership.
        :type is_owner: bool
        """

        self._is_owner = is_owner

    @property
    def is_token_holder(self) -> bool:
        """Gets the is_token_holder of this ProjectMembership.


        :return: The is_token_holder of this ProjectMembership.
        :rtype: bool
        """
        return self._is_token_holder

    @is_token_holder.setter
    def is_token_holder(self, is_token_holder: bool):
        """Sets the is_token_holder of this ProjectMembership.


        :param is_token_holder: The is_token_holder of this ProjectMembership.
        :type is_token_holder: bool
        """

        self._is_token_holder = is_token_holder

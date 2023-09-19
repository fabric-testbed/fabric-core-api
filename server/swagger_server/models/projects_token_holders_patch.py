# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ProjectsTokenHoldersPatch(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, token_holders: List[str]=None):  # noqa: E501
        """ProjectsTokenHoldersPatch - a model defined in Swagger

        :param token_holders: The token_holders of this ProjectsTokenHoldersPatch.  # noqa: E501
        :type token_holders: List[str]
        """
        self.swagger_types = {
            'token_holders': List[str]
        }

        self.attribute_map = {
            'token_holders': 'token_holders'
        }
        self._token_holders = token_holders

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectsTokenHoldersPatch':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The projects_token_holders_patch of this ProjectsTokenHoldersPatch.  # noqa: E501
        :rtype: ProjectsTokenHoldersPatch
        """
        return util.deserialize_model(dikt, cls)

    @property
    def token_holders(self) -> List[str]:
        """Gets the token_holders of this ProjectsTokenHoldersPatch.


        :return: The token_holders of this ProjectsTokenHoldersPatch.
        :rtype: List[str]
        """
        return self._token_holders

    @token_holders.setter
    def token_holders(self, token_holders: List[str]):
        """Sets the token_holders of this ProjectsTokenHoldersPatch.


        :param token_holders: The token_holders of this ProjectsTokenHoldersPatch.
        :type token_holders: List[str]
        """

        self._token_holders = token_holders
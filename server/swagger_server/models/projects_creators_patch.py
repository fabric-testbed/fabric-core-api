# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ProjectsCreatorsPatch(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, project_creators: List[str]=None):  # noqa: E501
        """ProjectsCreatorsPatch - a model defined in Swagger

        :param project_creators: The project_creators of this ProjectsCreatorsPatch.  # noqa: E501
        :type project_creators: List[str]
        """
        self.swagger_types = {
            'project_creators': List[str]
        }

        self.attribute_map = {
            'project_creators': 'project_creators'
        }
        self._project_creators = project_creators

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectsCreatorsPatch':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The projects_creators_patch of this ProjectsCreatorsPatch.  # noqa: E501
        :rtype: ProjectsCreatorsPatch
        """
        return util.deserialize_model(dikt, cls)

    @property
    def project_creators(self) -> List[str]:
        """Gets the project_creators of this ProjectsCreatorsPatch.


        :return: The project_creators of this ProjectsCreatorsPatch.
        :rtype: List[str]
        """
        return self._project_creators

    @project_creators.setter
    def project_creators(self, project_creators: List[str]):
        """Sets the project_creators of this ProjectsCreatorsPatch.


        :param project_creators: The project_creators of this ProjectsCreatorsPatch.
        :type project_creators: List[str]
        """

        self._project_creators = project_creators
# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ProjectsOwnersPatch(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, project_owners: List[str]=None):  # noqa: E501
        """ProjectsOwnersPatch - a model defined in Swagger

        :param project_owners: The project_owners of this ProjectsOwnersPatch.  # noqa: E501
        :type project_owners: List[str]
        """
        self.swagger_types = {
            'project_owners': List[str]
        }

        self.attribute_map = {
            'project_owners': 'project_owners'
        }
        self._project_owners = project_owners

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectsOwnersPatch':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The projects_owners_patch of this ProjectsOwnersPatch.  # noqa: E501
        :rtype: ProjectsOwnersPatch
        """
        return util.deserialize_model(dikt, cls)

    @property
    def project_owners(self) -> List[str]:
        """Gets the project_owners of this ProjectsOwnersPatch.


        :return: The project_owners of this ProjectsOwnersPatch.
        :rtype: List[str]
        """
        return self._project_owners

    @project_owners.setter
    def project_owners(self, project_owners: List[str]):
        """Sets the project_owners of this ProjectsOwnersPatch.


        :param project_owners: The project_owners of this ProjectsOwnersPatch.
        :type project_owners: List[str]
        """

        self._project_owners = project_owners

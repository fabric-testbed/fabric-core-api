# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ProjectsTopicsPatch(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, topics: List[str]=None):  # noqa: E501
        """ProjectsTopicsPatch - a model defined in Swagger

        :param topics: The topics of this ProjectsTopicsPatch.  # noqa: E501
        :type topics: List[str]
        """
        self.swagger_types = {
            'topics': List[str]
        }

        self.attribute_map = {
            'topics': 'topics'
        }
        self._topics = topics

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectsTopicsPatch':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The projects_topics_patch of this ProjectsTopicsPatch.  # noqa: E501
        :rtype: ProjectsTopicsPatch
        """
        return util.deserialize_model(dikt, cls)

    @property
    def topics(self) -> List[str]:
        """Gets the topics of this ProjectsTopicsPatch.


        :return: The topics of this ProjectsTopicsPatch.
        :rtype: List[str]
        """
        return self._topics

    @topics.setter
    def topics(self, topics: List[str]):
        """Sets the topics of this ProjectsTopicsPatch.


        :param topics: The topics of this ProjectsTopicsPatch.
        :type topics: List[str]
        """

        self._topics = topics

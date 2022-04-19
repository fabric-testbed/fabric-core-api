# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.preferences import Preferences  # noqa: F401,E501
from swagger_server.models.profile_people_other_identities import ProfilePeopleOtherIdentities  # noqa: F401,E501
from swagger_server.models.profile_people_personal_pages import ProfilePeoplePersonalPages  # noqa: F401,E501
from swagger_server import util


class ProfilePeople(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, bio: str=None, cv: str=None, job: str=None, other_identities: List[ProfilePeopleOtherIdentities]=None, preferences: Preferences=None, personal_pages: List[ProfilePeoplePersonalPages]=None, pronouns: str=None, website: str=None):  # noqa: E501
        """ProfilePeople - a model defined in Swagger

        :param bio: The bio of this ProfilePeople.  # noqa: E501
        :type bio: str
        :param cv: The cv of this ProfilePeople.  # noqa: E501
        :type cv: str
        :param job: The job of this ProfilePeople.  # noqa: E501
        :type job: str
        :param other_identities: The other_identities of this ProfilePeople.  # noqa: E501
        :type other_identities: List[ProfilePeopleOtherIdentities]
        :param preferences: The preferences of this ProfilePeople.  # noqa: E501
        :type preferences: Preferences
        :param personal_pages: The personal_pages of this ProfilePeople.  # noqa: E501
        :type personal_pages: List[ProfilePeoplePersonalPages]
        :param pronouns: The pronouns of this ProfilePeople.  # noqa: E501
        :type pronouns: str
        :param website: The website of this ProfilePeople.  # noqa: E501
        :type website: str
        """
        self.swagger_types = {
            'bio': str,
            'cv': str,
            'job': str,
            'other_identities': List[ProfilePeopleOtherIdentities],
            'preferences': Preferences,
            'personal_pages': List[ProfilePeoplePersonalPages],
            'pronouns': str,
            'website': str
        }

        self.attribute_map = {
            'bio': 'bio',
            'cv': 'cv',
            'job': 'job',
            'other_identities': 'other_identities',
            'preferences': 'preferences',
            'personal_pages': 'personal_pages',
            'pronouns': 'pronouns',
            'website': 'website'
        }
        self._bio = bio
        self._cv = cv
        self._job = job
        self._other_identities = other_identities
        self._preferences = preferences
        self._personal_pages = personal_pages
        self._pronouns = pronouns
        self._website = website

    @classmethod
    def from_dict(cls, dikt) -> 'ProfilePeople':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The profile_people of this ProfilePeople.  # noqa: E501
        :rtype: ProfilePeople
        """
        return util.deserialize_model(dikt, cls)

    @property
    def bio(self) -> str:
        """Gets the bio of this ProfilePeople.


        :return: The bio of this ProfilePeople.
        :rtype: str
        """
        return self._bio

    @bio.setter
    def bio(self, bio: str):
        """Sets the bio of this ProfilePeople.


        :param bio: The bio of this ProfilePeople.
        :type bio: str
        """

        self._bio = bio

    @property
    def cv(self) -> str:
        """Gets the cv of this ProfilePeople.


        :return: The cv of this ProfilePeople.
        :rtype: str
        """
        return self._cv

    @cv.setter
    def cv(self, cv: str):
        """Sets the cv of this ProfilePeople.


        :param cv: The cv of this ProfilePeople.
        :type cv: str
        """

        self._cv = cv

    @property
    def job(self) -> str:
        """Gets the job of this ProfilePeople.


        :return: The job of this ProfilePeople.
        :rtype: str
        """
        return self._job

    @job.setter
    def job(self, job: str):
        """Sets the job of this ProfilePeople.


        :param job: The job of this ProfilePeople.
        :type job: str
        """

        self._job = job

    @property
    def other_identities(self) -> List[ProfilePeopleOtherIdentities]:
        """Gets the other_identities of this ProfilePeople.


        :return: The other_identities of this ProfilePeople.
        :rtype: List[ProfilePeopleOtherIdentities]
        """
        return self._other_identities

    @other_identities.setter
    def other_identities(self, other_identities: List[ProfilePeopleOtherIdentities]):
        """Sets the other_identities of this ProfilePeople.


        :param other_identities: The other_identities of this ProfilePeople.
        :type other_identities: List[ProfilePeopleOtherIdentities]
        """

        self._other_identities = other_identities

    @property
    def preferences(self) -> Preferences:
        """Gets the preferences of this ProfilePeople.


        :return: The preferences of this ProfilePeople.
        :rtype: Preferences
        """
        return self._preferences

    @preferences.setter
    def preferences(self, preferences: Preferences):
        """Sets the preferences of this ProfilePeople.


        :param preferences: The preferences of this ProfilePeople.
        :type preferences: Preferences
        """

        self._preferences = preferences

    @property
    def personal_pages(self) -> List[ProfilePeoplePersonalPages]:
        """Gets the personal_pages of this ProfilePeople.


        :return: The personal_pages of this ProfilePeople.
        :rtype: List[ProfilePeoplePersonalPages]
        """
        return self._personal_pages

    @personal_pages.setter
    def personal_pages(self, personal_pages: List[ProfilePeoplePersonalPages]):
        """Sets the personal_pages of this ProfilePeople.


        :param personal_pages: The personal_pages of this ProfilePeople.
        :type personal_pages: List[ProfilePeoplePersonalPages]
        """

        self._personal_pages = personal_pages

    @property
    def pronouns(self) -> str:
        """Gets the pronouns of this ProfilePeople.


        :return: The pronouns of this ProfilePeople.
        :rtype: str
        """
        return self._pronouns

    @pronouns.setter
    def pronouns(self, pronouns: str):
        """Sets the pronouns of this ProfilePeople.


        :param pronouns: The pronouns of this ProfilePeople.
        :type pronouns: str
        """

        self._pronouns = pronouns

    @property
    def website(self) -> str:
        """Gets the website of this ProfilePeople.


        :return: The website of this ProfilePeople.
        :rtype: str
        """
        return self._website

    @website.setter
    def website(self, website: str):
        """Sets the website of this ProfilePeople.


        :param website: The website of this ProfilePeople.
        :type website: str
        """

        self._website = website

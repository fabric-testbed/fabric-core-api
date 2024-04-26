# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ProjectsFundingPatchProjectFunding(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, agency: str=None, award_amount: str=None, award_number: str=None, directorate: str=None):  # noqa: E501
        """ProjectsFundingPatchProjectFunding - a model defined in Swagger

        :param agency: The agency of this ProjectsFundingPatchProjectFunding.  # noqa: E501
        :type agency: str
        :param award_amount: The award_amount of this ProjectsFundingPatchProjectFunding.  # noqa: E501
        :type award_amount: str
        :param award_number: The award_number of this ProjectsFundingPatchProjectFunding.  # noqa: E501
        :type award_number: str
        :param directorate: The directorate of this ProjectsFundingPatchProjectFunding.  # noqa: E501
        :type directorate: str
        """
        self.swagger_types = {
            'agency': str,
            'award_amount': str,
            'award_number': str,
            'directorate': str
        }

        self.attribute_map = {
            'agency': 'agency',
            'award_amount': 'award_amount',
            'award_number': 'award_number',
            'directorate': 'directorate'
        }
        self._agency = agency
        self._award_amount = award_amount
        self._award_number = award_number
        self._directorate = directorate

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectsFundingPatchProjectFunding':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The projects_funding_patch_project_funding of this ProjectsFundingPatchProjectFunding.  # noqa: E501
        :rtype: ProjectsFundingPatchProjectFunding
        """
        return util.deserialize_model(dikt, cls)

    @property
    def agency(self) -> str:
        """Gets the agency of this ProjectsFundingPatchProjectFunding.


        :return: The agency of this ProjectsFundingPatchProjectFunding.
        :rtype: str
        """
        return self._agency

    @agency.setter
    def agency(self, agency: str):
        """Sets the agency of this ProjectsFundingPatchProjectFunding.


        :param agency: The agency of this ProjectsFundingPatchProjectFunding.
        :type agency: str
        """

        self._agency = agency

    @property
    def award_amount(self) -> str:
        """Gets the award_amount of this ProjectsFundingPatchProjectFunding.


        :return: The award_amount of this ProjectsFundingPatchProjectFunding.
        :rtype: str
        """
        return self._award_amount

    @award_amount.setter
    def award_amount(self, award_amount: str):
        """Sets the award_amount of this ProjectsFundingPatchProjectFunding.


        :param award_amount: The award_amount of this ProjectsFundingPatchProjectFunding.
        :type award_amount: str
        """

        self._award_amount = award_amount

    @property
    def award_number(self) -> str:
        """Gets the award_number of this ProjectsFundingPatchProjectFunding.


        :return: The award_number of this ProjectsFundingPatchProjectFunding.
        :rtype: str
        """
        return self._award_number

    @award_number.setter
    def award_number(self, award_number: str):
        """Sets the award_number of this ProjectsFundingPatchProjectFunding.


        :param award_number: The award_number of this ProjectsFundingPatchProjectFunding.
        :type award_number: str
        """

        self._award_number = award_number

    @property
    def directorate(self) -> str:
        """Gets the directorate of this ProjectsFundingPatchProjectFunding.


        :return: The directorate of this ProjectsFundingPatchProjectFunding.
        :rtype: str
        """
        return self._directorate

    @directorate.setter
    def directorate(self, directorate: str):
        """Sets the directorate of this ProjectsFundingPatchProjectFunding.


        :param directorate: The directorate of this ProjectsFundingPatchProjectFunding.
        :type directorate: str
        """

        self._directorate = directorate
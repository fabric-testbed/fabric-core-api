# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.people_one_roles import PeopleOneRoles  # noqa: F401,E501
from swagger_server.models.preferences import Preferences  # noqa: F401,E501
from swagger_server.models.profile_people import ProfilePeople  # noqa: F401,E501
from swagger_server import util


class PeopleOne(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, affiliation: str=None, bastion_login: str=None, cilogon_email: str=None, cilogon_family_name: str=None, cilogon_given_name: str=None, cilogon_id: str=None, cilogon_name: str=None, email: str=None, email_addresses: List[str]=None, eppn: str=None, fabric_id: str=None, gecos: str=None, name: str=None, preferences: Preferences=None, profile: ProfilePeople=None, registered_on: str=None, roles: List[PeopleOneRoles]=None, sshkeys: List[object]=None, user_sub_identities: List[str]=None, user_org_affiliations: List[str]=None, uuid: str=None):  # noqa: E501
        """PeopleOne - a model defined in Swagger

        :param affiliation: The affiliation of this PeopleOne.  # noqa: E501
        :type affiliation: str
        :param bastion_login: The bastion_login of this PeopleOne.  # noqa: E501
        :type bastion_login: str
        :param cilogon_email: The cilogon_email of this PeopleOne.  # noqa: E501
        :type cilogon_email: str
        :param cilogon_family_name: The cilogon_family_name of this PeopleOne.  # noqa: E501
        :type cilogon_family_name: str
        :param cilogon_given_name: The cilogon_given_name of this PeopleOne.  # noqa: E501
        :type cilogon_given_name: str
        :param cilogon_id: The cilogon_id of this PeopleOne.  # noqa: E501
        :type cilogon_id: str
        :param cilogon_name: The cilogon_name of this PeopleOne.  # noqa: E501
        :type cilogon_name: str
        :param email: The email of this PeopleOne.  # noqa: E501
        :type email: str
        :param email_addresses: The email_addresses of this PeopleOne.  # noqa: E501
        :type email_addresses: List[str]
        :param eppn: The eppn of this PeopleOne.  # noqa: E501
        :type eppn: str
        :param fabric_id: The fabric_id of this PeopleOne.  # noqa: E501
        :type fabric_id: str
        :param gecos: The gecos of this PeopleOne.  # noqa: E501
        :type gecos: str
        :param name: The name of this PeopleOne.  # noqa: E501
        :type name: str
        :param preferences: The preferences of this PeopleOne.  # noqa: E501
        :type preferences: Preferences
        :param profile: The profile of this PeopleOne.  # noqa: E501
        :type profile: ProfilePeople
        :param registered_on: The registered_on of this PeopleOne.  # noqa: E501
        :type registered_on: str
        :param roles: The roles of this PeopleOne.  # noqa: E501
        :type roles: List[PeopleOneRoles]
        :param sshkeys: The sshkeys of this PeopleOne.  # noqa: E501
        :type sshkeys: List[object]
        :param user_sub_identities: The user_sub_identities of this PeopleOne.  # noqa: E501
        :type user_sub_identities: List[str]
        :param user_org_affiliations: The user_org_affiliations of this PeopleOne.  # noqa: E501
        :type user_org_affiliations: List[str]
        :param uuid: The uuid of this PeopleOne.  # noqa: E501
        :type uuid: str
        """
        self.swagger_types = {
            'affiliation': str,
            'bastion_login': str,
            'cilogon_email': str,
            'cilogon_family_name': str,
            'cilogon_given_name': str,
            'cilogon_id': str,
            'cilogon_name': str,
            'email': str,
            'email_addresses': List[str],
            'eppn': str,
            'fabric_id': str,
            'gecos': str,
            'name': str,
            'preferences': Preferences,
            'profile': ProfilePeople,
            'registered_on': str,
            'roles': List[PeopleOneRoles],
            'sshkeys': List[object],
            'user_sub_identities': List[str],
            'user_org_affiliations': List[str],
            'uuid': str
        }

        self.attribute_map = {
            'affiliation': 'affiliation',
            'bastion_login': 'bastion_login',
            'cilogon_email': 'cilogon_email',
            'cilogon_family_name': 'cilogon_family_name',
            'cilogon_given_name': 'cilogon_given_name',
            'cilogon_id': 'cilogon_id',
            'cilogon_name': 'cilogon_name',
            'email': 'email',
            'email_addresses': 'email_addresses',
            'eppn': 'eppn',
            'fabric_id': 'fabric_id',
            'gecos': 'gecos',
            'name': 'name',
            'preferences': 'preferences',
            'profile': 'profile',
            'registered_on': 'registered_on',
            'roles': 'roles',
            'sshkeys': 'sshkeys',
            'user_sub_identities': 'user_sub_identities',
            'user_org_affiliations': 'user_org_affiliations',
            'uuid': 'uuid'
        }
        self._affiliation = affiliation
        self._bastion_login = bastion_login
        self._cilogon_email = cilogon_email
        self._cilogon_family_name = cilogon_family_name
        self._cilogon_given_name = cilogon_given_name
        self._cilogon_id = cilogon_id
        self._cilogon_name = cilogon_name
        self._email = email
        self._email_addresses = email_addresses
        self._eppn = eppn
        self._fabric_id = fabric_id
        self._gecos = gecos
        self._name = name
        self._preferences = preferences
        self._profile = profile
        self._registered_on = registered_on
        self._roles = roles
        self._sshkeys = sshkeys
        self._user_sub_identities = user_sub_identities
        self._user_org_affiliations = user_org_affiliations
        self._uuid = uuid

    @classmethod
    def from_dict(cls, dikt) -> 'PeopleOne':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The people_one of this PeopleOne.  # noqa: E501
        :rtype: PeopleOne
        """
        return util.deserialize_model(dikt, cls)

    @property
    def affiliation(self) -> str:
        """Gets the affiliation of this PeopleOne.


        :return: The affiliation of this PeopleOne.
        :rtype: str
        """
        return self._affiliation

    @affiliation.setter
    def affiliation(self, affiliation: str):
        """Sets the affiliation of this PeopleOne.


        :param affiliation: The affiliation of this PeopleOne.
        :type affiliation: str
        """
        if affiliation is None:
            raise ValueError("Invalid value for `affiliation`, must not be `None`")  # noqa: E501

        self._affiliation = affiliation

    @property
    def bastion_login(self) -> str:
        """Gets the bastion_login of this PeopleOne.


        :return: The bastion_login of this PeopleOne.
        :rtype: str
        """
        return self._bastion_login

    @bastion_login.setter
    def bastion_login(self, bastion_login: str):
        """Sets the bastion_login of this PeopleOne.


        :param bastion_login: The bastion_login of this PeopleOne.
        :type bastion_login: str
        """

        self._bastion_login = bastion_login

    @property
    def cilogon_email(self) -> str:
        """Gets the cilogon_email of this PeopleOne.


        :return: The cilogon_email of this PeopleOne.
        :rtype: str
        """
        return self._cilogon_email

    @cilogon_email.setter
    def cilogon_email(self, cilogon_email: str):
        """Sets the cilogon_email of this PeopleOne.


        :param cilogon_email: The cilogon_email of this PeopleOne.
        :type cilogon_email: str
        """

        self._cilogon_email = cilogon_email

    @property
    def cilogon_family_name(self) -> str:
        """Gets the cilogon_family_name of this PeopleOne.


        :return: The cilogon_family_name of this PeopleOne.
        :rtype: str
        """
        return self._cilogon_family_name

    @cilogon_family_name.setter
    def cilogon_family_name(self, cilogon_family_name: str):
        """Sets the cilogon_family_name of this PeopleOne.


        :param cilogon_family_name: The cilogon_family_name of this PeopleOne.
        :type cilogon_family_name: str
        """

        self._cilogon_family_name = cilogon_family_name

    @property
    def cilogon_given_name(self) -> str:
        """Gets the cilogon_given_name of this PeopleOne.


        :return: The cilogon_given_name of this PeopleOne.
        :rtype: str
        """
        return self._cilogon_given_name

    @cilogon_given_name.setter
    def cilogon_given_name(self, cilogon_given_name: str):
        """Sets the cilogon_given_name of this PeopleOne.


        :param cilogon_given_name: The cilogon_given_name of this PeopleOne.
        :type cilogon_given_name: str
        """

        self._cilogon_given_name = cilogon_given_name

    @property
    def cilogon_id(self) -> str:
        """Gets the cilogon_id of this PeopleOne.


        :return: The cilogon_id of this PeopleOne.
        :rtype: str
        """
        return self._cilogon_id

    @cilogon_id.setter
    def cilogon_id(self, cilogon_id: str):
        """Sets the cilogon_id of this PeopleOne.


        :param cilogon_id: The cilogon_id of this PeopleOne.
        :type cilogon_id: str
        """

        self._cilogon_id = cilogon_id

    @property
    def cilogon_name(self) -> str:
        """Gets the cilogon_name of this PeopleOne.


        :return: The cilogon_name of this PeopleOne.
        :rtype: str
        """
        return self._cilogon_name

    @cilogon_name.setter
    def cilogon_name(self, cilogon_name: str):
        """Sets the cilogon_name of this PeopleOne.


        :param cilogon_name: The cilogon_name of this PeopleOne.
        :type cilogon_name: str
        """

        self._cilogon_name = cilogon_name

    @property
    def email(self) -> str:
        """Gets the email of this PeopleOne.


        :return: The email of this PeopleOne.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email: str):
        """Sets the email of this PeopleOne.


        :param email: The email of this PeopleOne.
        :type email: str
        """

        self._email = email

    @property
    def email_addresses(self) -> List[str]:
        """Gets the email_addresses of this PeopleOne.


        :return: The email_addresses of this PeopleOne.
        :rtype: List[str]
        """
        return self._email_addresses

    @email_addresses.setter
    def email_addresses(self, email_addresses: List[str]):
        """Sets the email_addresses of this PeopleOne.


        :param email_addresses: The email_addresses of this PeopleOne.
        :type email_addresses: List[str]
        """

        self._email_addresses = email_addresses

    @property
    def eppn(self) -> str:
        """Gets the eppn of this PeopleOne.


        :return: The eppn of this PeopleOne.
        :rtype: str
        """
        return self._eppn

    @eppn.setter
    def eppn(self, eppn: str):
        """Sets the eppn of this PeopleOne.


        :param eppn: The eppn of this PeopleOne.
        :type eppn: str
        """

        self._eppn = eppn

    @property
    def fabric_id(self) -> str:
        """Gets the fabric_id of this PeopleOne.


        :return: The fabric_id of this PeopleOne.
        :rtype: str
        """
        return self._fabric_id

    @fabric_id.setter
    def fabric_id(self, fabric_id: str):
        """Sets the fabric_id of this PeopleOne.


        :param fabric_id: The fabric_id of this PeopleOne.
        :type fabric_id: str
        """

        self._fabric_id = fabric_id

    @property
    def gecos(self) -> str:
        """Gets the gecos of this PeopleOne.


        :return: The gecos of this PeopleOne.
        :rtype: str
        """
        return self._gecos

    @gecos.setter
    def gecos(self, gecos: str):
        """Sets the gecos of this PeopleOne.


        :param gecos: The gecos of this PeopleOne.
        :type gecos: str
        """

        self._gecos = gecos

    @property
    def name(self) -> str:
        """Gets the name of this PeopleOne.


        :return: The name of this PeopleOne.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this PeopleOne.


        :param name: The name of this PeopleOne.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def preferences(self) -> Preferences:
        """Gets the preferences of this PeopleOne.


        :return: The preferences of this PeopleOne.
        :rtype: Preferences
        """
        return self._preferences

    @preferences.setter
    def preferences(self, preferences: Preferences):
        """Sets the preferences of this PeopleOne.


        :param preferences: The preferences of this PeopleOne.
        :type preferences: Preferences
        """

        self._preferences = preferences

    @property
    def profile(self) -> ProfilePeople:
        """Gets the profile of this PeopleOne.


        :return: The profile of this PeopleOne.
        :rtype: ProfilePeople
        """
        return self._profile

    @profile.setter
    def profile(self, profile: ProfilePeople):
        """Sets the profile of this PeopleOne.


        :param profile: The profile of this PeopleOne.
        :type profile: ProfilePeople
        """

        self._profile = profile

    @property
    def registered_on(self) -> str:
        """Gets the registered_on of this PeopleOne.


        :return: The registered_on of this PeopleOne.
        :rtype: str
        """
        return self._registered_on

    @registered_on.setter
    def registered_on(self, registered_on: str):
        """Sets the registered_on of this PeopleOne.


        :param registered_on: The registered_on of this PeopleOne.
        :type registered_on: str
        """
        if registered_on is None:
            raise ValueError("Invalid value for `registered_on`, must not be `None`")  # noqa: E501

        self._registered_on = registered_on

    @property
    def roles(self) -> List[PeopleOneRoles]:
        """Gets the roles of this PeopleOne.


        :return: The roles of this PeopleOne.
        :rtype: List[PeopleOneRoles]
        """
        return self._roles

    @roles.setter
    def roles(self, roles: List[PeopleOneRoles]):
        """Sets the roles of this PeopleOne.


        :param roles: The roles of this PeopleOne.
        :type roles: List[PeopleOneRoles]
        """

        self._roles = roles

    @property
    def sshkeys(self) -> List[object]:
        """Gets the sshkeys of this PeopleOne.


        :return: The sshkeys of this PeopleOne.
        :rtype: List[object]
        """
        return self._sshkeys

    @sshkeys.setter
    def sshkeys(self, sshkeys: List[object]):
        """Sets the sshkeys of this PeopleOne.


        :param sshkeys: The sshkeys of this PeopleOne.
        :type sshkeys: List[object]
        """

        self._sshkeys = sshkeys

    @property
    def user_sub_identities(self) -> List[str]:
        """Gets the user_sub_identities of this PeopleOne.


        :return: The user_sub_identities of this PeopleOne.
        :rtype: List[str]
        """
        return self._user_sub_identities

    @user_sub_identities.setter
    def user_sub_identities(self, user_sub_identities: List[str]):
        """Sets the user_sub_identities of this PeopleOne.


        :param user_sub_identities: The user_sub_identities of this PeopleOne.
        :type user_sub_identities: List[str]
        """

        self._user_sub_identities = user_sub_identities

    @property
    def user_org_affiliations(self) -> List[str]:
        """Gets the user_org_affiliations of this PeopleOne.


        :return: The user_org_affiliations of this PeopleOne.
        :rtype: List[str]
        """
        return self._user_org_affiliations

    @user_org_affiliations.setter
    def user_org_affiliations(self, user_org_affiliations: List[str]):
        """Sets the user_org_affiliations of this PeopleOne.


        :param user_org_affiliations: The user_org_affiliations of this PeopleOne.
        :type user_org_affiliations: List[str]
        """

        self._user_org_affiliations = user_org_affiliations

    @property
    def uuid(self) -> str:
        """Gets the uuid of this PeopleOne.


        :return: The uuid of this PeopleOne.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this PeopleOne.


        :param uuid: The uuid of this PeopleOne.
        :type uuid: str
        """
        if uuid is None:
            raise ValueError("Invalid value for `uuid`, must not be `None`")  # noqa: E501

        self._uuid = uuid

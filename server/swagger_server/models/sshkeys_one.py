# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class SshkeysOne(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, comment: str=None, created_on: datetime=None, deactivated_on: datetime=None, deactivated_reason: str=None, description: str=None, expires_on: datetime=None, fabric_key_type: str='sliver', fingerprint: str=None, public_key: str=None, ssh_key_type: str=None, uuid: str=None):  # noqa: E501
        """SshkeysOne - a model defined in Swagger

        :param comment: The comment of this SshkeysOne.  # noqa: E501
        :type comment: str
        :param created_on: The created_on of this SshkeysOne.  # noqa: E501
        :type created_on: datetime
        :param deactivated_on: The deactivated_on of this SshkeysOne.  # noqa: E501
        :type deactivated_on: datetime
        :param deactivated_reason: The deactivated_reason of this SshkeysOne.  # noqa: E501
        :type deactivated_reason: str
        :param description: The description of this SshkeysOne.  # noqa: E501
        :type description: str
        :param expires_on: The expires_on of this SshkeysOne.  # noqa: E501
        :type expires_on: datetime
        :param fabric_key_type: The fabric_key_type of this SshkeysOne.  # noqa: E501
        :type fabric_key_type: str
        :param fingerprint: The fingerprint of this SshkeysOne.  # noqa: E501
        :type fingerprint: str
        :param public_key: The public_key of this SshkeysOne.  # noqa: E501
        :type public_key: str
        :param ssh_key_type: The ssh_key_type of this SshkeysOne.  # noqa: E501
        :type ssh_key_type: str
        :param uuid: The uuid of this SshkeysOne.  # noqa: E501
        :type uuid: str
        """
        self.swagger_types = {
            'comment': str,
            'created_on': datetime,
            'deactivated_on': datetime,
            'deactivated_reason': str,
            'description': str,
            'expires_on': datetime,
            'fabric_key_type': str,
            'fingerprint': str,
            'public_key': str,
            'ssh_key_type': str,
            'uuid': str
        }

        self.attribute_map = {
            'comment': 'comment',
            'created_on': 'created_on',
            'deactivated_on': 'deactivated_on',
            'deactivated_reason': 'deactivated_reason',
            'description': 'description',
            'expires_on': 'expires_on',
            'fabric_key_type': 'fabric_key_type',
            'fingerprint': 'fingerprint',
            'public_key': 'public_key',
            'ssh_key_type': 'ssh_key_type',
            'uuid': 'uuid'
        }
        self._comment = comment
        self._created_on = created_on
        self._deactivated_on = deactivated_on
        self._deactivated_reason = deactivated_reason
        self._description = description
        self._expires_on = expires_on
        self._fabric_key_type = fabric_key_type
        self._fingerprint = fingerprint
        self._public_key = public_key
        self._ssh_key_type = ssh_key_type
        self._uuid = uuid

    @classmethod
    def from_dict(cls, dikt) -> 'SshkeysOne':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The sshkeys_one of this SshkeysOne.  # noqa: E501
        :rtype: SshkeysOne
        """
        return util.deserialize_model(dikt, cls)

    @property
    def comment(self) -> str:
        """Gets the comment of this SshkeysOne.


        :return: The comment of this SshkeysOne.
        :rtype: str
        """
        return self._comment

    @comment.setter
    def comment(self, comment: str):
        """Sets the comment of this SshkeysOne.


        :param comment: The comment of this SshkeysOne.
        :type comment: str
        """

        self._comment = comment

    @property
    def created_on(self) -> datetime:
        """Gets the created_on of this SshkeysOne.


        :return: The created_on of this SshkeysOne.
        :rtype: datetime
        """
        return self._created_on

    @created_on.setter
    def created_on(self, created_on: datetime):
        """Sets the created_on of this SshkeysOne.


        :param created_on: The created_on of this SshkeysOne.
        :type created_on: datetime
        """

        self._created_on = created_on

    @property
    def deactivated_on(self) -> datetime:
        """Gets the deactivated_on of this SshkeysOne.


        :return: The deactivated_on of this SshkeysOne.
        :rtype: datetime
        """
        return self._deactivated_on

    @deactivated_on.setter
    def deactivated_on(self, deactivated_on: datetime):
        """Sets the deactivated_on of this SshkeysOne.


        :param deactivated_on: The deactivated_on of this SshkeysOne.
        :type deactivated_on: datetime
        """

        self._deactivated_on = deactivated_on

    @property
    def deactivated_reason(self) -> str:
        """Gets the deactivated_reason of this SshkeysOne.


        :return: The deactivated_reason of this SshkeysOne.
        :rtype: str
        """
        return self._deactivated_reason

    @deactivated_reason.setter
    def deactivated_reason(self, deactivated_reason: str):
        """Sets the deactivated_reason of this SshkeysOne.


        :param deactivated_reason: The deactivated_reason of this SshkeysOne.
        :type deactivated_reason: str
        """

        self._deactivated_reason = deactivated_reason

    @property
    def description(self) -> str:
        """Gets the description of this SshkeysOne.


        :return: The description of this SshkeysOne.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this SshkeysOne.


        :param description: The description of this SshkeysOne.
        :type description: str
        """

        self._description = description

    @property
    def expires_on(self) -> datetime:
        """Gets the expires_on of this SshkeysOne.


        :return: The expires_on of this SshkeysOne.
        :rtype: datetime
        """
        return self._expires_on

    @expires_on.setter
    def expires_on(self, expires_on: datetime):
        """Sets the expires_on of this SshkeysOne.


        :param expires_on: The expires_on of this SshkeysOne.
        :type expires_on: datetime
        """

        self._expires_on = expires_on

    @property
    def fabric_key_type(self) -> str:
        """Gets the fabric_key_type of this SshkeysOne.


        :return: The fabric_key_type of this SshkeysOne.
        :rtype: str
        """
        return self._fabric_key_type

    @fabric_key_type.setter
    def fabric_key_type(self, fabric_key_type: str):
        """Sets the fabric_key_type of this SshkeysOne.


        :param fabric_key_type: The fabric_key_type of this SshkeysOne.
        :type fabric_key_type: str
        """
        allowed_values = ["bastion", "sliver"]  # noqa: E501
        if fabric_key_type not in allowed_values:
            raise ValueError(
                "Invalid value for `fabric_key_type` ({0}), must be one of {1}"
                .format(fabric_key_type, allowed_values)
            )

        self._fabric_key_type = fabric_key_type

    @property
    def fingerprint(self) -> str:
        """Gets the fingerprint of this SshkeysOne.


        :return: The fingerprint of this SshkeysOne.
        :rtype: str
        """
        return self._fingerprint

    @fingerprint.setter
    def fingerprint(self, fingerprint: str):
        """Sets the fingerprint of this SshkeysOne.


        :param fingerprint: The fingerprint of this SshkeysOne.
        :type fingerprint: str
        """

        self._fingerprint = fingerprint

    @property
    def public_key(self) -> str:
        """Gets the public_key of this SshkeysOne.


        :return: The public_key of this SshkeysOne.
        :rtype: str
        """
        return self._public_key

    @public_key.setter
    def public_key(self, public_key: str):
        """Sets the public_key of this SshkeysOne.


        :param public_key: The public_key of this SshkeysOne.
        :type public_key: str
        """

        self._public_key = public_key

    @property
    def ssh_key_type(self) -> str:
        """Gets the ssh_key_type of this SshkeysOne.


        :return: The ssh_key_type of this SshkeysOne.
        :rtype: str
        """
        return self._ssh_key_type

    @ssh_key_type.setter
    def ssh_key_type(self, ssh_key_type: str):
        """Sets the ssh_key_type of this SshkeysOne.


        :param ssh_key_type: The ssh_key_type of this SshkeysOne.
        :type ssh_key_type: str
        """

        self._ssh_key_type = ssh_key_type

    @property
    def uuid(self) -> str:
        """Gets the uuid of this SshkeysOne.


        :return: The uuid of this SshkeysOne.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this SshkeysOne.


        :param uuid: The uuid of this SshkeysOne.
        :type uuid: str
        """

        self._uuid = uuid

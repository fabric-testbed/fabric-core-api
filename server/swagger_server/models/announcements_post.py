# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class AnnouncementsPost(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, button: str=None, content: str=None, display_date: str=None, end_date: str=None, is_active: bool=True, link: str=None, start_date: str=None, title: str=None, type: str='facility'):  # noqa: E501
        """AnnouncementsPost - a model defined in Swagger

        :param button: The button of this AnnouncementsPost.  # noqa: E501
        :type button: str
        :param content: The content of this AnnouncementsPost.  # noqa: E501
        :type content: str
        :param display_date: The display_date of this AnnouncementsPost.  # noqa: E501
        :type display_date: str
        :param end_date: The end_date of this AnnouncementsPost.  # noqa: E501
        :type end_date: str
        :param is_active: The is_active of this AnnouncementsPost.  # noqa: E501
        :type is_active: bool
        :param link: The link of this AnnouncementsPost.  # noqa: E501
        :type link: str
        :param start_date: The start_date of this AnnouncementsPost.  # noqa: E501
        :type start_date: str
        :param title: The title of this AnnouncementsPost.  # noqa: E501
        :type title: str
        :param type: The type of this AnnouncementsPost.  # noqa: E501
        :type type: str
        """
        self.swagger_types = {
            'button': str,
            'content': str,
            'display_date': str,
            'end_date': str,
            'is_active': bool,
            'link': str,
            'start_date': str,
            'title': str,
            'type': str
        }

        self.attribute_map = {
            'button': 'button',
            'content': 'content',
            'display_date': 'display_date',
            'end_date': 'end_date',
            'is_active': 'is_active',
            'link': 'link',
            'start_date': 'start_date',
            'title': 'title',
            'type': 'type'
        }
        self._button = button
        self._content = content
        self._display_date = display_date
        self._end_date = end_date
        self._is_active = is_active
        self._link = link
        self._start_date = start_date
        self._title = title
        self._type = type

    @classmethod
    def from_dict(cls, dikt) -> 'AnnouncementsPost':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The announcements_post of this AnnouncementsPost.  # noqa: E501
        :rtype: AnnouncementsPost
        """
        return util.deserialize_model(dikt, cls)

    @property
    def button(self) -> str:
        """Gets the button of this AnnouncementsPost.


        :return: The button of this AnnouncementsPost.
        :rtype: str
        """
        return self._button

    @button.setter
    def button(self, button: str):
        """Sets the button of this AnnouncementsPost.


        :param button: The button of this AnnouncementsPost.
        :type button: str
        """

        self._button = button

    @property
    def content(self) -> str:
        """Gets the content of this AnnouncementsPost.


        :return: The content of this AnnouncementsPost.
        :rtype: str
        """
        return self._content

    @content.setter
    def content(self, content: str):
        """Sets the content of this AnnouncementsPost.


        :param content: The content of this AnnouncementsPost.
        :type content: str
        """
        if content is None:
            raise ValueError("Invalid value for `content`, must not be `None`")  # noqa: E501

        self._content = content

    @property
    def display_date(self) -> str:
        """Gets the display_date of this AnnouncementsPost.


        :return: The display_date of this AnnouncementsPost.
        :rtype: str
        """
        return self._display_date

    @display_date.setter
    def display_date(self, display_date: str):
        """Sets the display_date of this AnnouncementsPost.


        :param display_date: The display_date of this AnnouncementsPost.
        :type display_date: str
        """

        self._display_date = display_date

    @property
    def end_date(self) -> str:
        """Gets the end_date of this AnnouncementsPost.


        :return: The end_date of this AnnouncementsPost.
        :rtype: str
        """
        return self._end_date

    @end_date.setter
    def end_date(self, end_date: str):
        """Sets the end_date of this AnnouncementsPost.


        :param end_date: The end_date of this AnnouncementsPost.
        :type end_date: str
        """

        self._end_date = end_date

    @property
    def is_active(self) -> bool:
        """Gets the is_active of this AnnouncementsPost.


        :return: The is_active of this AnnouncementsPost.
        :rtype: bool
        """
        return self._is_active

    @is_active.setter
    def is_active(self, is_active: bool):
        """Sets the is_active of this AnnouncementsPost.


        :param is_active: The is_active of this AnnouncementsPost.
        :type is_active: bool
        """
        if is_active is None:
            raise ValueError("Invalid value for `is_active`, must not be `None`")  # noqa: E501

        self._is_active = is_active

    @property
    def link(self) -> str:
        """Gets the link of this AnnouncementsPost.


        :return: The link of this AnnouncementsPost.
        :rtype: str
        """
        return self._link

    @link.setter
    def link(self, link: str):
        """Sets the link of this AnnouncementsPost.


        :param link: The link of this AnnouncementsPost.
        :type link: str
        """

        self._link = link

    @property
    def start_date(self) -> str:
        """Gets the start_date of this AnnouncementsPost.


        :return: The start_date of this AnnouncementsPost.
        :rtype: str
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date: str):
        """Sets the start_date of this AnnouncementsPost.


        :param start_date: The start_date of this AnnouncementsPost.
        :type start_date: str
        """
        if start_date is None:
            raise ValueError("Invalid value for `start_date`, must not be `None`")  # noqa: E501

        self._start_date = start_date

    @property
    def title(self) -> str:
        """Gets the title of this AnnouncementsPost.


        :return: The title of this AnnouncementsPost.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title: str):
        """Sets the title of this AnnouncementsPost.


        :param title: The title of this AnnouncementsPost.
        :type title: str
        """
        if title is None:
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def type(self) -> str:
        """Gets the type of this AnnouncementsPost.


        :return: The type of this AnnouncementsPost.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this AnnouncementsPost.


        :param type: The type of this AnnouncementsPost.
        :type type: str
        """
        allowed_values = ["facility", "maintenance"]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"
                .format(type, allowed_values)
            )

        self._type = type

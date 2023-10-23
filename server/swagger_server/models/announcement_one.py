# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class AnnouncementOne(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, announcement_type: str=None, background_image_url: str=None, button: str=None, content: str=None, display_date: date=None, end_date: date=None, is_active: bool=None, link: str=None, sequence: int=None, start_date: date=None, title: str=None, uuid: str=None):  # noqa: E501
        """AnnouncementOne - a model defined in Swagger

        :param announcement_type: The announcement_type of this AnnouncementOne.  # noqa: E501
        :type announcement_type: str
        :param background_image_url: The background_image_url of this AnnouncementOne.  # noqa: E501
        :type background_image_url: str
        :param button: The button of this AnnouncementOne.  # noqa: E501
        :type button: str
        :param content: The content of this AnnouncementOne.  # noqa: E501
        :type content: str
        :param display_date: The display_date of this AnnouncementOne.  # noqa: E501
        :type display_date: date
        :param end_date: The end_date of this AnnouncementOne.  # noqa: E501
        :type end_date: date
        :param is_active: The is_active of this AnnouncementOne.  # noqa: E501
        :type is_active: bool
        :param link: The link of this AnnouncementOne.  # noqa: E501
        :type link: str
        :param sequence: The sequence of this AnnouncementOne.  # noqa: E501
        :type sequence: int
        :param start_date: The start_date of this AnnouncementOne.  # noqa: E501
        :type start_date: date
        :param title: The title of this AnnouncementOne.  # noqa: E501
        :type title: str
        :param uuid: The uuid of this AnnouncementOne.  # noqa: E501
        :type uuid: str
        """
        self.swagger_types = {
            'announcement_type': str,
            'background_image_url': str,
            'button': str,
            'content': str,
            'display_date': date,
            'end_date': date,
            'is_active': bool,
            'link': str,
            'sequence': int,
            'start_date': date,
            'title': str,
            'uuid': str
        }

        self.attribute_map = {
            'announcement_type': 'announcement_type',
            'background_image_url': 'background_image_url',
            'button': 'button',
            'content': 'content',
            'display_date': 'display_date',
            'end_date': 'end_date',
            'is_active': 'is_active',
            'link': 'link',
            'sequence': 'sequence',
            'start_date': 'start_date',
            'title': 'title',
            'uuid': 'uuid'
        }
        self._announcement_type = announcement_type
        self._background_image_url = background_image_url
        self._button = button
        self._content = content
        self._display_date = display_date
        self._end_date = end_date
        self._is_active = is_active
        self._link = link
        self._sequence = sequence
        self._start_date = start_date
        self._title = title
        self._uuid = uuid

    @classmethod
    def from_dict(cls, dikt) -> 'AnnouncementOne':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The announcement_one of this AnnouncementOne.  # noqa: E501
        :rtype: AnnouncementOne
        """
        return util.deserialize_model(dikt, cls)

    @property
    def announcement_type(self) -> str:
        """Gets the announcement_type of this AnnouncementOne.


        :return: The announcement_type of this AnnouncementOne.
        :rtype: str
        """
        return self._announcement_type

    @announcement_type.setter
    def announcement_type(self, announcement_type: str):
        """Sets the announcement_type of this AnnouncementOne.


        :param announcement_type: The announcement_type of this AnnouncementOne.
        :type announcement_type: str
        """
        if announcement_type is None:
            raise ValueError("Invalid value for `announcement_type`, must not be `None`")  # noqa: E501

        self._announcement_type = announcement_type

    @property
    def background_image_url(self) -> str:
        """Gets the background_image_url of this AnnouncementOne.


        :return: The background_image_url of this AnnouncementOne.
        :rtype: str
        """
        return self._background_image_url

    @background_image_url.setter
    def background_image_url(self, background_image_url: str):
        """Sets the background_image_url of this AnnouncementOne.


        :param background_image_url: The background_image_url of this AnnouncementOne.
        :type background_image_url: str
        """

        self._background_image_url = background_image_url

    @property
    def button(self) -> str:
        """Gets the button of this AnnouncementOne.


        :return: The button of this AnnouncementOne.
        :rtype: str
        """
        return self._button

    @button.setter
    def button(self, button: str):
        """Sets the button of this AnnouncementOne.


        :param button: The button of this AnnouncementOne.
        :type button: str
        """

        self._button = button

    @property
    def content(self) -> str:
        """Gets the content of this AnnouncementOne.


        :return: The content of this AnnouncementOne.
        :rtype: str
        """
        return self._content

    @content.setter
    def content(self, content: str):
        """Sets the content of this AnnouncementOne.


        :param content: The content of this AnnouncementOne.
        :type content: str
        """
        if content is None:
            raise ValueError("Invalid value for `content`, must not be `None`")  # noqa: E501

        self._content = content

    @property
    def display_date(self) -> date:
        """Gets the display_date of this AnnouncementOne.


        :return: The display_date of this AnnouncementOne.
        :rtype: date
        """
        return self._display_date

    @display_date.setter
    def display_date(self, display_date: date):
        """Sets the display_date of this AnnouncementOne.


        :param display_date: The display_date of this AnnouncementOne.
        :type display_date: date
        """

        self._display_date = display_date

    @property
    def end_date(self) -> date:
        """Gets the end_date of this AnnouncementOne.


        :return: The end_date of this AnnouncementOne.
        :rtype: date
        """
        return self._end_date

    @end_date.setter
    def end_date(self, end_date: date):
        """Sets the end_date of this AnnouncementOne.


        :param end_date: The end_date of this AnnouncementOne.
        :type end_date: date
        """

        self._end_date = end_date

    @property
    def is_active(self) -> bool:
        """Gets the is_active of this AnnouncementOne.


        :return: The is_active of this AnnouncementOne.
        :rtype: bool
        """
        return self._is_active

    @is_active.setter
    def is_active(self, is_active: bool):
        """Sets the is_active of this AnnouncementOne.


        :param is_active: The is_active of this AnnouncementOne.
        :type is_active: bool
        """
        if is_active is None:
            raise ValueError("Invalid value for `is_active`, must not be `None`")  # noqa: E501

        self._is_active = is_active

    @property
    def link(self) -> str:
        """Gets the link of this AnnouncementOne.


        :return: The link of this AnnouncementOne.
        :rtype: str
        """
        return self._link

    @link.setter
    def link(self, link: str):
        """Sets the link of this AnnouncementOne.


        :param link: The link of this AnnouncementOne.
        :type link: str
        """

        self._link = link

    @property
    def sequence(self) -> int:
        """Gets the sequence of this AnnouncementOne.


        :return: The sequence of this AnnouncementOne.
        :rtype: int
        """
        return self._sequence

    @sequence.setter
    def sequence(self, sequence: int):
        """Sets the sequence of this AnnouncementOne.


        :param sequence: The sequence of this AnnouncementOne.
        :type sequence: int
        """

        self._sequence = sequence

    @property
    def start_date(self) -> date:
        """Gets the start_date of this AnnouncementOne.


        :return: The start_date of this AnnouncementOne.
        :rtype: date
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date: date):
        """Sets the start_date of this AnnouncementOne.


        :param start_date: The start_date of this AnnouncementOne.
        :type start_date: date
        """
        if start_date is None:
            raise ValueError("Invalid value for `start_date`, must not be `None`")  # noqa: E501

        self._start_date = start_date

    @property
    def title(self) -> str:
        """Gets the title of this AnnouncementOne.


        :return: The title of this AnnouncementOne.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title: str):
        """Sets the title of this AnnouncementOne.


        :param title: The title of this AnnouncementOne.
        :type title: str
        """
        if title is None:
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def uuid(self) -> str:
        """Gets the uuid of this AnnouncementOne.


        :return: The uuid of this AnnouncementOne.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this AnnouncementOne.


        :param uuid: The uuid of this AnnouncementOne.
        :type uuid: str
        """

        self._uuid = uuid

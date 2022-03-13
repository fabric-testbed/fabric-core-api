import json
import os
import re
from abc import ABC


class CoreApiOptions(ABC):
    """
    Core API Options object
    """
    api_endpoints: [str]
    description: str
    key_value_pairs: {}
    name: str
    options: [str]

    def __init__(self, file_name: str = None):
        if file_name:
            file_path = os.path.join(os.path.dirname(__file__), 'json_data', file_name)
            with open(file_path) as file:
                file_dict = json.load(file)
            self.name = file_dict['name']
            self.description = file_dict['description']
            self.api_endpoints = []
            for ep in file_dict['api_endpoints']:
                self.api_endpoints.append({"description": ep['description'], "endpoint": ep['endpoint']})
            self.key_value_pairs = []
            for key in file_dict['key_value_pairs'].keys():
                self.key_value_pairs.append({key: file_dict['key_value_pairs'][key]})
            self.options = list(file_dict['key_value_pairs'].keys())

    def search(self, pattern: str = None) -> [str]:
        if pattern:
            found = [item for item in self.options if pattern.casefold() in item.casefold()]
        else:
            found = self.options
        return sorted(found)


def is_valid_url(url: str = None) -> bool:
    """
    Validate URL format
    """
    url_regex = ("((http|https)://)(www.)?" +
                 "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                 "{2,256}\\.[a-z]" +
                 "{2,6}\\b([-a-zA-Z0-9@:%" +
                 "._\\+~#?&//=]*)")

    url_check = re.compile(url_regex)

    if url and re.search(url_check, url):
        return True
    else:
        return False

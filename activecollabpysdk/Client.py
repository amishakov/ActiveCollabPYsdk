from io import BufferedReader
from typing import Any

from requests.models import Response
from Exceptions import InvalidArgumentError
from token_sdk import Token
from urllib import parse
import requests
import os
from client_interface import ClientInterface

class Client(ClientInterface):
    """Client connection class for connecting to ActiveCollab API"""

    def __init__(self, token: Token, api_version: int = None) -> None:
        self.token = token
        
        if api_version != None:
            if api_version < 0:
                raise InvalidArgumentError(f'{api_version} is not a valid API version')
            self.api_version = api_version                

        self.header = {'X-Angie-AuthApiToken: ' + self.token.token}
        self.info_response: Any = False
    
    

    def __prepare_url(self, url: str) -> str:
        """Prepares a given URL for making http requests"""
        if not url:
            raise InvalidArgumentError("Invalid URL")

        parse_url = parse(url)
            
        path = parse_url.path or '/'
        
        path = '/' + path if path[0] == '/' else path

        query = '/' + parse_url.query if parse_url.query else ''

        return url + 'api/v' + str(self.api_version) + path + query

    def __prepare_params(self, params: dict) -> dict:
        """Prepare given dictionary {parameters} to post to ActiveCollab"""
        return params or {}

    def __prepare_files(self, attachments: list[str]) -> dict[str, BufferedReader]:
        """Converts a list of file paths to file objects.

        Converts a list of file paths to file objects. Used by post() method to post files to ActiveCollab

        :param list[str] attachments: List of file paths
        :return: dictionary of filenames (key) and file objects (value).
        :rtype: dict[str, BufferedReader]
        """

        file_params = {}

        if attachments:
            counter = 1

            for attachment in attachments:
                path = attachment[0] if type(attachment) is list else attachment

                if not os.path.isfile(path):
                    raise FileNotFoundError(f'{path} not found')

                with open(path, 'rb') as file:
                    file_params['attachment_' + str(counter)] = file
                    counter +=1

        return file_params

    def info(self, property: Any = False):
        """Retrieves a cached info response

        :param Any property: Flag
        :return: Cached info response if succesful; False otherwise
        :rtype: str|bool
        """

        if not self.info_response and type(self.info_response) is bool:
            self.info_response = self.get('info').json()
        
        if type(property) is not bool:
            return self.info_response[property] or None
        else:
            return self.info_response

    def get(self, url: str) -> Response:
        """HTTP Get request to ActiveCollab

            Makes a get request to active collab using the provided URL

            :param str url: URL to send get request.
            :raise: SystemExit() on failure
            :return: HTTP response
            :rtype: Response
        
        """
        try:
            r = requests.get(url=self.__prepare_url(url), headers=self.header)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        return r

    def post(self, url: str, params: dict = {}, attachments: list[str] = []) -> None:
        """HTTP Post request to ActiveCollab (Create New)

            Makes a post request to ActiveCollab using the provided URL, parameters/data, and attachments (optional)

            :param str url: URL to make post request.
            :param dict param: Data to post to ActiveCollab.
            :param list[str] attachments: Data to post to ActiveCollab.
            :raise: SystemExit() on request, connection, or HTTP failure
            :return: HTTP response
            :rtype: Response
        
        """
        try:

            r = requests.post(url=self.__prepare_url(url), json=self.__prepare_params(params), headers=self.header, files=self.__prepare_files(attachments))
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
                raise SystemExit(e)

    def put(self, url: str, params: dict = {}) -> None:
        """HTTP Put request from ActiveCollab (Insert/Replace)

            Makes a get request to active collab using the provided URL

            :param str url: URL to send get request.
            :param dict params: parameters to put to ActiveCollab
            :raise: SystemExit() on request, connection, or HTTP failure
            :return:
            :rtype: None
        """
        try:

            r = requests.post(url=self.__prepare_url(url), json=self.__prepare_params(params), headers=self.header)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
                raise SystemExit(e)

    def delete(self, url:str, params: dict) -> None:
        """HTTP Delete request from ActiveCollab

            Makes a delete request to ActiveCollab using the provided URL and parameters

            :param str url: URL to send get request.
            :param dict params: parameters to delete from ActiveCollab
            :raise: SystemExit() on request, connection, or HTTP failure
            :return:
            :rtype: None
        """
        try:
            r = requests.delete(url = self.__prepare_url(url), headers=self.header, json=self.__prepare_params(params))
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
                raise SystemExit(e)
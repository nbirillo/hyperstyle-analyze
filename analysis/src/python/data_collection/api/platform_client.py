import datetime
import logging
from dataclasses import asdict
from typing import Dict, List, Optional, Type, TypeVar

import requests
from dacite import Config, from_dict

from analysis.src.python.data_collection.api.platform_auth import OauthServer
from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.api.utils import str_to_datetime
from analysis.src.python.data_collection.utils.json_utils import kebab_to_snake_case

T = TypeVar('T', bound=Object)


class PlatformClient:
    """ Base class for Hyperskill and Stepik clients which wraps data exchange process according to open APIs. """

    def __init__(self, host: str, client_id: str, client_secret: str, port: int):
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.port = port
        self.token = self._get_authentication_code_token()

    def _get_authentication_code_token(self):
        """ Runs authorization process using authentication-code grant type and
        gets session token for data exchange. """

        server = OauthServer(self.host, self.client_id, self.client_secret, self.port)
        server.open_oauth_page()
        return server.get_token()

    def _get_client_credential_token(self) -> str:
        """ Runs authorization process using client-credential grant type and
        gets session token for data exchange. """

        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        response = requests.post('{host}/oauth2/token/'.format(host=self.host),
                                 data={'grant_type': 'client_credentials'},
                                 auth=auth)
        token = response.json().get('access_token', None)
        if not token:
            logging.error('Unable to authorize with provided credentials')
            exit(1)
        logging.info(f'Got token: {token}')
        return token

    def _get_objects(self,
                     obj_class: str,
                     obj_response_type: Type[ObjectResponse[T]],
                     params: BaseRequestParams,
                     obj_id: Optional[int] = None,
                     count: Optional[int] = None) -> List[T]:
        """ Get objects (steps, topics, ect.) from platform by given `obj_class`, `params` and `obj_id`."""

        objects = []
        page = 1
        while count is None or len(objects) < count:
            logging.info(f'Getting {obj_class} page={page} params={params}')
            try:
                params.page = page
                response = self._fetch(obj_class, params, obj_response_type, obj_id)
                if response is None:
                    break
                objects += response.get_objects()

                if count is not None and len(objects) >= count:
                    return objects[:count]

                if response.meta.has_next:
                    page += 1
                else:
                    break
            except Exception as e:
                logging.error(f'Unable to get {obj_class} page={page} params={params}: {e}')

        return objects

    def _get_objects_by_ids(self,
                            obj_class: str,
                            obj_ids: List[int],
                            obj_response_type: Type[ObjectResponse[T]],
                            params: BaseRequestParams,
                            count: Optional[int] = None) -> List[T]:
        """ Get objects (steps, topics, ect.) from platform by given `obj_class`, `params` and `obj_ids`."""

        objects = []
        for obj_id in obj_ids:
            objects += self._get_objects(obj_class, obj_response_type, params, obj_id)
            if count is not None and len(objects) >= count:
                return objects[:count]

        return objects

    @staticmethod
    def _prepare_params(params: BaseRequestParams) -> Dict[str, str]:
        """ Prepare request params. Remove None params and convert list request values to string objects,
        separated by comma. """

        dict_params = {}
        for key, value in asdict(params).items():
            if value is None:
                continue
            if isinstance(value, list):
                value = ','.join(map(str, value))
            dict_params[key] = value
        return dict_params

    def _fetch(self,
               obj_class: str,
               params: BaseRequestParams,
               obj_response_type: Type[ObjectResponse[T]],
               obj_id: Optional[int] = None) -> Optional[ObjectResponse[T]]:
        """ Builds, executed and processes request to educational platform.
        Response is parsed to `obj_response_type`."""

        dict_params = self._prepare_params(params)
        api_url = '{host}/api/{obj_class}s'.format(host=self.host, obj_class=obj_class)

        if obj_id is not None:
            api_url = '{url}/{obj_id}'.format(url=api_url, obj_id=obj_id)
        if self.token is not None:
            raw_response = requests.get(api_url, headers={'Authorization': 'Bearer {token}'.format(token=self.token)},
                                        params=dict_params, timeout=None)
        else:
            raw_response = requests.get(api_url, params=dict_params, timeout=None)

        if raw_response is None or raw_response.status_code != 200:
            logging.warning(f"Failed to fetch {api_url}: {raw_response}")
            return None
        else:
            response_json = raw_response.json()

        preprocessed_response = kebab_to_snake_case(response_json)
        return from_dict(data_class=obj_response_type,
                         data=preprocessed_response,
                         config=Config(type_hooks={datetime.datetime: str_to_datetime}))

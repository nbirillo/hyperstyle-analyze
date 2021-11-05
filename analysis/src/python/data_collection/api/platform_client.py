import datetime
import logging
import urllib
from dataclasses import asdict
from typing import List, Type, Optional, TypeVar

import requests
from dacite import from_dict, Config

from analysis.src.python.data_collection.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from analysis.src.python.data_collection.api.utlis import str_to_datetime
from analysis.src.python.data_collection.utils.json_utils import kebab_to_snake_case

T = TypeVar('T', bound=Object)


class PlatformClient:
    """ Base class for hyperskill and stepik clients which wraps data exchange process according to open APIs. """

    def __init__(self, host: str, client_id: str, client_secret: str):
        self.host = host
        self.token = self._get_token(host, client_id, client_secret)

    @staticmethod
    def _get_token(host: str, client_id: str, client_secret: str) -> str:
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        response = requests.post('{}/oauth2/token/'.format(host),
                                 data={'grant_type': 'client_credentials'},
                                 auth=auth)
        token = response.json().get('access_token', None)
        if not token:
            print('Unable to authorize with provided credentials')
            exit(1)
        return token

    def get_objects(self,
                    obj_class: str,
                    obj_response_type: Type[ObjectResponse[T]],
                    params: BaseRequestParams = BaseRequestParams(),
                    obj_id: Optional[int] = None,
                    start_page=1, end_page=None) -> List[T]:
        """
        Get objects (steps, topics, ect.) from platform by given `obj_class` and `params`.
        To parse response of platform `obj_response_type` parametrized with `obj_type` is used.
        """
        objects = []
        page = start_page
        while end_page is None or page <= end_page:
            logging.info(f'Getting {obj_class} page={page} params={params}')
            try:
                params.page = page
                response = self._fetch(obj_class, params, obj_response_type, obj_id)
                if response is None:
                    break
                objects += response.get_objects()
                if response.meta.has_next:
                    page += 1
                else:
                    break
            except Exception as e:
                logging.error(f'Unable to get {obj_class} page={page} params={params}: {e}')
        return objects

    def get_objects_by_ids(self,
                           obj_class: str,
                           obj_ids: List[int],
                           obj_response_type: Type[ObjectResponse[T]],
                           params: BaseRequestParams = BaseRequestParams()) -> List[T]:
        """
        Get objects (steps, topics, ect.) from platform by given `obj_class`, `obj_ids` and `params`.
        To parse response of platform `obj_response_type` parametrized with `obj_type` is used.
        """
        objects = []
        for obj_id in obj_ids:
            objects += self.get_objects(obj_class, obj_response_type, params, obj_id)
        return objects

    def _fetch(self,
               obj_class: str,
               params: BaseRequestParams,
               obj_response_type: Type[ObjectResponse[T]],
               obj_id: Optional[int] = None) -> Optional[ObjectResponse[T]]:

        api_url = '{}/api/{}s'.format(self.host, obj_class)
        if obj_id is not None:
            api_url = '{}/{}'.format(api_url, obj_id)
        if params is not None:
            dict_params = {k: v for k, v in asdict(params).items() if v is not None}
            api_url = '{}?{}'.format(api_url, urllib.parse.urlencode(dict_params))
        if self.token is not None:
            raw_response = requests.get(api_url, headers={'Authorization': 'Token ' + self.token}, timeout=None)
        else:
            raw_response = requests.get(api_url, timeout=None)

        if raw_response is None or raw_response.status_code != 200:
            logging.warning(f"Failed to fetch {api_url}: {raw_response}")
            return None
        else:
            response_json = raw_response.json()

        preprocessed_response = kebab_to_snake_case(response_json)
        return from_dict(data_class=obj_response_type,
                         data=preprocessed_response,
                         config=Config(type_hooks={datetime.datetime: str_to_datetime}))

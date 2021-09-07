import urllib
from dataclasses import asdict
from typing import Dict, List

import requests
from dacite import from_dict

from data.common_api.response import PageRequestParams, Object, RequestParams
from data.utils.json import kebab_to_snake_case


class PlatformApi:

    def __init__(self, host: str, token: str = None):
        self.host = host
        self.token = token

    def fetch_object(self, obj_class: str, params: RequestParams, obj_id: int = None) -> Dict:
        api_url = '{}/api/{}s'.format(self.host, obj_class, obj_id)
        if obj_id is not None:
            api_url = '{}/{}'.format(api_url, obj_id)
        if params is not None:
            api_url = '{}?{}'.format(api_url, urllib.parse.urlencode(params))
        if self.token is not None:
            response = requests.get(api_url, headers={'Authorization': 'Bearer ' + self.token}).json()
        else:
            response = requests.get(api_url).json()
        return response

    def get_objects_from_pages(self, obj_class: str, obj_response_type, params: PageRequestParams) -> List[Object]:
        objects = []
        page = 1
        while True:
            print(f'Getting {obj_class} page: {page}')
            try:
                params.page = page
                response = self.fetch_object(obj_class, asdict(params))
                response_json = kebab_to_snake_case(response)
                response = from_dict(data_class=obj_response_type, data=response_json)
                objects += response.get_objects()
                if response.meta.has_next:
                    page += 1
                else:
                    return objects
            except Exception as e:
                print(f'Unable to get {obj_class}: {e}')
                return objects

    def get_objects_by_ids(self, obj_class: str, obj_response_type, params: PageRequestParams, obj_ids: List[int]) \
            -> List[Object]:
        objects = []
        for obj_id in obj_ids:
            page = 1
            while True:
                print(f'Getting object {obj_class} by id {obj_id} page: {page}')
                try:
                    params.page = page
                    response = self.fetch_object(obj_class, asdict(params), obj_id)
                    response_json = kebab_to_snake_case(response)
                    response = from_dict(data_class=obj_response_type, data=response_json)
                    objects += response.get_objects()
                    if response.meta.has_next:
                        page += 1
                    else:
                        break
                except Exception as e:
                    print(f'Unable to get {obj_class} with id {obj_id}: {e}')

        return objects

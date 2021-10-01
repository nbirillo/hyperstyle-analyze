import urllib
from dataclasses import asdict
from typing import List, Type, Optional, TypeVar

import requests
from dacite import from_dict

from analysis.src.python.data_collection.api.platform_entities import RequestParams, Object, Response
from analysis.src.python.data_collection.utils.csv_utils import save_objects_to_csv
from analysis.src.python.data_collection.utils.json_utils import kebab_to_snake_case

T = TypeVar('T', bound=Object)


# Base class for hyperskill and stepik clients which wraps data exchange process with platforms according to open APIs.
class PlatformClient:

    def __init__(self, host: str, token: str = None):
        self.host = host
        self.token = token

    def _fetch(self,
               obj_class: str,
               params: RequestParams,
               obj_response_type: Type[Response[T]],
               obj_id: int = None) -> Optional[Response[T]]:
        api_url = '{}/api/{}s'.format(self.host, obj_class, obj_id)
        if obj_id is not None:
            api_url = '{}/{}'.format(api_url, obj_id)
        if params is not None:
            dict_params = {k: v for k, v in asdict(params).items() if v is not None}
            api_url = '{}?{}'.format(api_url, urllib.parse.urlencode(dict_params))
        if self.token is not None:
            raw_response = requests.get(api_url, headers={'Authorization': 'Bearer ' + self.token})
        else:
            raw_response = requests.get(api_url)

        if raw_response.status_code == 200:
            response_json = raw_response.json()
        else:
            print(f"Failed to fetch {api_url}: {raw_response}")
            return None

        preprocessed_response = kebab_to_snake_case(response_json)
        response = from_dict(data_class=obj_response_type, data=preprocessed_response)
        return response

    def get_objects(self,
                    obj_class: str,
                    obj_type: Type[T],
                    obj_response_type: Type[Response[T]],
                    params: RequestParams,
                    obj_ids: List[int] = None,
                    save_to_csv: bool = False) -> List[T]:
        if obj_ids is None:
            objects = self._get_objects_all(obj_class, obj_response_type, params)
        else:
            objects = self._get_objects_by_ids(obj_class, obj_response_type, params, obj_ids)
        if save_to_csv:
            save_objects_to_csv(objects, obj_class, obj_type)
        return objects

    def _get_objects_all(self,
                         obj_class: str,
                         obj_response_type: Type[Response[T]],
                         params: RequestParams) -> List[T]:
        objects = []
        page = 1
        while True:
            print(f'Getting {obj_class} page: {page}')
            try:
                params.page = page
                response = self._fetch(obj_class, params, obj_response_type)
                if response is None:
                    return objects
                objects += response.get_objects()
                if response.meta.has_next:
                    page += 1
                else:
                    return objects
            except Exception as e:
                print(f'Unable to get {obj_class}: {e}')
                return objects

    def _get_objects_by_ids(self,
                            obj_class: str,
                            obj_response_type: Type[Response[T]],
                            params: RequestParams,
                            obj_ids: List[int]) -> List[T]:
        objects = []
        for obj_id in obj_ids:
            page = 1
            while True:
                print(f'Getting object {obj_class} by id {obj_id} page: {page}')
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
                    print(f'Unable to get {obj_class} with id {obj_id}: {e}')

        return objects

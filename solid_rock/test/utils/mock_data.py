"""
Copyright 2019 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
import hashlib
import inspect
from pathlib import Path

from solid_rock.api.sr.data import GsDataApi
from solid_rock.test.utils.mock_request import MockRequest


class MockData(MockRequest):
    api = GsDataApi
    method = 'query_data'
    api_method = GsDataApi.query_data

    def __init__(self, mocker, save_files=False, paths=None, application='sr-quant'):
        super().__init__(mocker, save_files, paths, application)
        self.paths = paths if paths else \
            Path(next(filter(lambda x: x.code_context and 'MockData' in x.code_context[0],
                             inspect.stack())).filename).parents[1]

    def mock_calc_create_files(self, *args, **kwargs):
        from orjson import orjson

        def get_json(*i_args, **i_kwargs):
            this_json = self.api_method(*i_args, **i_kwargs)

            return this_json
        result = get_json(*args, **kwargs)
        result_json = orjson.dumps(result,
                                   option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS | orjson.OPT_SORT_KEYS)
        request_id = self.get_request_id(args, kwargs)
        self.create_files(request_id, result_json)

        return result

    def get_request_id(self, args, kwargs):
        query = args[0]
        identifier = args[1] + '_' + query.where['bbid'] + '_' + str(query.start_date)
        return hashlib.md5(identifier.encode('utf-8')).hexdigest()

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
import logging
from typing import Tuple, List

from solid_rock.session import SrSession
from solid_rock.target.screens import Screen
from solid_rock.target.assets_screener import AssetScreenerRequest

_logger = logging.getLogger(__name__)


class GsScreenApi:

    @classmethod
    def get_screens(cls, screen_ids: List[str] = None, screen_names: List[str] = None, limit: int = 100) \
            -> Tuple[Screen]:
        url = '/screens?'
        if screen_ids:
            url += f'&id={"&id=".join(screen_ids)}'
        if screen_names:
            url += f'&name={"&name=".join(screen_names)}'
        return SrSession.current._get(f'{url}&limit={limit}', cls=Screen)['results']

    @classmethod
    def get_screen(cls, screen_id: str) -> Screen:
        return SrSession.current._get(f'/screens/{screen_id}', cls=Screen)

    @classmethod
    def create_screen(cls, screen: Screen) -> Screen:
        return SrSession.current._post('/screens', screen, cls=Screen)

    @classmethod
    def update_screen(cls, screen: Screen) -> Screen:
        return SrSession.current._put(f'/screens/{screen.id}', screen, cls=Screen)

    @classmethod
    def delete_screen(cls, screen_id: str) -> str:
        return SrSession.current._delete(f'/screens/{screen_id}')

    @classmethod
    def get_filter_options(cls) -> dict:
        return SrSession.current._get('/assets/screener/options')

    @classmethod
    def calculate(cls, payload: AssetScreenerRequest) -> dict:
        return SrSession.current._post('/assets/screener', payload=payload)

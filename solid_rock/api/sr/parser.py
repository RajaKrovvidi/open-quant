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

from solid_rock.session import SrSession

_logger = logging.getLogger(__name__)


class OqParserApi:
    """GS instrument parser API client implementation"""

    @classmethod
    def get_instrument_from_text_asset_class(cls, text: str, asset_class: str) -> dict:
        res = SrSession.current._post('/parser/quoteTicket', payload={'message': text, 'assetClass': asset_class})
        return res['ticket']['quote']['instrument']

    @classmethod
    def get_instrument_from_text(cls, text: str) -> dict:
        res = SrSession.current._post('/parser/portfolio', payload={'message': text})
        return res['instruments']

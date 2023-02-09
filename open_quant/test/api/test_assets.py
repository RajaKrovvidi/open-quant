"""
Copyright 2018 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

import datetime as dt

import dateutil.parser as dup
import pytest
import testfixtures
from open_quant.api.oq.assets import OqAssetApi, OqAsset, OqTemporalXRef, ENABLE_ASSET_CACHING
from open_quant.session import *
from open_quant.common import PositionType
from open_quant.target.assets import FieldFilterMap, Position, PositionSet, EntityQuery
from open_quant.target.common import XRef


def test_get_asset(mocker):
    marquee_id = 'MQA1234567890'

    mock_response = OqAsset(id=marquee_id, assetClass='Equity', type='Single Stock', name='Test Asset')

    # mock OqSession
    mocker.patch.object(OqSession.__class__, 'default_value',
                        return_value=OqSession.get(Environment.QA, 'client_id', 'secret'))
    mocker.patch.object(OqSession.current, '_get', return_value=mock_response)

    # run test
    response = OqAssetApi.get_asset(marquee_id)

    OqSession.current._get.assert_called_with('/assets/{id}'.format(id=marquee_id), cls=OqAsset)

    assert response == mock_response


def test_get_many_assets(mocker, monkeypatch):
    marquee_id_1 = 'MQA1234567890'
    marquee_id_2 = 'MQA4567890123'

    query = {'id': [marquee_id_1, marquee_id_2]}
    as_of = dt.datetime.utcnow()

    inputs = EntityQuery(
        where=FieldFilterMap(**query),
        fields=None,
        asOfTime=as_of,
        limit=100
    )

    mock_response = {'results': (
        OqAsset.from_dict({'id': marquee_id_1, 'assetClass': 'Equity', 'type': 'Single Stock', 'name': 'Test 1'}),
        OqAsset.from_dict({'id': marquee_id_2, 'assetClass': 'Equity', 'type': 'Single Stock', 'name': 'Test 2'})
    )}

    expected_response = (
        OqAsset(id=marquee_id_1, assetClass='Equity', type='Single Stock', name='Test 1'),
        OqAsset(id=marquee_id_2, assetClass='Equity', type='Single Stock', name='Test 2')
    )

    # mock OqSession
    mocker.patch.object(OqSession.__class__, 'default_value',
                        return_value=OqSession.get(Environment.QA, 'client_id', 'secret'))
    mocker.patch.object(OqSession.current, '_post', return_value=mock_response)

    # run test
    monkeypatch.delenv(ENABLE_ASSET_CACHING, raising=False)
    response = OqAssetApi.get_many_assets(id=[marquee_id_1, marquee_id_2], as_of=as_of)
    OqSession.current._post.assert_called_with('/assets/query', cls=OqAsset, payload=inputs)
    assert response == expected_response

    monkeypatch.setenv(ENABLE_ASSET_CACHING, '1')  # run 2x with cache on
    response = OqAssetApi.get_many_assets(id=[marquee_id_1, marquee_id_2], as_of=as_of)
    assert response == expected_response
    response = OqAssetApi.get_many_assets(id=[marquee_id_1, marquee_id_2], as_of=as_of)
    assert response == expected_response


def test_get_asset_xrefs(mocker):
    marquee_id = 'MQA1234567890'

    mock_response = {'xrefs': (
        {
            'startDate': '1952-01-01',
            'endDate': '2018-12-31',
            'identifiers': {
                'ric': '.GSTHHOLD',
                'bbid': 'GSTHHOLD',
                'cusip': '9EQ24FOLD',
                'ticker': 'GSTHHOLD'
            }
        },
        {
            'startDate': '2019-01-01',
            'endDate': '2952-12-31',
            'identifiers': {
                'ric': '.GSTHHVIP',
                'bbid': 'GSTHHVIP',
                'cusip': '9EQ24FPE5',
                'ticker': 'GSTHHVIP',
            }
        }
    )}

    expected_response = (
        OqTemporalXRef(dt.date(1952, 1, 1), dt.date(2018, 12, 31), XRef(
            ric='.GSTHHOLD',
            bbid='GSTHHOLD',
            cusip='9EQ24FOLD',
            ticker='GSTHHOLD',
        )),
        OqTemporalXRef(dt.date(2019, 1, 1), dt.date(2952, 12, 31), XRef(
            ric='.GSTHHVIP',
            bbid='GSTHHVIP',
            cusip='9EQ24FPE5',
            ticker='GSTHHVIP',
        ))
    )

    # mock OqSession
    mocker.patch.object(OqSession.__class__, 'default_value',
                        return_value=OqSession.get(Environment.QA, 'client_id', 'secret'))
    mocker.patch.object(OqSession.current, '_get', return_value=mock_response)

    # run test
    response = OqAssetApi.get_asset_xrefs(marquee_id)

    OqSession.current._get.assert_called_with('/assets/{id}/xrefs'.format(id=marquee_id))
    testfixtures.compare(response, expected_response)


def test_get_asset_positions_for_date(mocker):
    marquee_id = 'MQA1234567890'
    position_date = dt.date(2019, 2, 19)

    mock_response = {'results': (
        {
            'id': 'mock1',
            'positionDate': '2019-02-19',
            'lastUpdateTime': '2019-02-19T12:10:32.401Z',
            'positions': [
                {'assetId': 'MQA123', 'quantity': 0.3},
                {'assetId': 'MQA456', 'quantity': 0.7}
            ],
            'type': 'open',
            'divisor': 100
        },
        {
            'id': 'mock2',
            'positionDate': '2019-02-19',
            'lastUpdateTime': '2019-02-20T05:04:32.981Z',
            'positions': [
                {'assetId': 'MQA123', 'quantity': 0.4},
                {'assetId': 'MQA456', 'quantity': 0.6}
            ],
            'type': 'close',
            'divisor': 120
        }
    )}

    expected_response = (
        PositionSet(
            id_='mock1',
            position_date=dt.date(2019, 2, 19),
            last_update_time=dup.parse('2019-02-19T12:10:32.401Z'),
            positions=(
                Position(assetId='MQA123', quantity=0.3),
                Position(assetId='MQA456', quantity=0.7)
            ),
            type_='open',
            divisor=100),
        PositionSet(
            id_='mock2',
            position_date=dt.date(2019, 2, 19),
            last_update_time=dup.parse('2019-02-20T05:04:32.981Z'),
            positions=(
                Position(assetId='MQA123', quantity=0.4),
                Position(assetId='MQA456', quantity=0.6)
            ),
            type_='close',
            divisor=120)
    )

    # mock OqSession
    mocker.patch.object(OqSession.__class__, 'default_value',
                        return_value=OqSession.get(Environment.QA, 'client_id', 'secret'))
    mocker.patch.object(OqSession.current, '_get', return_value=mock_response)

    # run test
    response = OqAssetApi.get_asset_positions_for_date(marquee_id, position_date)

    OqSession.current._get.assert_called_with('/assets/{id}/positions/{date}'.format(
        id=marquee_id, date=position_date))

    testfixtures.compare(response, expected_response)

    mock_response = {'results': [{
        'id': 'mock',
        'positionDate': '2019-02-19',
        'lastUpdateTime': '2019-02-20T05:04:32.981Z',
        'positions': [
            {'assetId': 'MQA123', 'quantity': 0.4},
            {'assetId': 'MQA456', 'quantity': 0.6}
        ],
        'type': 'close',
        'divisor': 120
    }]}

    expected_response = (
        PositionSet(
            id_='mock',
            position_date=dt.date(2019, 2, 19),
            last_update_time=dup.parse('2019-02-20T05:04:32.981Z'),
            positions=(
                Position(assetId='MQA123', quantity=0.4),
                Position(assetId='MQA456', quantity=0.6)
            ),
            type_='close',
            divisor=120),
    )

    # mock OqSession
    mocker.patch.object(OqSession.__class__, 'default_value',
                        return_value=OqSession.get(Environment.QA, 'client_id', 'secret'))
    mocker.patch.object(OqSession.current, '_get', return_value=mock_response)

    # run test

    response = OqAssetApi.get_asset_positions_for_date(marquee_id, position_date, PositionType.CLOSE)

    testfixtures.compare(response, expected_response)

    OqSession.current._get.assert_called_with('/assets/{id}/positions/{date}?type=close'.format(
        id=marquee_id, date=position_date))


if __name__ == "__main__":
    pytest.main(args=[__file__])

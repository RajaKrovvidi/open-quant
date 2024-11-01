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

from solid_rock.api.sr.portfolios import GsPortfolioApi, Portfolio, PositionSet
from solid_rock.session import *
from solid_rock.target.common import Position


def test_get_many_portfolios(mocker):
    id_1 = 'MP1'
    id_2 = 'MP2'

    mock_response = {'results': (
        Portfolio.from_dict({'id': id_1, 'currency': 'USD', 'name': 'Example Port 1'}),
        Portfolio.from_dict({'id': id_2, 'currency': 'USD', 'name': 'Example Port 2'})
    ), 'totalResults': 2}

    expected_response = (
        Portfolio(id=id_1, currency='USD', name='Example Port 1'),
        Portfolio(id=id_2, currency='USD', name='Example Port 2')
    )

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_get', return_value=mock_response)

    # run test
    response = GsPortfolioApi.get_portfolios()
    SrSession.current._get.assert_called_with('/portfolios?&limit=100', cls=Portfolio)
    assert response == expected_response


def test_get_portfolio(mocker):
    id_1 = 'MP1'
    mock_response = Portfolio(id=id_1, currency='USD', name='Example Port')

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_get', return_value=mock_response)

    # run test
    response = GsPortfolioApi.get_portfolio(id_1)
    SrSession.current._get.assert_called_with('/portfolios/{id}'.format(id=id_1), cls=Portfolio)
    assert response == mock_response


def test_create_portfolio(mocker):
    id_1 = 'MP1'

    portfolio = Portfolio(id=id_1, currency='USD', name='Example Port')

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_post', return_value=portfolio)

    # run test
    response = GsPortfolioApi.create_portfolio(portfolio)
    SrSession.current._post.assert_called_with('/portfolios', portfolio, cls=Portfolio)
    assert response == portfolio


def test_update_portfolio(mocker):
    id_1 = 'MP1'

    portfolio = Portfolio(id=id_1, currency='USD', name='Example Port Renamed')

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_put', return_value=portfolio)

    # run test
    response = GsPortfolioApi.update_portfolio(portfolio)
    SrSession.current._put.assert_called_with('/portfolios/{id}'.format(id=id_1), portfolio, cls=Portfolio)
    assert response == portfolio


def test_delete_portfolio(mocker):
    id_1 = 'MP1'

    mock_response = "Successfully deleted portfolio."

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_delete', return_value=mock_response)

    # run test
    response = GsPortfolioApi.delete_portfolio(id_1)
    SrSession.current._delete.assert_called_with('/portfolios/{id}'.format(id=id_1))
    assert response == mock_response


def test_get_portfolio_positions(mocker):
    id_1 = 'MP1'
    start_date = dt.date(2019, 2, 18)
    end_date = dt.date(2019, 2, 19)

    mock_response = {'positionSets': (
        {
            'id': 'mock1',
            'positionDate': '2019-02-18',
            'lastUpdateTime': '2019-02-19T12:10:32.401Z',
            'positions': [
                {'assetId': 'MQA123', 'quantity': 0.3},
                {'assetId': 'MQA456', 'quantity': 0.7}
            ]
        },
        {
            'id': 'mock2',
            'positionDate': '2019-02-19',
            'lastUpdateTime': '2019-02-20T05:04:32.981Z',
            'positions': [
                {'assetId': 'MQA123', 'quantity': 0.4},
                {'assetId': 'MQA456', 'quantity': 0.6}
            ]
        }
    )}

    expected_response = (
        PositionSet(
            id_='mock1',
            position_date=start_date,
            last_update_time=dup.parse('2019-02-19T12:10:32.401Z'),
            positions=(
                Position(assetId='MQA123', quantity=0.3),
                Position(assetId='MQA456', quantity=0.7)
            )),
        PositionSet(
            id_='mock2',
            position_date=end_date,
            last_update_time=dup.parse('2019-02-20T05:04:32.981Z'),
            positions=(
                Position(assetId='MQA123', quantity=0.4),
                Position(assetId='MQA456', quantity=0.6)
            ))
    )

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_get', return_value=mock_response)

    # run test
    response = GsPortfolioApi.get_positions(id_1, start_date, end_date)

    SrSession.current._get.assert_called_with(
        '/portfolios/{id}/positions?type=close&startDate={sd}&endDate={ed}'.format(id=id_1, sd=start_date, ed=end_date))

    assert response == expected_response


def test_get_portfolio_positions_for_date(mocker):
    id_1 = 'MP1'
    date = dt.date(2019, 2, 18)

    mock_response = {'results': (
        PositionSet.from_dict({
            'id': 'mock1',
            'positionDate': '2019-02-18',
            'lastUpdateTime': '2019-02-19T12:10:32.401Z',
            'positions': [
                {'assetId': 'MQA123', 'quantity': 0.3},
                {'assetId': 'MQA456', 'quantity': 0.7}
            ]
        }),
    )}

    expected_response = (
        PositionSet(
            id_='mock1',
            position_date=date,
            last_update_time=dup.parse('2019-02-19T12:10:32.401Z'),
            positions=(
                Position(assetId='MQA123', quantity=0.3),
                Position(assetId='MQA456', quantity=0.7)
            ))
    )

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_get', return_value=mock_response)

    # run test
    response = GsPortfolioApi.get_positions_for_date(id_1, date)

    SrSession.current._get.assert_called_with(
        '/portfolios/{id}/positions/{d}?type=close'.format(id=id_1, d=date),
        cls=PositionSet)

    assert response == expected_response


def test_get_latest_portfolio_positions(mocker):
    id_1 = 'MP1'
    date = dt.date(2019, 2, 18)

    mock_response = {
        'results': {
            'id': 'mock1',
            'positionDate': '2019-02-18',
            'lastUpdateTime': '2019-02-19T12:10:32.401Z',
            'positions': [
                {'assetId': 'MQA123', 'quantity': 0.3},
                {'assetId': 'MQA456', 'quantity': 0.7}
            ]
        }
    }

    expected_response = PositionSet(
        id_='mock1',
        position_date=date,
        last_update_time=dup.parse('2019-02-19T12:10:32.401Z'),
        positions=(
            Position(assetId='MQA123', quantity=0.3),
            Position(assetId='MQA456', quantity=0.7)
        ))

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_get', return_value=mock_response)

    # run test
    response = GsPortfolioApi.get_latest_positions(id_1)

    SrSession.current._get.assert_called_with(
        '/portfolios/{id}/positions/last?type=close'.format(id=id_1))

    assert response == expected_response


def test_get_portfolio_position_dates(mocker):
    id_1 = 'MP1'

    mock_response = {'results': ('2019-02-18', '2019-02-19'), 'totalResults': 2}

    expected_response = (dt.date(2019, 2, 18), dt.date(2019, 2, 19))

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_get', return_value=mock_response)

    # run test
    response = GsPortfolioApi.get_position_dates(id_1)

    SrSession.current._get.assert_called_with('/portfolios/{id}/positions/dates'.format(id=id_1))

    assert response == expected_response


def test_portfolio_positions_data(mocker):
    mock_response = {'results': [
        {
            'underlyingAssetId': 'MA4B66MW5E27UAFU2CD',
            'divisor': 8305900333.262549,
            'quantity': 0.016836826158,
            'positionType': 'close',
            'bbid': 'EXPE UW',
            'assetId': 'MA4B66MW5E27U8P32SB',
            'positionDate': '2019-11-07',
            'assetClassificationsGicsSector': 'Consumer Discretionary',
            'closePrice': 98.29,
            'ric': 'EXPE.OQ'
        },
    ]}

    expected_response = [
        {
            'underlyingAssetId': 'MA4B66MW5E27UAFU2CD',
            'divisor': 8305900333.262549,
            'quantity': 0.016836826158,
            'positionType': 'close',
            'bbid': 'EXPE UW',
            'assetId': 'MA4B66MW5E27U8P32SB',
            'positionDate': '2019-11-07',
            'assetClassificationsGicsSector': 'Consumer Discretionary',
            'closePrice': 98.29,
            'ric': 'EXPE.OQ'
        },
    ]

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_get', return_value=mock_response)

    # run test
    response = GsPortfolioApi.get_positions_data('portfolio_id', dt.date(2020, 1, 1), dt.date(2021, 1, 1))

    SrSession.current._get.assert_called_with(
        '/portfolios/portfolio_id/positions/data?startDate=2020-01-01&endDate=2021-01-01')

    assert response == expected_response


def test_get_risk_models_by_coverage(mocker):
    mock_response = {'results': [
        {
            'model': "AXUS4S",
            'businessDate': "2021-03-18",
            'percentInModel': 0.9984356667970278
        },
        {
            'model': "AXUS4M",
            'businessDate': "2021-03-18",
            'percentInModel': 0.9984356667970278
        }
    ]
    }

    expected_response = [
        {
            'model': "AXUS4S",
            'businessDate': "2021-03-18",
            'percentInModel': 0.9984356667970278
        },
        {
            'model': "AXUS4M",
            'businessDate': "2021-03-18",
            'percentInModel': 0.9984356667970278
        }
    ]

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_get', return_value=mock_response)

    # run test
    response = GsPortfolioApi.get_risk_models_by_coverage('portfolio_id')

    SrSession.current._get.assert_called_with('/portfolios/portfolio_id/models?sortByTerm=Medium')

    assert response == expected_response

"""
Copyright 2020 Goldman Sachs.
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

import datetime as dt

import pandas as pd
import pytest
from pandas.testing import assert_series_equal
from testfixtures import Replacer
from testfixtures.mock import Mock

import solid_rock.timeseries.measures as tm_rates
import solid_rock.timeseries.measures_fx_vol as tm_fxo
import solid_rock.timeseries.measures_xccy as tm
from solid_rock.api.sr.assets import OqAsset
from solid_rock.api.sr.data import GsDataApi, MarketDataResponseFrame, QueryType
from solid_rock.errors import MqError, MqValueError
from solid_rock.session import SrSession, Environment
from solid_rock.target.common import PricingLocation
from solid_rock.test.timeseries.utils import mock_request
from solid_rock.timeseries import Currency, Cross, Bond, CurrencyEnum, SecurityMaster
from solid_rock.timeseries.measures_fx_vol import _currencypair_to_tdapi_fxo_asset, _currencypair_to_tdapi_fxfwd_asset

_index = [pd.Timestamp('2021-03-30')]
_test_datasets = ('TEST_DATASET',)


def test_currencypair_to_tdapi_fxfwd_asset():
    mock_eur = Cross('MA8RY265Q34P7TWZ', 'EURUSD')
    assert _currencypair_to_tdapi_fxfwd_asset(mock_eur) == "MA8RY265Q34P7TWZ"


def test_currencypair_to_tdapi_fxo_asset(mocker):
    replace = Replacer()
    mocker.patch.object(SrSession.__class__, 'current',
                        return_value=SrSession.get(Environment.QA, 'client_id', 'secret'))
    mocker.patch.object(SrSession.current, '_get', side_effect=mock_request)
    mocker.patch.object(SecurityMaster, 'get_asset', side_effect=mock_request)
    bbid_mock = replace('solid_rock.timeseries.measures_fx_vol.Asset.get_identifier', Mock())

    with tm_rates.PricingContext(dt.date.today()):
        cur = [
            {
                "currency_assetId": "MAK1FHKH5P5GJSHH",
                "currency": "USDJPY",
                "id": "MAQ7YRZ4P94M9N9C"
            },
            {
                "currency_assetId": "MA66CZBQJST05XKG",
                "currency": "GBPUSD",
                "id": "MAEHA6WVHJ2S3JY9"
            },
            {
                "currency_assetId": "MAJNQPFGN1EBDHAE",
                "currency": "EURUSD",
                "id": "MAT1J37C9ZPMANFP"
            },
        ]
        for c in cur:
            print(c)
            asset = Currency(c.get("currency_assetId"), c.get("currency"))
            bbid_mock.return_value = c.get("currency")
            mqid = _currencypair_to_tdapi_fxo_asset(asset)
            assert mqid == c.get("id")

        bbid_mock.return_value = None
        assert _currencypair_to_tdapi_fxo_asset(asset) == c.get("currency_assetId")
        replace.restore()


def test_get_fxo_defaults():
    result_dict = dict(under="AUD", over="JPY",
                       expirationTime="NYC", premiumPaymentDate="Fwd Settle")
    defaults = tm_fxo._get_fxo_defaults("AUDJPY")
    assert result_dict == defaults

    result_dict = dict(under="CAD", over="JPY",
                       expirationTime="NYC", premiumPaymentDate="Fwd Settle")
    defaults = tm_fxo._get_fxo_defaults("CADJPY")
    assert result_dict == defaults

    result_dict = dict(under="EUR", over="NOK",
                       expirationTime="NYC", premiumPaymentDate="Fwd Settle")
    defaults = tm_fxo._get_fxo_defaults("EURNOK")
    assert result_dict == defaults

    result_dict = dict(under="GBP", over="USD",
                       expirationTime="NYC", premiumPaymentDate="Fwd Settle")
    defaults = tm_fxo._get_fxo_defaults("GBPUSD")
    assert result_dict == defaults

    result_dict = dict(under="EUR", over="NZD",
                       expirationTime="NYC", premiumPaymentDate="Fwd Settle")
    defaults = tm_fxo._get_fxo_defaults("EURNZD")
    assert result_dict == defaults


def test_get_fxo_csa_terms():
    assert dict(csaTerms='USD-1') == tm_fxo._get_fx_csa_terms()


def test_check_valid_indices():
    valid_indices = ['LIBOR']
    for index in valid_indices:
        assert tm.CrossCurrencyRateOptionType[index] == tm._check_crosscurrency_rateoption_type(CurrencyEnum.GBP, index)

    invalid_indices = ['LIBORED', 'TestRateOption']
    for index in invalid_indices:
        with pytest.raises(MqError):
            tm._check_crosscurrency_rateoption_type(CurrencyEnum.GBP, index)


def test_cross_stored_direction_for_fx_vol():
    replace = Replacer()
    mock_gbp = Cross('MA26QSMPX9990G66', 'GBPUSD')
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'GBPUSD'
    assert "MAEHA6WVHJ2S3JY9" == tm_fxo.cross_stored_direction_for_fx_vol(mock_gbp)
    replace.restore()
    mock_gbp_reversed = Cross('MA26QSMPX9990G67', 'USDGBP')
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.side_effect = ['USDGBP', 'GBPUSD']
    assets = replace('solid_rock.markets.securities.SecurityMaster.get_asset', Mock())
    assets.return_value = mock_gbp
    assert "MAEHA6WVHJ2S3JY9" == tm_fxo.cross_stored_direction_for_fx_vol(mock_gbp_reversed)
    replace.restore()

    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.side_effect = [mock_gbp, 'GBPUSD']
    assets = replace('solid_rock.markets.securities.SecurityMaster.get_asset', Mock())
    assets.return_value = mock_gbp
    assert "MAEHA6WVHJ2S3JY9" == tm_fxo.cross_stored_direction_for_fx_vol(mock_gbp)
    replace.restore()


def test_get_tdapi_fxo_assets():
    mock_asset_1 = OqAsset(asset_class='FX', id='MAW8SAXPSKYA94E2', type_='Option', name='Test_asset')
    mock_asset_2 = OqAsset(asset_class='FX', id='MATDD783JM1C2GGD', type_='Option', name='Test_asset')

    replace = Replacer()
    assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
    assets.return_value = [mock_asset_1]
    assert 'MAW8SAXPSKYA94E2' == tm_fxo._get_tdapi_fxo_assets()
    replace.restore()

    assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
    assets.return_value = [mock_asset_1, mock_asset_2]
    kwargs = dict(asset_parameters_expiration_date='5y', asset_parameters_call_currency='USD',
                  asset_parameters_put_currency='EUR')
    with pytest.raises(MqValueError):
        tm_fxo._get_tdapi_fxo_assets(**kwargs)
    replace.restore()

    assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
    assets.return_value = []
    kwargs = dict(asset_parameters_expiration_date='5y', asset_parameters_call_currency='USD',
                  asset_parameters_put_currency='EUR')
    with pytest.raises(MqValueError):
        tm_fxo._get_tdapi_fxo_assets(**kwargs)
    replace.restore()

    assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
    assets.return_value = [mock_asset_1, mock_asset_2]
    kwargs = dict()
    assert ['MAW8SAXPSKYA94E2', 'MATDD783JM1C2GGD'] == tm._get_tdapi_crosscurrency_rates_assets(**kwargs)
    replace.restore()

    #   test case will test matching sofr maturity with libor leg and flipping legs to get right asset
    kwargs = dict(Asset_class='FX',
                  type='Option',
                  asset_parameters_call_currency='USD',
                  asset_parameters_put_currency='EUR',
                  asset_parameters_expiration_date='1m',
                  asset_parameters_expiration_time='NYC',
                  asset_parameters_option_type='Put',
                  asset_parameters_premium_payment_date='Fwd Settle',
                  asset_parameters_strike_price_relative='10d',
                  pricing_location='NYC')

    assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
    assets.return_value = [mock_asset_1]
    assert 'MAW8SAXPSKYA94E2' == tm_fxo._get_tdapi_fxo_assets(**kwargs)
    replace.restore()


def mock_curr(_cls, _q):
    d = {
        'impliedVolatility': [1, 2, 3],
        'fwdPoints': [4, 5, 6]
    }
    df = MarketDataResponseFrame(data=d, index=_index * 3)
    df.dataset_ids = _test_datasets
    return df


def test_fx_vol_measure(mocker):
    replace = Replacer()
    args = dict(expiry_tenor='1m', strike='ATMF', option_type='Put',
                expiration_location=None,
                location=None, premium_payment_date=None, )

    mock_gbp = Cross('MA26QSMPX9990G66', 'GBPUSD')
    args['asset'] = mock_gbp
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'GBPUSD'

    args['expiry_tenor'] = '1yr'
    with pytest.raises(MqValueError):
        tm_fxo.implied_volatility_new(**args)
    args['expiry_tenor'] = '1m'

    args['real_time'] = True
    with pytest.raises(NotImplementedError):
        tm_fxo.implied_volatility_new(**args)
    args['real_time'] = False

    args['asset'] = Cross('MA666', 'USDAED')
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'AEDUSD'
    with pytest.raises(NotImplementedError):
        tm_fxo.implied_volatility_new(**args)
    args['asset'] = mock_gbp

    args['asset'] = Bond('MA667', 'TEST')
    with pytest.raises(NotImplementedError):
        tm_fxo.implied_volatility_new(**args)
    args['asset'] = mock_gbp

    args['asset'] = Cross('MA667', 'GBPUSD')
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'GBPUSD'
    identifiers = replace('solid_rock.timeseries.measures_fx_vol._get_tdapi_fxo_assets', Mock())
    identifiers.return_value = {'MA7F5P92330NGKAR'}
    mocker.patch.object(GsDataApi, 'get_market_data', return_value=mock_curr(None, None))
    actual = tm_fxo.implied_volatility_new(**args)
    expected = tm.ExtendedSeries([1, 2, 3], index=_index * 3, name='impliedVolatility')
    expected.dataset_ids = _test_datasets
    assert_series_equal(expected, actual)
    assert actual.dataset_ids == _test_datasets

    args['asset'] = Cross('MA667', 'USDCAD')
    args['location'] = PricingLocation.LDN
    args['premium_payment_date'] = 'Fwd Settle'
    args['expiration_location'] = 'NYC'
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'USDCAD'
    identifiers = replace('solid_rock.timeseries.measures_fx_vol._get_tdapi_fxo_assets', Mock())
    identifiers.return_value = {'MA7F5P92330NGKAR'}
    mocker.patch.object(GsDataApi, 'get_market_data', return_value=mock_curr(None, None))
    actual = tm_fxo.implied_volatility_new(**args)
    expected = tm.ExtendedSeries([1, 2, 3], index=_index * 3, name='impliedVolatility')
    expected.dataset_ids = _test_datasets
    assert_series_equal(expected, actual)
    assert actual.dataset_ids == _test_datasets

    args['option_type'] = 'Call'
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'GBPUSD'
    identifiers = replace('solid_rock.timeseries.measures_fx_vol._get_tdapi_fxo_assets', Mock())
    identifiers.return_value = {'MA7F5P92330NGKAR'}
    mocker.patch.object(GsDataApi, 'get_market_data', return_value=mock_curr(None, None))
    actual = tm_fxo.implied_volatility_new(**args)
    expected = tm.ExtendedSeries([1, 2, 3], index=_index * 3, name='impliedVolatility')
    expected.dataset_ids = _test_datasets
    assert_series_equal(expected, actual)
    assert actual.dataset_ids == _test_datasets

    replace.restore()


def test_fwd_points(mocker):
    replace = Replacer()
    args = dict(settlement_date="6m", location='LDN')
    mock_eur = Cross('MAGZMXVM0J282ZTR', 'EURUSD')
    args['asset'] = mock_eur
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'EURUSD'

    args['settlement_date'] = '1yr'
    with pytest.raises(MqValueError):
        tm_fxo.fwd_points(**args)
    args['settlement_date'] = '6m'

    args['real_time'] = True
    with pytest.raises(NotImplementedError):
        tm_fxo.fwd_points(**args)
    args['real_time'] = False

    args['asset'] = Cross('MAGZMXVM0J282ZTR', 'EURUSD')
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'EURUSD'
    identifiers = replace('solid_rock.timeseries.measures_fx_vol._get_tdapi_fxo_assets', Mock())
    identifiers.return_value = {'MAGZMXVM0J282ZTR'}
    mocker.patch.object(GsDataApi, 'get_market_data', return_value=mock_curr(None, None))
    actual = tm_fxo.fwd_points(**args)
    expected = tm.ExtendedSeries([4, 5, 6], index=_index * 3, name='fwdPoints')
    expected.dataset_ids = _test_datasets
    assert_series_equal(expected, actual)
    assert actual.dataset_ids == _test_datasets

    args['location'] = None
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'EURUSD'
    identifiers = replace('solid_rock.timeseries.measures_fx_vol._get_tdapi_fxo_assets', Mock())
    identifiers.return_value = {'MAGZMXVM0J282ZTR'}
    mocker.patch.object(GsDataApi, 'get_market_data', return_value=mock_curr(None, None))
    actual = tm_fxo.fwd_points(**args)
    expected = tm.ExtendedSeries([4, 5, 6], index=_index * 3, name='fwdPoints')
    expected.dataset_ids = _test_datasets
    assert_series_equal(expected, actual)
    assert actual.dataset_ids == _test_datasets

    replace.restore()


def test_fx_vol_measure_legacy(mocker):
    replace = Replacer()
    args = dict(tenor='1m', strike_reference=tm_fxo.VolReference('delta_neutral'), relative_strike=0,
                location=None, legacy_implementation=True)

    mock_gbp = Cross('MA26QSMPX9990G66', 'GBPUSD')
    args['asset'] = mock_gbp
    expected = tm.ExtendedSeries([1, 2, 3], index=_index * 3, name='impliedVolatility')
    expected.dataset_ids = _test_datasets
    mocker.patch.object(tm_rates, 'get_historical_and_last_for_measure',
                        return_value=expected)
    mocker.patch.object(tm_rates, '_extract_series_from_df',
                        return_value=expected)
    xrefs = replace('solid_rock.timeseries.measures.cross_stored_direction_for_fx_vol', Mock())
    xrefs.return_value = 'MA26QSMPX9990G66'
    actual = tm_fxo.implied_volatility_fxvol(**args)
    assert_series_equal(expected, actual)
    replace.restore()

    args['legacy_implementation'] = False
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = None
    with pytest.raises(MqValueError):
        tm_fxo.implied_volatility_fxvol(**args)

    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'GBPUSD'
    xrefs = replace('solid_rock.timeseries.measures._cross_stored_direction_helper', Mock())
    xrefs.return_value = 'GBPUSD'
    mocker.patch.object(tm_fxo, 'implied_volatility_new',
                        return_value=expected)
    actual = tm_fxo.implied_volatility_fxvol(**args)
    assert_series_equal(expected, actual)

    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'USDUSD'
    xrefs = replace('solid_rock.timeseries.measures_fx_vol._cross_stored_direction_helper', Mock())
    xrefs.return_value = 'GBPUSD'
    assets = replace('solid_rock.markets.securities.SecurityMaster.get_asset', Mock())
    assets.return_value = mock_gbp
    actual = tm_fxo.implied_volatility_fxvol(**args)
    assert_series_equal(expected, actual)

    args['strike_reference'] = tm_fxo.VolReference('delta_call')
    args['relative_strike'] = 25
    actual = tm_fxo.implied_volatility_fxvol(**args)
    assert_series_equal(expected, actual)

    args['strike_reference'] = tm_fxo.VolReference('delta_put')
    args['relative_strike'] = 25
    actual = tm_fxo.implied_volatility_fxvol(**args)
    assert_series_equal(expected, actual)

    args['strike_reference'] = tm_fxo.VolReference('spot')
    args['relative_strike'] = 100
    actual = tm_fxo.implied_volatility_fxvol(**args)
    assert_series_equal(expected, actual)

    args['strike_reference'] = tm_fxo.VolReference('forward')
    args['relative_strike'] = 100
    actual = tm_fxo.implied_volatility_fxvol(**args)
    assert_series_equal(expected, actual)

    args['strike_reference'] = tm_fxo.VolReference('normalized')
    args['relative_strike'] = 100
    xrefs = replace('solid_rock.timeseries.measures_fx_vol._preprocess_implied_vol_strikes_fx', Mock())
    xrefs.return_value = ['normalized', 0]
    with pytest.raises(MqValueError):
        tm_fxo.implied_volatility_fxvol(**args)

    replace.restore()


def mock_df():
    d = {
        'strikeVol': [5, 1, 2],
    }
    df = MarketDataResponseFrame(data=d, index=_index * 3)
    df.dataset_ids = "FX_VOLATILITY_SWAP"
    return df


def test_vol_swap_strike_raises_exception():
    with pytest.raises(NotImplementedError):
        mock_asset_1 = OqAsset(asset_class='FX', id='MAW8SAXPSKYA94E2', type_='Option', name='Test_asset')
        tm_fxo.vol_swap_strike(mock_asset_1, "none", "none", location=PricingLocation.LDN, real_time=True)


def test_vol_swap_strike_unsupported_cross():
    with pytest.raises(NotImplementedError):
        replace = Replacer()
        mock_asset_1 = Cross('MA667', 'USDPLN')
        xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
        xrefs.return_value = 'USDPLN'

        tm_fxo.vol_swap_strike(mock_asset_1, "none", "none", location=PricingLocation.LDN, real_time=False)
    replace.restore()


def test_vol_swap_strike_matches_multiple_assets():
    with pytest.raises(MqValueError):
        replace = Replacer()
        base = Cross('MA667', 'EURUSD')
        xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
        xrefs.return_value = 'EURUSD'
        mock_asset_1 = OqAsset(asset_class='FX', id='MA123', type_='VolatilitySwap', name='Test_asset')
        assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
        assets.return_value = [mock_asset_1, mock_asset_1]
        tm_fxo.vol_swap_strike(base, None, location=PricingLocation.LDN, real_time=False)
    replace.restore()


def test_vol_swap_strike_matches_no_assets():
    with pytest.raises(MqValueError):
        replace = Replacer()
        base = Cross('MA667', 'EURUSD')
        xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
        xrefs.return_value = 'EURUSD'

        assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
        assets.return_value = []
        tm_fxo.vol_swap_strike(base, None, location=PricingLocation.LDN, real_time=False)
    replace.restore()


def test_vol_swap_strike_matches_no_assets_when_expiry_tenor_is_not_none():
    with pytest.raises(MqValueError):
        replace = Replacer()
        base = Cross('MA667', 'EURUSD')
        xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
        xrefs.return_value = 'EURUSD'

        mock_asset_1 = OqAsset(asset_class='FX', id='MA123', type_='VolatilitySwap', name='Test_asset',
                               parameters={"lastFixingDate": "1y"})

        mock_asset_2 = OqAsset(asset_class='FX', id='MA123', type_='VolatilitySwap', name='Test_asset',
                               parameters={"lastFixingDate": "1y"})

        assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
        assets.return_value = [mock_asset_1, mock_asset_2]

        tm_fxo.vol_swap_strike(base, "10m", location=PricingLocation.LDN, real_time=False)
    replace.restore()


def test_currencypair_to_tdapi_fx_vol_swap_asset():
    replace = Replacer()
    base = Cross('MA667', 'EURUSD')
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'EURUSD'

    asset = tm_fxo._currencypair_to_tdapi_fx_vol_swap_asset(base)
    assert asset == "MA66A4X4PRTC3N7B"
    replace.restore()


def test_vol_swap_strike():
    replace = Replacer()
    base = Cross('MA667', 'EURUSD')
    xrefs = replace('solid_rock.timeseries.measures.Asset.get_identifier', Mock())
    xrefs.return_value = 'EURUSD'

    mock_asset_1 = OqAsset(asset_class='FX', id='MA123', type_='VolatilitySwap', name='Test_asset',
                           parameters={"lastFixingDate": "1y"})
    mock_asset_2 = OqAsset(asset_class='FX', id='MA123', type_='VolatilitySwap', name='Test_asset',
                           parameters={"lastFixingDate": "2y"})

    assets = replace('solid_rock.timeseries.measures.OqAssetApi.get_many_assets', Mock())
    assets.return_value = [mock_asset_1, mock_asset_2]
    mock_data = replace('solid_rock.timeseries.measures.GsDataApi.get_market_data', Mock())
    mock_data.return_value = mock_df()
    actual = tm_fxo.vol_swap_strike(base, "1y", location=PricingLocation.LDN, real_time=False)
    assert_series_equal(tm_rates._extract_series_from_df(mock_df(), QueryType.STRIKE_VOL), actual)

    actual = tm_fxo.vol_swap_strike(base, "1y", None, real_time=False)
    assert_series_equal(tm_rates._extract_series_from_df(mock_df(), QueryType.STRIKE_VOL), actual)
    replace.restore()


if __name__ == '__main__':
    pytest.main(args=["test_measures_fx_vol.py"])

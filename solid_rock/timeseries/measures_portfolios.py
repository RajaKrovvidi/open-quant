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
import logging
from typing import Optional

import datetime as dt
import pandas as pd

from solid_rock.markets.report import PerformanceReport
from solid_rock.api.sr.portfolios import GsPortfolioApi
from solid_rock.api.sr.data import QueryType
from solid_rock.entities.entity import EntityType
from solid_rock.target.reports import ReportType
from solid_rock.timeseries import plot_measure_entity
from solid_rock.timeseries.measures import _extract_series_from_df

LOGGER = logging.getLogger(__name__)


@plot_measure_entity(EntityType.PORTFOLIO, [QueryType.PNL])
def portfolio_pnl(portfolio_id: str, start_date: dt.date = None, end_date: dt.date = None, *, source: str = None,
                  real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Returns the PnL of a portfolio
    :param portfolio_id: id of portfolio
    :param start_date: start date for getting pnl
    :param end_date: end date for getting pnl
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio pnl values
    """

    reports = GsPortfolioApi.get_reports(portfolio_id)
    performance_report_id = ""
    for report in reports:
        if report.type == ReportType.Portfolio_Performance_Analytics:
            performance_report_id = report.id
    if performance_report_id:
        ppa_report = PerformanceReport.get(performance_report_id)
        data = ppa_report.get_pnl(start_date, end_date)
        df = pd.DataFrame.from_records(data)
        df.set_index(pd.DatetimeIndex(df['date']), inplace=True)
        df.drop(columns=['date'])
        return _extract_series_from_df(df, QueryType.PNL, True)


@plot_measure_entity(EntityType.PORTFOLIO, [QueryType.AUM])
def aum(portfolio_id: str, start_date: dt.date = None, end_date: dt.date = None, *,
        source: str = None, real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Returns the Custom AUM uploaded for the portfolio
    :param portfolio_id: id of portfolio
    :param start_date: start date for getting aum
    :param end_date: end date for getting aum
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio aum values
    """
    data = GsPortfolioApi.get_custom_aum(portfolio_id, start_date, end_date)
    df = pd.DataFrame.from_records(data)
    df.set_index(pd.DatetimeIndex(df['date']), inplace=True)
    return _extract_series_from_df(df, QueryType.AUM, True)

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

from solid_rock.api.sr.reports import GsReportApi
from solid_rock.session import *
from solid_rock.target.reports import Report, ReportJob, ReportParameters


def test_get_reports(mocker):
    id_1 = 'RX1'
    id_2 = 'RX2'

    mock_response = {'results': (
        Report.from_dict({'id': id_1, 'positionSourceType': 'Portfolio', 'positionSourceId': 'MP1',
                          'type': 'Portfolio Performance Analytics', 'parameters': {'transactionCostModel': 'FIXED'}}),
        Report.from_dict({'id': id_2, 'positionSourceType': 'Portfolio', 'positionSourceId': 'MP2',
                          'type': 'Portfolio Performance Analytics', 'parameters': {'transactionCostModel': 'FIXED'}})
    ), 'totalResults': 2}

    expected_response = (
        Report(id=id_1, positionSourceType='Portfolio', positionSourceId='MP1', type='Portfolio Performance Analytics',
               parameters=ReportParameters(transactionCostModel='FIXED')),
        Report(id=id_2, positionSourceType='Portfolio', positionSourceId='MP2', type='Portfolio Performance Analytics',
               parameters=ReportParameters(transactionCostModel='FIXED'))
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
    response = GsReportApi.get_reports()
    SrSession.current._get.assert_called_with('/reports?limit=100', cls=Report)
    assert response == expected_response


def test_get_report(mocker):
    id_1 = 'MP1'
    mock_response = Report.from_dict({'id': id_1, 'positionSourceType': 'Portfolio', 'positionSourceId': 'MP1',
                                      'type': 'Portfolio Performance Analytics',
                                      'parameters': {'transactionCostModel': 'FIXED'}})

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
    response = GsReportApi.get_report(id_1)
    SrSession.current._get.assert_called_with('/reports/{id}'.format(id=id_1), cls=Report)
    assert response == mock_response


def test_create_report(mocker):
    id_1 = 'RX1'

    report = Report.from_dict({'id': id_1, 'positionSourceType': 'Portfolio', 'positionSourceId': 'MP1',
                               'type': 'Portfolio Performance Analytics',
                               'parameters': {'transactionCostModel': 'FIXED'}})

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_post', return_value=report)

    # run test
    response = GsReportApi.create_report(report)
    SrSession.current._post.assert_called_with('/reports', report, cls=Report)
    assert response == report


def test_update_report(mocker):
    id_1 = 'RX1'

    report = Report.from_dict({'id': id_1, 'positionSourceType': 'Portfolio', 'positionSourceId': 'MP25',
                               'type': 'Portfolio Performance Analytics',
                               'parameters': {'transactionCostModel': 'FIXED'}})

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_put', return_value=report)

    # run test
    response = GsReportApi.update_report(report)
    SrSession.current._put.assert_called_with('/reports/{id}'.format(id=id_1), report, cls=Report)
    assert response == report


def test_delete_portfolio(mocker):
    id_1 = 'RX1'

    mock_response = "Deleted Report"

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
    response = GsReportApi.delete_report(id_1)
    SrSession.current._delete.assert_called_with('/reports/{id}'.format(id=id_1))
    assert response == mock_response


def test_schedule_report(mocker):
    id_1 = 'RX1'
    start_date = dt.date(2019, 2, 18)
    end_date = dt.date(2019, 2, 19)

    mock_response = ""

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_post', return_value=mock_response)

    # run test
    response = GsReportApi.schedule_report(id_1, start_date, end_date)

    SrSession.current._post.assert_called_with(
        '/reports/{id}/schedule'.format(id=id_1), {'endDate': '2019-02-19', 'startDate': '2019-02-18'})

    assert response == mock_response


def test_get_report_status(mocker):
    id_1 = 'RJW55950MF0S0HKN'

    mock_response = ({'reportJobId': id_1, 'startDate': dt.date(2018, 12, 12), 'endDate': dt.date(2018, 12, 18)},
                     {'reportJobId': id_1, 'startDate': dt.date(2017, 12, 12), 'endDate': dt.date(2017, 12, 16)})

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
    response = GsReportApi.get_report_status(id_1)
    SrSession.current._get.assert_called_with('/reports/{id}/status'.format(id=id_1))
    assert response == mock_response


def test_get_report_jobs(mocker):
    id_1 = 'RJW55950MF0S0HKN'

    mock_response = {'results': (
        ReportJob.from_dict({'id': id_1, 'positionSourceType': 'Portfolio', 'positionSourceId': 'MP1',
                             'parameters': {'transactionCostModel': 'FIXED'}}),
        ReportJob.from_dict({'id': id_1, 'positionSourceType': 'Portfolio', 'positionSourceId': 'MP2',
                             'parameters': {'transactionCostModel': 'FIXED'}})
    ), 'totalResults': 2}

    expected_response = (
        ReportJob(id=id_1, positionSourceType='Portfolio', positionSourceId='MP1',
                  parameters=ReportParameters(transactionCostModel='FIXED')),
        ReportJob(id=id_1, positionSourceType='Portfolio', positionSourceId='MP2',
                  parameters=ReportParameters(transactionCostModel='FIXED'))
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
    response = GsReportApi.get_report_jobs(id_1)
    SrSession.current._get.assert_called_with('/reports/{id}/jobs'.format(id=id_1))
    assert response == expected_response


def test_report_job(mocker):
    id_1 = 'RX1'
    mock_response = ReportJob(id=id_1, positionSourceType='Portfolio', positionSourceId='MP1',
                              parameters=ReportParameters(transactionCostModel='FIXED'))

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
    response = GsReportApi.get_report_job(id_1)
    SrSession.current._get.assert_called_with('/reports/jobs/{id}'.format(id=id_1))
    assert response == mock_response


def test_cancel_report_job(mocker):
    id_1 = 'RX1'

    mock_response = ""

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_post', return_value=mock_response)

    # run test
    response = GsReportApi.cancel_report_job(id_1)
    SrSession.current._post.assert_called_with('/reports/jobs/{id}/cancel'.format(id=id_1))
    assert response == mock_response


def test_update_report_job(mocker):
    id_1 = 'RX1'
    status = 'done'
    mock_response = ""

    # mock SrSession
    mocker.patch.object(
        SrSession.__class__,
        'default_value',
        return_value=SrSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(SrSession.current, '_post', return_value=mock_response)

    # run test
    response = GsReportApi.update_report_job(id_1, status)
    status_body = {
        "status": 'done'
    }
    SrSession.current._post.assert_called_with('/reports/jobs/{id}/update'.format(id=id_1), status_body)
    assert response == mock_response


def test_get_factor_risk_report_results(mocker):
    mock_response = [
        {
            "date": "2003-01-03",
            "factor": "Value",
            "factorCategory": "Style",
            "pnl": 0.002877605406002121,
            "exposure": 12.105457414400002,
            "sensitivity": 0.026861678358408886,
            "proportionOfRisk": 0.0038230454885067183
        },
        {
            "date": "2003-01-06",
            "factor": "Value",
            "factorCategory": "Style",
            "pnl": 0,
            "exposure": 12.1028697664,
            "sensitivity": 0.02668134999120776,
            "proportionOfRisk": 0.0036290846167489335
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
    response = GsReportApi.get_factor_risk_report_results('reportId')

    SrSession.current._get.assert_called_with('/risk/factors/reports/reportId/results?')
    assert response == mock_response


def test_get_factor_risk_report_view(mocker):
    report_id = 'RP123'
    mock_response = {
        "summary": {
            "riskModel": "BARRA_USSLOWL",
            "fxHedged": True,
            "assetCount": 1,
            "longExposure": 415,
            "shortExposure": 0,
            "factorProportionOfRisk": 70.28206437467601,
            "specificProportionOfRisk": 29.71793562532398,
            "date": "2021-08-12"
        }
    }
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
    response = GsReportApi.get_factor_risk_report_view(report_id, view='Risk')

    SrSession.current._get.assert_called_with(f'/risk/factors/reports/{report_id}/views?view=Risk')
    assert response == mock_response

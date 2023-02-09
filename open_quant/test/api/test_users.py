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
from unittest import mock

import pytest

from open_quant.api.oq.users import GsUsersApi
from open_quant.session import *
from open_quant.target.reports import User


def test_get_users(mocker):
    mock_response = {
        "totalResults": 1,
        "results": [
            {
                "internal": True,
                "systemUser": False,
                "appUser": False,
                "analyticsId": "id123",
                "city": "New York",
                "company": "Goldman Sachs Group",
                "rootOEId": "id123",
                "rootOEIndustry": {
                    "name": "Multi-Business Organization"
                },
                "oeIndustry": {
                    "name": "Multi-Business Organization"
                },
                "oeAlias": 17670,
                "country": "US",
                "coverage": [
                    {
                        "phone": "+1 855-MARQUE-0",
                        "name": "Marquee Help Desk",
                        "email": "oq-marquee-help@oq.com"
                    }
                ],
                "email": "jane.doe@oq.com",
                "kerberos": "doeja",
                "id": "id",
                "name": "Doe, Jane",
                "firstName": "Jane",
                "lastName": "Doe",
                "internalID": "doeja",
                "region": "Americas",
                "departmentCode": "Y362",
                "departmentName": "Marquee Engineering",
                "divisionName": "Global Markets Division",
                "businessUnit": "Marquee Engineering",
                "title": "Analyst",
                "login": "doeja",
                "tokens": [
                    "active"
                ],
                "roles": [
                    "MarqueeResearchExperienceEligible"
                ],
                "groups": [
                    "3AV5PPWJBS4B89X76"
                ],
                "expertiseTags": []
            }
        ]
    }

    # mock OqSession
    from open_quant.session import OAuth2Session
    OAuth2Session.init = mock.MagicMock(return_value=None)
    OqSession.use(Environment.QA, 'client_id', 'secret')
    mocker.patch.object(
        OqSession.__class__,
        'default_value',
        return_value=OqSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(OqSession.current, '_get', return_value=mock_response)

    # run test
    response = GsUsersApi.get_users(user_ids=['doeja'],
                                    user_emails=['jane.doe@oq.com'])
    OqSession.current._get.assert_called_with('/users?&id=doeja&email=jane.doe@oq.com&limit=100&offset=0', cls=User)
    assert response == mock_response['results']


def test_get_current_user_info(mocker):
    mock_response = {
        "internal": True,
        "systemUser": False,
        "appUser": False,
        "analyticsId": "id123",
        "city": "New York",
        "company": "Goldman Sachs Group",
        "rootOEId": "id123",
        "rootOEIndustry": {
            "name": "Multi-Business Organization"
        },
        "oeIndustry": {
            "name": "Multi-Business Organization"
        },
        "oeAlias": 17670,
        "country": "US",
        "coverage": [
            {
                "phone": "+1 855-MARQUE-0",
                "name": "Marquee Help Desk",
                "email": "oq-marquee-help@oq.com"
            }
        ],
        "email": "jane.doe@oq.com",
        "kerberos": "doeja",
        "id": "id",
        "name": "Doe, Jane",
        "firstName": "Jane",
        "lastName": "Doe",
        "internalID": "doeja",
        "region": "Americas",
        "departmentCode": "Y362",
        "departmentName": "Marquee Engineering",
        "divisionName": "Global Markets Division",
        "businessUnit": "Marquee Engineering",
        "title": "Analyst",
        "login": "doeja",
        "tokens": [
            "active"
        ],
        "roles": [
            "MarqueeResearchExperienceEligible"
        ],
        "groups": [
            "3AV5PPWJBS4B89X76"
        ],
        "expertiseTags": []
    }

    # mock OqSession
    from open_quant.session import OAuth2Session
    OAuth2Session.init = mock.MagicMock(return_value=None)
    OqSession.use(Environment.QA, 'client_id', 'secret')
    mocker.patch.object(
        OqSession.__class__,
        'default_value',
        return_value=OqSession.get(
            Environment.QA,
            'client_id',
            'secret'))
    mocker.patch.object(OqSession.current, '_get', return_value=mock_response)

    # run test
    response = GsUsersApi.get_current_user_info()
    OqSession.current._get.assert_called_with('/users/self')
    assert response == mock_response


if __name__ == '__main__':
    pytest.main(args=[__file__])

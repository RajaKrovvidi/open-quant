from unittest import TestCase
from server.payload_parser import PayloadParser

class TestPayloadParser(TestCase):

    def setUp(self) -> None:
        self.payload = { 'positions' :
                    [{'instrument': {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'EUR',
                                    'expirationDate': '3m', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption'},
                     'instrumentName': 'EUR3m5y', 'quantity': 1},
                    {'instrument': {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'EUR',
                                    'expirationDate': '6m', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption'},
                     'instrumentName': 'EUR6m5y', 'quantity': 1},
                    {'instrument': {'payOrReceive': 'Pay', 'terminationDate': '2Y', 'notionalCurrency': 'EUR',
                                    'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swap'}, 'quantity': 1}],
                    'measures':
                    [{'measureType': 'Dollar Price'}, {'assetClass': 'Rates', 'measureType': 'Delta'}, {
                        'assetClass': 'Rates', 'measureType': 'Gamma'}, {'assetClass': 'Rates',
                                                                         'measureType': 'Vega'}],
                    'pricingAndMarketDataAsOf' :
                    [{'pricingDate': '2023-06-19',
                      'market': {'date': '2023-06-16', 'location': 'LDN', 'marketType': 'CloseMarket'}}]
                    }

    def test_parse_payload(self):

        parsed_data = PayloadParser.parse_payload(self.payload)
        print (parsed_data)
        self.assertEqual(len(parsed_data.get('Rates')), 2)
        self.assertEqual(len(parsed_data.get('Rates').get('Swap')), 1)
        self.assertEqual(len(parsed_data.get('Rates').get('Swaption')),2)
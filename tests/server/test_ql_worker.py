from unittest import TestCase
from server.ql_worker import QuantLibWorker

class TestQlWorker(TestCase):
    def test_get_yield_curve(self):
        self.fail()

    def test_get_libor_index(self):
        self.fail()

    def test_construct_swap_schedules(self):
        self.fail()

    def test_construct_swap(self):
        self.fail()


class TestMarket(TestCase):
    def setUp(self) -> None:
        self.payload1 = {
            'key': 'abcd-1',
            'request':
                {'Rates': {'Swaption': [
                {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'USD', 'expirationDate': '3m', 'notionalAmount' : 1E7,
                 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption', 'sequence_no': 0},
                {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'USD', 'expirationDate': '6m', 'notionalAmount' : 1E7,
                 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption', 'sequence_no': 1}], 'Swap': [
                {'payOrReceive': 'Pay', 'fixedRate': 0.042, 'terminationDate': '2Y', 'notionalCurrency': 'USD', 'fee': 0.0, 'notionalAmount' : 1E7,
                 'assetClass': 'Rates', 'type': 'Swap', 'sequence_no': 2}]},
             'measures': [{'measureType': 'Dollar Price'}, {'assetClass': 'Rates', 'measureType': 'Delta'},
                          {'assetClass': 'Rates', 'measureType': 'Gamma'},
                          {'assetClass': 'Rates', 'measureType': 'Vega'}], 'pricingAndMarketDataAsOf': [
                {'pricingDate': '2023-06-19',
                 'market': {'date': '2023-06-16', 'location': 'LDN', 'marketType': 'CloseMarket'}}]
                }
        }
        self.swap_swaption_hedged_payload = {
            'key': 'abcd-1',
            'request':
                {'Rates': {'Swaption': [
                {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'USD', 'expirationDate': '3m', 'notionalAmount' : 1E7,
                 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption', 'sequence_no': 0},
                {'payOrReceive': 'Pay', 'startDate':'2023-09-21', 'terminationDate': '5Y', 'notionalCurrency': 'USD', 'fee': 0.0, 'notionalAmount' : 1E7,
                 'assetClass': 'Rates', 'type': 'Swap', 'sequence_no': 1}]},
                'measures': [{'measureType': 'Dollar Price'}, {'assetClass': 'Rates', 'measureType': 'Delta'},
                          {'assetClass': 'Rates', 'measureType': 'Gamma'},
                          {'assetClass': 'Rates', 'measureType': 'Vega'}],
                'pricingAndMarketDataAsOf': [{'pricingDate': '2023-06-19','market': {'date': '2023-06-16', 'location': 'LDN', 'marketType': 'CloseMarket'}}]
                }
        }
        self.fxo_payload  = {
                 'key': 'fxo_portfolio-1',
                 'request':
                     {'FX': {
                         'Option': [
                                {'pair': 'EURUSD', 'optionType': 'Call', 'strikePrice': 'ATMF', 'expirationDate': '1y', 'assetClass': 'FX', 'type': 'Option','sequence_no': 0}
                             ]},
                 'measures': [{'measureType': 'Dollar Price'}, {'assetClass': 'Rates', 'measureType': 'Delta'},
                              {'assetClass': 'Rates', 'measureType': 'Gamma'},
                              {'assetClass': 'Rates', 'measureType': 'Vega'}],
                 'pricingAndMarketDataAsOf': [{'pricingDate': '2023-06-19','market': {'date': '2023-06-16', 'location': 'LDN','marketType': 'CloseMarket'}}]
                 }
        }
        self.fxo_payload2  = {
                 'key': 'fxo_portfolio-1',
                 'request':
                     {'FX': {
                         'Option': [
                             {'pair': 'EURUSD', 'optionType': 'Call', 'strikePrice': 'ATMF', 'expirationDate': '1y', 'assetClass': 'FX', 'type': 'Option','sequence_no': 0},
                             {'pair': 'GBPUSD', 'optionType': 'Call', 'strikePrice': 1.0025, 'expirationDate': '2y', 'assetClass': 'FX', 'type': 'Option', 'sequence_no': 1},
                             {'pair': 'GBPUSD', 'optionType': 'Call', 'strikePrice': 'ATMF', 'expirationDate': '2y', 'assetClass': 'FX', 'type': 'Option', 'sequence_no': 2},
                             {'pair': 'USDINR', 'optionType': 'Call', 'strikePrice': '83', 'expirationDate': '1y', 'assetClass': 'FX', 'type': 'Option', 'sequence_no': 3}
                         ]},
                 'measures': [{'measureType': 'Dollar Price'}, {'assetClass': 'Rates', 'measureType': 'Delta'},
                              {'assetClass': 'Rates', 'measureType': 'Gamma'},
                              {'assetClass': 'Rates', 'measureType': 'Vega'}],
                 'pricingAndMarketDataAsOf': [{'pricingDate': '2023-06-19','market': {'date': '2023-06-16', 'location': 'LDN','marketType': 'CloseMarket'}}]
                 }
        }

        self.worker = QuantLibWorker( "test_request", "test_response")

    def test_build_market_curves(self):
        self.fail()

    def test_construct_swap(self):
        self.fail()

    def test_swap_swaption(self):

        vals = self.worker.process_message(self.swap_swaption_hedged_payload)
        expected = [[{'$type': 'Risk', 'val': 150391.16254638787}, {'$type': 'Risk', 'val': 0.0}], [{'$type': 'Risk', 'val': 2229.785210993403}, {'$type': 'Risk', 'val': -22.057219911832362}],
                    [{'$type': 'Risk', 'val': 18.170200030639535}, {'$type': 'Risk', 'val': 0.012199914548546076}],
                    [{'$type': 'Risk', 'val': 441262.70378871914}, {'$type': 'Risk', 'val': 'Unsupported'}]]
        #self.assertEqual(vals, expected)

    def test_process_message(self):

        vals = self.worker.process_message(self.payload1)
        expected = [[[[{'$type': 'Risk', 'val': 150391.16254638787}], [{'$type': 'Risk', 'val': 201101.7375688183}], [{'$type': 'Risk', 'val': -192367.76098476048}]],
                     [[{'$type': 'Risk', 'val': 2229.785210993403}], [{'$type': 'Risk', 'val': 2155.328947221249}], [{'$type': 'Risk', 'val': 13.186445090919733}]],
                     [[{'$type': 'Risk', 'val': 18.170200030639535}], [{'$type': 'Risk', 'val': 12.030347647785675}], [{'$type': 'Risk', 'val': -0.0019750328501686454}]],
                     [[{'$type': 'Risk', 'val': 441262.70378871914}], [{'$type': 'Risk', 'val': 588632.2426292432}], [{'$type': 'Risk', 'val': 'Unsupported'}]]]]
        self.assertEqual(vals, expected)

    def test_fx_option(self):
        vals = self.worker.process_message(self.fxo_payload)
        print(vals)
        expected = [[[[{'$type': 'Risk', 'val': 93628811.67667359}]],
                     [[{'$type': 'Risk', 'val': 542777479.6886424}]],
                     [[{'$type': 'Risk', 'val': 1661901667.2100887}]],
                     [[{'$type': 'Risk', 'val': 455281398.41486824}]]]]

        self.assertEqual(vals, expected)

    def test_fx_option2(self):
        vals = self.worker.process_message(self.fxo_payload2)
        #print(vals)
        expected = [[[[{'$type': 'Risk', 'val': 93628811.67667359}], [{'$type': 'Risk', 'val': 260458085.25952336}], [{'$type': 'Risk', 'val': 119728146.75937147}], [{'$type': 'Risk', 'val': 4334364048.590718}]],
                     [[{'$type': 'Risk', 'val': 542777479.6886424}], [{'$type': 'Risk', 'val': 727431566.6065466}], [{'$type': 'Risk', 'val': 466620567.4397771}], [{'$type': 'Risk', 'val': 530691703.05997294}]],
                     [[{'$type': 'Risk', 'val': 1661901667.2100887}], [{'$type': 'Risk', 'val': 667753859.5202978}], [{'$type': 'Risk', 'val': 958239136.5446649}], [{'$type': 'Risk', 'val': 36374484.81816094}]],
                     [[{'$type': 'Risk', 'val': 455281398.41486824}], [{'$type': 'Risk', 'val': 474802544.301826}], [{'$type': 'Risk', 'val': 681350431.1421534}], [{'$type': 'Risk', 'val': 33424509614.882572}]]
                     ]]
        self.assertEqual(vals, expected)

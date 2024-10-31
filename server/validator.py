""""
Module to validate an incoming palyload.

{'instrument': {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'EUR', 'expirationDate': '3m', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption'}, 'instrumentName': 'EUR3m5y', 'quantity': 1}
{'instrument': {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'EUR', 'expirationDate': '6m', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption'}, 'instrumentName': 'EUR6m5y', 'quantity': 1}
{'instrument': {'payOrReceive': 'Pay', 'terminationDate': '2Y', 'notionalCurrency': 'EUR', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swap'}, 'quantity': 1}
[{'measureType': 'Dollar Price'}, {'assetClass': 'Rates', 'measureType': 'Delta'}, {'assetClass': 'Rates', 'measureType': 'Gamma'}, {'assetClass': 'Rates', 'measureType': 'Vega'}]
[{'pricingDate': '2023-06-19', 'market': {'date': '2023-06-16', 'location': 'LDN', 'marketType': 'CloseMarket'}}]

"""
from abc import ABC, abstractmethod


class Validator(ABC):

    @abstractmethod
    def validate(self):
        pass

class PayloadValidator(Validator):


    def validate(self):
        pass

class RatesValidator(Validator):

    def validate(self):
        print('Rates Validator ')


class SwapValidator(RatesValidator):
    def validate(self):
        print('Swap Validator ')


class SwaptionValidator(SwapValidator):
    def validate(self):
        print('Swaption Validator ')


class MeasureTypeValidator(Validator):
    def validate(self):
        print('Measure Type Validator ')
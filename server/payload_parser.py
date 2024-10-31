class PayloadParser:

    @classmethod
    def parse_payload(cls, payload):
        """
            Objective of this function is parse the payload and break it down into
            # instruments
            # measures
            # market context

        Sample payload could be

        {'instrument': {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'EUR', 'expirationDate': '3m', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption'}, 'instrumentName': 'EUR3m5y', 'quantity': 1}
        {'instrument': {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'EUR', 'expirationDate': '6m', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption'}, 'instrumentName': 'EUR6m5y', 'quantity': 1}
        {'instrument': {'payOrReceive': 'Pay', 'terminationDate': '2Y', 'notionalCurrency': 'EUR', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swap'}, 'quantity': 1}
        [{'measureType': 'Dollar Price'}, {'assetClass': 'Rates', 'measureType': 'Delta'}, {'assetClass': 'Rates', 'measureType': 'Gamma'}, {'assetClass': 'Rates', 'measureType': 'Vega'}]
        [{'pricingDate': '2023-06-19', 'market': {'date': '2023-06-16', 'location': 'LDN', 'marketType': 'CloseMarket'}}]

        :return:
        """
        parsed_data = {}
        if not payload:
            return parsed_data
        if isinstance(payload, list):
            payload = payload[0]
        positions = payload.get('positions')
        for idx, pos in enumerate(positions):
            asset_info = pos.get('instrument', {})
            asset_info.update({'sequence_no': idx})
            asset_class = asset_info.get('assetClass')
            asset_type = asset_info.get('type')
            if asset_class and asset_type:
                assets_for_class = parsed_data.get(asset_class, {})
                assets_for_type = assets_for_class.get(asset_type, [])
                assets_for_type.append(asset_info)
                assets_for_class[asset_type] = assets_for_type
                parsed_data[asset_class] = assets_for_class
        parsed_data['measures'] = payload.get('measures')
        parsed_data['pricingAndMarketDataAsOf'] = payload.get('pricingAndMarketDataAsOf')
        return parsed_data

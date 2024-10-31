import logging

import QuantLib as ql
import msgpack

import numpy as np
from oq_to_ql_mappings import measures_map
from persist_queue_manager import PersistQueueManager

logger = logging.getLogger()

ccy_inst_dcc_map = {
    ('USD',None): ql.ActualActual(ql.ActualActual.ISDA),
    ('USD','Swap'): ql.ActualActual(ql.ActualActual.ISDA),
    ('USD','Bond'): ql.Thirty360(ql.Thirty360.BondBasis),
    ('EUR',None): ql.ActualActual(ql.ActualActual.ISDA),
    ('EUR','Swap'): ql.ActualActual(ql.ActualActual.ISDA),
    ('EUR','Bond'): ql.Thirty360(ql.Thirty360.BondBasis),
    ('GBP',None): ql.ActualActual(ql.ActualActual.ISDA),
    ('GBP','Swap'): ql.ActualActual(ql.ActualActual.ISDA),
    ('GBP','Bond'): ql.Thirty360(ql.Thirty360.BondBasis),
    ('INR',None): ql.ActualActual(ql.ActualActual.ISDA),
    ('INR', 'Swap'): ql.ActualActual(ql.ActualActual.ISDA),
    ('JPY',None): ql.ActualActual(ql.ActualActual.ISDA),
    ('JPY', 'Swap'): ql.ActualActual(ql.ActualActual.ISDA),
    ('AUD',None): ql.ActualActual(ql.ActualActual.ISDA),
    ('AUD', 'Swap'): ql.ActualActual(ql.ActualActual.ISDA),
    ('NZD',None): ql.ActualActual(ql.ActualActual.ISDA),
    ('NZD', 'Swap'): ql.ActualActual(ql.ActualActual.ISDA),
}

ccy_calendar_map= { 'USD': ql.UnitedStates(ql.UnitedStates.Settlement),
                    'USD-Bond': ql.UnitedStates(ql.UnitedStates.GovernmentBond),
                    'USD-NYSE': ql.UnitedStates(ql.UnitedStates.NYSE),
                    'GBP': ql.UnitedKingdom(ql.UnitedKingdom.Settlement),
                    'EUR': ql.TARGET(),
                    'JPY': ql.Japan(),
                    'INR': ql.India(ql.India.NSE),
                    'AUD': ql.Australia(ql.Australia.Settlement),
                    'NZD': ql.NewZealand()
                    }

fx_calendars = {
    'USDAUD': ql.UnitedStates(ql.UnitedStates.Settlement),
    'USDCAD': ql.UnitedStates(ql.UnitedStates.Settlement),
    'USDEUR': ql.UnitedStates(ql.UnitedStates.Settlement),
    'USDJPY': ql.UnitedStates(ql.UnitedStates.Settlement),
    'USDINR': ql.UnitedStates(ql.UnitedStates.Settlement),
    'GBPUSD':ql.UnitedStates(ql.UnitedStates.Settlement),
    'GBPEUR':ql.UnitedKingdom(ql.UnitedKingdom.Settlement),
    'GBPCAD':ql.UnitedKingdom(ql.UnitedKingdom.Settlement),
    'GBPJPY':ql.UnitedKingdom(ql.UnitedKingdom.Settlement),
}

for k in list(fx_calendars.keys()):
    fx_calendars[k[3:]+k[:3]] = fx_calendars[k]


TOLERANCE = 1E-6

def get_swap_pay_rec(pay_or_rec):
    return ql.VanillaSwap.Payer if pay_or_rec == 'pay' else ql.VanillaSwap.Receiver

def print_curve(xlist, ylist, precision=4):
    """
    Method to print curve in a nice format
    """
    print ("----------------------")
    print ("Maturities\tCurve")
    print ("----------------------")
    for x,y in zip(xlist, ylist):
        print (x,"\t\t", round(y, precision))
    print ("----------------------")

def get_day_count_convention(currency='USD', inst='Swap'):
    return ccy_inst_dcc_map.get((currency, inst))


def getYieldCurve(calc_date, depo_maturities, depo_rates, bond_maturities, bond_rates):
    """
    method to build yield curve from deposit rates and bond rates
    :return: YieldCurve instance
    """
    #print_curve(depo_maturities + bond_maturities, depo_rates + bond_rates)

    ql.Settings.instance().evaluationDate = calc_date

    bus_cal = ql.UnitedKingdom()
    bus_convention = ql.Unadjusted
    eom = True
    settlement_days = 0
    face_amount = 100
    coupon_freq = ql.Period(ql.Semiannual)
    fixing_days = 2
    day_count_convention = get_day_count_convention()
    # create deposit rate helpers from depo_rates

    depo_helpers = [ ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(r/100.0)), m, fixing_days,  bus_cal, bus_convention, eom, day_count_convention) for r, m in zip(depo_rates, depo_maturities) ]

    bond_helpers = []

    for r, m in zip(bond_rates, bond_maturities):
        termination_date = calc_date + m
        schedule = ql.Schedule(calc_date, termination_date, coupon_freq, bus_cal, bus_convention, bus_convention, ql.DateGeneration.Backward, eom)
        helper = ql.FixedRateBondHelper(ql.QuoteHandle(ql.SimpleQuote(face_amount)), settlement_days, face_amount, schedule, [r/100.0], day_count_convention, bus_convention,)
        bond_helpers.append(helper)

    rate_helpers = depo_helpers + bond_helpers

    yield_curve = ql.PiecewiseLogCubicDiscount(calc_date, rate_helpers, ccy_inst_dcc_map.get(('USD','Bond')))
    return yield_curve

def get_libor_index(n_months, libor_maturities, libor_rates, calendar, calc_date, day_count_convention):

    if n_months not in [ 1, 3, 6, 12]:
        raise Exception("Invalid months for fetching libor index - got " + str(n_months))

    #print_curve(libor_maturities, libor_rates)
    logger.info('Constructing curve with tenor months ' + str(n_months))
    libor_dates = [calendar.advance(calc_date, i, ql.Months ) for i in libor_maturities ]
    libor_curve = ql.YieldTermStructureHandle((ql.ZeroCurve(libor_dates, libor_rates, day_count_convention, calendar)))
    libor_curve.enableExtrapolation()

    return ql.USDLibor(ql.Period(n_months, ql.Months), libor_curve)



#libor_helpers = []
#for r, m in zip(libor_rates, libor_maturities):
#    termination_date = calc_date + m
#    schedule = ql.Schedule(calc_date, termination_date, coupon_freq, bus_cal, bus_convention, bus_convention, ql.DateGeneration.Backward, eom)
#    helper = ql.ZeroHelper(, settlement_days, face_amount, schedule, [r/100.0], day_counter, bus_convention,)
#    bond_helpers.append(helper)

def construct_swap_schedules(calendar, calc_date, start_date, maturity_in_years):
    """
    Construct T+2 to maturity schedules
    :return:
    """
    settlement_date = start_date if start_date else calendar.advance(calc_date, 2, ql.Days)
    maturity_date = calendar.advance(calc_date, int(maturity_in_years), ql.Years)

    fixed_leg_tenor = ql.Period(6, ql.Months)
    fixed_schedule = ql.Schedule(settlement_date, maturity_date, fixed_leg_tenor, calendar, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)

    float_leg_tenor = ql.Period(3, ql.Months)
    float_leg_schedule = ql.Schedule(settlement_date, maturity_date, float_leg_tenor, calendar, ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)

    return fixed_schedule, float_leg_schedule

def construct_swap(calc_date, libor_index, calendar, pay_or_receive,  currency, notional, fixed_rate, start_date, maturity_in_years):

    fixed_schedule, float_schedule = construct_swap_schedules(calendar, calc_date, start_date, maturity_in_years)
    notional = float(notional)
    fixed_leg_daycount = ql.Actual360()
    float_spread = 0.000
    float_leg_daycount = ql.Actual360()
    #print(pay_or_receive, notional, fixed_schedule, fixed_rate, fixed_leg_daycount, float_schedule, libor_index, float_spread, float_leg_daycount)
    ir_swap = ql.VanillaSwap(pay_or_receive, notional, fixed_schedule, fixed_rate, fixed_leg_daycount, float_schedule, libor_index, float_spread, float_leg_daycount)

    return ir_swap


def get_ql_date_from_string(date_str):
    return ql.DateParser().parse(date_str, 'YYYY-MM-DD')


class Market:

    def __init__(self, calc_date):
        self.calc_date = calc_date or ql.Date.todaysDate()
        print( 'Calc date is '+ str(self.calc_date))
        self.libor1m_index, self.libor3m_index, self.libor6m_index, self.libor12m_index = None, None, None, None
        self.bumped_libor1m_index, self.bumped_libor3m_index, self.bumped_libor6m_index, self.bumped_libor12m_index = None, None, None, None
        self.dbl_bumped_libor1m_index, self.dbl_bumped_libor3m_index, self.dbl_bumped_libor6m_index, self.dbl_bumped_libor12m_index = None, None, None, None

        self.day_count_convention = ql.Thirty360(ql.Thirty360.BondBasis)
        self.buildMarketCurves()
        self.swap_index_lookup_map = {
            ('1M', False, False): self.libor1m_index,
            ('1M', True, False): self.bumped_libor1m_index,
            ('1M', True, True): self.dbl_bumped_libor1m_index,
            ('3M', False, False): self.libor3m_index,
            ('3M', True, False): self.bumped_libor3m_index,
            ('3M', True, True): self.dbl_bumped_libor3m_index,
            ('6M', False, False): self.libor6m_index,
            ('6M', True, False): self.bumped_libor6m_index,
            ('6M', True, True): self.dbl_bumped_libor6m_index,
            ('12M', False, False): self.libor12m_index,
            ('12M', True, False): self.bumped_libor12m_index,
            ('12M', True, True): self.dbl_bumped_libor12m_index,
        }
        self.buildMarketCurves()
        self.construct_flat_int_rate_tss()
        self.build_swap_enginges()
        self.construct_fx_spot_handles()
        self.construct_flat_vol_tss()
        self.build_fx_engines()

    def construct_fx_spot_handles(self):
        self.fx_spots = {
            'USDAUD': 1.57,
            'USDCAD': 1.3524,
            'USDJPY': 146.13,
            'USDEUR': 0.919978,
            'GBPUSD': 1.2752,
            'GBPEUR': 1.11728,
            'GBPCAD': 1.7245,
            'GBPJPY': 186.34,
            'USDINR': 80.25,
        }

        for i in list(self.fx_spots.keys()):
            self.fx_spots[i[3:] + i[:3]] = round(1 / self.fx_spots[i], 5)

        self.fx_spot_handles = {k: ql.QuoteHandle(ql.SimpleQuote(v)) for k,v in self.fx_spots.items()}

    def construct_flat_int_rate_tss(self):
        self.ir_tss = {
            'INR':ql.YieldTermStructureHandle(ql.FlatForward(self.calc_date, ql.QuoteHandle(ql.SimpleQuote(0.065)), ccy_inst_dcc_map.get(('USD',None)))),
            'GBP':ql.YieldTermStructureHandle(ql.FlatForward(self.calc_date, ql.QuoteHandle(ql.SimpleQuote(0.045)), ccy_inst_dcc_map.get(('USD',None)))),
            'USD':ql.YieldTermStructureHandle(ql.FlatForward(self.calc_date, ql.QuoteHandle(ql.SimpleQuote(0.03)), ccy_inst_dcc_map.get(('USD',None)))),
            'EUR':ql.YieldTermStructureHandle(ql.FlatForward(self.calc_date, ql.QuoteHandle(ql.SimpleQuote(0.023)), ccy_inst_dcc_map.get(('USD',None)))),
            'AUD':ql.YieldTermStructureHandle(ql.FlatForward(self.calc_date, ql.QuoteHandle(ql.SimpleQuote(0.0345)), ccy_inst_dcc_map.get(('USD',None)))),
            'CAD':ql.YieldTermStructureHandle(ql.FlatForward(self.calc_date, ql.QuoteHandle(ql.SimpleQuote(0.0284)), ccy_inst_dcc_map.get(('USD',None)))),
            'JPY':ql.YieldTermStructureHandle(ql.FlatForward(self.calc_date, ql.QuoteHandle(ql.SimpleQuote(0.0015)), ccy_inst_dcc_map.get(('USD',None)))),
        }

    def construct_flat_vol_tss(self):
        fx_vols = {
            'USDAUD': 0.287,
            'USDCAD': 0.1755,
            'USDEUR': 0.195,
            'USDJPY': 0.22,
            'GBPCAD': 0.1755,
            'GBPJPY': 0.3455,
            'GBPUSD': 0.2,
            'GBPEUR': 0.223,
            #'GBPCAD': 0.165,
            #'GBPJPY': 0.155,
            'USDINR': 0.12,
        }

        for i in list(fx_vols.keys()):
            fx_vols[i[3:] + i[:3]] = fx_vols[i]

        day_count = ql.Actual365Fixed()

        self.flat_vol_ts = {k:ql.BlackVolTermStructureHandle(ql.BlackConstantVol(self.calc_date, fx_calendars.get(k), v, day_count))
                                for k,v in fx_vols.items()}

    def build_fx_engines(self):
        self.gk_procs = {k: ql.GarmanKohlagenProcess(self.fx_spot_handles.get(k),self.ir_tss[k[:3]], self.ir_tss[k[3:]], self.flat_vol_ts[k]) for k,v in self.fx_spots.items()}
        self.fxo_engines = {'European':  {k : ql.AnalyticEuropeanEngine(v) for k, v in self.gk_procs.items()}}


    def build_swap_enginges(self):
        self.base_swap_engine = ql.DiscountingSwapEngine(self.disc_curve)
        self.bumped_swap_engine = ql.DiscountingSwapEngine(self.bumped_disc_curve)
        self.dbl_bumped_swap_engine = ql.DiscountingSwapEngine(self.dbl_bumped_disc_curve)

        self.swaption_black_engine = ql.BlackSwaptionEngine(self.disc_curve, ql.QuoteHandle(ql.SimpleQuote(0.34)),
                                         ql.ActualActual(ql.ActualActual.ISMA))

    def buildMarketCurves(self):

        # deposit rates
        depo_maturities = [ql.Period(6, ql.Months), ql.Period(12, ql.Months)]
        depo_rates = [4.25 , 4.5]

        # bond rates
        bond_maturities = [ql.Period( 6*i , ql.Months) for i in range(3,21)]
        bond_rates = [ 5.75 + i* 0.25 for i in range(18)]

        self.yield_curve = getYieldCurve( self.calc_date, depo_maturities, depo_rates, bond_maturities, bond_rates)
        self.yield_curve.enableExtrapolation()
        self.bumped_yield_curve = getYieldCurve(self.calc_date, depo_maturities, [i + 0.01 for i in depo_rates] , bond_maturities, [i + 0.01 for i in bond_rates])
        self.bumped_yield_curve.enableExtrapolation()
        self.dbl_bumped_yield_curve = getYieldCurve(self.calc_date, depo_maturities, [i + 0.02 for i in depo_rates] , bond_maturities, [i + 0.02 for i in bond_rates])
        self.dbl_bumped_yield_curve.enableExtrapolation()

        # get spot rates


        self.disc_curve = ql.YieldTermStructureHandle(self.yield_curve)
        self.bumped_disc_curve = ql.YieldTermStructureHandle(self.bumped_yield_curve)
        self.dbl_bumped_disc_curve = ql.YieldTermStructureHandle(self.dbl_bumped_yield_curve)

        # libor rates
        libor_maturities = [ql.Period(i, ql.Months) for i in [ 0, 1, 3,6, 12] ]
        libor_rates = [0, 0.047, 0.0482, 0.0495, 0.050875]
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        day_count_convention = get_day_count_convention()

        delta_upsize = 0.0 # 0.0001
        gamma_upsize = 0.0 # 0.0002

        self.libor1m_index = get_libor_index(1, libor_maturities, libor_rates,calendar, self.calc_date, day_count_convention)
        self.bumped_libor1m_index = get_libor_index(1, libor_maturities, [i + delta_upsize for i in libor_rates], calendar, self.calc_date, day_count_convention)
        self.dbl_bumped_libor1m_index = get_libor_index(1, libor_maturities, [i + gamma_upsize for i in libor_rates], calendar, self.calc_date, day_count_convention)

        self.libor3m_index = get_libor_index(3, libor_maturities, libor_rates,calendar, self.calc_date, day_count_convention)
        self.bumped_libor3m_index = get_libor_index(3, libor_maturities, [i + delta_upsize for i in libor_rates], calendar, self.calc_date, day_count_convention)
        self.dbl_bumped_libor3m_index = get_libor_index(3, libor_maturities, [i + gamma_upsize for i in libor_rates], calendar, self.calc_date, day_count_convention)
        self.libor3m_index.addFixing(ql.Date(25, 8, 2023), 0.0051)
        self.bumped_libor3m_index.addFixing(ql.Date(25, 8, 2023), 0.0051)
        self.dbl_bumped_libor3m_index.addFixing(ql.Date(25, 8, 2023), 0.0051)

        self.libor6m_index = get_libor_index(6, libor_maturities, libor_rates,calendar, self.calc_date, day_count_convention)
        self.bumped_libor6m_index = get_libor_index(6, libor_maturities, [i + delta_upsize for i in libor_rates], calendar, self.calc_date, day_count_convention)
        self.dbl_bumped_libor6m_index = get_libor_index(6, libor_maturities, [i + gamma_upsize for i in libor_rates], calendar, self.calc_date, day_count_convention)

        self.libor12m_index = get_libor_index(12, libor_maturities, libor_rates,calendar, self.calc_date, day_count_convention)
        self.bumped_libor12m_index = get_libor_index(12, libor_maturities, [i + delta_upsize for i in libor_rates], calendar, self.calc_date, day_count_convention)
        self.dbl_bumped_libor12m_index = get_libor_index(12, libor_maturities, [i + gamma_upsize for i in libor_rates], calendar, self.calc_date, day_count_convention)

    def ql_date_from_tenor(self, tenor_str, calendar):

        if not tenor_str:
            return tenor_str

        tenor_map = {'D': ql.Days,
                     'M': ql.Months,
                     'Y': ql.Years}

        ql_timeline = tenor_map.get(tenor_str[-1].upper())
        units = float(tenor_str[:-1])

        return calendar.advance(self.calc_date, units, ql_timeline)

    def construct_swap(self, floating_index_tenor, pay_or_receive,  currency, notional,
                       fixed_rate, start_date, maturity_in_years, for_delta = False, for_gamma = False, for_swaption = False):

        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)

        if for_swaption:
            key = (floating_index_tenor.upper(), False, False)
        else:
            key = (floating_index_tenor.upper(), for_delta, for_gamma)

        index = self.swap_index_lookup_map.get(key)

        #print('Using key ' + str(key) + ' Got index ' + str(index))
        if not index:
            raise Exception("Unsupported floating leg tenor to construct Libor swap " + str(floating_index_tenor))
        start_date = start_date if start_date else calendar.advance(self.calc_date, 2, ql.Days)
        #print(self.calc_date, index, calendar, pay_or_receive, currency, fixed_rate, start_date, maturity_in_years)


        if not fixed_rate:
            try:
                key_fr = (floating_index_tenor.upper(), False, False)
                index_fr = self.swap_index_lookup_map.get(key)
                dummy_rate = 0.02
                #print('Using key ' + str(key_fr) + ' Got index ' + str(index_fr))
                swap = construct_swap(self.calc_date, index_fr, calendar, pay_or_receive, currency, notional, dummy_rate,
                                      start_date, maturity_in_years)
                swap.setPricingEngine(self.base_swap_engine)
                fixed_rate = swap.fairRate()
            except Exception as e:
                print("Could not calculate par rate for swap " + str(e))
                raise e

        if for_swaption:
            if for_gamma:
               fixed_rate = fixed_rate + 0.0002
            elif for_delta:
                fixed_rate = fixed_rate + 0.0001
            else:
                pass

        #print('Swap ... ', start_date, fixed_rate)
        swap = construct_swap(self.calc_date, index, calendar, pay_or_receive, currency, notional, fixed_rate, start_date,
                              maturity_in_years)

        if for_gamma:
            swap.setPricingEngine(self.dbl_bumped_swap_engine)
        elif for_delta:
            swap.setPricingEngine(self.bumped_swap_engine)
        else:
            swap.setPricingEngine(self.base_swap_engine)

        return swap

    def construct_swaption(self, floating_index_tenor, pay_or_receive, currency, notional,
                           fixed_rate, start_date, maturity_in_years, expiration_period,
                           for_delta=False, for_gamma=False):

        """
        {'payOrReceive': 'Rec', 'terminationDate': '5y', 'notionalCurrency': 'EUR',
        'expirationDate': '3m', 'fee': 0.0, 'assetClass': 'Rates', 'type': 'Swaption'},
        'instrumentName': 'EUR3m5y', 'quantity': 1}
        """
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)

        exercise_date = calendar.advance(self.calc_date, ql.Period(expiration_period))
        exercise = ql.EuropeanExercise(exercise_date)
        start_date = start_date if start_date else calendar.advance(exercise_date, 2, ql.Days)

        if not fixed_rate:
            swap = self.construct_swap(floating_index_tenor, pay_or_receive, currency, notional,
                                                  fixed_rate, start_date, maturity_in_years)

            fixed_rate = swap.fairRate()

        underlying_swap = self.construct_swap(floating_index_tenor, pay_or_receive, currency, notional,
                                   fixed_rate, start_date, maturity_in_years, for_delta, for_gamma, for_swaption=True)

        swaption = ql.Swaption(underlying_swap, exercise, ql.Settlement.Cash, ql.Settlement.ParYieldCurve)
        swaption.setPricingEngine(self.swaption_black_engine)
        return swaption


class CalcContext:

    def __init__(self, date_str, market):
        self.calc_date = ql.DateParser().parse(date_str, 'YYYY-MM-DD')
        self.market = market # dict {'date': '2023-07-06', 'location': 'LDN', 'marketType': 'CloseMarket'}


class QuantLibWorker:

    def __init__(self, request_queue_path = None, response_queue_path = None):
        print('Initializing QL Worker.....')
        self._listen = True
        request_queue_path = request_queue_path or 'OpenQuantAPI_Server_v1.0_request'
        response_queue_path = response_queue_path or 'OpenQuantAPI_Server_v1.0_response'
        global task_manager
        self._in_queue = PersistQueueManager(request_queue_path)
        self._out_queue = PersistQueueManager(response_queue_path)

    def get_calc_contexts(self, request):
        calc_contexts = []
        for pricing_details in request.get('pricingAndMarketDataAsOf'):
            calc_contexts.append(CalcContext(pricing_details.get('pricingDate'), pricing_details.get('market')))

        logger.debug('Got Calculation contexts ' + str(calc_contexts))
        return calc_contexts

    def maturity_in_years(self, maturity):
        if not maturity:
            return maturity

        if maturity[-1] in ( 'Y', 'y'):
            return float(maturity[:-1])
        elif maturity[-1] in ( 'M', 'm'):
            return round(float(maturity[:-1]) / 12, 2)
        else:
            raise Exception('Unsupported maturity ' + str(maturity))

    def parse_fx_option(self, inst_map,market, need_delta_insts, need_gamma_insts):
        inst, delta_inst, gamma_inst = None, None, None
        buy_sell = inst_map.get('buySell') or 'Buy'
        notional = inst_map.get('notionalAmount') or 10E8
        maturity_in_years = self.maturity_in_years(inst_map.get('expirationDate'))
        start_date = ql.DateParser().parse(inst_map.get('startDate'), 'YYYY-MM-DD') if inst_map.get(
            'startDate') else ql.Date.todaysDate()

        pair = inst_map.get('pair')
        strike_price = inst_map.get('strikePrice')
        strike_price = market.fx_spots[pair] if strike_price == 'ATMF' else float(strike_price)
        inst_quantity = notional * 1 if buy_sell == 'Buy' else -1
        option_type = ql.Option.Call if inst_map.get('optionType') == 'Call' else ql.Option.Put
        payoff = ql.PlainVanillaPayoff(option_type, strike_price)

        calendar = fx_calendars.get(pair)
        settlement_date = start_date if start_date else calendar.advance(start_date, 2, ql.Days)
        maturity_date = calendar.advance(settlement_date, int(maturity_in_years), ql.Years)

        europeanExercise = ql.EuropeanExercise(maturity_date)
        inst = ql.VanillaOption(payoff, europeanExercise)
        if inst_map.get('optionStyle') == 'European' or not inst_map.get('optionStyle'):
            inst.setPricingEngine(market.fxo_engines.get('European').get(pair))

        return inst, None, None, inst_quantity
        # {'pair': 'EURUSD', 'optionType': 'Call', 'strikePrice': 'ATMF',
        #                'expirationDate': '1y', 'assetClass': 'FX', 'type': 'Option'}

    def parse_swap(self, inst_map,market, need_delta_insts, need_gamma_insts):
        inst, delta_inst, gamma_inst = None, None, None
        pay_or_rec = inst_map.get('payOrReceive')
        ccy = inst_map.get('notionalCurrency')
        notional = inst_map.get('notionalAmount') or 10E8
        maturity_in_years = self.maturity_in_years(inst_map.get('terminationDate'))
        fixed_rate = float(inst_map.get('fixedRate')) if inst_map.get('fixedRate') else None
        start_date = ql.DateParser().parse(inst_map.get('startDate'), 'YYYY-MM-DD') if inst_map.get(
            'startDate') else None
        # print('building swap ... ')
        pay_or_rec = get_swap_pay_rec(pay_or_rec)  # swap Pay Rec func
        floating_rate_tenor = inst_map.get('floating_rate_designated_maturity') or '3m'
        inst = market.construct_swap(floating_rate_tenor, pay_or_rec, ccy, notional, fixed_rate, start_date,
                                     maturity_in_years)

        if need_delta_insts:
            # print('building swap for delta... ')
            delta_inst = market.construct_swap(floating_rate_tenor, pay_or_rec, ccy, notional, fixed_rate, start_date,
                                               maturity_in_years, True)
        if need_gamma_insts:
            # print('building swap for gamma... ')
            gamma_inst = market.construct_swap(floating_rate_tenor, pay_or_rec, ccy, notional, fixed_rate, start_date,
                                               maturity_in_years, True, True)
        return inst, delta_inst, gamma_inst, 1.0

    def parse_swaption(self, inst_map,market, need_delta_insts, need_gamma_insts):
        inst, delta_inst, gamma_inst = None, None, None
        pay_or_rec = inst_map.get('payOrReceive')
        ccy = inst_map.get('notionalCurrency')
        notional = inst_map.get('notionalAmount') or 10E8
        maturity_in_years = self.maturity_in_years(inst_map.get('terminationDate'))
        fixed_rate = float(inst_map.get('fixedRate')) if inst_map.get('fixedRate') else None
        start_date = ql.DateParser().parse(inst_map.get('startDate'), 'YYYY-MM-DD') if inst_map.get(
            'startDate') else None
        # print('building swaption ... ')
        pay_or_rec = get_swap_pay_rec(pay_or_rec)  # swap Pay Rec func
        floating_rate_tenor = inst_map.get('floating_rate_designated_maturity') or '3m'
        expiration_period = inst_map.get('expirationDate') or '3M'  # For swaps this field is 1M, 2M,..
        start_date = inst_map.get('startDate')
        # logger.info('{0}, {1} , {2}, {3} '.format(floating_rate_tenor, pay_or_rec, expiration_period, str(maturity_in_years)))

        inst = market.construct_swaption(floating_rate_tenor, pay_or_rec, ccy, notional, fixed_rate, start_date,
                                         maturity_in_years, expiration_period)

        if need_delta_insts:
            # print('building swaption for delta... ')
            delta_inst = market.construct_swaption(floating_rate_tenor, pay_or_rec, ccy, notional,
                                                   fixed_rate,
                                                   start_date, maturity_in_years, expiration_period,
                                                   for_delta=True, for_gamma=False)
        if need_gamma_insts:
            # print('building swaption for gamma... ')
            gamma_inst = market.construct_swaption(floating_rate_tenor, pay_or_rec, ccy, notional,
                                                   fixed_rate,
                                                   start_date, maturity_in_years,
                                                   expiration_period, for_delta=True, for_gamma=True)
        return inst, delta_inst, gamma_inst, 1.0

    def build_instruments(self, payload, market, need_delta_insts, need_gamma_insts):
        instruments = {}
        delta_instruments = {}
        gamma_instruments = {}
        quantities = {}
        type_to_parse = { 'FXOption': self.parse_fx_option,
                          'Swap': self.parse_swap,
                          'Swaption': self.parse_swaption
                          }
        #print( 'Payload ' + str(payload))
        request_data = payload.get('request', {})
        for asset_class in request_data.keys():
            if not isinstance(request_data.get(asset_class), dict):
                continue
            for asset_type in request_data.get(asset_class):
                for inst_map in request_data.get(asset_class).get(asset_type):
                    inst_type = inst_map.get('type')
                    inst_idx = inst_map.get('sequence_no')
                    parser_fn = type_to_parse.get(inst_type) or type_to_parse.get(asset_class + inst_type)
                    inst, delta_inst, gamma_inst, quantity = parser_fn(inst_map,market, need_delta_insts, need_gamma_insts)
                    instruments[inst_idx] = inst
                    delta_instruments[inst_idx] = delta_inst or None
                    gamma_instruments[inst_idx] = gamma_inst or None
                    quantities[inst_idx] = quantity

        return instruments, delta_instruments , gamma_instruments, quantities

    def get_measures(self, payload):
        measures = []

        for i in payload.get('measures'):
            measures.append(i.get('measureType'))

        logger.debug('Got measures ' + str(measures))

        return measures

    def unpack_message(self, payload):
        """
        wrote this just to make testing easy
        """
        key = payload.get('key')
        calc_contexts = self.get_calc_contexts(payload.get('request'))
        measures = self.get_measures(payload.get('request'))
        return key, calc_contexts, measures

    def validate_message(self, payload):
        key = payload.get('key')

        if not key:
            raise Exception('Invalid message ... ')

        if not payload.get('request'):
            raise Exception('No valid request found for message with key ' + str(key))


    def get_measure(self, measure, inst, delta_inst, gamma_inst, quantity):
        val = np.nan
        ql_measure = measures_map.get(measure)
        try:
            if not ql_measure:
                logger.error('Could not find an equivalent QuantLib measure for ' + str(measure))
            elif ql_measure == 'NPV':
                val = inst.NPV()
            elif ql_measure == 'Delta' and delta_inst:
                base_npv = inst.NPV()
                bumped_npv = delta_inst.NPV()
                val = bumped_npv - base_npv
                #print(inst, base_npv, bumped_npv, val)
            elif ql_measure == 'Gamma' and delta_inst and gamma_inst:
                base_npv = inst.NPV()
                bumped_npv = delta_inst.NPV()
                dbl_bumped_npv = gamma_inst.NPV()
                val = (dbl_bumped_npv - bumped_npv) - (bumped_npv - base_npv)
                #print(inst, base_npv, bumped_npv, dbl_bumped_npv, val)
            else:
                measure_fn = None
                try:
                    try:
                        measure_fn = getattr(inst, ql_measure)
                    except AttributeError as ae:
                        try:
                            measure_fn = getattr(inst, ql_measure.lower())
                        except AttributeError as ae:
                            pass

                    if measure_fn:
                        val = measure_fn()
                except AttributeError as ae:
                    val = np.nan
                    #print('Measure {0} is not supported on inst {1}'.format(str(measure), type(inst)))
        except Exception as e:
            print(e)

        #print("Returning val {0} for measure {1}".format(str(val), measure))
        if isinstance(val, float):
            val = 0.0 if abs(val) < TOLERANCE else val * quantity
        return val

    def process_message(self, payload):
        logger.debug('processing message ' )
        key, calc_contexts, measures = self.unpack_message(payload)

        # Py Quantlib does not expose all the second order analytics on a given instrument
        # We need to construct with bumped curves and fetch delta, gamma

        need_gamma_insts = 'Gamma' in measures
        need_delta_insts = 'Delta' in measures or need_gamma_insts  # We need delta to calc gamma
        all_vals = []
        if not calc_contexts:
            raise Exception('No dates')
        calc_ctx = calc_contexts[0]
        market = Market(calc_ctx.calc_date)
        #one_date =
        insts, delta_insts, gamma_insts, quantities = self.build_instruments(payload, market, need_delta_insts, need_gamma_insts)
        print('Measures ', measures, len(insts), "quantities", quantities)
        measure_vals = []
        for measure in measures:
            inst_vals = []
            for idx in range(0, len(insts)):
                date_vals = []
                for calc_ctx in calc_contexts:
                    #if
                    market = Market(calc_ctx.calc_date)
                    insts, delta_insts, gamma_insts, quantities = self.build_instruments(payload, market, need_delta_insts, need_gamma_insts)
                    val = self.get_measure(measure, insts[idx], delta_insts[idx] if delta_insts else None, gamma_insts[idx] if gamma_insts else None, quantities[idx])
                    val_dict = {
                        '$type': 'Risk',
                        'val': val,
                    }
                    date_vals.append(val_dict)
                inst_vals.append(date_vals)
            measure_vals.append(inst_vals)
        #print('Results ..... ' + str([measure_vals]))
        self._out_queue.put([measure_vals])
        return [measure_vals]

    def start(self):
        print('Starting QL Worker....')
        while (self._listen):
            logger.debug('Waiting to get a message ')
            payload = msgpack.loads(self._in_queue.get())
            print(payload)
            self.validate_message(payload)
            self.process_message(payload)

    def stop(self):
        self._listen = False

def main():
    # start the worker
    # construct instruments
    # get analytics for each instrument
    # aggregate results
    # add responses to a queue
    qlw = QuantLibWorker()
    qlw.start()


if __name__ == '__main__':
    main()
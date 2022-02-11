import yfinance as yf
from .utils import Utils
import datetime as dt
import pandas as pd
"""
contractSymbol lastTradeDate  strike  lastPrice bid  ask  change  percentChange  volume  openInterest  impliedVolatility  inTheMoney contractSize currency
"""


class OptionsChain:

    def __init__(self, ticker):
        self._ticker = yf.Ticker(ticker)
        self._options_dates = self._ticker.options

    @property
    def dates(self):
        return self._options_dates

    @staticmethod
    def options_extras(opts, opt_name, price, drift, volatility, days, rfir):
        opt_extra = []
        for i, rec in opts.iterrows():
            #
            option_price = Utils.peg(rec['bid'], rec['ask'], 0.5)
            if option_price <= 0.001:
                option_price = rec['lastPrice']
            #
            prob_itm = 0
            est_price = 0
            delta = 0
            durr_vol = 0
            eprob_itm = 0
            bsm_price = 0
            bprob_itm = 0
            idv = 0
            #
            if not rec["inTheMoney"]:
                #
                prob_itm = Utils.itm_option(
                    opt_name, price, rec['strike'], volatility, drift, days)
                prob_itm *= 100
                #
                est_price, delta, durr_vol, eprob_itm = Utils.option_price(
                    opt_name, price, rec['strike'], volatility, days, rfir)
                eprob_itm *= 100
                #
                bsm_price, delta, durr_vol, bprob_itm, idv = Utils.bsm_idv(
                    opt_name, price, rec['strike'], option_price, days, rfir)
                bprob_itm *= 100
            #
            opt_extra.append({
                "mid": option_price,
                "probabilityITM": prob_itm,
                "estimatedPrice": est_price,
                "estimatedProbability": eprob_itm,
                "bsmPrice": bsm_price,
                "bsmProbability": bprob_itm,
                "delta": delta,
                "durrationVolatility": durr_vol,
                "idv": idv
            })
        return pd.DataFrame(opt_extra)

    def extended_options_chain(
        self,
        date,
        price,
        drift,
        volatility,
        days=None,
        rfir=0.001,
        exclude=[
            "contractSymbol",
            "lastTradeDate",
            "contractSize",
            "currency"]):
        if days is None:
            date_string = self._options_dates[date] if isinstance(
                date, int) else date
            timedelta = dt.date.fromisoformat(date_string) - dt.date.today()
            days = timedelta.days
        #
        calls, puts = self.get_option_chain(date)
        puts.drop(columns=exclude, inplace=True)
        calls.drop(columns=exclude, inplace=True)
        #
        put_extras = OptionsChain.options_extras(
            puts, "PUT", price, drift, volatility, days, rfir)
        extended_puts = puts.join(put_extras)
        #
        call_extras = OptionsChain.options_extras(
            calls, "CALL", price, drift, volatility, days, rfir)
        extended_calls = calls.join(call_extras)
        return extended_calls, extended_puts

    def get_option_chain(self, date):
        date_string = self._options_dates[date] if isinstance(
            date, int) else date
        return self._ticker.option_chain(date_string)

    def get_option_calls(self, date):
        calls, _ = self.get_option_chain(date)
        return calls

    def get_option_puts(self, date):
        _, puts = self.get_option_chain(date)
        return puts

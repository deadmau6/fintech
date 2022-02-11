"""
# Original version May 7, 2017
# This version 2.9, June 6, 2020
# Maintained by Professor Evans
#
# Copyright 2020 Gary R. Evans
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# DESCRIPTION
#
# These are the utilities that are used throughout the various financial models
# for such things as calculating options prices and volatilities. These are
# designed to be used with Version 3.7 or higher of Python.
#
# THE SECTION FOR TIME AND CALENDAR COUNTS was moved from here to timeutil.py on
# August 14, 2019. Methods moved include daysto, iso_saysto, iso_daysto_days and
# monthname. Not all programs have been tested for the transfer.
"""
import math
import datetime
import scipy.integrate
from scipy.stats import norm, kurtosis, skew, sem
import numpy as np
from datetime import datetime
from collections import deque
from typing import List


class Utils:

    @staticmethod
    def price_range(current_price: float, spread: int = 1, show_amount: int = 5) -> List[float]:
        current_price = round(current_price, 2)
        up, down = current_price, current_price
        prices = deque([current_price])
        #
        for i in range(0, spread * show_amount, spread):
            up = round(up + spread, 2)
            # add to the right side
            prices.append(up)
            down = round(down - spread, 2)
            # add to the left
            prices.appendleft(down)
            #
            if (down - spread) <= 0:
                break
        return prices

    @staticmethod
    def bsm_prices_matrix(option, prices: list, days: int, rfir: float) -> list:
        matrix = {}
        while days > 0:
            bsm_prices = Utils.bsm_prices(option, prices, days, rfir)
            matrix[days] = bsm_prices
            days -= 1
        return matrix

    @staticmethod
    def bsm_prices(option, prices: List[float], days: int, rfir: float) -> list:
        bsm_prices = {}
        for price in prices:
            # TODO: fix `option.price` to take into account time decay.
            bsm_price = Utils.bsm_idv(option.typ, price, option.strike, option.price, days, rfir)[0]
            bsm_prices[price] = bsm_price
        return bsm_prices

    @staticmethod
    def estimated_prices_matrix(option, prices: list, day_vol: float, days: int, rfir: float) -> list:
        matrix = {}
        while days > 0:
            estimated_prices = Utils.estimated_prices(option, prices, day_vol, days, rfir)
            matrix[days] = estimated_prices
            days -= 1
        return matrix

    @staticmethod
    def estimated_prices(option, prices: list, day_vol: float, days: int, rfir: float) -> list:
        estimated_prices = {}
        for price in prices:
            est_price = Utils.option_price(option.typ, price, option.strike, day_vol, days, rfir)[0]
            estimated_prices[price] = est_price
        return estimated_prices

    @staticmethod
    def get_stats(ndata):
        return {
            'mean': np.mean(ndata),
            'variance': np.var(ndata),
            'standard_deviation': np.std(ndata),
            'median': np.median(ndata),
            'max': np.max(ndata),
            'min': np.min(ndata),
            'skew': skew(ndata),
            'kurtosis': kurtosis(ndata),
            'standard_error_mean': sem(ndata)
        }

    @staticmethod
    def remove_nulls(data, index=None):
        if index is None:
            clean = [(i, d) for i, d in enumerate(data) if d]
            return clean
        clean = [(i, d) for i, d in zip(index, data) if d]
        return clean

    @staticmethod
    def convert_numpy_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime):
            try:
                return obj.isoformat()
            except Exception as e:
                return obj.__str__()

    @staticmethod
    def csnd(point: float) -> float:
        """Integrates a standard normal distribution up to some sigma."""
        return (1.0 + math.erf(point / math.sqrt(2.0))) / 2.0

    @staticmethod
    def cnd(center: float, point: float, stdev: float) -> float:
        """Integrates a Gaussian distribution up to some value."""
        return (1.0 + math.erf((point - center) / (stdev * math.sqrt(2.0)))) / 2.0

    @staticmethod
    def make_bitseq(s: str) -> str:
        """
        Used to convert any string into sequences of 8 bits.
        NOTE: This was put at the top of the utility as an example of the newer formatting for methods.
        """
        return " ".join(f"{ord(i):08b}" for i in s)

    @staticmethod
    def durration_volatility(daily_vol: float, time) -> float:
        """
        The primary method for converting daily volatility to duration volatility. This
        function below requires the sigma argument.
        """
        return daily_vol * math.sqrt(time)

    @staticmethod
    def bsm_idv(
            option_type: str,
            stock: float,
            strike: float,
            option_price: float,
            days: int,
            rate: float) -> list:
        """ Runs Black-Scholes-Merton IDV for options."""
        if option_type == 'CALL':
            return Utils.bsm_idv_call(stock, strike, option_price, days, rate)
        return Utils.bsm_idv_put(stock, strike, option_price, days, rate)

    @staticmethod
    def bsm_idv_call(
            stock: float,
            strike: float,
            target: float,
            days: int,
            rate: float) -> list:
        """
        A modification of the call_idv_bsdc model. This is the B-S-M IDV
        model for calls only, using divide and conquer iteration for conversion. This model
        requires stock price, strike price, days (use timeutil.iso_daysto_days if you have
        a calendar date), call price (use peg within this utility if you have bid/ask), and
        interest rate (0 is allowed). This passes out a list of the delta, probability ITM,
        and implied volatility. This is called often from the spread models.
        Added May 2020.
        """
        precision = float(1e-3)
        low = 0.0
        high = 1.0
        idv = float((high + low) / 2)
        temp = Utils.call_option_price(
            stock,
            strike,
            idv,
            days,
            rate)  # passes out a tuple
        temp_price = temp[0]
        i = 2e6
        while temp_price <= (target - precision) or temp_price >= (target + precision):
            if temp_price >= (target + precision):
                high = idv
            else:
                low = idv
            idv = float((high + low) / 2)
            temp = Utils.call_option_price(stock, strike, idv, days, rate)
            temp_price = temp[0]
            if temp_price <= 0.0:
                break
            if i == 0:
                print("Reached max limit")
                break
            i -= 1
        price, delta, durvol, prob_itm = temp
        return price, delta, durvol, prob_itm, idv

    @staticmethod
    def bsm_idv_put(
            stock: float,
            strike: float,
            target: float,
            days: int,
            rate: float) -> list:
        """
        A modification of the put_idv_bsdc model. This is the B-S-M IDV
        model for puts only, using divide and conquer iteration for conversion. This model
        requires stock price, strike price, days (use timeutil.iso_daysto_days if you have
        a calendar date), put price (use peg within this utility if you have bid/ask), and
        interest rate (0 is allowed). This passes out a tuple of the delta, probability ITM,
        and implied volatility. This is called often from the spread models.
        Added May 2020.
        """
        precision = float(1e-3)
        low = 0.0
        high = 1.0
        idv = float((high + low) / 2)
        temp = Utils.call_option_price(
            stock,
            strike,
            idv,
            days,
            rate)  # passes out a tuple
        temp_price = temp[0]
        i = 2e6
        while temp_price <= (target - precision) or temp_price >= (target + precision):
            if temp_price >= (target + precision):
                high = idv
            else:
                low = idv
            idv = float((high + low) / 2)
            temp = Utils.put_option_price(stock, strike, idv, days, rate)
            temp_price = temp[0]
            if temp_price <= 0.0:
                break
            if i == 0:
                print("Reached max limit")
                break
            i -= 1
        price, delta, durvol, prob_itm = temp
        return price, delta, durvol, prob_itm, idv

    @staticmethod
    def option_price(
            option_type: str,
            stock: float,
            strike: float,
            day_vol: float,
            days: int,
            rfir: float) -> list:
        if option_type == 'CALL':
            return Utils.call_option_price(stock, strike, day_vol, days, rfir)
        return Utils.put_option_price(stock, strike, day_vol, days, rfir)

    @staticmethod
    def call_option_price(
            stock: float,
            strike: float,
            day_vol: float,
            days: int,
            rfir: float) -> list:
        """
        Calculating exactly the same as copo, but also passing out one more
        variable in the tuple, probability of being in the money (at expiry).
        Calculating the BSM CALL option price, traditional model. This requires the
        user to provide stock price, strike price, daily volatility, risk-free interest
        rate and days to expiry. (To calculate days use method daysto below).
        This returns the call price, the delta, and duration volatility as a tuple
        array. See popo below for puts. NOTE: Since cum2 is itm_prob, expand the tuple
        to pass out itm_prob at some point for this and popo.
        """
        d1 = math.log(stock / strike) + ((rfir / 365) + (day_vol**2) / 2) * days
        # durvol = dayvol * math.sqrt(days)
        durr_vol = Utils.durration_volatility(day_vol, days)
        delta = Utils.csnd(d1 / durr_vol) if durr_vol > 0.0 else 0.0
        prob_itm = Utils.csnd((d1 / durr_vol) - durr_vol) if durr_vol > 0.0 else 0.0
        discount = math.exp(-rfir * days / 365)
        price = (stock * delta) - (strike * discount * prob_itm)
        return price, delta, durr_vol, prob_itm

    @staticmethod
    def put_option_price(
            stock: float,
            strike: float,
            day_vol: float,
            days: int,
            rfir: float) -> list:
        """
        Calculating exactly the same as popo, but also passing out one more
        variable in the tuple, probability of being in the money (at expiry).
        Calculating the BSM PUT option price, traditional model. This requires the
        user to provide stock price, strike price, daily volatility, risk-free interest
        rate and days to expiry. (To calculate days use method daysto above).
        This returns the put price, the delta, and duration volatility as a tuple
        array. See copo above for calls..
        """
        d1 = math.log(stock / strike) + ((rfir / 365) + (day_vol**2) / 2) * days
        # durvol = dayvol * math.sqrt(days)
        durr_vol = Utils.durration_volatility(day_vol, days)
        delta = Utils.csnd(-d1 / durr_vol) if durr_vol > 0.0 else 0.0
        prob_itm = Utils.csnd(-(d1 / durr_vol - durr_vol)) if durr_vol > 0.0 else 0.0
        discount = math.exp(-rfir * days / 365)
        price = -(stock * delta) + (strike * discount * prob_itm)
        return price, delta, durr_vol, prob_itm

    @staticmethod
    def delta_call(
            stock_price: float,
            strike: float,
            sigma: float,
            alpha: float,
            rate: float,
            days: float) -> float:
        """
        The estimator for the classical call delta.
        This version allows for drift and uses the half-variance ITO
        adjustment. This takes the risk-free rate into account.
        See also delta_put. For documentation ...
        """
        sto_pr_exp = stock_price * math.exp(alpha * days)
        # dur_vol = sigma * math.sqrt(days)
        dur_vol = Utils.durration_volatility(sigma, days)
        log_spread = math.log(strike / sto_pr_exp)
        ito_adj = Utils.discount_rfrate(rate, sigma, days)  # Ito ajustment
        norm_ls = log_spread / dur_vol
        norm_ls_adj = norm_ls - (dur_vol / 2) - ito_adj
        return 1 - Utils.csnd(norm_ls_adj)

    @staticmethod
    def delta_put(
            stock_price: float,
            strike: float,
            sigma: float,
            alpha: float,
            rate: float,
            days: float) -> float:
        """
        The estimator for the classical put delta.
        This version allows for drift and uses the half-variance ITO
        adjustment. This takes the risk-free rate into account.
        """
        sto_pr_exp = stock_price * math.exp(alpha * days)
        dur_vol = Utils.durration_volatility(sigma, days)
        log_spread = math.log(strike / sto_pr_exp)
        ito_adj = Utils.discount_rfrate(rate, sigma, days)  # Ito ajustment
        norm_ls = log_spread / dur_vol
        norm_ls_adj = norm_ls - (dur_vol / 2) - ito_adj
        return Utils.csnd(norm_ls_adj)

    @staticmethod
    def drift(alpha: float, time) -> float:
        """
        An elementary function for calculating the stock price adjusted for drift.
        Time can be an integer or a float.
        """
        return 1.0 * math.exp(alpha * time)

    @staticmethod
    def discount(risk_free_rate: float, time) -> float:
        """
        A time-discount function to discount the value of a future payment (like an
        option) discounted at the risk-free interest rate. The variable risk_free_rate
        is annual and time is in days.
        """
        return 1.0 * math.exp(-1.0 * (risk_free_rate / 365) * time)

    @staticmethod
    def discount_rfrate(risk_free_rate: float, sigma, time) -> float:
        """
        A component of options pricing models and calculators for delta
        and prob ITM. It is usually called as a component of the delta (d1) or prob_itm (d2)
        formula in options pricing models. It is equal to rfr/365 times days divided by
        duration volatility [sqrt(t)/t] reduced to [sqrt(t)].
        """
        return ((risk_free_rate / 365) * math.sqrt(time)) / sigma

    @staticmethod
    def itm_option(
            option_type: str,
            stock_price: float,
            strike: float,
            sigma: float,
            alpha: float,
            days: float) -> float:
        """
        itm_option: itm_call and itm_put rolled into one - indentical except the user
        sets true of false to the question of whether this is a call.
        This provides the estimator for the probability that the option will be ITM at expiry.
        This version allows for drift and uses the half-variance ITO
        adjustment.
        itm_call: The estimator for the probability that the call will be ITM at expiry.
        This version allows for drift and uses the half-variance ITO
        adjustment.
        itm_put: the estimator for the probability that the call will be ITM at expiry.
        This version allows for drift and uses the half-variance ITO
        adjustment.
        """
        sto_pr_exp = stock_price * math.exp(alpha * days)
        # dur_vol = sigma * math.sqrt(days)
        dur_vol = Utils.durration_volatility(sigma, days)
        log_spread = math.log(strike / sto_pr_exp)
        norm_ls = log_spread / dur_vol
        norm_ls_adj = norm_ls + (dur_vol / 2)    # This is the Ito ajustment
        if option_type == 'CALL':
            return 1 - Utils.csnd(norm_ls_adj)
        return Utils.csnd(norm_ls_adj)

    @staticmethod
    def itm_option_rfr(
            option_type: str,
            stock_price: float,
            strike: float,
            sigma: float,
            alpha: float,
            rfrate: float,
            days: float) -> float:
        """
        itm_option_rfr: itm_call_rfr and itm_put_rfr rolled into one - indentical except
        the user sets true of false to the question of whether this is a call.
        This providesthe estimator for the probability that the option will be ITM at expiry.
        This version allows for drift, takes an interest rate (which is how it differs from
        itm_option) and uses the half-variance ITO adjustment.
         * itm_call_rfr: the estimator for the probability that the call will be ITM at expiry.
        This version allows for drift and allows for a risk-free rate. itm_call was left
        unaltered because it is used on a lot of legacy programs single-day trade programs.
        This is for longer-duration trades. Only line 5 is changed.
         * itm_put_rfr: the estimator for the probability that the put will be ITM at expiry.
        This version allows for drift and allows for a risk-free rate. itm_put was left
        unaltered because it is used on a lot of legacy programs single-day trade programs.
        This is for longer-duration trades. Only line 5 is changed.
        """
        sto_pr_exp = stock_price * math.exp(alpha * days)
        # dur_vol = sigma * math.sqrt(days)
        dur_vol = Utils.durration_volatility(sigma, days)
        log_spread = math.log(strike / sto_pr_exp)
        ito_adj = Utils.discount_rfrate(rfrate, sigma, days)  # Ito ajustment
        norm_ls = log_spread / dur_vol
        norm_ls_adj = norm_ls + (dur_vol / 2) - ito_adj
        if option_type == 'CALL':
            return 1 - Utils.csnd(norm_ls_adj)
        return Utils.csnd(norm_ls_adj)

    @staticmethod
    def ito_half_var(sigma: float, days: float) -> float:
        """
        ito_half-var is the adjustment that must be made to drift in the Geometric
        Brownian Motion Model, such as calculating the probability of being ITM
        for an option. Similar to lnmeanshift.
        """
        return (sigma * sigma * days / 2)

    @staticmethod
    def lnmeanshift(sigma: float) -> float:
        """
        lnmeanshift is an elementary price expected-mean-value adjustment multiplier
        for log distributed prices for 1 day only. The mean of a log-distributed pdf is adjusted by
        minus one-half variance. NOTE: This is similar to half_var. Various models
        used both names and we didn't want to break anything.
        """
        return 1.0 * math.exp(-1.0 * (sigma * sigma / 2))

    @staticmethod
    def norm_dist(x: float, mu: float, sigma: float) -> float:
        """
        norm_dist (normal distribution) accepts a single value for x, mu, and sigma
        and returns a scalar solution for the pdf (the MLE). This is ideal for use with a
        lambda function. See also stan_norm_dist below (for standard normal).
        """
        always = 1 / math.sqrt(2 * math.pi * (sigma**2))
        expo = -((x - mu)**2) / (2 * (sigma**2))
        pdf = always * math.exp(expo)
        return pdf

    @staticmethod
    def norm_dist_vec(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
        """
        norm_dist_vec (normal distribution) is designed to accept x as a NUMPY
        ARRAY that has been established with a numpy command like np.linspace(-3,3,61),
        along with scalars for mu and sigma. This returns another numpy array of the
        pdf. Note the difference between this and norm_dist. See also stan_nd_vec
        for standard normal array. This can be integrated with a lambda function.
        """
        always = 1 / math.sqrt(2 * math.pi * (sigma**2))
        length = x.size
        pdf_vec = np.zeros(length)
        pdf_vec = always * np.exp(-((x - mu)**2) / (2 * (sigma**2)))
        return pdf_vec

    @staticmethod
    def norm_dist_cdf(
            mu: float,
            sigma: float,
            low_lim: float,
            point: float) -> tuple:
        """
        norm_dist_cdf integrates a normal vector using a lambda function and
        scipy's integration function (which can only take a function as an input).
        See the explanation for the stan_norm_cdf function (standard normal) below
        because this is easier to understand after seeing that. The output
        is usually thought of as a probability. Note the use of lambda and its use of
        z.
        """
        def nd_function(z):
            return Utils.norm_dist(z, mu, sigma)
        return scipy.integrate.quad(nd_function, low_lim, point)

    @staticmethod
    def otranche(stock, strike, dur_sigma, call):
        """
        OTRANCHE is an option tranche value calculator function that assumes you
        have a stock price and strike price, adjusted externally (for example, drift
        is adjusted with drift above). This will calculate the strike-price adjusted
        tranche from either -5 sigma to the strike or from the strike to +5 sigma.
        Sigma used here is duration sigma, adjusted outside using durvol above.
        Main program must set call to true if a call, false if a put.
            NOT DIRECTLY RETESTED AS OF JUNE 27, 2019 - HOWEVER, otranche is called
        extensively by oidv in many applications with no problems.
        """
        sigma_spread = (math.log(strike / stock)) / dur_sigma
        if call:
            bin_border = np.linspace(sigma_spread, 5.00, num=24, dtype=float)
        else:
            bin_border = np.linspace(-5.0, sigma_spread, num=24, dtype=float)
        size = len(bin_border)
        bin_edge_prob = np.zeros(size)
        for i in range(0, size):
            bin_edge_prob[i] = Utils.csnd(bin_border[i])
        size = size - 1
        bin_prob = np.zeros(size)
        bin_mid_price = np.zeros(size)
        bin_value = np.zeros(size)
        for i in range(0, size):
            bin_prob[i] = bin_edge_prob[i + 1] - bin_edge_prob[i]
            bin_mid_price[i] = ((stock * math.exp(((bin_border[i + 1] + bin_border[i]) / 2.0)
                                                  * dur_sigma)) * Utils.lnmeanshift(dur_sigma)) - strike
            bin_value[i] = bin_mid_price[i] * bin_prob[i]
        if call:
            return np.sum(bin_value[0:(i + 1)])
        return (np.sum(bin_value[0:(i + 1)])) * -1.0

    @staticmethod
    def ftranche(stock, strike, sigma, left):
        """
        FTRANCHE is a full tranche value calculator function that assumes you have a
        stock price and reference price, usually a strike price (and still called that
        here). This will calculate the tranche value from either -5 sigma to the
        reference price (left is true) or from the reference to +5 sigma (left
        is false). This is similar to otranche except that it does not subtract the
        strike price and therefore gives the full value of the tranche. It is
        designed to be used primarily by the Aruba Model to calculate the value of
        the remaining stock tranche if the covered call you wrote has been exercised.
            NOT RETESTED AS OF JUNE 27, 2019
        """
        sigma_spread = (math.log(strike / stock)) / sigma
        if left:
            bin_border = np.linspace(-5.0, sigma_spread, num=24, dtype=float)
        else:
            bin_border = np.linspace(sigma_spread, 5.00, num=24, dtype=float)
        size = len(bin_border)
        bin_edge_prob = np.zeros(size)
        for i in range(0, size):
            bin_edge_prob[i] = Utils.csnd(bin_border[i])
        size = size - 1
        # size += 1
        bin_prob = np.zeros(size)
        bin_mid_price = np.zeros(size)
        bin_value = np.zeros(size)
        for i in range(0, size):
            bin_prob[i] = bin_edge_prob[i + 1] - bin_edge_prob[i]
            bin_mid_price[i] = ((stock *
                                 math.exp(((bin_border[i +
                                                       1] +
                                            bin_border[i]) /
                                           2.0) *
                                          sigma)) *
                                Utils.lnmeanshift(sigma))
            bin_value[i] = bin_mid_price[i] * bin_prob[i]
        tranche_price = np.sum(bin_value[0:(i + 1)])
        return tranche_price

    @staticmethod
    def oidv(
            stock: float,
            strike: float,
            ovalue: float,
            days,
            call: bool) -> list:
        """
        OIDV calculates implied daily and duration volatility for a call or a put
        using divide and conquer (the default for most models). Also see oidvnm.
        This uses an iterative process that uses otranche (above) to calculate the
        sigma, here an implied sigma, from the existing option value (ovalue).
        The call variable is True for a call, False for a put. The convergence is
        within the while loop. This function returns a tuple of two values, daily
        IDV and duration IDV.
        """
        precision = float(1e-4)
        low = 0.0
        high = 1.0
        day_sigma = float((high + low) / 2)
        dur_sigma = Utils.durration_volatility(day_sigma, days)
        tempop = Utils.otranche(stock, strike, dur_sigma, call)
        while tempop <= (ovalue - precision) or tempop >= (ovalue + precision):
            if tempop >= (ovalue + precision):
                high = day_sigma
            else:
                low = day_sigma
            day_sigma = float((high + low) / 2)
            dur_sigma = Utils.durration_volatility(day_sigma, days)
            tempop = Utils.otranche(stock, strike, dur_sigma, call)
        # End of Loop!
        return day_sigma, dur_sigma

    @staticmethod
    def oidvnm(stock, strike, ovalue, days, call):
        """
        oidvnm calculates implied daily and duration volatility for a call or a put
        using Newton's Method for convergence (default is divide and conquer).
        This uses an iterative process that uses otranche (above) to calculate the
        sigma, here an implied sigma, from the existing option value (ovalue).
        The call variable is True for a call, False for a put. The convergence is
        within the while loop. This function returns a tuple of two values, daily
        IDV and duration IDV.
            NO LONGER USING BECAUSE OF EXPLOSIONS ... USE DIVIDE AND CONQUER (oidv). This
        should still work, though, for most applications.
        """
        seedsigma = 1e-6
        durseed = Utils.durration_volatility(seedsigma, days)
        # NOTE: daysigma is supposed to be set at a reasonable estimate of the
        # actual idv. The Newton method can explode if it is not (especially if you
        # enter option price, strike, and value data that are very unrealistic).
        # Consider setting daysigma at sqrt*time*ln(strike/stock). It was
        # originally set at 0.05
        daysigma = (math.log(strike / stock)) * math.sqrt(days)
        dursigma = Utils.durration_volatility(daysigma, days)
        cutoff = 1e-4
        tempop = float(0.00)
        #
        # The loop starts here. You start with a test sigma and converge to the
        # actual sigma. The convergence shown here (Newton's method) was designed
        # by Alec Griffith '17
        #
        while np.abs(tempop - ovalue) > cutoff:
            tempop = Utils.otranche(stock, strike, dursigma, call)
            price2 = Utils.otranche(stock, strike, dursigma + durseed, call)
            deriv = (price2 - tempop) / seedsigma
            daysigma -= (tempop - ovalue) / deriv
            dursigma = daysigma * durvol(days)
        # End of Loop!
        return daysigma, dursigma

    @staticmethod
    def peg(bid: float, ask: float, spread_perc: float) -> float:
        """
        PEG: Simply takes the bid and ask and spread, and calculates the peg price.
        Used in combination with programs that also use bsm_idv_X and similar, which
        don't calculate peg. The spread_perc is a value between 0 and 1 and is added
        to the bid floor. Default is 0.50. Many IB algos use 0.70 for buy-to-open,
        0.30 for sell-to-close as default.
        This is the IEEE754 standard for rounding numbers to nearest even.
        """
        ba_spread = ask - bid
        spread = ba_spread * spread_perc
        single_price_peg = round(bid + spread, 2)
        return single_price_peg

    @staticmethod
    def snormdf(point: float) -> float:
        """
        st_norm_df maps the standard normal probability density function of a point
        (the maximum likelihood estimator). This is an older method used in older
        programs and has been replaced with stan_norm_dist below, which lends itself
        to more complicated applications like stan_nd_vec.
        The point will be a float between -4.0 and 4.0.
        """
        return (1 / (math.sqrt(2 * math.pi))) * \
            math.pow(math.e, -0.5 * point**2)

    @staticmethod
    def stan_norm_dist(x: float) -> float:
        """
        stan_norm_dist (standard normal distribution) is designed to accept a single
        value for x and returns as scalar solution for the standard normal pdf. This
        gives the same solution as snormdf above (MLE).
        This is ideal for use with a lambda function.
        """
        always = 1 / math.sqrt(2 * math.pi)
        expo = -(0.5 * x**2)
        pdf_sn = always * math.exp(expo)
        return pdf_sn

    @staticmethod
    def stan_nd_vec(x: np.ndarray) -> np.ndarray:
        """
        stan_nd_vec (standard normal distribution) is designed to accept x as a NUMPY
        ARRAY that has been established with a numpy command like np.linspace(-3,3,61).
        Mu is zero and sigma is one. This returns another numpy array of the pdf.
        Note the difference between this and stan_norm_dist. Note that we must use
        np.exp (returns array) rather than math.exp (returns scalar).
        """
        always = 1 / math.sqrt(2 * math.pi)
        length = x.size
        pdf_sn_vec = np.zeros(length)
        pdf_sn_vec = always * np.exp(-(0.5 * x**2))
        return pdf_sn_vec

    @staticmethod
    def stan_norm_cdf(low_lim: float, point: float) -> tuple:
        """
        stan_norm_cdf integrates a standard normal vector using a lambda function and
        scipy's integration function (which can only take a function as an input).
        Because you can't integrate from minus infinity, use a low_limit of -3.5 or
        similar if you are integrating from minus infinity. You are integrating to
        the point, which will effectively be a value between -3.5 and 3.5. The output
        is usually thought of as a probability. Note the use of lambda and its use of
        z.
        """
        def snd_function(z):
            return Utils.stan_norm_dist(z)
        return scipy.integrate.quad(snd_function, low_lim, point)

    @staticmethod
    def tdecay(
            stock: float,
            strike: float,
            daysigma: float,
            oprice: float,
            days,
            call: bool) -> float:
        """
        TDECAY adds an extension to the otranche calculator (Taboga model)
        to calculate one-day time decay.
        """
        days -= 1.0
        dursigma = Utils.durration_volatility(daysigma, days)
        oprice1d = Utils.otranche(stock, strike, dursigma, call)
        timedecay = oprice - oprice1d
        return timedecay

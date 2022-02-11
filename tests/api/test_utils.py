import unittest
import pytest
from fintech.api.utils import Utils
from fintech.api.types.option_stats import OptionBSM, OptionPrice, OptionIDV
"""
import numpy as np
results = []

results.append(Utils.call_option_price(101.24, 105.0, 0.0160, 8, 0.020))
results.append(Utils.delta_call(101.24, 105.0, 0.0160, 0.0, 0.020, 8))
results.append(Utils.delta_put(101.24, 98.0, 0.0160, 0.00021, 0.020, 8))
results.append(Utils.bsm_idv_call(101.24, 105.0, 0.565, 8, 0.01))
results.append(Utils.bsm_idv_put(101.24, 98.0, 0.610, 8, 0.01))
results.append(Utils.peg(2.40, 2.50, 0.5))
results.append(Utils.put_option_price(101.24, 98.0, 0.0160, 8, 0.020))
results.append(Utils.oidv(101.24, 105.0, 0.555, 8, True))
# Note: if oidv works, otranche works.
results.append(Utils.tdecay(101.24, 105, 0.016, 0.555, 8, True))
# If 1, should be 0.24, if 0, should be slightly less than 0.40
results.append(Utils.stan_norm_dist(1.0))
results.append(Utils.ito_half_var(0.30, 1))
x = np.linspace(-4.0, 0.0, 31)
results.append(Utils.stan_nd_vec(x))
results.append(Utils.norm_dist(1.00, 1.0, 0.5))
results.append(Utils.norm_dist_vec(x, 0.0, 1.0))
results.append(Utils.stan_norm_cdf(-3.5, 0.8))
results.append(Utils.norm_dist_cdf(2.0, 1.0, -1.5, 2.8))
results.append(Utils.durration_volatility(0.20, 9))
results.append(Utils.itm_option('CALL', 101.24, 105.0, 0.0160, 0.000, 8))
results.append(
    Utils.itm_option_rfr(
        'CALL',
        101.24,
        105.0,
        0.0160,
        0.00,
        0.020,
        8))
results.append(Utils.itm_option('PUT', 100.0, 105.0, 0.025, 0.000794, 16))
results.append(
    Utils.itm_option_rfr(
        'PUT',
        101.24,
        98.0,
        0.0160,
        0.00021,
        0.020,
        8))

pprint(results)
print("  Completed, no obvious bugs.")
[(0.5645167696167235,
  0.21961689707933502,
  0.04525483399593905,
  0.2064666564851645),
 0.21961689707933507,
 0.21529662982989245,
 (0.5641959774931493,
  0.2189778030455098,
  0.04540260826466358,
  0.2058081208560285,
  0.01605224609375),
 (0.6099021262867019,
  0.2264361314071588,
  0.04497102453591202,
  0.24019851874642345,
  0.015899658203125),
 2.45,
 (0.6133920010267992,
  0.22631015161634183,
  0.04525483399593905,
  0.24015659544816592),
 (0.015956878662109375, 0.045132868434193854),
 0.0818037222196441,
 0.24197072451914337,
 0.045,
 array([1.33830226e-04, 2.26108838e-04, 3.75284024e-04, 6.11901930e-04,
       9.80127961e-04, 1.54227900e-03, 2.38408820e-03, 3.62043623e-03,
       5.40105618e-03, 7.91545158e-03, 1.13959860e-02, 1.61178581e-02,
       2.23945303e-02, 3.05672097e-02, 4.09872560e-02, 5.39909665e-02,
       6.98670761e-02, 8.88184611e-02, 1.10920835e-01, 1.36082482e-01,
       1.64010075e-01, 1.94186055e-01, 2.25862827e-01, 2.58077826e-01,
       2.89691553e-01, 3.19448006e-01, 3.46053893e-01, 3.68270140e-01,
       3.85006875e-01, 3.95411841e-01, 3.98942280e-01]),
 0.7978845608028654,
 array([1.33830226e-04, 2.26108838e-04, 3.75284024e-04, 6.11901930e-04,
       9.80127961e-04, 1.54227900e-03, 2.38408820e-03, 3.62043623e-03,
       5.40105618e-03, 7.91545158e-03, 1.13959860e-02, 1.61178581e-02,
       2.23945303e-02, 3.05672097e-02, 4.09872560e-02, 5.39909665e-02,
       6.98670761e-02, 8.88184611e-02, 1.10920835e-01, 1.36082482e-01,
       1.64010075e-01, 1.94186055e-01, 2.25862827e-01, 2.58077826e-01,
       2.89691553e-01, 3.19448006e-01, 3.46053893e-01, 3.68270140e-01,
       3.85006875e-01, 3.95411841e-01, 3.98942280e-01]),
 (0.7879119723375678, 5.350700536852496e-11),
 (0.7879119723375678, 5.350700536852496e-11),
 0.6000000000000001,
 0.20371380930908667,
 0.2064666564851645,
 0.6594130047450031,
 0.22876444339064916]
  Completed, no obvious bugs.
"""

class TestUtils(unittest.TestCase):
    
    def test_call_option_price(self):
        stock = 101.24
        strike = 105.0
        day_vol = 0.0160
        days = 8
        rfir = 0.02
        expected = OptionPrice(0.5645167696167235, 0.21961689707933502, 0.04525483399593905, 0.2064666564851645)
        result: OptionPrice = Utils.call_option_price(stock, strike, day_vol, days, rfir)
        assert expected == result
    
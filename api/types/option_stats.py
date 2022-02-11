from typing import NamedTuple


class OptionPrice(NamedTuple):
    price: float
    delta: float
    durr_vol: float
    prob_itm: float


class OptionBSM(OptionPrice):
    idv: float


class OptionIDV(NamedTuple):
    day_sigma: float
    dur_sigma: float

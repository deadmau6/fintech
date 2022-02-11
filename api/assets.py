import datetime as dt
from .config import CONFIG


class AssetTypes:
    VALID_TYPES = {"FINANCIAL", "PHYSICAL", "DERIVITIVE"}
    FINANCIAL = 'FINANCIAL'
    PHYSICAL = 'PHYSICAL'
    DERIVITIVE = 'DERIVITIVE'

    @classmethod
    def get_asset_type(cls, typ):
        return getattr(cls, typ.upper())


class BaseAsset:
    def __init__(self, asset_type):
        self._asset_type = AssetTypes().get_asset_type(asset_type)

    @property
    def asset_type(self):
        return self._asset_type


class Financial(BaseAsset):
    _TYPES = {'STOCK', 'BOND', 'CASH'}

    def __init__(self, asset_subtype):
        super().__init__('FINANCIAL')
        asset_subtype = asset_subtype.upper()
        if asset_subtype not in self._TYPES:
            raise Exception(
                f"Asset Sub Type: {asset_subtype} not found in {self._TYPES}")
        self._asset_subtype = asset_subtype

    @property
    def asset_subtype(self):
        return self._asset_subtype


class Derivative(BaseAsset):
    _TYPES = {'FUTURES', 'OPTIONS'}

    def __init__(self, asset_subtype):
        super().__init__('DERIVITIVE')
        asset_subtype = asset_subtype.upper()
        if asset_subtype not in self._TYPES:
            raise Exception(
                f"Asset Sub Type: {asset_subtype} not found in {self._TYPES}")
        self._asset_subtype = asset_subtype

    @property
    def asset_subtype(self):
        return self._asset_subtype


class Physical(BaseAsset):
    _TYPES = {'COMODITIES'}

    def __init__(self, asset_subtype):
        super().__init__('PHYSICAL')
        asset_subtype = asset_subtype.upper()
        if asset_subtype not in self._TYPES:
            raise Exception(
                f"Asset Sub Type: {asset_subtype} not found in {self._TYPES}")
        self._asset_subtype = asset_subtype

    @property
    def asset_subtype(self):
        return self._asset_subtype


class StockAsset(Financial):

    def __init__(self, symbol=None, price=None, shares=0):
        super().__init__('STOCK')
        self._set_symbol(symbol)
        self.price = price
        self.shares = shares
        self._price_profit = {}

    @property
    def symbol(self):
        return self._symbol

    def _set_symbol(self, tick):
        if isinstance(tick, str):
            self._symbol = tick.upper()
        else:
            # No Error - useful for batching.
            raise Exception(f"Stock Symbol is required, recieved:({tick}).")

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        if isinstance(price, int) and price > 0:
            self._price = float(price)
        elif isinstance(price, float) and price > 0:
            self._price = price
        else:
            try:
                self._price = float(price)
            except Exception:
                raise Exception(f"Price ({price}) must be type float")

    @property
    def shares(self):
        return self._shares

    @shares.setter
    def shares(self, shares):
        if shares is None:
            self._shares = 1
        elif isinstance(shares, int) and shares > 0:
            self._shares = shares
        else:
            shares = int(shares)
            self._shares = 1 if shares <= 0 else shares

    @property
    def cost(self):
        return self.price * self.shares

    @property
    def break_even_price(self):
        return self.price

    @property
    def profit_loss(self):
        return self._profit_loss

    @property
    def name(self):
        return f"{self.symbol} {self.shares} SHARES"

    @property
    def id_string(self):
        """Format: STOCK|symbol|price|shares"""
        return f"STOCK|{self.symbol}|{self.price}|{self.shares}"

    @property
    def asset_id_string(self):
        return f"{self.asset_type}|{self.asset_subtype}|{self.id_string}"

    def profit(self, price):
        return (price - self.price) * self.shares

    def get_profit(self, price):
        if price in self._price_profit:
            return self._price_profit[price]
        return self.profit(price)

    def add_profit(self, price):
        if price not in self._price_profit:
            self._price_profit[price] = self.profit(price)
        return self._price_profit[price]

    def ordered_prices(self):
        return sorted(list(self._price_profit.keys()))

    def ordered_prices_profits(self):
        prices = self.ordered_prices()
        profits = [self._price_profit[price] for price in prices]
        return prices, profits

    def set_profit_loss(self, price_range=None):
        if price_range is None:
            _, self._profit_loss = self.ordered_prices_profits()
        else:
            for price in price_range:
                self.add_profit(price)
            _, self._profit_loss = self.ordered_prices_profits()


class OptionsContract(Derivative):
    # TODO: expand on the fees
    _fees = CONFIG.OPTIONS_FEES
    _writing_fees = _fees  # CONFIG.WRITING_OPTIONS_FEES or _fees
    _buying_fees = _fees  # CONFIG.BUYING_OPTIONS_FEES or _fees

    def __init__(self, symbol=None, typ=None, subtype=None, strike=None, price=None, expiration=None, amount=0):
        super().__init__('OPTIONS')
        # Read ONLY
        self._set_symbol(symbol)
        self._set_typ(typ)
        self._set_subtype(subtype)
        # Required
        self.strike = strike
        self.price = price
        # Optional
        self.expiration = expiration
        self.amount = amount
        # Empty values
        self._price_profit = {}
        # Set the profit function
        if self.typ == 'CALL':
            if self.subtype == 'BUY':
                self._profit = self._buy_call_profit
            else:
                self._profit = self._sell_call_profit
        else:
            if self.subtype == 'BUY':
                self._profit = self._buy_put_profit
            else:
                self._profit = self._sell_put_profit

    @property
    def fees(self):
        return self._fees

    @property
    def symbol(self):
        return self._symbol

    def _set_symbol(self, tick):
        if isinstance(tick, str):
            self._symbol = tick.upper()
        else:
            # No Error - useful for batching.
            self._symbol = None

    @property
    def typ(self):
        return self._typ

    def _set_typ(self, t):
        if not isinstance(t, str):
            raise Exception(f"Typ({t}) is the wrong type, must be a string")
        t = t.upper()
        if t not in ('CALL', 'PUT'):
            raise Exception(f"Typ({t}) must be either CALL or PUT")
        self._typ = t

    @property
    def subtype(self):
        return self._subtype

    def _set_subtype(self, t):
        if not isinstance(t, str):
            raise Exception(
                f"Subtype ({t}) is the wrong type, must be a string")
        t = t.upper()
        if t not in ('BUY', 'SELL'):
            raise Exception(f"Subtype ({t}) must be either BUY or SELL")
        self._subtype = t

    @property
    def strike(self):
        return self._strike

    @strike.setter
    def strike(self, price):
        if isinstance(price, int) and price > 0:
            self._strike = float(price)
        elif isinstance(price, float) and price > 0:
            self._strike = price
        else:
            try:
                self._strike = float(price)
            except Exception:
                raise Exception(f"Strike({price}) must be type float")

    @property
    def expiration(self):
        return self._expiration

    @expiration.setter
    def expiration(self, expires):
        if isinstance(expires, dt.datetime):
            self._expiration = expires.date()
        elif isinstance(expires, dt.date):
            self._expiration = expires
        elif expires:
            try:
                self._expiration = dt.datetime.strptime(
                    expires, "%Y-%m-%d").date()
            except ValueError:
                raise Exception(
                    f"Expiration date: {expires}, does not follow the format: YYYY-MM-DD.")
        else:
            self._expiration = dt.datetime.today().date()

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        if isinstance(price, int) and price > 0:
            self._price = float(price)
        elif isinstance(price, float) and price > 0:
            self._price = price
        else:
            try:
                self._price = float(price)
            except Exception:
                raise Exception(f"Price({price}) must be type float")

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        if amount is None:
            self._amount = 1
        elif isinstance(amount, int) and amount > 0:
            self._amount = amount
        else:
            amount = int(amount)
            self._amount = 1 if amount <= 0 else amount

    @property
    def shares_amount(self):
        return self.amount * 100

    @property
    def premium(self):
        return self.price * self.amount * 100

    @property
    def cost(self):
        if self.subtype == 'BUY':
            return self.premium + self._buying_fees
        return self._writing_fees

    @property
    def break_even_price(self):
        if self.typ == 'CALL':
            return (self.strike + self.price) + (self.fees / 100)
        return (self.strike - self.price) - (self.fees / 100)

    @property
    def profit_loss(self):
        return self._profit_loss

    @property
    def name(self):
        return f"{self.symbol} {self.subtype} {self.typ}"

    @property
    def id_string(self):
        """Format: OPTIONS|symbol|typ|subtype|strike|price|amount|expiration"""
        return f"OPTIONS|{self.symbol}|{self.typ}|{self.subtype}|{self.strike}|{self.price}|{self.amount}|{self.expiration}"

    @property
    def asset_id_string(self):
        return f"{self.asset_type}|{self.asset_subtype}|{self.id_string}"

    def itm(self, current_price):
        # In The Money
        if self.typ == 'CALL':
            return self.strike <= current_price
        else:
            return self.strike >= current_price

    def intrinsic_value(self, current_price):
        if self.typ == 'CALL':
            if self.strike >= current_price:
                return 0
            return current_price - self.strike
        else:
            if self.strike <= current_price:
                return 0
            return self.strike - current_price

    def _buy_call_profit(self, price):
        if price > self.strike:
            return ((price - self.strike) * self.shares_amount) - self.cost
        return -self.cost

    def _sell_call_profit(self, price):
        if price > self.strike:
            return self.premium - self.cost - \
                ((price - self.strike) * self.shares_amount)
        return self.premium - self.cost

    def _buy_put_profit(self, price):
        if price < self.strike:
            return ((self.strike - price) * self.shares_amount) - self.cost
        return -self.cost

    def _sell_put_profit(self, price):
        if price < self.strike:
            return self.premium - self.cost - \
                ((self.strike - price) * self.shares_amount)
        return self.premium - self.cost

    def profit(self, price):
        # the correct profit function should be established on init to reduce checks when this runs iteratively
        # see the init function to see what self._profit should be.
        return self._profit(price)

    def get_profit(self, price):
        if price in self._price_profit:
            return self._price_profit[price]
        return self.profit(price)

    def add_profit(self, price):
        if price not in self._price_profit:
            self._price_profit[price] = self.profit(price)
        return self._price_profit[price]

    def ordered_prices(self):
        return sorted(list(self._price_profit.keys()))

    def ordered_prices_profits(self):
        prices = self.ordered_prices()
        profits = [self._price_profit[price] for price in prices]
        return prices, profits

    def set_profit_loss(self, price_range=None):
        if price_range is None:
            _, self._profit_loss = self.ordered_prices_profits()
        else:
            for price in price_range:
                self.add_profit(price)
            _, self._profit_loss = self.ordered_prices_profits()


class Asset:

    @staticmethod
    def to_stock_id(symbol=None, price=None, shares=0):
        return f"STOCK|{symbol}|{price}|{shares}"

    @staticmethod
    def to_options_id(
            symbol=None,
            typ=None,
            subtype=None,
            strike=None,
            price=None,
            amount=0,
            expiration=None):
        return f"OPTIONS|{symbol}|{typ}|{subtype}|{strike}|{price}|{amount}|{expiration}"

    @staticmethod
    def from_string(id_string):
        """Format: <asset_type>|<asset_subtype>|<**kwargs>

        Stock Format: STOCK|<symbol>|<price>|<shares>
        OptionsContract: OPTIONS|<symbol>|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        """
        args = [x.strip() for x in id_string.split('|')]
        if args[0] in AssetTypes.VALID_TYPES:
            asset_type = args.pop(0)
            asset_subtype = args.pop(0)
        typ = args.pop(0)
        if typ == 'STOCK':
            # Format: STOCK|symbol|price|shares
            kwargs = {k: v for k, v in zip(
                ['symbol', 'price', 'shares'], args)}
            return StockAsset(**kwargs)
        elif typ == 'OPTIONS':
            # Format: OPTIONS|symbol|typ|subtype|strike|price|amount|expiration
            kwargs = {k: v for k, v in zip(
                ['symbol', 'typ', 'subtype', 'strike', 'price', 'amount', 'expiration'], args)}
            return OptionsContract(**kwargs)
        else:
            raise Exception(
                f"Not found, string not in the correct format: {id_string}.")

    @staticmethod
    def load(asset_type, *args, **kwargs):
        asset_type = asset_type.upper()
        if asset_type == 'STOCK':
            if len(args) == 3:
                kwargs = {k: v for k, v in zip(
                    ['symbol', 'price', 'shares'], args)}
            return StockAsset(**kwargs)
        elif asset_type == 'OPTIONS':
            if len(args) >= 4:
                kwargs = {k: v for k, v in zip(
                    ['symbol', 'typ', 'subtype', 'amount', 'strike', 'price', 'expiration'], args)}
            return OptionsContract(**kwargs)
        else:
            raise Exception(f"Not found asset_type: {asset_type}.")

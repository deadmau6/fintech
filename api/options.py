import datetime as dt
from collections import deque
"""
contractSymbol lastTradeDate  strike  lastPrice bid  ask  change  percentChange  volume  openInterest  impliedVolatility  inTheMoney contractSize currency
"""


class Receipt:

    def __init__(
            self,
            owner,
            purchase_price,
            amount,
            contract_name,
            event_price):
        # owner must be unique id
        self.owner = owner
        self.amount = amount
        self.purchase_price = purchase_price
        self.contract_name = contract_name
        self.event_price = event_price
        self._id = f"{self.name}:{dt.datetime.now()}"

    @staticmethod
    def format_name(owner, contract_name):
        return f"{owner}:{contract_name}"

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, name):
        if name is None:
            raise Exception(f"Owner Name is required cannot be None - {name}")
        self._contract_name = str(name)

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        if isinstance(amount, int) and amount > 0:
            self._amount = amount
        else:
            amount = int(amount)
            self._amount = 1 if amount <= 0 else amount

    @property
    def purchase_price(self):
        return self._purchase_price

    @purchase_price.setter
    def purchase_price(self, price):
        if isinstance(price, int) and price > 0:
            self._purchase_price = float(price)
        elif isinstance(price, float) and price > 0:
            self._purchase_price = price
        else:
            raise Exception(f"Purchase Price({price}) must be type float")

    @property
    def contract_name(self):
        return self._contract_name

    @contract_name.setter
    def contract_name(self, name):
        if name is None:
            raise Exception(
                f"Contract Name is required cannot be None - {name}")
        self._contract_name = str(name)

    @property
    def event_price(self):
        return self._event_price

    @event_price.setter
    def event_price(self, price):
        if isinstance(price, int) and price > 0:
            self._even_price = float(price)
        elif isinstance(price, float) and price > 0:
            self._even_price = price
        else:
            raise Exception(f"Even Price({price}) must be type float")

    @property
    def cost(self):
        return self.purchase_price * self.amount

    @property
    def name(self):
        return Receipt.format_name(self.owner, self.contract_name)

    def to_dict(self):
        return {
            '_id': self._id,
            'cost': self.cost,
            'name': self.name,
            'owner': self.owner,
            'amount': self.amount,
            'even_price': self.even_price,
            'contract_name': self.contract_name,
            'purchase_price': self.purchase_price
        }

    def __str__(self):
        return str(self.to_dict())


class Contract:

    def __init__(
            self,
            typ=None,
            strike=None,
            expiration=None,
            price=None,
            open_interest=None,
            name=None):
        self.typ = typ
        self.strike = strike
        self.expiration = expiration
        self.price = price
        # NUmber of Contracst available for purchase
        self.open_interest = open_interest
        self.name = name

    @staticmethod
    def format_name(typ, strike, expiration_date):
        return f'{typ}:{strike}:{expiration_date}'

    @property
    def typ(self):
        return self._typ

    @typ.setter
    def typ(self, t):
        if not isinstance(t, str):
            raise Exception(f"Typ({t}) is the wrong type, must be a string")
        t = t.upper()
        if t not in ('CALL', 'PUT'):
            raise Exception(f"Typ({t}) must be either CALL or PUT")
        self._typ = t

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
            raise Exception(f"Strike({price}) must be type float")

    @property
    def expiration(self):
        return self._expiration

    @expiration.setter
    def expiration(self, expires):
        if isinstance(expires, dt.datetime):
            self._expiration = expires
        elif isinstance(expires, dt.date):
            self._expiration = dt.datetime.fromisoformat(expires.isoformat())
        elif expires:
            try:
                self._expiration = dt.datetime.strptime(expires, "%Y-%m-%d")
            except ValueError:
                raise Exception(
                    f"Expiration date: {expires}, does not follow the format: YYYY-MM-DD.")
        else:
            self._expiration = dt.datetime.today()

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
            raise Exception(f"Price({price}) must be type float")

    @property
    def open_interest(self):
        return self._open_interest

    @open_interest.setter
    def open_interest(self, op_int):
        if isinstance(op_int, int) and op_int > 0:
            self._open_interest = op_int
        elif isinstance(op_int, float) and op_int > 0:
            self._open_interest = int(op_int)
        else:
            self._open_interest = 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name is not None and isinstance(name, str):
            self._name = name
        else:
            self._name = Contract.format_name(
                self.typ, self.strike, self.expiration.date())

    @property
    def even_price(self):
        if self.typ == 'CALL':
            return self.strike + self.price
        return self.strike - self.price

    def to_dict(self):
        return {
            'typ': self.typ,
            'name': self.name,
            'price': self.price,
            'strike': self.strike,
            'even_price': self.even_price,
            'expiration': self.expiration,
            'open_interest': self.open_interest
        }

    def __str__(self):
        return str(self.to_dict())

    def purchase(self, num, owner):
        if num <= 0:
            raise Exception(f"Must purchase at least 1 contract.")
        if num > self.open_interest:
            raise Exception(
                f"Not enough contracts to fill order try {self.open_interest} or less.")
        self.open_interest = self.open_interest - num
        return Receipt(owner, self.price, num, self.name, self.even_price)

    def intrinsic_value(self, current_price):
        if self.typ == 'CALL':
            if self.strike >= current_price:
                return 0
            return current_price - self.strike
        else:
            if self.strike <= current_price:
                return 0
            return self.strike - current_price

    def premium(self, current_price=None, amount=1, purchase_price=None):
        price = purchase_price if purchase_price is not None else self.price
        prem = price - \
            self.intrinsic_value(current_price) if current_price else price
        return prem * amount * 100.0

    def exercise(self, current_price, receipt):
        if self.typ == 'CALL':
            # buyer purchases the stock at the strike price
            buyer_purchase = (receipt.amount * 100) * self.strike
            # current stock value
            value = (receipt.amount * 100) * current_price
            return (value - buyer_purchase) - receipt.cost
        else:
            # buyer purchases the stock at the current price
            buyer_purchase = (receipt.amount * 100) * current_price
            # writer purchases the stock at the strike price
            writer_purchase = (receipt.amount * 100) * self.strike
            return (writer_purchase - buyer_purchase) - receipt.cost

    def itm(self, current_price):
        # In The Money
        if self.typ == 'CALL':
            return self.strike <= current_price
        else:
            return self.strike >= current_price


class Options:

    def __init__(self, contracts=[]):
        self.contracts = {}
        self.purchased = {}
        self.receipts = {}
        self.calls = deque([])
        self.puts = deque([])
        if len(contracts) > 0:
            for c in contracts:
                self.add_contract(c)

    @staticmethod
    def get_even_price(typ, strike, price):
        contract = Contract(typ=typ, strike=strike, price=price)
        return contract.even_price

    @staticmethod
    def format_contract_name(typ, strike, expiration_date):
        return Contract.format_name(typ.upper(), strike, expiration_date)

    def _clean_receipts(self, receipt_ids):
        response = []
        for rid in receipt_ids:
            response.append(self.receipts.pop(rid))
        return response

    def _remove_receipt(self, receipt_id):
        receipt_id = receipt._id if isinstance(
            receipt_id, Receipt) else receipt_id
        receipt = self.receipts.pop(receipt_id)
        self.purchased[receipt.contract_name].remove(receipt._id)

    def add_contract(self, contract_args):
        contract = Contract(**contract_args)
        if contract.name not in self.contracts:
            #
            if contract.typ == 'CALL':
                self.calls.append(contract.name)
            else:
                self.puts.append(contract.name)
            #
            self.contracts[contract.name] = contract
        else:
            print(f"Contract {contract.name} already exists.")

    def remove_contract(self, contract):
        name = contract.name if isinstance(contract, Contract) else contract
        receipt_ids = []
        if name not in self.contracts:
            raise Exception(f"{name} not found")
        else:
            contract = self.contracts.pop(name)
            #
            if name in self.purchased:
                receipt_ids = self.purchased.pop(name)
            #
            if contract.typ == 'CALL':
                self.calls.remove(contract.name)
            else:
                self.puts.remove(contract.name)
        contract_receipts = self._clean_receipts(receipt_ids)
        return contract, contract_receipts

    def get_contract(self, typ=None, strike=None, expiration=None, name=None):
        if name:
            return self.contracts.get(name)
        else:
            name = Contract.format_contract_name(typ, strike, expiration)
            return self.contracts.get(name)

    def exercise(self, closing_price, receipt):
        receipt = receipt if isinstance(
            receipt, Receipt) else self.receipt.get(receipt)
        contract = self.contracts.get(receipt.contract_name)
        value = contract.exercise(closing_price, receipt)
        self._remove_receipt(receipt)
        return value

    def premium(
            self,
            current_price,
            amount=1,
            purchase_price=None,
            receipt=None,
            contract=None,
            **kwargs):
        if receipt:
            receipt = receipt if isinstance(
                receipt, Receipt) else self.receipt.get(receipt)
            contract = self.contracts.get(receipt.contract_name)
            return contract.premium(
                current_price,
                receipt.amount,
                receipt.purchase_price)
        elif contract:
            contract = contract if isinstance(
                contract, Contract) else self.contracts.get(contract)
            return contract.premium(current_price, amount, purchase_price)
        else:
            contract = self.get_contract(**kwargs)
            return contract.premium(current_price, amount, purchase_price)

    def buy_contract(self, owner, contract, amount=1):
        #
        name = contract.name if isinstance(contract, Contract) else contract
        if name not in self.contracts:
            raise Exception(f"{name} not found")
        #
        contract = self.contracts.get(name)
        receipt = contract.purchase(amount, owner)
        #
        if receipt._id in self.receipts:
            raise Exception(f" Receipt already exists! {receipt}")
        #
        self.receipt[receipt._id] = receipt
        #
        if contract.name in self.purchased:
            self.purchased[contract.name].append(receipt._id)
        else:
            self.purchased[contract.name] = deque([receipt._id])
        return receipt

    def expire_contract(
            self,
            closing_price,
            typ=None,
            strike=None,
            expiration=None,
            name=None,
            contract=None):
        # if contract is None:
        #     contract = self.get_contract(typ, strike, expiration, name)
        # contract, rece
        pass

    def load_itm_contracts(self, current_price):
        for k, contract in self.contracts.items():
            if contract.itm(current_price):
                yield k, contract

from .assets import Asset, StockAsset, OptionsContract


class Positions:

    @staticmethod
    def buy_shares(*args):
        """Expected String Format: 'symbol|price|shares(optional)'.
        Case insensitive and whitespace is ignored.
        Examples: 'MSFT|230.0' or ' run | 50.0 | 100'
        """
        if len(args) == 1:
            args = [x.trim() for x in args[0].split('|')]
        kwargs = {k: v for k, v in zip(['symbol', 'price', 'shares'], args)}
        return StockAsset(*args, **kwargs)

    @staticmethod
    def buy_call(*args):
        """Expected String Format: 'symbol|strike|price|amount(optional)|expiration(optional)'.
        Case insensitive and whitespace is ignored.
        Examples: 'MSFT|245|1.90' or ' run | 45.0 | 1.00| 2 | 2021-09-01'
        """
        if len(args) == 1:
            args = [x.trim() for x in args[0].split('|')]
        kwargs = {k: v for k, v in zip(
            ['symbol', 'strike', 'price', 'amount', 'expiration'], args)}
        kwargs['subtype'] = 'BUY'
        kwargs['typ'] = 'CALL'
        return OptionsContract(**kwargs)

    @staticmethod
    def buy_put(*args):
        """Expected String Format: 'symbol|strike|price|amount(optional)|expiration(optional)'.
        Case insensitive and whitespace is ignored.
        Examples: 'MSFT|245|1.90' or ' run | 45.0 | 1.00| 2 | 2021-09-01'
        """
        kwargs = {}
        if len(args) == 1:
            args = [x.trim() for x in args[0].split('|')]
        kwargs = {k: v for k, v in zip(
            ['symbol', 'strike', 'price', 'amount', 'expiration'], args)}
        kwargs['subtype'] = 'BUY'
        kwargs['typ'] = 'PUT'
        return OptionsContract(**kwargs)

    @staticmethod
    def sell_call(*args):
        """Expected String Format: 'symbol|strike|price|amount(optional)|expiration(optional)'.
        Case insensitive and whitespace is ignored.
        Examples: 'MSFT|245|1.90' or ' run | 45.0 | 1.00| 2 | 2021-09-01'
        """
        kwargs = {}
        if len(args) == 1:
            args = [x.trim() for x in args[0].split('|')]
        kwargs = {k: v for k, v in zip(
            ['symbol', 'strike', 'price', 'amount', 'expiration'], args)}
        kwargs['subtype'] = 'SELL'
        kwargs['typ'] = 'CALL'
        return OptionsContract(**kwargs)

    @staticmethod
    def sell_put(*args):
        """Expected String Format: 'symbol|strike|price|amount(optional)|expiration(optional)'.
        Case insensitive and whitespace is ignored.
        Examples: 'MSFT|245|1.90' or ' run | 45.0 | 1.00| 2 | 2021-09-01'
        """
        kwargs = {}
        if len(args) == 1:
            args = [x.trim() for x in args[0].split('|')]
        kwargs = {k: v for k, v in zip(
            ['symbol', 'strike', 'price', 'amount', 'expiration'], args)}
        kwargs['subtype'] = 'SELL'
        kwargs['typ'] = 'PUT'
        return OptionsContract(**kwargs)


class OptionStrategies:

    @staticmethod
    def covered_call(
            stock,
            current_price,
            strike,
            call_price,
            amount=1,
            shares=0,
            price_range=[]):
        # get shares
        shares = shares if shares > 0 else amount * 100
        # get price range
        if len(price_range) == 0:
            price_range = [i for i in range(int(current_price + 1) * 2)]
        # STOCK|<symbol>|<price>|<shares>
        own_stock = StockAsset(stock, current_price, shares)
        own_stock.set_profit_loss(price_range)
        # OPTIONS|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        # sell_call = Asset.from_string(f'OPTIONS|{stock}|CALL|SELL|{amount}|{strike}|{call_price}')
        sell_call = Positions.sell_call(stock, strike, call_price, amount)
        sell_call.set_profit_loss(price_range)
        #
        profit_loss = [
            a + b for a,
            b in zip(
                own_stock.profit_loss,
                sell_call.profit_loss)]
        #
        # this is left of the strike price
        break_even_prices = [own_stock.price -
                             (sell_call.premium / own_stock.shares)]
        A = sell_call.amount * 100
        if own_stock.shares < A:
            # this is the right side of the strike
            right_of_strike = ((own_stock.price * own_stock.shares) - (A *
                               sell_call.strike) - sell_call.premium) / (own_stock.shares - A)
            break_even_prices.append(right_of_strike)
        return {
            'stock': own_stock,
            'sell_call': sell_call,
            'profit_loss': profit_loss,
            'price_range': price_range,
            'break_even_prices': tuple(break_even_prices),
        }

    @staticmethod
    def married_put(
            stock,
            current_price,
            strike,
            put_price,
            amount=1,
            shares=0,
            price_range=[]):
        # get shares
        shares = shares if shares > 0 else amount * 100
        # get price range
        if len(price_range) == 0:
            price_range = [i for i in range(int(current_price + 1) * 2)]
        # STOCK|<symbol>|<price>|<shares>
        own_stock = StockAsset(stock, current_price, shares)
        own_stock.set_profit_loss(price_range)
        # OPTIONS|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        # buy_put = Asset.from_string(f'OPTIONS|{stock}|PUT|BUY|{amount}|{strike}|{put_price}')
        buy_put = Positions.buy_put(stock, strike, put_price, amount)
        buy_put.set_profit_loss(price_range)
        #
        profit_loss = [
            a + b for a,
            b in zip(
                own_stock.profit_loss,
                buy_put.profit_loss)]
        #
        # this is right of the strike price
        break_even_prices = [own_stock.price +
                             ((buy_put.premium + buy_put.fees) / own_stock.shares)]
        A = buy_put.amount * 100
        if own_stock.shares < A:
            # this is the left side of the strike
            left_of_strike = (buy_put.fees + buy_put.premium + (own_stock.price *
                              own_stock.shares) - (A * buy_put.strike)) / (own_stock.shares - A)
            break_even_prices.append(left_of_strike)
        return {
            'stock': own_stock,
            'buy_put': buy_put,
            'profit_loss': profit_loss,
            'price_range': price_range,
            'break_even_prices': tuple(break_even_prices)
        }

    @staticmethod
    def bull_call_spread(
            stock,
            current_price,
            buy_call_price,
            sell_call_price,
            low_strike=None,
            high_strike=None,
            buy_amount=1,
            sell_amount=1,
            spread_percent=0.1,
            price_range=[]):
        # get shares
        low_strike = low_strike if low_strike else current_price - \
            (current_price * spread_percent)
        high_strike = high_strike if high_strike else current_price + \
            (current_price * spread_percent)
        # get price range
        if len(price_range) == 0:
            price_range = [i for i in range(int(current_price + 1) * 2)]
        # OPTIONS|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        # sell_call = Asset.from_string(f'OPTIONS|{stock}|CALL|SELL|{sell_amount}|{high_strike}|{sell_call_price}')
        sell_call = Positions.sell_call(
            stock, high_strike, sell_call_price, sell_amount)
        sell_call.set_profit_loss(price_range)
        #
        # buy_call = Asset.from_string(f'OPTIONS|{stock}|CALL|BUY|{buy_amount}|{low_strike}|{buy_call_price}')
        buy_call = Positions.buy_call(
            stock, low_strike, buy_call_price, buy_amount)
        buy_call.set_profit_loss(price_range)
        #
        profit_loss = [
            a + b for a,
            b in zip(
                buy_call.profit_loss,
                sell_call.profit_loss)]
        #
        A = buy_call.amount * 100
        break_even_price = (
            (A * buy_call.strike) + buy_call.premium + buy_call.fees - sell_call.premium) / A
        return {
            'buy_call': buy_call,
            'sell_call': sell_call,
            'profit_loss': profit_loss,
            'price_range': price_range,
            'break_even_prices': (break_even_price)
        }

    @staticmethod
    def bear_put_spread(
            stock,
            current_price,
            buy_put_price,
            sell_put_price,
            low_strike=None,
            high_strike=None,
            buy_amount=1,
            sell_amount=1,
            spread_percent=0.1,
            price_range=[]):
        # get shares
        low_strike = low_strike if low_strike else current_price - \
            (current_price * spread_percent)
        high_strike = high_strike if high_strike else current_price + \
            (current_price * spread_percent)
        # get price range
        if len(price_range) == 0:
            price_range = [i for i in range(int(current_price + 1) * 2)]
        # OPTIONS|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        # sell_put = Asset.from_string(f'OPTIONS|{stock}|PUT|SELL|{sell_amount}|{low_strike}|{sell_put_price}')
        sell_put = Positions.sell_put(
            stock, low_strike, sell_put_price, sell_amount)
        sell_put.set_profit_loss(price_range)
        #
        # buy_put = Asset.from_string(f'OPTIONS|{stock}|PUT|BUY|{buy_amount}|{high_strike}|{buy_put_price}')
        buy_put = Positions.buy_put(
            stock, high_strike, buy_put_price, buy_amount)
        buy_put.set_profit_loss(price_range)
        #
        profit_loss = [
            a + b for a,
            b in zip(
                buy_put.profit_loss,
                sell_put.profit_loss)]
        #
        A = buy_put.amount * 100
        break_even_price = (
            sell_put.premium + (A * buy_put.strike) - buy_put.premium - buy_put.fees) / A
        return {
            'buy_put': buy_put,
            'sell_put': sell_put,
            'profit_loss': profit_loss,
            'price_range': price_range,
            'break_even_prices': (break_even_price)
        }

    @staticmethod
    def protective_collar(
            stock,
            current_price,
            buy_put_price,
            sell_call_price,
            put_otm_strike=None,
            call_otm_strike=None,
            buy_amount=1,
            sell_amount=1,
            spread_percent=0.1,
            shares=0,
            price_range=[]):
        put_otm_strike = put_otm_strike if put_otm_strike else current_price - \
            (current_price * spread_percent)
        call_otm_strike = call_otm_strike if call_otm_strike else current_price + \
            (current_price * spread_percent)
        # get shares
        shares = shares if shares > 0 else sell_amount * 100
        # get price range
        if len(price_range) == 0:
            price_range = [i for i in range(int(current_price + 1) * 2)]
        # STOCK|<symbol>|<price>|<shares>
        own_stock = StockAsset(stock, current_price, shares)
        own_stock.set_profit_loss(price_range)
        # OPTIONS|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        # sell_call = Asset.from_string(f'OPTIONS|{stock}|CALL|SELL|{sell_amount}|{call_otm_strike}|{sell_call_price}')
        sell_call = Positions.sell_call(
            stock, call_otm_strike, sell_call_price, sell_amount)
        sell_call.set_profit_loss(price_range)
        #
        # buy_put = Asset.from_string(f'OPTIONS|{stock}|PUT|BUY|{buy_amount}|{put_otm_strike}|{buy_put_price}')
        buy_put = Positions.buy_put(
            stock, put_otm_strike, buy_put_price, buy_amount)
        buy_put.set_profit_loss(price_range)
        #
        profit_loss = [
            a + b + c for a,
            b,
            c in zip(
                own_stock.profit_loss,
                buy_put.profit_loss,
                sell_call.profit_loss)]
        #
        # middle range
        break_even_prices = [
            ((buy_put.premium +
              buy_put.fees -
              sell_call.premium) /
             own_stock.shares) +
            own_stock.price]
        # Left side
        A = buy_put.amount * 100
        if own_stock.shares < A:
            left = (buy_put.premium + buy_put.fees - sell_call.premium - (A * buy_put.strike) +
                    (own_stock.price * own_stock.shares)) / (own_stock.shares - A)
            break_even_prices.append(left)
        # right side
        A = sell_call.amount * 100
        if own_stock.shares < A:
            right = (buy_put.premium + buy_put.fees - sell_call.premium - (A * sell_call.strike) +
                     (own_stock.price * own_stock.shares)) / (own_stock.shares - A)
            break_even_prices.append(right)
        return {
            'stock': own_stock,
            'sell_call': sell_call,
            'buy_put': buy_put,
            'profit_loss': profit_loss,
            'price_range': price_range,
            'break_even_prices': tuple(break_even_prices)
        }

    @staticmethod
    def long_straddle(
            stock,
            current_price,
            strike,
            put_price,
            call_price,
            put_amount=1,
            call_amount=1,
            price_range=[]):
        # get price range
        if len(price_range) == 0:
            price_range = [i for i in range(int(current_price + 1) * 2)]
        # OPTIONS|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        # buy_put = Asset.from_string(f'OPTIONS|{stock}|PUT|BUY|{put_amount}|{strike}|{put_price}')
        buy_put = Positions.buy_put(stock, strike, put_price, put_amount)
        buy_put.set_profit_loss(price_range)
        #
        # buy_call = Asset.from_string(f'OPTIONS|{stock}|CALL|BUY|{call_amount}|{strike}|{call_price}')
        buy_call = Positions.buy_call(stock, strike, call_price, call_amount)
        buy_call.set_profit_loss(price_range)
        #
        profit_loss = [
            a + b for a,
            b in zip(
                buy_call.profit_loss,
                buy_put.profit_loss)]
        #
        A = buy_put.amount * 100
        # left of strike
        left_break_even = buy_put.strike - \
            ((buy_put.premium + buy_put.fees + buy_call.premium + buy_call.fees) / A)
        B = buy_call.amount * 100
        # right of strike
        right_break_even = ((buy_put.premium + buy_put.fees +
                            buy_call.premium + buy_call.fees) / B) + buy_call.strike
        return {
            'buy_call': buy_call,
            'buy_put': buy_put,
            'profit_loss': profit_loss,
            'price_range': price_range,
            'break_even_prices': (left_break_even, right_break_even)
        }

    @staticmethod
    def long_strangle(
            stock,
            current_price,
            put_price,
            call_price,
            put_otm_strike=None,
            call_otm_strike=None,
            put_amount=1,
            call_amount=1,
            spread_percent=0.1,
            price_range=[]):
        #
        put_otm_strike = put_otm_strike if put_otm_strike else current_price - \
            (current_price * spread_percent)
        call_otm_strike = call_otm_strike if call_otm_strike else current_price + \
            (current_price * spread_percent)
        # get price range
        if len(price_range) == 0:
            price_range = [i for i in range(int(current_price + 1) * 2)]
        # OPTIONS|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        # buy_put = Asset.from_string(f'OPTIONS|{stock}|PUT|BUY|{put_amount}|{put_otm_strike}|{put_price}')
        buy_put = Positions.buy_put(
            stock, put_otm_strike, put_price, put_amount)
        buy_put.set_profit_loss(price_range)
        #
        # buy_call = Asset.from_string(f'OPTIONS|{stock}|CALL|BUY|{call_amount}|{call_otm_strike}|{call_price}')
        buy_call = Positions.buy_call(
            stock, call_otm_strike, call_price, call_amount)
        buy_call.set_profit_loss(price_range)
        #
        profit_loss = [
            a + b for a,
            b in zip(
                buy_call.profit_loss,
                buy_put.profit_loss)]
        #
        adjusted_fees = (buy_put.fees / 100)
        call_break_even = buy_call.break_even_price + buy_put.price + adjusted_fees
        put_break_even = buy_put.break_even_price - buy_call.price - adjusted_fees
        return {
            'buy_call': buy_call,
            'buy_put': buy_put,
            'profit_loss': profit_loss,
            'price_range': price_range,
            'break_even_prices': (call_break_even, put_break_even)
        }

    @staticmethod
    def call_butterfly_spread(
            stock,
            current_price,
            otm_price,
            itm_price,
            atm_price,
            itm_strike=None,
            otm_strike=None,
            itm_amount=1,
            otm_amount=1,
            atm_amount=2,
            spread_percent=0.1,
            price_range=[]):
        #
        itm_strike = itm_strike if itm_strike else current_price - \
            (current_price * spread_percent)
        otm_strike = otm_strike if otm_strike else current_price + \
            (current_price * spread_percent)
        # get price range
        if len(price_range) == 0:
            price_range = [i for i in range(int(current_price + 1) * 2)]
        # OPTIONS|<typ>|<subtype>|<amount>|<strike>|<price>|<expiration>
        # buy_itm = Asset.from_string(f'OPTIONS|{stock}|CALL|BUY|{itm_amount}|{itm_strike}|{itm_price}')
        buy_itm = Positions.buy_call(stock, itm_strike, itm_price, itm_amount)
        buy_itm.set_profit_loss(price_range)
        #
        # buy_otm = Asset.from_string(f'OPTIONS|{stock}|CALL|BUY|{otm_amount}|{otm_strike}|{otm_price}')
        buy_otm = Positions.buy_call(stock, otm_strike, otm_price, otm_amount)
        buy_otm.set_profit_loss(price_range)
        #
        # sell_atm = Asset.from_string(f'OPTIONS|{stock}|CALL|SELL|{atm_amount}|{current_price}|{atm_price}')
        sell_atm = Positions.sell_call(
            stock, current_price, atm_price, atm_amount)
        sell_atm.set_profit_loss(price_range)
        #
        profit_loss = [
            a + b + c for a,
            b,
            c in zip(
                buy_itm.profit_loss,
                sell_atm.profit_loss,
                buy_otm.profit_loss)]
        #
        # left of current price
        A = buy_itm.amount * 100
        break_even_prices = [buy_itm.strike +
                             ((buy_itm.contract_cost +
                               buy_otm.contract_cost -
                               sell_atm.premium) /
                              A)]
        # right of current price
        A_atm = sell_atm.amount * 100
        A_itm = buy_itm.amount * 100
        if A_atm != A_itm:
            B = A_itm - A_atm
            right = ((A_itm * buy_itm.strike) - sell_atm.premium - (A_atm *
                     sell_atm.strike) + buy_itm.contract_cost + buy_otm.contract_cost) / B
            break_even_prices.append(right)
        return {
            'buy_itm': buy_itm,
            'buy_otm': buy_otm,
            'sell_atm': sell_atm,
            'profit_loss': profit_loss,
            'price_range': price_range,
            'break_even_prices': tuple(break_even_prices)
        }

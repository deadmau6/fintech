import numpy as np
import pandas as pd


class Indicators:

    available_indicators = [
        'obv',
        'ema',
        'sma',
        'rsi',
        'dema',
        'macd',
        'macd_crossover',
        'bollinger_bands',
        'money_flow_index',
        'dual_moving_average',
        'three_moving_average'
    ]

    @staticmethod
    def obv(df, column='Close', period=20):
        """On Balance Volume (OBV) Strategy:
         * Buy: when the OBV goes above the OBV_EMA
         * Sell: when the OBV_EMA goes above the OBV.
        """
        if column == 'Volume':
            raise Exception(f"Column {column} cannot be 'Volume'.")
        #
        obv = [0]
        for i in range(1, len(df[column])):
            if df[column][i] > df[column][i - 1]:
                obv.append(obv[-1] + df['Volume'][i])
            elif df[column][i] < df[column][i - 1]:
                obv.append(obv[-1] - df['Volume'][i])
            else:
                obv.append(obv[-1])
        #
        obv_df = pd.DataFrame({'OBV': obv})
        obv_ema = obv_df['OBV'].ewm(span=period, adjust=True).mean()
        #
        earnings = []
        sig_buy = []
        sig_sell = []
        flag = -1
        for i in range(len(df)):
            if obv[i] > obv_ema[i] and flag != 1:
                # Buy
                earnings.append((df.index[i], -df[column][i]))
                sig_buy.append(df[column][i])
                sig_sell.append(None)
                flag = 1
            elif obv[i] < obv_ema[i] and flag != 0:
                # Sell
                earnings.append((df.index[i], df[column][i]))
                sig_sell.append(df[column][i])
                sig_buy.append(None)
                flag = 0
            else:
                sig_buy.append(None)
                sig_sell.append(None)
        return {
            'Buy': sig_buy,
            'Sell': sig_sell,
            'OBV': obv,
            'OBV_EMA': obv_ema,
            'Earnings': earnings,
            'Period': period}

    @staticmethod
    def sma(df, column='Close', period=30):
        return df[column].rolling(window=period).mean()

    @staticmethod
    def ema(df, column='Close', period=20, adjust=False):
        return df[column].ewm(span=period, adjust=adjust).mean()

    @staticmethod
    def rsi(df, column='Close', period=14, over=80, under=20):
        """RSI - Relative Strength Index
         * if a stock is over sold then it is a good time to buy
         * if a stock is over bought then it is a good time to sell
         * common period is 14 days
         * values from 0-100 with high levels:[90,80,70] and lows levels:[10,20,30].
         * the higher the high level the stonger the price momentum shift of being Over Bought.
         * the lower the low - the stronger the stock is Over Sold.
        """
        delta = df[column].diff(1)
        delta.dropna(inplace=True)
        #
        up = delta.copy()
        down = delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        #
        avg_gain = up.rolling(window=period).mean()
        avg_loss = abs(down.rolling(window=period).mean())
        #
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        nrsi = rsi.to_numpy()
        # New Frame in correct Period.
        ndf = df[period:]
        earnings = []
        buy_signal = []
        sell_signal = []
        for i in range(len(nrsi)):
            if nrsi[i] == np.nan:
                buy_signal.append(None)
                sell_signal.append(None)
            elif nrsi[i] > over:
                # Sell
                earnings.append((df.index[i], df[column][i]))
                buy_signal.append(None)
                sell_signal.append(ndf[column][i])
            elif nrsi[i] < under:
                # Buy
                earnings.append((df.index[i], -df[column][i]))
                buy_signal.append(ndf[column][i])
                sell_signal.append(None)
            else:
                buy_signal.append(None)
                sell_signal.append(None)
        return {
            'Buy': buy_signal,
            'Sell': sell_signal,
            'Earnings': earnings,
            'RSI': rsi,
            'Period': period}

    @staticmethod
    def money_flow_index(df, column='Close', period=14, high=80, low=20):
        """MFI - Money Flow Index (an Oscilator)
         * AKA Volume wieghted RSI
         * Buy = if MFI < 20, which means stock is over sold
         * Sell = if MFI > 80, which means stock is over bought
         * More info: https://www.investopedia.com/terms/m/mfi.asp
        """
        typical_price = (df['Close'] + df['High'] + df['Low']) / 3
        money_flow = typical_price * df['Volume']
        #
        pos_flow = []
        neg_flow = []
        for i in range(1, len(typical_price)):
            # Increasing
            if typical_price[i] > typical_price[i - 1]:
                pos_flow.append(money_flow[i - 1])
                neg_flow.append(0)
            # Decreasing
            elif typical_price[i] < typical_price[i - 1]:
                neg_flow.append(money_flow[i - 1])
                pos_flow.append(0)
            # Even
            else:
                pos_flow.append(0)
                neg_flow.append(0)
        # Positive Money Flow Rate
        pos_mf = []
        for i in range(period - 1, len(pos_flow)):
            pos_mf.append(sum(pos_flow[i + 1 - period: i + 1]))
        # Negative Money Flow Rate
        neg_mf = []
        for i in range(period - 1, len(neg_flow)):
            neg_mf.append(sum(neg_flow[i + 1 - period: i + 1]))
        # Money Flow Index
        mfi = 100 * (np.array(pos_mf) / (np.array(pos_mf) + np.array(neg_mf)))
        # New Frame in correct Period.
        ndf = df[period:]
        earnings = []
        buy_signal = []
        sell_signal = []
        for i in range(len(mfi)):
            if mfi[i] > high:
                # Sell
                earnings.append((df.index[i], df[column][i]))
                buy_signal.append(None)
                sell_signal.append(ndf[column][i])
            elif mfi[i] < low:
                # Buy
                earnings.append((df.index[i], -df[column][i]))
                buy_signal.append(ndf[column][i])
                sell_signal.append(None)
            else:
                buy_signal.append(None)
                sell_signal.append(None)
        return {
            'Buy': buy_signal,
            'Sell': sell_signal,
            'MFI': mfi,
            'High': high,
            'Low': low,
            'Period': period,
            'Earnings': earnings}

    @staticmethod
    def macd(
            df,
            column='Close',
            short_period=12,
            long_period=26,
            signal_period=9):
        """Strategy - Moving Average Convergence Divergence
         * MACD follows momentum between two moving averages (Short term EMA - Long term EMA).
         * Signal line is 9 period exponentially smooth average of the MACD line.
        """
        # Short term exponential moving average
        short_ema = Indicators.ema(df, column=column, period=short_period)
        # Long term exponential moving average
        long_ema = Indicators.ema(df, column=column, period=long_period)
        # MACD and Signal exponential moving average
        macd = short_ema - long_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        return {
            'MACD': macd,
            'Signal': signal,
            'Short_Period': short_period,
            'Long_Period': long_period,
            'Signal_Period': signal_period}

    @staticmethod
    def macd_crossover(
            df,
            column='Close',
            short_period=12,
            long_period=26,
            signal_period=9):
        """Strategy - Moving Average Convergence Divergence Crossover
         * MACD follows momentum between two moving averages (Short term EMA - Long term EMA).
         * Signal line is 9 period exponentially smooth average of the MACD line.
         * short term period = 12 & long term period = 26
         * Buy = when the MACD is above the signal line
         * Sell = when the MACD is below the signal line
        """
        res = Indicators.macd(
            df,
            column=column,
            short_period=short_period,
            long_period=long_period,
            signal_period=signal_period)
        #
        macd = res['MACD']
        signal = res['Signal']
        earnings = []
        sig_buy = []
        sig_sell = []
        flag = -1
        for i in range(len(df)):
            if macd[i] > signal[i]:
                # Buy
                sig_sell.append(None)
                if flag != 1:
                    earnings.append((df.index[i], -df[column][i]))
                    current = df[column][i]
                    sig_buy.append(df[column][i])
                    flag = 1
                else:
                    sig_buy.append(None)
            elif macd[i] < signal[i]:
                # Sell
                sig_buy.append(None)
                if flag != 0:
                    earnings.append((df.index[i], df[column][i]))
                    sig_sell.append(df[column][i])
                    flag = 0
                else:
                    sig_sell.append(None)
            else:
                sig_buy.append(None)
                sig_sell.append(None)
        return {
            'Buy': sig_buy,
            'Sell': sig_sell,
            'MACD': macd,
            'Signal': signal,
            'Earnings': earnings,
            'Short_Period': short_period,
            'Long_Period': long_period,
            'Signal_Period': signal_period}

    @staticmethod
    def bollinger_bands(df, column='Close', period=20):
        """Bollinger Bands"""
        sma = Indicators.sma(df, column=column, period=period)
        std = df[column].rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        earnings = []
        sig_buy = []
        sig_sell = []
        for i in range(len(df[column])):
            if df[column][i] > upper_band[i]:
                # Sell
                earnings.append((df.index[i], df[column][i]))
                sig_sell.append(df[column][i])
                sig_buy.append(None)
            elif df[column][i] < lower_band[i]:
                # Buy
                earnings.append((df.index[i], -df[column][i]))
                sig_buy.append(df[column][i])
                sig_sell.append(None)
            else:
                sig_buy.append(None)
                sig_sell.append(None)
        target = {'buy': round(
            lower_band[-1] - 0.05, 2), 'sell': round(upper_band[-1] + 0.05, 2)}
        return {
            'Buy': sig_buy,
            'Sell': sig_sell,
            'UpperBand': upper_band,
            'LowerBand': lower_band,
            'SMA': sma, 'STD': std,
            'Period': period,
            'Earnings': earnings,
            'Target': target}

    @staticmethod
    def dual_moving_average(
            df,
            column='Close',
            short_period=30,
            long_period=100):
        """Strategy - Dual Moving Average Cross Over
         * Buy = when short term avg crosses above long term avg
         * Sell = when long term avg crosses above short term avg
        """
        # Short term average
        short_avg = Indicators.sma(df, column=column, period=short_period)
        # Long term average
        long_avg = Indicators.sma(df, column=column, period=long_period)
        #
        earnings = []
        sig_buy = []
        sig_sell = []
        flag = -1
        for i in range(len(df)):
            if short_avg[i] > long_avg[i]:
                if flag != 1:
                    # Buy
                    earnings.append((df.index[i], -df[column][i]))
                    sig_buy.append(df[column][i])
                    sig_sell.append(None)
                    flag = 1
                else:
                    sig_buy.append(None)
                    sig_sell.append(None)
            elif short_avg[i] < long_avg[i]:
                if flag != 0:
                    # Sell
                    earnings.append((df.index[i], df[column][i]))
                    sig_buy.append(None)
                    sig_sell.append(df[column][i])
                    flag = 0
                else:
                    sig_buy.append(None)
                    sig_sell.append(None)
            else:
                sig_buy.append(None)
                sig_sell.append(None)
        return {
            'Buy': sig_buy,
            'Sell': sig_sell,
            'Short': short_avg,
            'Long': long_avg,
            'Earnings': earnings,
            'Short_Period': short_period,
            'Long_Period': long_period}

    @staticmethod
    def _dema(data, time_period, column):
        # calc the expot moving average for some time_period
        ema = Indicators.ema(data, column=column, period=time_period)
        dema = 2 * ema - ema.ewm(span=time_period, adjust=False).mean()
        return dema

    @staticmethod
    def dema(df, column='Close', short_period=20, long_period=50):
        """DEMA: Double Exponential Moving Average
         * BUY: when short term dema crosses ABOVE long term dema
         * SELL: when short term dema crosses BELOW long term dema
        """
        DEMA_short = Indicators._dema(df, short_period, column)
        DEMA_long = Indicators._dema(df, long_period, column)
        sig_buy = []
        sig_sell = []
        earnings = []
        flag = False
        for i in range(len(df)):
            if DEMA_short[i] > DEMA_long[i] and not flag:
                # Buy
                earnings.append((df.index[i], -df[column][i]))
                sig_buy.append(df[column][i])
                sig_sell.append(None)
                flag = True
            elif DEMA_short[i] < DEMA_long[i] and flag:
                # Sell
                earnings.append((df.index[i], df[column][i]))
                sig_buy.append(None)
                sig_sell.append(df[column][i])
                flag = False
            else:
                sig_buy.append(None)
                sig_sell.append(None)
        return {
            'Buy': sig_buy,
            'Sell': sig_sell,
            'Short': DEMA_short,
            'Long': DEMA_long,
            'Earnings': earnings,
            'Short_Period': short_period,
            'Long_Period': long_period}

    @staticmethod
    def three_moving_average(
            df,
            column='Close',
            short_period=5,
            medium_period=21,
            long_period=63):
        """Strategy - Three Moving Average Cross Over
         * Short, medium, and long averages with 2 buy/sell signals.
         * Buy_A = when medium avg crosses above long avg AND short avg crosses above medium avg.
         * Buy_B = when medium avg crosses below long avg AND short avg crosses below medium avg.
         * Sell_A = when short avg crosses below medium avg.
         * Sell_B = when short avg crosses above medium avg.
        """
        # Short Exponential Moving Average
        short_ema = Indicators.ema(df, column=column, period=short_period)
        # Medium Exponential Moving Average
        medium_ema = Indicators.ema(df, column=column, period=medium_period)
        # Long Exponential Moving Average
        long_ema = Indicators.ema(df, column=column, period=long_period)
        # Create buy and sell signals
        sig_buy = []
        sig_sell = []
        flag_A = False
        flag_B = False
        earnings = []
        for i in range(len(df)):
            if medium_ema[i] < long_ema[i] and short_ema[i] < medium_ema[i] and not flag_A and not flag_B:
                # BUY_B
                earnings.append((df.index[i], -df[column][i]))
                sig_buy.append(df[column][i])
                sig_sell.append(None)
                flag_B = True
            elif flag_B and short_ema[i] > medium_ema[i]:
                # SELL_B
                earnings.append((df.index[i], df[column][i]))
                sig_sell.append(df[column][i])
                sig_buy.append(None)
                flag_B = False
            elif medium_ema[i] > long_ema[i] and short_ema[i] > medium_ema[i] and not flag_A and not flag_B:
                # BUY_A
                earnings.append((df.index[i], -df[column][i]))
                sig_buy.append(df[column][i])
                sig_sell.append(None)
                flag_A = True
            elif flag_A and short_ema[i] < medium_ema[i]:
                # SELL_A
                earnings.append((df.index[i], df[column][i]))
                sig_sell.append(df[column][i])
                sig_buy.append(None)
                flag_A = False
            else:
                sig_buy.append(None)
                sig_sell.append(None)
        return {
            'Buy': sig_buy,
            'Sell': sig_sell,
            'Short': short_ema,
            'Medium': medium_ema,
            'Long': long_ema,
            'Earnings': earnings,
            'Short_Period': short_period,
            'Medium_Period': medium_period,
            'Long_Period': long_period}

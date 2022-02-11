import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score


class Predictors:
    available = [
        'svr',
        'linear_regression',
        'decision_tree']

    @staticmethod
    def decision_tree(df, column='Adj Close', future_days=25, max_depth=None):
        from sklearn.tree import DecisionTreeRegressor
        #
        predictions = df[column].shift(-1)
        # print(predictions)
        end = len(df) - future_days
        X = np.array([[x] for x in df[column][:end]])
        Y = np.array(predictions[:end])
        x_train, x_test, y_train, y_test = train_test_split(
            X, Y, test_size=0.25)
        #
        tree = DecisionTreeRegressor(max_depth=max_depth).fit(x_train, y_train)
        #
        x_future = X[len(X) - future_days:]
        x_future = np.append(x_future, [[x] for x in df[column][end:]], axis=0)
        tree_pred = tree.predict(x_future)
        return {'DecisionTree': tree_pred, 'future_days': future_days}

    @staticmethod
    def linear_regression(df, column='Adj Close', future_days=25):
        from sklearn.linear_model import LinearRegression
        #
        predictions = df[column].shift(-future_days)
        #
        end = len(df) - future_days
        X = np.array([[x] for x in df[column][:end]])
        Y = np.array(predictions[:end])
        x_train, x_test, y_train, y_test = train_test_split(
            X, Y, test_size=0.25)  # , shuffle=False)
        #
        lr = LinearRegression().fit(x_train, y_train)
        #
        x_future = X[len(X) - future_days:]
        x_future = np.append(x_future, [[x] for x in df[column][end:]], axis=0)
        lr_pred = lr.predict(x_future)
        # print(lr_pred)
        # print()
        # print(x_future)
        # print()
        return {'LinearRegression': lr_pred, 'future_days': future_days}

    @staticmethod
    def svr(
            df,
            column='Adj Close',
            prev_days=15,
            buff_days=3,
            lookahead_days=3):
        from sklearn.svm import SVR
        #
        actual_prices = df.tail(buff_days)
        ndf = df.head(len(df) - buff_days)
        #
        total_days = len(ndf.index)
        prev_days = total_days if prev_days >= total_days else prev_days
        days = [[i] for i in range(prev_days)]
        #
        start = 0 if prev_days >= total_days else total_days - prev_days
        df_prices = ndf.loc[:, column]
        prices = [float(price) for price in df_prices[start:]]
        # Linear
        lin_svr = SVR(kernel='linear', C=1000.0)
        lin_svr.fit(days, prices)
        # Polynomial
        poly_svr = SVR(kernel='poly', C=1000.0, degree=2)
        poly_svr.fit(days, prices)
        # RBF
        rbf_svr = SVR(kernel='rbf', C=1000.0, gamma=0.15)
        rbf_svr.fit(days, prices)
        #
        for i in range(buff_days):
            days.append([prev_days + i])
            prices.append(float(actual_prices[column][i]))
        for i in range(lookahead_days):
            days.append([prev_days + buff_days + i])
            prices.append(None)
        linear = lin_svr.predict(days)
        polynomial = poly_svr.predict(days)
        rbf = rbf_svr.predict(days)
        return {
            'Linear': linear,
            'Polynomial': polynomial,
            'RBF': rbf,
            'Prices': prices,
            'TrainDays': prev_days,
            'TestDays': buff_days,
            'LookaheadDays': lookahead_days}

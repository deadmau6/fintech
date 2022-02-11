import pandas as pd
import numpy as np
#
from sklearn.linear_model import Ridge
from sklearn.svm import LinearSVR, NuSVR
from sklearn.pipeline import make_pipeline
from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.ensemble import AdaBoostRegressor, RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import max_error, mean_squared_error, mean_absolute_error, explained_variance_score, r2_score
from collections import deque
#
from .schemas import regression_args
from .decorators import validate_kwargs


class RegressionModels:

    def __init__(
            self,
            predictions=5,
            lookback=2,
            feature_column='Close',
            continuous=False):
        self.predictions = predictions
        self.lookback = lookback
        self.continuous = continuous
        self.feature_column = feature_column

    def run_featured(self, method, data, kwargs):
        # lookback = 2 bc can't really predict any further foward for a single column while
        # requiring n features for each prediction.
        guesses = data.loc[:, self.feature_column]
        guesses = guesses.iloc[1:]
        data = data.iloc[:len(data) - 1]
        #
        X_past = data.iloc[:len(data) - self.predictions]
        X_future = data.iloc[len(data) - self.predictions - 1:]
        #
        Y_past = guesses.iloc[:len(data) - self.predictions]
        Y_future = guesses.iloc[len(data) - self.predictions:]
        #
        Y = Y_past.to_numpy()
        X = X_past.to_numpy()
        #
        regr = self.get_method(method, X, Y, kwargs)
        #
        x = X_future.to_numpy()
        preds = regr.predict(x)
        final = preds[-1]
        preds = preds[:-1]
        #
        y = Y_future.to_numpy()
        me = max_error(y, preds)
        mse = mean_squared_error(y, preds)
        mae = mean_absolute_error(y, preds)
        evs = explained_variance_score(y, preds)
        rs = r2_score(y, preds)
        return {
            'past': Y_past,
            'future': Y_future,
            'predictions': preds,
            'final': final,
            'max_error': me,
            'mean_squared_error': mse,
            'mean_absolute_error': mae,
            'variance_score': evs,
            'r2_score': rs
        }

    def run_single(self, method, data, kwargs):
        past = data.iloc[: len(data) - self.predictions]
        future = data.iloc[len(data) - self.predictions - self.lookback:]
        #
        Y = past.iloc[self.lookback + 1:].to_numpy()
        xvs = [past.shift(-i).iloc[:len(past) - self.lookback - 1]
               for i in range(1, self.lookback + 1)]
        X = pd.concat(xvs, axis=1)
        X = X.to_numpy()
        #
        regr = self.get_method(method, X, Y, kwargs)
        #
        xv_futures = [future.shift(-i).iloc[:len(future) - self.lookback]
                      for i in range(self.lookback)]
        X_future = pd.concat(xv_futures, axis=1)
        X_future = X_future.to_numpy()
        #
        if self.continuous:
            val = deque(X_future[0])
            preds = []
            for i in range(len(X_future)):
                pred = regr.predict([val])
                val.popleft()
                val.append(pred[0])
                preds.append(pred[0])
            prev = preds[len(preds) - self.lookback:]
        else:
            preds = regr.predict(X_future)
            prev = future.iloc[len(future) - self.lookback:].to_numpy()
        #
        final = regr.predict([prev])[0]
        future = future.iloc[self.lookback:]
        n_future = future.to_numpy()
        #
        me = max_error(n_future, preds)
        mse = mean_squared_error(n_future, preds)
        mae = mean_absolute_error(n_future, preds)
        evs = explained_variance_score(n_future, preds)
        rs = r2_score(n_future, preds)
        return {
            'future': future,
            'past': past,
            'predictions': preds,
            'final': final,
            'max_error': me,
            'mean_squared_error': mse,
            'mean_absolute_error': mae,
            'variance_score': evs,
            'r2_score': rs
        }

    def get_method(self, method, X, Y, kwargs):
        method = method.lower()
        if method == 'linear_svm':
            return RegressionModels.linear_svm(X, Y, **kwargs)
        elif method == 'nu_svm':
            return RegressionModels.nu_svm(X, Y, **kwargs)
        elif method == 'adaboost':
            return RegressionModels.adaboost(X, Y, **kwargs)
        elif method == 'random_forrest':
            return RegressionModels.random_forrest(X, Y, **kwargs)
        elif method == 'gradient_boost':
            return RegressionModels.gradient_boost(X, Y, **kwargs)
        elif method == 'histogram_boost':
            return RegressionModels.histogram_boost(X, Y, **kwargs)
        return RegressionModels.ridge(X, Y, **kwargs)

    @staticmethod
    @validate_kwargs(regression_args.RIDGE)
    def ridge(X, Y, **kwargs):
        """
        Ridge(alpha=1.0, fit_intercept=True, normalize=False, copy_X=True, max_iter=None, tol=0.001, solver='auto', random_state=None)
        """
        rid = Ridge(**kwargs)
        rid.fit(X, Y)
        return rid

    @staticmethod
    @validate_kwargs(regression_args.LINEAR_SVM)
    def linear_svm(X, Y, **kwargs):
        """
        LinearSVR(epsilon=0.0, tol=0.0001, C=1.0, loss='epsilon_insensitive', fit_intercept=True, intercept_scaling=1.0, dual=True, verbose=0, random_state=None, max_iter=1000)
        """
        # LinearSVR are less sensitive to C when it becomes large, and prediction results stop improving after a certain threshold.
        # Meanwhile, larger C values will take more time to train, sometimes up to 10 times longer.
        # https://stackoverflow.com/questions/52670012/convergencewarning-liblinear-failed-to-converge-increase-the-number-of-iterati
        lsvr = make_pipeline(StandardScaler(), LinearSVR(**kwargs))
        lsvr.fit(X, Y)
        return lsvr

    @staticmethod
    @validate_kwargs(regression_args.NU_SVM)
    def nu_svm(X, Y, **kwargs):
        """
        NuSVR(nu=0.5, C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True, tol=0.001, cache_size=200, verbose=False, max_iter=-1)
        """
        knsvr = make_pipeline(StandardScaler(), NuSVR(**kwargs))
        knsvr.fit(X, Y)
        return knsvr

    @staticmethod
    @validate_kwargs(regression_args.ADABOOST)
    def adaboost(X, Y, **kwargs):
        """
        AdaBoostRegressor(n_estimators=50, learning_rate=1.0, loss='linear', random_state=None)
        """
        abe = AdaBoostRegressor(**kwargs)
        abe.fit(X, Y)
        return abe

    @staticmethod
    @validate_kwargs(regression_args.RANDOM_FORREST)
    def random_forrest(X, Y, **kwargs):
        """
        RandomForestRegressor(n_estimators=100, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=False, ccp_alpha=0.0, max_samples=None)
        """
        rf = RandomForestRegressor(**kwargs)
        rf.fit(X, Y)
        return rf

    @staticmethod
    @validate_kwargs(regression_args.GRADIENT_BOOST)
    def gradient_boost(X, Y, **kwargs):
        """
        GradientBoostingRegressor(loss='ls', learning_rate=0.1, n_estimators=100, subsample=1.0, criterion='friedman_mse', min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_depth=3, min_impurity_decrease=0.0, min_impurity_split=None, init=None, random_state=None, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False, validation_fraction=0.1, n_iter_no_change=None, tol=0.0001, ccp_alpha=0.0)
        """
        gb = GradientBoostingRegressor(**kwargs)
        gb.fit(X, Y)
        return gb

    @staticmethod
    @validate_kwargs(regression_args.HISTOGRAM_BOOST)
    def histogram_boost(X, Y, **kwargs):
        """
        HistGradientBoostingRegressor(loss='least_squares', learning_rate=0.1, max_iter=100, max_leaf_nodes=31, max_depth=None, min_samples_leaf=20, l2_regularization=0.0, max_bins=255, categorical_features=None, monotonic_cst=None, warm_start=False, early_stopping='auto', scoring='loss', validation_fraction=0.1, n_iter_no_change=10, tol=1e-07, verbose=0, random_state=None)
        """
        print(kwargs)
        hb = HistGradientBoostingRegressor(**kwargs)
        hb.fit(X, Y)
        return hb

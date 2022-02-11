def _to_bool(x): return x.lower() in ('1', 'true')


LINEAR_SVM = {
    'epsilon': {"type": "float", "coerce": float},
    'tol': {"type": "float", "coerce": float},
    'C': {"type": "float", "coerce": float},
    'loss': {"type": "string"},
    'fit_intercept': {"type": "boolean", "coerce": (str, _to_bool)},
    'intercept_scaling': {"type": "float", "coerce": float},
    'dual': {"type": "boolean", "coerce": (str, _to_bool)},
    'verbose': {"type": "integer", "coerce": int},
    'random_state': {"type": "integer", "coerce": int},
    'max_iter': {"type": "integer", "coerce": int}
    }

RIDGE = {
    'alpha': {"type": "float", "coerce": float},
    'fit_intercept': {"type": "boolean", "coerce": (str, _to_bool)},
    'normalize': {"type": "boolean", "coerce": (str, _to_bool)},
    'copy_X': {"type": "boolean", "coerce": (str, _to_bool)},
    'max_iter': {"type": "integer", "coerce": int},
    'tol': {"type": "float", "coerce": float},
    'solver': {"type": "string"},
    'random_state': {"type": "integer", "coerce": int}
    }

NU_SVM = {
    'nu': {"type": "float", "coerce": float},
    'C': {"type": "float", "coerce": float},
    'kernel': {"type": "string"},
    'degree': {"type": "integer", "coerce": int},
    'gamma': {"type": "string"},
    'coef0': {"type": "float", "coerce": float},
    'shrinking': {"type": "boolean", "coerce": (str, _to_bool)},
    'tol': {"type": "float", "coerce": float},
    'cache_size': {"type": "integer", "coerce": int},
    'verbose': {"type": "boolean", "coerce": (str, _to_bool)},
    'max_iter': {"type": "integer", "coerce": int}
    }

ADABOOST = {
    'n_estimators': {"type": "integer", "coerce": int},
    'learning_rate': {"type": "float", "coerce": float},
    'loss': {"type": "string"},
    'random_state': {"type": "integer", "coerce": int}
    }

RANDOM_FORREST = {
    'n_estimators': {"type": "integer", "coerce": int},
    'criterion': {"type": "string"},
    'max_depth': {"type": "integer", "coerce": int},
    'min_samples_split': {"type": "integer", "coerce": int},
    'min_samples_leaf': {"type": "integer", "coerce": int},
    'min_weight_fraction_leaf': {"type": "float", "coerce": float},
    'max_features': {"type": "string"},
    'max_leaf_nodes': {"type": "integer", "coerce": int},
    'min_impurity_decrease': {"type": "float", "coerce": float},
    'min_impurity_split': {"type": "float", "coerce": float},
    'bootstrap': {"type": "boolean", "coerce": (str, _to_bool)},
    'oob_score': {"type": "boolean", "coerce": (str, _to_bool)},
    'n_jobs': {"type": "integer", "coerce": int},
    'random_state': {"type": "integer", "coerce": int},
    'verbose': {"type": "integer", "coerce": int},
    'warm_start': {"type": "boolean", "coerce": (str, _to_bool)},
    'ccp_alpha': {"type": "float", "coerce": float},
    'max_samples': {"type": "float", "coerce": float}
    }

GRADIENT_BOOST = {
    'loss': {"type": "string"},
    'learning_rate': {"type": "float", "coerce": float},
    'subsample': {"type": "float", "coerce": float},
    'init': {"type": "string"},
    'alpha': {"type": "float", "coerce": float},
    'warm_start': {"type": "boolean", "coerce": (str, _to_bool)},
    'validation_fraction': {"type": "float", "coerce": float},
    'n_iter_no_change': {"type": "integer", "coerce": int},
    'tol': {"type": "float", "coerce": float},
    'n_estimators': {"type": "integer", "coerce": int},
    'criterion': {"type": "string"},
    'max_depth': {"type": "integer", "coerce": int},
    'min_samples_split': {"type": "integer", "coerce": int},
    'min_samples_leaf': {"type": "integer", "coerce": int},
    'min_weight_fraction_leaf': {"type": "float", "coerce": float},
    'max_features': {"type": "string"},
    'max_leaf_nodes': {"type": "integer", "coerce": int},
    'min_impurity_decrease': {"type": "float", "coerce": float},
    'min_impurity_split': {"type": "float", "coerce": float},
    'random_state': {"type": "integer", "coerce": int},
    'verbose': {"type": "integer", "coerce": int},
    'ccp_alpha': {"type": "float", "coerce": float}
    }

HISTOGRAM_BOOST = {
    'loss': {"type": "string"},
    'learning_rate': {"type": "float", "coerce": float},
    'max_iter': {"type": "integer", "coerce": int},
    'max_leaf_nodes': {"type": "integer", "coerce": int},
    'max_depth': {"type": "integer", "coerce": int},
    'min_samples_leaf': {"type": "integer", "coerce": int},
    'l2_regularization': {"type": "float", "coerce": float},
    'max_bins': {"type": "integer", "coerce": int},
    'monotonic_cst': {"type":'list', 'schema':{"type": "integer"}},
    'categorical_features': {"type":'list', 'schema':{"type": "integer"}},
    'warm_start': {"type": "boolean", "coerce": (str, _to_bool)},
    'early_stopping': {"type": "boolean", "coerce": (str, _to_bool)},
    'scoring': {"type": "string"},
    'validation_fraction': {"type": "float", "coerce": float},
    'n_iter_no_change': {"type": "integer", "coerce": int},
    'tol': {"type": "float", "coerce": float},
    'verbose': {"type": "integer", "coerce": int},
    'random_state': {"type": "integer", "coerce": int}
    }

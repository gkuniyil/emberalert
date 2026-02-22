import pytest
import numpy as np
import pandas as pd
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.xgboost_model import FireRiskXGBoost

@pytest.fixture
def sample_features():
    return pd.DataFrame({
        'temperature':  [38.5, 22.0, 45.0, 15.0, 30.0],
        'humidity':     [12.0, 65.0,  5.0, 80.0, 35.0],
        'wind_speed':   [25.0,  8.0, 40.0,  3.0, 15.0],
        'latitude':     [34.05, 37.77, 33.9, 40.1, 36.5],
        'longitude':    [-118.24, -122.4, -117.5, -105.0, -119.0],
    })

@pytest.fixture
def sample_labels():
    return np.array([0.85, 0.2, 0.95, 0.05, 0.5])

@pytest.fixture
def trained_model(sample_features, sample_labels):
    model = FireRiskXGBoost()
    model.train(sample_features, sample_labels)
    return model

class TestInitialization:
    def test_default_params_are_set(self):
        model = FireRiskXGBoost()
        assert model.params['max_depth'] == 6
        assert model.params['learning_rate'] == 0.1
        assert model.params['n_estimators'] == 100

    def test_custom_params_override_defaults(self):
        model = FireRiskXGBoost(params={'max_depth': 3})
        assert model.params['max_depth'] == 3
        assert model.params['n_estimators'] == 100

    def test_model_initializes_with_no_feature_names(self):
        model = FireRiskXGBoost()
        assert model.feature_names is None

class TestTraining:
    def test_train_returns_model(self, sample_features, sample_labels):
        model = FireRiskXGBoost()
        result = model.train(sample_features, sample_labels)
        assert result is not None

    def test_feature_names_saved_after_training(self, sample_features, sample_labels):
        model = FireRiskXGBoost()
        model.train(sample_features, sample_labels)
        assert model.feature_names == ['temperature', 'humidity', 'wind_speed', 'latitude', 'longitude']

    def test_train_with_validation_set(self, sample_features, sample_labels):
        model = FireRiskXGBoost()
        model.train(sample_features.iloc[:3], sample_labels[:3],
                    X_val=sample_features.iloc[3:], y_val=sample_labels[3:])
        assert model.feature_names is not None

class TestPrediction:
    def test_predictions_are_between_0_and_1(self, trained_model, sample_features):
        preds = trained_model.predict(sample_features)
        assert np.all(preds >= 0.0)
        assert np.all(preds <= 1.0)

    def test_prediction_shape_matches_input(self, trained_model, sample_features):
        preds = trained_model.predict(sample_features)
        assert preds.shape == (len(sample_features),)

    def test_high_risk_scores_higher_than_low_risk(self, trained_model):
        high_risk = pd.DataFrame({'temperature': [45.0], 'humidity': [5.0],
                                   'wind_speed': [40.0], 'latitude': [34.05], 'longitude': [-118.24]})
        low_risk  = pd.DataFrame({'temperature': [15.0], 'humidity': [80.0],
                                   'wind_speed': [3.0],  'latitude': [34.05], 'longitude': [-118.24]})
        assert trained_model.predict(high_risk)[0] > trained_model.predict(low_risk)[0]

    def test_prediction_returns_numpy_array(self, trained_model, sample_features):
        assert isinstance(trained_model.predict(sample_features), np.ndarray)

class TestFeatureImportance:
    def test_returns_dict(self, trained_model):
        assert isinstance(trained_model.get_feature_importance(), dict)

    def test_has_all_features(self, trained_model):
        keys = set(trained_model.get_feature_importance().keys())
        assert keys == {'temperature', 'humidity', 'wind_speed', 'latitude', 'longitude'}

class TestSaveLoad:
    def test_save_creates_file(self, trained_model):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'model.pkl')
            trained_model.save(path)
            assert os.path.exists(path)

    def test_load_restores_predictions(self, trained_model, sample_features):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'model.pkl')
            trained_model.save(path)
            loaded = FireRiskXGBoost.load(path)
            np.testing.assert_array_almost_equal(
                trained_model.predict(sample_features),
                loaded.predict(sample_features)
            )

    def test_load_restores_feature_names(self, trained_model):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'model.pkl')
            trained_model.save(path)
            loaded = FireRiskXGBoost.load(path)
            assert loaded.feature_names == trained_model.feature_names

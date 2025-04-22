from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import json
import requests
from werkzeug.middleware.proxy_fix import ProxyFix
import random
import logging
import xgboost as xgb

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Realtor API Config
REALTOR_API_KEY = "6b504def46msha6bf4ff53605f98p1c0c1djsn3fcd43362b33"
REALTOR_HOST = "realty-in-us.p.rapidapi.com"
HEADERS = {
    "X-RapidAPI-Key": REALTOR_API_KEY,
    "X-RapidAPI-Host": REALTOR_HOST,
    "Content-Type": "application/json"
}

# Load both models
def load_models():
    """Load both models"""
    models = {}
    
    # Load sale price model
    sale_model_path = 'ml_models/price-prediction-model/xgboost_final_model.json'
    try:
        # Create XGBoost Booster and load JSON model
        sale_model = xgb.Booster()
        sale_model.load_model(sale_model_path)
        models['sale'] = sale_model
        print(f"Sale price model loaded successfully from {sale_model_path}")
        print(f"Model type: {type(sale_model)}")
        print(f"Model features: {sale_model.feature_names}")
    except Exception as e:
        print(f"Error loading sale price model: {e}")
        models['sale'] = None
    
    # Load rental model
    rental_model_path = 'ml_models/rental_model.pkl'
    try:
        models['rental'] = joblib.load(rental_model_path)
        print(f"Rental model loaded successfully from {rental_model_path}")
        print(f"Model type: {type(models['rental'])}")
    except Exception as e:
        print(f"Error loading rental model: {e}")
        models['rental'] = None
    
    return models

MODELS = load_models()

def fetch_properties_from_api(location):
    """Fetch properties from Realtor API"""
    url = "https://realty-in-us.p.rapidapi.com/properties/v3/list"
    payload = {
        "limit": 15,
        "offset": 0,
        "status": ["for_sale"],
        "sort": {"direction": "desc", "field": "list_date"},
        "search_location": location
    }

    if location.isdigit() and len(location) == 5:
        payload["postal_code"] = location
    else:
        payload["city"] = location

    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", {}).get("home_search", {}).get("results", [])
        else:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Request Exception: {e}")
        return []

@app.route('/')
def home():
    """Simple endpoint to verify server is running"""
    return jsonify({
        'status': 'success',
        'message': 'Server is running',
        'models_loaded': {
            'sale': MODELS['sale'] is not None,
            'rental': MODELS['rental'] is not None
        }
    })

@app.route('/api/search', methods=['POST'])
def search_properties():
    """Search for properties in a location"""
    try:
        data = request.get_json()
        location = data.get("location", "").strip()
        
        if not location:
            return jsonify({"status": "error", "message": "Location is required."}), 400
            
        properties = fetch_properties_from_api(location)
        if not properties:
            return jsonify({"status": "error", "message": "No properties found."}), 404
            
        # Process and return properties with predictions
        results = []
        for prop in properties:
            try:
                # Get property details
                location_data = prop.get("location", {}).get("address", {})
                desc = prop.get("description", {})
                
                property_data = {
                    "address": location_data.get("line", "N/A"),
                    "city": location_data.get("city", "N/A"),
                    "state": location_data.get("state_code", "N/A"),
                    "beds": desc.get("beds", "N/A"),
                    "baths": desc.get("baths", "N/A"),
                    "sqft": desc.get("sqft", 1500),
                    "year_built": desc.get("year_built", 2005),
                    "property_type": desc.get("type", "SINGLE_FAMILY"),
                    "list_price": prop.get("list_price", 0),
                    "image_url": prop.get("photos", [{}])[0].get("href", "https://via.placeholder.com/400x300?text=No+Image"),
                    "latitude": prop.get("location", {}).get("coordinate", {}).get("lat"),
                    "longitude": prop.get("location", {}).get("coordinate", {}).get("lon")
                }
                
                # Get predictions
                predictions = get_predictions(property_data)
                property_data.update(predictions)
                
                results.append(property_data)
            except Exception as e:
                logger.error(f"Error processing property: {e}")
                continue
                
        return jsonify({"status": "success", "results": results})
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for making predictions"""
    try:
        # Get data from request
        data = request.get_json()
        print("Received data:", data)
        
        # Required fields
        required_fields = ['zipcode', 'bedrooms', 'propertyType']
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Prepare input data
        input_data = {
            'zipcode': data['zipcode'],
            'bedrooms': int(data['bedrooms']),
            'bathrooms': float(data.get('bathrooms', 1)),
            'propertyType': data['propertyType'],
            'livingArea': int(data.get('livingArea', 1000)),
            'lotArea': float(data.get('lotArea', 0.25)),
            'daysOnMarket': int(data.get('daysOnMarket', 0)),
            'yearBuilt': int(data.get('yearBuilt', 1980)),
            'hasGarage': int(data.get('hasGarage', 1)),
            'hasPool': int(data.get('hasPool', 0)),
            'hasFireplace': int(data.get('hasFireplace', 0)),
            'hasBasement': int(data.get('hasBasement', 1)),
            'hasCentralAir': int(data.get('hasCentralAir', 1)),
            'hasSecuritySystem': int(data.get('hasSecuritySystem', 0)),
            'hasSprinklerSystem': int(data.get('hasSprinklerSystem', 0)),
            'hasSolarPanels': int(data.get('hasSolarPanels', 0))
        }
        
        print("Input data for prediction:", input_data)
        
        # Initialize result dictionary
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        # Sale Price Prediction
        if MODELS['sale'] is not None:
            try:
                # Prepare features for XGBoost
                print("Preparing sale features...")
                sale_features = prepare_sale_features(input_data)
                print("Features prepared:", sale_features)
                
                # Make prediction using XGBoost Booster
                print("Making sale price prediction...")
                sale_prediction = MODELS['sale'].predict(sale_features)
                result['predictedSalePrice'] = round(float(sale_prediction[0]), 2)  # Get first prediction
                print(f"Raw sale prediction: {sale_prediction}")
                print(f"Final sale price prediction: {result['predictedSalePrice']}")
            except Exception as e:
                print(f"Detailed error in sale price prediction: {str(e)}")
                print("Using fallback prediction for sale price")
                result['predictedSalePrice'] = fallback_sale_prediction(input_data)
                result['sale_note'] = 'Using fallback prediction'
        else:
            print("Sale model is not loaded, using fallback")
            result['predictedSalePrice'] = fallback_sale_prediction(input_data)
            result['sale_note'] = 'Using fallback prediction (model not loaded)'
            
        # Rental Price Prediction
        if MODELS['rental'] is not None:
            try:
                rental_features = prepare_rental_features(input_data)
                rental_prediction = MODELS['rental'].predict(rental_features)[0]
                result['predictedRent'] = round(float(rental_prediction), 2)
                print(f"Rental price prediction: {result['predictedRent']}")
            except Exception as e:
                print(f"Error in rental price prediction: {e}")
                result['predictedRent'] = calculate_rental_estimate(input_data)
                result['rental_note'] = 'Using fallback prediction'
        else:
            result['predictedRent'] = calculate_rental_estimate(input_data)
            result['rental_note'] = 'Using fallback prediction (model not loaded)'
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in prediction endpoint: {e}")
        return jsonify({'error': str(e)}), 500

def get_predictions(data):
    """Get predictions from both models"""
    result = {}
    
    # Sale Price Prediction
    if MODELS['sale'] is not None:
        try:
            # Prepare features for XGBoost
            sale_features = prepare_sale_features(data)
            
            # Make prediction using XGBoost Booster
            sale_prediction = MODELS['sale'].predict(sale_features)
            result['predictedSalePrice'] = round(float(sale_prediction), 2)
            logger.info(f"Sale price prediction: {result['predictedSalePrice']}")
        except Exception as e:
            logger.error(f"Error in sale price prediction: {e}")
            result['predictedSalePrice'] = fallback_sale_prediction(data)
            result['sale_note'] = 'Using fallback prediction'
    else:
        logger.warning("Sale price model not loaded, using fallback")
        result['predictedSalePrice'] = fallback_sale_prediction(data)
        result['sale_note'] = 'Using fallback prediction (model not loaded)'
    
    # Rental Price Prediction
    if MODELS['rental'] is not None:
        try:
            rental_features = prepare_rental_features(data)
            rental_prediction = MODELS['rental'].predict(rental_features)[0]
            result['predictedRent'] = round(float(rental_prediction), 2)
            logger.info(f"Rental price prediction: {result['predictedRent']}")
        except Exception as e:
            logger.error(f"Error in rental price prediction: {e}")
            result['predictedRent'] = calculate_rental_estimate(data)
            result['rental_note'] = 'Using fallback prediction'
    else:
        logger.warning("Rental model not loaded, using fallback")
        result['predictedRent'] = calculate_rental_estimate(data)
        result['rental_note'] = 'Using fallback prediction (model not loaded)'
    
    return result

def prepare_sale_features(data):
    """Prepare features for sale price prediction"""
    try:
        print("Input data for sale features:", data)
        
        # Calculate derived features
        bedrooms = float(data.get('bedrooms', 3))
        bathrooms = float(data.get('bathrooms', 2))
        living_area = float(data.get('livingArea', 1500))
        year_built = float(data.get('yearBuilt', 1980))
        
        # Create a DataFrame with enhanced features
        features = pd.DataFrame({
            'bedrooms': [bedrooms],
            'bathrooms': [bathrooms],
            'living_area': [living_area],
            'year_built': [year_built],
            'property_age': [datetime.now().year - year_built],
            'bed_bath_ratio': [bedrooms / max(1, bathrooms)],  # Avoid division by zero
            'sqft_per_bedroom': [living_area / max(1, bedrooms)],
            'year': [datetime.now().year],
            'month': [datetime.now().month],
            'has_garage': [int(data.get('hasGarage', 0))],
            'has_pool': [int(data.get('hasPool', 0))],
            'has_fireplace': [int(data.get('hasFireplace', 0))],
            'has_basement': [int(data.get('hasBasement', 0))],
            'has_central_air': [int(data.get('hasCentralAir', 0))],
            'property_type_condo': [1 if data.get('propertyType') == 'CONDO' else 0],
            'property_type_single_family': [1 if data.get('propertyType') == 'SINGLE_FAMILY' else 0],
            'property_type_townhouse': [1 if data.get('propertyType') == 'TOWNHOUSE' else 0],
            'property_type_multi_family': [1 if data.get('propertyType') == 'MULTI_FAMILY' else 0],
            'zipcode': [data.get('zipcode', '02190')]
        })
        
        # Add location-based features for Weymouth
        weymouth_center = (42.2184, -70.9415)  # Weymouth center coordinates
        if 'latitude' in data and 'longitude' in data:
            lat, lon = float(data['latitude']), float(data['longitude'])
            features['distance_from_center'] = [np.sqrt((lat - weymouth_center[0])**2 + (lon - weymouth_center[1])**2)]
        else:
            features['distance_from_center'] = [0.0]  # Default to center
            
        print("Created features DataFrame:", features)
        
        # Convert to numpy array and ensure float32 type
        features_array = features.values.astype(np.float32)
        print("Features array shape:", features_array.shape)
        
        # Create DMatrix with feature names
        dmatrix = xgb.DMatrix(features_array, feature_names=features.columns.tolist())
        print("Created DMatrix with features:", features.columns.tolist())
        
        return dmatrix
        
    except Exception as e:
        logger.error(f"Detailed error preparing sale features: {str(e)}")
        logger.error(f"Input data that caused error: {data}")
        raise

def prepare_rental_features(data):
    """Prepare features for rental price prediction"""
    try:
        # Calculate derived features
        bedrooms = float(data.get('bedrooms', 3))
        bathrooms = float(data.get('bathrooms', 2))
        living_area = float(data.get('livingArea', 1500))
        
        # Create a DataFrame with all required features
        features = pd.DataFrame({
            'propertyType': [data.get('propertyType', 'SINGLE_FAMILY')],
            'latitude': [42.3601],  # Default to Boston
            'lotAreaValue': [float(data.get('lotArea', 0.25))],
            'bed_bath_ratio': [bedrooms / bathrooms if bathrooms > 0 else 0],
            'livingArea': [living_area],
            'daysOnZillow': [0],  # Placeholder
            'living_area_sqrt': [np.sqrt(living_area)],
            'longitude': [-71.0589],  # Default to Boston
            'bed_area_ratio': [bedrooms / living_area if living_area > 0 else 0],
            'bedrooms_squared': [bedrooms ** 2],
            'cambridge_distance': [2.5],  # Placeholder
            'boston_distance': [0.0],  # Placeholder
            'bathrooms_squared': [bathrooms ** 2]
        })
        
        return features
        
    except Exception as e:
        logger.error(f"Error preparing rental features: {e}")
        raise

def fallback_sale_prediction(data):
    """Fallback prediction for sale price"""
    try:
        # Base price for Weymouth area
        base_price = 450000  # Adjusted for Weymouth's market
        
        # Property type factors (adjusted for Weymouth)
        type_factors = {
            'CONDO': 0.85,
            'SINGLE_FAMILY': 1.2,
            'MULTI_FAMILY': 1.4,
            'TOWNHOUSE': 1.1,
            'MANUFACTURED': 0.7
        }
        
        # Get property characteristics
        bedrooms = float(data.get('bedrooms', 3))
        bathrooms = float(data.get('bathrooms', 2))
        living_area = float(data.get('livingArea', 1500))
        year_built = int(data.get('yearBuilt', 1980))
        property_type = data.get('propertyType', 'SINGLE_FAMILY')
        
        # Calculate property age
        current_year = datetime.now().year
        property_age = current_year - year_built
        
        # Start with base price
        predicted_price = base_price
        
        # Adjust for property type
        predicted_price *= type_factors.get(property_type, 1.0)
        
        # Adjust for bedrooms (non-linear scaling)
        bed_factor = 1 + (0.12 * bedrooms) + (0.02 * bedrooms ** 2)
        predicted_price *= bed_factor
        
        # Adjust for bathrooms (diminishing returns)
        bath_factor = 1 + (0.1 * bathrooms) - (0.01 * bathrooms ** 2)
        predicted_price *= bath_factor
        
        # Adjust for square footage (non-linear scaling)
        if living_area > 0:
            sqft_factor = (living_area / 1500) ** 0.8
            predicted_price *= sqft_factor
        
        # Adjust for property age (depreciation)
        age_factor = 1 - (property_age * 0.002)  # 0.2% depreciation per year
        predicted_price *= max(0.7, age_factor)  # Cap depreciation at 30%
        
        # Adjust for amenities
        if data.get('hasGarage', 0):
            predicted_price *= 1.1
        if data.get('hasPool', 0):
            predicted_price *= 1.15
        if data.get('hasFireplace', 0):
            predicted_price *= 1.05
        if data.get('hasBasement', 0):
            predicted_price *= 1.08
        if data.get('hasCentralAir', 0):
            predicted_price *= 1.07
        
        # Adjust for location in Weymouth
        if 'latitude' in data and 'longitude' in data:
            weymouth_center = (42.2184, -70.9415)
            lat, lon = float(data['latitude']), float(data['longitude'])
            distance = np.sqrt((lat - weymouth_center[0])**2 + (lon - weymouth_center[1])**2)
            if distance < 0.02:  # Close to center
                predicted_price *= 1.15
            elif distance < 0.05:  # Mid-range
                predicted_price *= 1.05
        
        return round(predicted_price, 2)
    except Exception as e:
        logger.error(f"Error in fallback sale prediction: {e}")
        return 450000  # Return base price for Weymouth

def calculate_rental_estimate(data):
    """Calculate rental estimate"""
    try:
        base_rent = 1500
        
        type_factors = {
            'CONDO': 1.1,
            'SINGLE_FAMILY': 1.3,
            'MULTI_FAMILY': 0.95,
            'TOWNHOUSE': 1.2,
            'MANUFACTURED': 0.85
        }
        base_rent *= type_factors.get(data.get('propertyType', 'SINGLE_FAMILY'), 1.0)
        base_rent *= (1 + 0.15 * int(data['bedrooms']))
        base_rent *= (1 + 0.1 * float(data.get('bathrooms', 1)))
        
        if 'livingArea' in data:
            sqft_factor = (int(data['livingArea']) / 1000) ** 0.7
            base_rent *= sqft_factor
        
        return round(base_rent, 2)
    except Exception as e:
        logger.error(f"Error calculating rental estimate: {e}")
        return 1500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 
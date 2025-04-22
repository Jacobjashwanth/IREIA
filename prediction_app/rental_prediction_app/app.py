from flask import Flask, render_template, request, jsonify
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

# Import from our modules
from config import Config
from models.model import predict_rent
from data.zillow_api import fetch_rental_listings

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configure CORS to allow requests from the React app
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ============== MODEL LOADING ==============

# Load the trained rental model
RENTAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'rental_model.pkl')
try:
    rental_model = joblib.load(RENTAL_MODEL_PATH)
    print(f"✅ Rental model loaded successfully from {RENTAL_MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading rental model: {e}")
    rental_model = None

# Load the XGBoost sales price model
SALES_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'price-prediction-model', 'xgboost_final_model.json')
try:
    sales_model = xgb.Booster()
    sales_model.load_model(SALES_MODEL_PATH)
    print(f"✅ Sales price model loaded successfully from {SALES_MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading sales price model: {e}")
    sales_model = None

# ============== REALTOR API CONFIG ==============
REALTOR_API_KEY = "6b504def46msha6bf4ff53605f98p1c0c1djsn3fcd43362b33"
REALTOR_HOST = "realty-in-us.p.rapidapi.com"
REALTOR_HEADERS = {
    "X-RapidAPI-Key": REALTOR_API_KEY,
    "X-RapidAPI-Host": REALTOR_HOST,
    "Content-Type": "application/json"
}

# ============== WEB ROUTES ==============

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', 
                           api_key=app.config['GOOGLE_MAPS_API_KEY'])

# ============== API ROUTES ==============

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
        
        # Prepare input data with defaults for optional fields
        input_data = {
            'zipcode': data['zipcode'],
            'bedrooms': int(data['bedrooms']),
            'bathrooms': int(data.get('bathrooms', 1)),  # Default to 1 if not provided
            'propertyType': data['propertyType'],
            'livingArea': float(data.get('livingArea', 1000)),  # Default value
            'lotArea': float(data.get('lotArea', 0.25)),  # Default value
            'daysOnMarket': int(data.get('daysOnMarket', 0)),  # Default value
            'yearBuilt': int(data.get('yearBuilt', 1980)),  # Default value
            'hasGarage': int(data.get('hasGarage', 1)),  # Default value
            'hasPool': int(data.get('hasPool', 0)),  # Default value
            'hasFireplace': int(data.get('hasFireplace', 0)),  # Default value
            'hasBasement': int(data.get('hasBasement', 1)),  # Default value
            'hasCentralAir': int(data.get('hasCentralAir', 1)),  # Default value
            'hasSecuritySystem': int(data.get('hasSecuritySystem', 0)),  # Default value
            'hasSprinklerSystem': int(data.get('hasSprinklerSystem', 0)),  # Default value
            'hasSolarPanels': int(data.get('hasSolarPanels', 0))  # Default value
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
                # Convert to numpy array for sale prediction
                sale_features = np.array([
                    input_data['bedrooms'],
                    input_data['bathrooms'],
                    input_data['livingArea'],
                    input_data['lotArea'],
                    input_data['daysOnMarket'],
                    input_data['yearBuilt'],
                    input_data['hasGarage'],
                    input_data['hasPool'],
                    input_data['hasFireplace'],
                    input_data['hasBasement'],
                    input_data['hasCentralAir'],
                    input_data['hasSecuritySystem'],
                    input_data['hasSprinklerSystem'],
                    input_data['hasSolarPanels'],
                    1 if input_data['propertyType'] == 'CONDO' else 0,
                    1 if input_data['propertyType'] == 'SINGLE_FAMILY' else 0
                ]).reshape(1, -1)
                
                sale_prediction = MODELS['sale'].predict(sale_features)[0]
                result['predictedSalePrice'] = round(float(sale_prediction), 2)
            except Exception as e:
                print(f"Error in sale price prediction: {e}")
                result['predictedSalePrice'] = fallback_sale_prediction(input_data)
                result['sale_note'] = 'Using fallback prediction'
        else:
            result['predictedSalePrice'] = fallback_sale_prediction(input_data)
            result['sale_note'] = 'Using fallback prediction (model not loaded)'
        
        # Rental Price Prediction
        if MODELS['rental'] is not None:
            try:
                # Convert to numpy array for rental prediction
                rental_features = np.array([
                    input_data['bedrooms'],
                    input_data['bathrooms'],
                    input_data['livingArea'],
                    input_data['lotArea'],
                    input_data['daysOnMarket'],
                    input_data['yearBuilt'],
                    input_data['hasGarage'],
                    input_data['hasPool'],
                    input_data['hasFireplace'],
                    input_data['hasBasement'],
                    input_data['hasCentralAir'],
                    input_data['hasSecuritySystem'],
                    input_data['hasSprinklerSystem'],
                    input_data['hasSolarPanels'],
                    1 if input_data['propertyType'] == 'CONDO' else 0,
                    1 if input_data['propertyType'] == 'SINGLE_FAMILY' else 0
                ]).reshape(1, -1)
                
                rental_prediction = MODELS['rental'].predict(rental_features)[0]
                result['predictedRent'] = round(float(rental_prediction), 2)
            except Exception as e:
                print(f"Error in rental price prediction: {e}")
                result['predictedRent'] = calculate_rental_estimate(input_data)
                result['rental_note'] = 'Using fallback prediction'
        else:
            result['predictedRent'] = calculate_rental_estimate(input_data)
            result['rental_note'] = 'Using fallback prediction (model not loaded)'
        
        print("Prediction result:", result)
        return jsonify(result)
            
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rentals', methods=['GET'])
def get_rentals():
    """Get rental listings near a location"""
    try:
        # Get parameters
        latitude = request.args.get('latitude', '42.3601')
        longitude = request.args.get('longitude', '-71.0589')
        radius = request.args.get('radius', '10')  # in miles
        
        # Get listings
        listings = fetch_rental_listings(
            latitude=float(latitude),
            longitude=float(longitude),
            radius=float(radius)
        )
        
        return jsonify({
            'status': 'success',
            'count': len(listings),
            'listings': listings
        })
    except Exception as e:
        print(f"Error fetching rentals: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-stats', methods=['GET'])
def get_market_stats():
    """Get rental market statistics"""
    # Get parameters
    city = request.args.get('city', 'Boston')
    
    # In a real application, you would query a database or API
    # for this data. Here we're using hardcoded values for demonstration.
    stats = {
        'Boston': {
            'averageRent': 2850,
            'pricePerSqFt': 2.15,
            'rentYoYChange': 4.7,
            'vacancyRate': 3.2
        },
        'Cambridge': {
            'averageRent': 3100,
            'pricePerSqFt': 2.45,
            'rentYoYChange': 5.2,
            'vacancyRate': 2.9
        },
        'Somerville': {
            'averageRent': 2750,
            'pricePerSqFt': 2.05,
            'rentYoYChange': 4.3,
            'vacancyRate': 3.5
        }
    }
    
    # Get stats for the requested city, or use Boston as default
    city_stats = stats.get(city, stats['Boston'])
    
    return jsonify({
        'status': 'success',
        'city': city,
        'stats': city_stats
    })

@app.route('/api/nearby-properties', methods=['GET'])
def get_nearby_properties():
    """Get nearby properties for a given location"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        
        # In a real application, you would query a database or API
        # For now, we'll generate some sample properties
        properties = []
        
        # Generate 5 sample properties around the given location
        for i in range(5):
            # Add some random variation to the coordinates
            prop_lat = lat + (random.random() - 0.5) * 0.01
            prop_lng = lng + (random.random() - 0.5) * 0.01
            
            # Generate random property details
            bedrooms = random.randint(1, 5)
            bathrooms = bedrooms + random.random()
            living_area = random.randint(800, 3000)
            property_type = random.choice(['CONDO', 'SINGLE_FAMILY', 'MULTI_FAMILY', 'TOWNHOUSE'])
            
            # Create input data for prediction
            input_data = {
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'livingArea': living_area,
                'lotArea': random.uniform(0.1, 0.5),
                'daysOnMarket': random.randint(0, 30),
                'yearBuilt': random.randint(1950, 2020),
                'hasGarage': random.choice([0, 1]),
                'hasPool': random.choice([0, 1]),
                'hasFireplace': random.choice([0, 1]),
                'hasBasement': random.choice([0, 1]),
                'hasCentralAir': random.choice([0, 1]),
                'hasSecuritySystem': random.choice([0, 1]),
                'hasSprinklerSystem': random.choice([0, 1]),
                'hasSolarPanels': random.choice([0, 1]),
                'propertyType': property_type
            }
            
            # Convert to numpy array for prediction
            features = np.array([
                input_data['bedrooms'],
                input_data['bathrooms'],
                input_data['livingArea'],
                input_data['lotArea'],
                input_data['daysOnMarket'],
                input_data['yearBuilt'],
                input_data['hasGarage'],
                input_data['hasPool'],
                input_data['hasFireplace'],
                input_data['hasBasement'],
                input_data['hasCentralAir'],
                input_data['hasSecuritySystem'],
                input_data['hasSprinklerSystem'],
                input_data['hasSolarPanels'],
                1 if input_data['propertyType'] == 'CONDO' else 0,
                1 if input_data['propertyType'] == 'SINGLE_FAMILY' else 0
            ]).reshape(1, -1)
            
            # Make prediction
            predicted_rent = rental_model.predict(features)[0] if rental_model else calculate_rental_estimate(input_data)
            
            properties.append({
                'latitude': prop_lat,
                'longitude': prop_lng,
                'address': f'Property {i+1}',
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'living_area': living_area,
                'property_type': property_type,
                'predicted_rent': round(float(predicted_rent), 2)
            })
        
        return jsonify({
            'status': 'success',
            'properties': properties
        })
        
    except Exception as e:
        print(f"Error fetching nearby properties: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def get_predictions(data):
    """Get predictions from both models"""
    try:
        # Prepare features for both models
        sale_features = prepare_sale_features(data)
        rental_features = prepare_rental_features(data)
        
        # Make predictions
        sale_price = None
        rental_price = None
        notes = []
        
        # Sales price prediction
        if sales_model is not None:
            try:
                # Convert features to DMatrix format required by XGBoost
                dmatrix = xgb.DMatrix(sale_features)
                sale_price = sales_model.predict(dmatrix)[0]
            except Exception as e:
                logger.error(f"Error predicting sale price: {e}")
                notes.append("Using fallback sale price prediction")
                sale_price = calculate_fallback_sale_price(data)
        else:
            notes.append("Sales model not loaded, using fallback prediction")
            sale_price = calculate_fallback_sale_price(data)
        
        # Rental price prediction
        if rental_model is not None:
            try:
                rental_price = rental_model.predict(rental_features)[0]
            except Exception as e:
                logger.error(f"Error predicting rental price: {e}")
                notes.append("Using fallback rental price prediction")
                rental_price = calculate_fallback_rental_price(data)
        else:
            notes.append("Rental model not loaded, using fallback prediction")
            rental_price = calculate_fallback_rental_price(data)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "predictedSalePrice": float(sale_price),
            "predictedRent": float(rental_price),
            "notes": notes
        }
        
    except Exception as e:
        logger.error(f"Error in get_predictions: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# Change the line at the bottom of app.py
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5001)  # Changed from 5000 to 5001
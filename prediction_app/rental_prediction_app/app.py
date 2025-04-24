
from flask import Flask, render_template, request, jsonify
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import json
import requests
from werkzeug.middleware.proxy_fix import ProxyFix

# Import from our modules
from config import Config
from models.model import predict_rent
from data.zillow_api import fetch_rental_listings

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.config.from_object(Config)

# Load the trained model
model_path = os.path.join(app.root_path, 'models', 'rental_model.pkl')
try:
    model = joblib.load(model_path)
    print(f"Model loaded successfully from {model_path}")
except FileNotFoundError:
    print(f"Warning: Model file not found at {model_path}")
    model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', 
                           api_key=app.config['GOOGLE_MAPS_API_KEY'])

# @app.route('/api/predict', methods=['POST'])
# def predict():
#     """API endpoint for making rental predictions"""
#     try:
#         # Get data from request
#         data = request.get_json()
        
#         # Required fields
#         required_fields = ['latitude', 'longitude', 'propertyType', 
#                           'bedrooms', 'bathrooms', 'livingArea']
        
#         # Check if all required fields are present
#         for field in required_fields:
#             if field not in data:
#                 return jsonify({'error': f'Missing required field: {field}'}), 400
        
#         # Use our model prediction function
#         if model is not None:
#             predicted_rent = predict_rent(
#                 model,
#                 latitude=float(data['latitude']),
#                 longitude=float(data['longitude']),
#                 property_type=data['propertyType'],
#                 bedrooms=int(data['bedrooms']),
#                 bathrooms=float(data['bathrooms']),
#                 living_area=int(data['livingArea']),
#                 lot_area=float(data.get('lotArea', 0.25)),
#                 days_on_market=int(data.get('daysOnMarket', 0))
#             )
            
#             # Format the result
#             result = {
#                 'predictedRent': round(predicted_rent, 2),
#                 'status': 'success',
#                 'timestamp': datetime.now().isoformat()
#             }
            
#             return jsonify(result)
#         else:
#             # If model is not available, use a fallback method
#             return jsonify({
#                 'predictedRent': fallback_prediction(data),
#                 'status': 'fallback',
#                 'message': 'Using fallback prediction as model is unavailable',
#                 'timestamp': datetime.now().isoformat()
#             })
            
#     except Exception as e:
#         print(f"Error during prediction: {e}")
#         return jsonify({'error': str(e)}), 500



@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for making rental predictions"""
    try:
        # Get data from request
        data = request.get_json()
        
        # Required fields
        required_fields = ['zipcode', 'bedrooms', 'bathrooms']
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Use our model prediction function
        if model is not None:
            predicted_rent = predict_rent(
                model,
                bedrooms=int(data['bedrooms']),
                bathrooms=float(data['bathrooms']),
                zipcode=data['zipcode'],
                latitude=float(data.get('latitude', 42.3601)),
                longitude=float(data.get('longitude', -71.0589)),
                property_type=data.get('propertyType', 'SINGLE_FAMILY'),
                living_area=int(data.get('livingArea', 1000)),
                lot_area=float(data.get('lotArea', 0.25)),
                days_on_market=int(data.get('daysOnMarket', 0))
            )
            
            # Convert NumPy types to Python native types
            if hasattr(predicted_rent, 'item'):  # Check if it's a NumPy type
                predicted_rent = predicted_rent.item()  # Convert to Python native type
            else:
                predicted_rent = float(predicted_rent)  # Ensure it's a Python float
            
            # Format the result
            result = {
                'predictedRent': round(predicted_rent, 2),
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(result)
        else:
            # If model is not available, use a fallback method
            return jsonify({
                'predictedRent': fallback_prediction(data),
                'status': 'fallback',
                'message': 'Using fallback prediction as model is unavailable',
                'timestamp': datetime.now().isoformat()
            })
            
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

# def fallback_prediction(data):
#     """Fallback prediction method when model is unavailable"""
#     # Base rent starts at $1500
#     predicted_rent = 1500
    
#     # Adjust for property type
#     type_factors = {
#         'CONDO': 1.1,
#         'SINGLE_FAMILY': 1.3,
#         'MULTI_FAMILY': 0.95,
#         'TOWNHOUSE': 1.2,
#         'MANUFACTURED': 0.85
#     }
#     predicted_rent *= type_factors.get(data['propertyType'], 1.0)
    
#     # Adjust for bedrooms
#     predicted_rent *= (1 + 0.15 * int(data['bedrooms']))
    
#     # Adjust for bathrooms
#     predicted_rent *= (1 + 0.1 * float(data['bathrooms']))
    
#     # Adjust for square footage
#     sqft_factor = (int(data['livingArea']) / 1000) ** 0.7  # Non-linear scaling
#     predicted_rent *= sqft_factor
    
#     # Adjust for location
#     # Simple adjustment based on distance from downtown Boston
#     boston_lat, boston_lng = 42.3601, -71.0589
#     distance = np.sqrt((float(data['latitude']) - boston_lat)**2 + 
#                         (float(data['longitude']) - boston_lng)**2)
    
#     if distance < 0.03:
#         location_factor = 1.5  # Downtown/central Boston premium
#     elif distance < 0.1:
#         location_factor = 1.3  # Inner Boston/Cambridge/Somerville
#     elif distance < 0.2:
#         location_factor = 1.15  # Greater Boston area
#     elif distance < 0.4:
#         location_factor = 1.0  # Suburbs
#     else:
#         location_factor = 0.85  # Further out
    
#     predicted_rent *= location_factor
    
#     # Round to nearest $10
#     return round(predicted_rent / 10) * 10




def fallback_prediction(data):
    """Fallback prediction method when model is unavailable"""
    # Base rent starts at $1500
    predicted_rent = 1500
    
    # Adjust for property type
    type_factors = {
        'CONDO': 1.1,
        'SINGLE_FAMILY': 1.3,
        'MULTI_FAMILY': 0.95,
        'TOWNHOUSE': 1.2,
        'MANUFACTURED': 0.85
    }
    predicted_rent *= type_factors.get(data.get('propertyType', 'SINGLE_FAMILY'), 1.0)
    
    # Adjust for bedrooms
    predicted_rent *= (1 + 0.15 * int(data['bedrooms']))
    
    # Adjust for bathrooms
    predicted_rent *= (1 + 0.1 * float(data['bathrooms']))
    
    # Adjust for square footage if available
    if 'livingArea' in data:
        sqft_factor = (int(data['livingArea']) / 1000) ** 0.7  # Non-linear scaling
        predicted_rent *= sqft_factor
    
    # Adjust for zipcode (simplified approach)
    # Premium zipcodes in Boston area
    premium_zipcodes = ['02108', '02109', '02110', '02111', '02113', '02114', '02115', '02116', 
                        '02118', '02138', '02139', '02140', '02142', '02210']
    
    mid_tier_zipcodes = ['02119', '02120', '02121', '02122', '02125', '02126', '02127', '02128', 
                         '02129', '02130', '02131', '02132', '02134', '02141', '02143', '02144']
    
    zipcode = data.get('zipcode', '02108')
    
    if zipcode in premium_zipcodes:
        zipcode_factor = 1.3  # Premium areas
    elif zipcode in mid_tier_zipcodes:
        zipcode_factor = 1.1  # Mid-tier areas
    else:
        zipcode_factor = 1.0  # Other areas
    
    predicted_rent *= zipcode_factor
    
    # Adjust for location if available
    if 'latitude' in data and 'longitude' in data:
        boston_lat, boston_lng = 42.3601, -71.0589
        distance = np.sqrt((float(data['latitude']) - boston_lat)**2 + 
                           (float(data['longitude']) - boston_lng)**2)
        
        if distance < 0.03:
            location_factor = 1.5  # Downtown/central Boston premium
        elif distance < 0.1:
            location_factor = 1.3  # Inner Boston/Cambridge/Somerville
        elif distance < 0.2:
            location_factor = 1.15  # Greater Boston area
        elif distance < 0.4:
            location_factor = 1.0  # Suburbs
        else:
            location_factor = 0.85  # Further out
        
        predicted_rent *= location_factor
    
    # Round to nearest $10
    return round(predicted_rent / 10) * 10

# Change the line at the bottom of app.py
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5001)  # Changed from 5000 to 5001
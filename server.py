from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS to accept requests from your React app
CORS(app, resources={r"/*": {"origins": "*"}})

# Load the XGBoost model
MODEL_PATH = 'ml_models/price-prediction-model/xgboost/xgboost_final_model.pkl'

try:
    model = joblib.load(MODEL_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")

        # Calculate predictions
        sale_price = calculate_sale_price(data)
        rental_price = calculate_rental_price(data)
        
        # Get coordinates for the map (using a default location if zipcode mapping is not available)
        coordinates = get_coordinates(data.get('zipcode', '02108'))

        response = {
            'predictedSalePrice': sale_price,
            'predictedRent': rental_price,
            'coordinates': coordinates,
            'status': 'success'
        }
        
        logger.info(f"Sending response: {response}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

def calculate_sale_price(data):
    try:
        if model is not None:
            # Prepare features for the model
            features = {
                'Year': datetime.now().year,
                'Month': datetime.now().month,
                'Crime Rate': 0.05,
                'sentiment_score': 0,
                'Bedrooms': int(data.get('bedrooms', 2)),
                'Bathrooms': float(data.get('bathrooms', 1)),
                'Square Footage': float(data.get('livingArea', 1000)),
                'Year Built': 2000,
                'Price': 0
            }
            df = pd.DataFrame([features])
            prediction = model.predict(df)[0]
            return round(float(prediction), 2)
        else:
            return fallback_sale_price(data)
    except Exception as e:
        logger.error(f"Error in sale price calculation: {e}")
        return fallback_sale_price(data)

def fallback_sale_price(data):
    base_price = 300000
    bedrooms = int(data.get('bedrooms', 2))
    bathrooms = float(data.get('bathrooms', 1))
    living_area = float(data.get('livingArea', 1000))
    
    # Adjust price based on features
    price = base_price * (1 + 0.1 * bedrooms)
    price *= (1 + 0.05 * bathrooms)
    price *= (living_area / 1000)
    
    return round(price, 2)

def calculate_rental_price(data):
    base_rent = 2000
    bedrooms = int(data.get('bedrooms', 2))
    bathrooms = float(data.get('bathrooms', 1))
    living_area = float(data.get('livingArea', 1000))
    
    # Adjust rent based on features
    rent = base_rent * (1 + 0.15 * bedrooms)
    rent *= (1 + 0.1 * bathrooms)
    rent *= (living_area / 1000)
    
    return round(rent, 2)

def get_coordinates(zipcode):
    # This is a simplified version. In a real app, you'd want to use a geocoding service
    # Default to Boston coordinates
    coordinates = {
        '02108': {'lat': 42.3601, 'lng': -71.0589},
        '02109': {'lat': 42.3621, 'lng': -71.0550},
        '02110': {'lat': 42.3590, 'lng': -71.0510}
    }
    return coordinates.get(zipcode, {'lat': 42.3601, 'lng': -71.0589})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 
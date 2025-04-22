# Property Price Prediction Server

This Flask server provides APIs for predicting both sale prices and rental prices for properties.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure model files are in the correct locations:
- Sale price model: `ml_models/price-prediction-model/xgboost_final_model.json`
- Rental model: `ml_models/rental_model.pkl`

## Running the Server

1. Activate the virtual environment if not already activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Start the server:
```bash
python app.py
```

The server will run on `http://0.0.0.0:5001` with the following endpoints:

- `GET /`: Health check endpoint
- `POST /api/predict`: Make predictions for both sale and rental prices

## API Usage

### Predict Endpoint

Send a POST request to `/api/predict` with JSON data:

```json
{
    "zipcode": "02108",
    "bedrooms": 3,
    "bathrooms": 2,
    "propertyType": "SINGLE_FAMILY",
    "livingArea": 1500,
    "yearBuilt": 2000,
    "hasGarage": 1,
    "hasPool": 0,
    "hasFireplace": 0,
    "hasBasement": 1
}
```

Response will include both sale and rental predictions:

```json
{
    "status": "success",
    "timestamp": "2024-03-14T12:00:00.000Z",
    "predictedSalePrice": 500000.00,
    "predictedRent": 2500.00
}
```

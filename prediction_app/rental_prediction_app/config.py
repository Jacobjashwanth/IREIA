class Config:
    """Configuration settings for the application"""
    # Flask settings
    SECRET_KEY = 'dev-rental-prediction-secret-key-2025'
    DEBUG = True
    PORT = 5000
    
    # API keys (hardcoded - not recommended for production)
    GOOGLE_MAPS_API_KEY = 'AIzaSyCHI_Gj3CheYyq_5ExMEXWJdzBb8DLQUm4'  # Replace with your actual Google Maps API key
    ZILLOW_API_KEY = '30c130cfe6mshb5b1c7bdb9d6832p10fad8jsnb59fe5804bc3'  # Replace with your actual Zillow API key
    ZILLOW_API_HOST = 'zillow-com1.p.rapidapi.com'
    
    # Model settings
    MODEL_PATH = 'models/rental_model.pkl'



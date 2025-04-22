import tkinter as tk
from tkinter import messagebox
from flask import Flask, request, jsonify
import threading
import joblib
import requests
import numpy as np
import time

# Load model and scaler
model = joblib.load("rental_model.pkl")
scaler = joblib.load("scaler.pkl")

# ---------- FLASK BACKEND ----------
app = Flask(__name__)

@app.route('/predict_rent', methods=['POST'])
def predict_rent():
    data = request.get_json()

    postal = str(data.get("postal_code", ""))
    if not postal.isdigit() or len(postal) != 5:
        return jsonify({"error": "Invalid postal code. It must be a 5-digit number."}), 400

    # Extract and convert to float, defaulting to 0.0
    features = [
        float(data.get("bedrooms", 0)),
        float(data.get("bathrooms", 0)),
        float(data.get("sqft", 0)),
        float(postal),
        0.0 
    ]

    scaled_features = scaler.transform([features])
    prediction = model.predict(scaled_features)
    predicted_rent = float(prediction[0])

    # Zone logic (adjust thresholds as needed)
    if predicted_rent >= 25000:
        zone = "High Rent Area"
    elif predicted_rent >= 15000:
        zone = "Mid Rent Area"
    else:
        zone = "Low Rent Area"

    return jsonify({
        "predicted_rent": predicted_rent,
        "zone": zone
    })

# Additional endpoint for property data
@app.route('/properties', methods=['GET'])
def get_properties():
    # Sample static data for properties (In real-world, fetch from a DB or API)
    properties = [
        {"postal_code": "02138", "lat": 42.373611, "lng": -71.109733, "rent": 2000, "zone": "Low Rent Area"},
        {"postal_code": "02139", "lat": 42.373611, "lng": -71.108156, "rent": 3000, "zone": "Mid Rent Area"},
        # Add more properties here
    ]
    return jsonify(properties)

# Run Flask in background thread
def run_flask():
    app.run(debug=False)

# ---------- UI ----------
from tkinterweb import HtmlFrame

FIELDS = [
    ("Bedrooms", "bedrooms"),
    ("Bathrooms", "bathrooms"),
    ("Square Foot", "sqft"),
    ("Postal Code", "postal_code")  
]

def show_map():
    # Create a new window for the map
    map_window = tk.Toplevel()
    map_window.title("Property Map")
    map_window.geometry("800x600")

    # Create the HTML frame to display Google Maps
    frame = HtmlFrame(map_window, width=800, height=600)
    frame.pack(fill="both", expand=True)

    # Get properties from Flask backend
    response = requests.get("http://127.0.0.1:5000/properties")
    if response.status_code == 200:
        properties = response.json()
        markers = ""
        
        for prop in properties:
            lat = prop["lat"]
            lng = prop["lng"]
            rent = prop["rent"]
            zone = prop["zone"]
            
            markers += f"""
                var marker = new google.maps.Marker({
                    position: {{ lat: {lat}, lng: {lng} }},
                    map: map,
                    title: 'Rent: ${rent}, Zone: {zone}'
                });
            """
        
        # Google Maps HTML template with JavaScript for markers
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Property Map</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY_HERE&callback=initMap" async defer></script>
            <script type="text/javascript">
                var map;
                function initMap() {{
                    map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 13,
                        center: {{ lat: 42.373611, lng: -71.109733 }}
                    }});
                    {markers}
                }}
            </script>
        </head>
        <body>
            <div id="map" style="height: 100%;"></div>
        </body>
        </html>
        """
        
        # Load the map in the frame
        frame.set_content(html_content)

    else:
        print(f"Error fetching properties: {response.status_code}")

def start_ui():
    def predict_rent():
        try:
            input_data = {}
            for label, key in FIELDS:
                value = entries[key].get()

                # Validate postal code
                if key == "postal_code":
                    if not value.isdigit() or len(value) != 5:
                        messagebox.showerror("Input Error", "Postal code must be a 5-digit number.")
                        return
                    input_data[key] = value  # Send as string
                else:
                    input_data[key] = float(value) if value else 0.0

            response = requests.post("http://127.0.0.1:5000/predict_rent", json=input_data)
            if response.status_code == 200:
                result = response.json()
                rent_var.set(f"${result['predicted_rent']:.2f}")
                zone_var.set(result['zone'])
            else:
                error_msg = response.json().get("error", "Unknown error")
                messagebox.showerror("API Error", f"Status Code: {response.status_code}\n{error_msg}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("Rental Price Predictor")
    root.geometry("450x500")
    root.resizable(False, False)

    tk.Label(root, text="Enter Property Details", font=("Helvetica", 16, "bold")).pack(pady=10)

    global entries
    entries = {}
    for label_text, key in FIELDS:
        frame = tk.Frame(root)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=25, anchor='w').pack(side="left")
        entry = tk.Entry(frame, width=20)
        entry.pack(side="right")
        entries[key] = entry

    tk.Button(root, text="Predict Rent", command=predict_rent, bg="#4CAF50", fg="black", font=("Helvetica", 12, "bold")).pack(pady=20)

    output_frame = tk.Frame(root)
    output_frame.pack(pady=10)

    tk.Label(output_frame, text="Estimated Rent:", font=("Helvetica", 12)).grid(row=0, column=0, sticky='w', padx=10)
    rent_var = tk.StringVar()
    tk.Label(output_frame, textvariable=rent_var, font=("Helvetica", 12, "bold")).grid(row=0, column=1)

    tk.Label(output_frame, text="Zone:", font=("Helvetica", 12)).grid(row=1, column=0, sticky='w', padx=10)
    zone_var = tk.StringVar()
    tk.Label(output_frame, textvariable=zone_var, font=("Helvetica", 12, "bold")).grid(row=1, column=1)

    # Button to show the map
    tk.Button(root, text="Show Properties on Map", command=show_map, bg="#4CAF50", fg="black", font=("Helvetica", 12, "bold")).pack(pady=20)

    root.mainloop()

# ---------- MAIN ----------
if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(1.5)  
    start_ui()

# 🏠 IREIA – Intelligent Real Estate Investment Advisor

![IREIA Logo](./assets/logo.png)

**IREIA** is an AI-powered real estate investment platform that helps users predict future home prices and rental returns based on real-time data, local market trends, and machine learning models.

---

## 📌 Overview

IREIA empowers potential homebuyers and investors to make smart, data-driven decisions by offering:

- 📈 Future property price predictions
- 💰 Rental income forecasts
- 🗺️ Nearby property and school visualizations
- 🏆 Investment recommendations

All powered through a user-friendly Zillow-style frontend and a machine learning backend integrated with the **Realtor API**.

---

## ❓ Problem Statement

Many buyers and investors struggle with evaluating if a property is truly worth investing in. Traditional listings show prices, but **lack predictive insights** into:

- Future home value trends
- Rental income potential
- Local investment risks

---

## ✅ Our Solution

**IREIA** bridges this gap by combining:
- 🧠 ML-based price prediction (XGBoost)
- 📊 Rental estimation model
- 🧭 Google Maps integration for nearby data
- 📡 Live property data via Realtor API

> "We don't just show you what a home costs—we show you what it's worth."

---

## 🛠 Tech Stack

**Frontend:**  
- HTML, CSS, JavaScript (Zillow-style responsive design)  
- React (in-progress branch)  
- Google Maps API (for pins, schools, walk score)

**Backend:**  
- Flask (Python API)  
- XGBoost for price prediction  
- Scikit-learn for rental forecasting  
- Realtor API (live property and historical data)

**Others:**  
- Chart.js for price and rent trend visualization  
- Pandas, NumPy for feature engineering  
- joblib, pickle for model handling

---

## 🚀 Features

- 🔍 Search by ZIP code, address, or city
- 💵 Predict future 3-year property prices
- 📈 Chart-based rent forecast per property
- 🟢 Investment suggestion engine (worth investing / overpriced)
- 🏫 Nearby school lookup (Google Places API)
- 🏡 Map pins with price tags for neighboring properties

---

## 🧰 Installation

```bash
git clone https://github.com/your-username/IREIA.git
cd IREIA
pip install -r requirements.txt
```

> Make sure you have Python 3.10+ and Node.js (if using React frontend)

---

## ▶️ Running the App

**Backend:**
```bash
cd backend
python app.py
```

**Frontend (static version):**
Open `frontend/index.html` in your browser

**Frontend (React version):**
```bash
cd frontend2/ireia-ui
npm install
npm run dev
```

---

## 👨‍👩‍👦 Team

- **Jacob Jashwanth Patoju** – ML Lead, Backend Dev
- *(Add teammate names + roles)*

---

## 🧠 Lessons Learned

- Training domain-specific models (price vs. rent) requires proper ground truth separation
- Real-time APIs offer massive potential but pose rate-limiting and formatting challenges
- Integrating charts, maps, and ML in a single app builds full-stack confidence!

---

## 📸 Screenshots

> Add screenshots of:
- Homepage with map
- Property detail page
- Price and Rent chart
- Nearby schools view

---

## 📜 License

This project is licensed under MIT. Feel free to use, extend, or contribute.

---

## 🔗 Links

- [Realtor API](https://rapidapi.com/apidojo/api/realty-in-us)
- [IREIA Live Demo](https://your-demo-link.com) *(if deployed)*
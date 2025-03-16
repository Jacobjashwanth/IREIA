# API Summary: Realtor & Zillow API (RapidAPI)

## Overview
This document provides an analysis of the Realtor and Zillow APIs available on RapidAPI, focusing on the response format, available data fields, and their suitability for the IREIA project.

## API Requests Tested
- **API Names:** Realtor API & Zillow API (RapidAPI)
- **Tested Endpoints:**
  - `GET /listings` (Realtor API)
  - `POST /properties/list` (Realtor API)
  - `GET /property-list` (Zillow API)
  - `GET /market-data` (Zillow API)
- **Locations Tested:** Boston, MA & Los Angeles, CA & Anchorage, AK & Orlando, FL
- **Response Format:** JSON

## API Response Breakdown
The API responses contain four major types of data:
1. **City Search Data:** Metadata on cities, states, and counties.
2. **Property Listings Data:** Information about properties listed for sale.
3. **Zillow-Specific Data:** Property valuation, tax history, mortgage rates, climate risk, school ratings.
4. **Market Data:** Median rent prices over time, market temperature, nearby area trends.

**City Search Response Data (Realtor API):**
- **City Name** (`city`)
- **State Code** (`state_code`)
- **County Information** (`counties` → name, fips, state_code)
- **Geolocation Data** (`centroid` → latitude, longitude)
- **Unique Slug ID** (`slug_id`)
- **Geo ID** (`geo_id`)

### **Property Listings Response Data (Realtor API):**
- **Property ID & Listing ID** (`property_id`, `listing_id`)
- **Status of Listing** (`status` → for_sale, pending, etc.)
- **Address Information** (`location.address` → city, street, postal code, state, country)
- **Geolocation Data** (`coordinate.lat`, `coordinate.lon`)
- **Price & Valuation** (`list_price`, `estimate.estimate`, `last_sold_price`)
- **Property Details** (`beds`, `baths`, `sqft`, `lot_sqft`)
- **Open House Information** (`open_houses.start_date`, `open_houses.end_date`)
- **Photo Count & URL** (`photo_count`, `primary_photo.href`)
- **Real Estate Agent Details** (`advertisers.name`, `advertisers.email`, `advertisers.href`)
- **Property Features & Flags** (`flags.is_new_listing`, `flags.is_foreclosure`, `flags.is_contingent`)
- **MLS Source & Agent Info** (`source.agents.agent_name`, `source.agents.office_name`)

### **Zillow-Specific Property Data:**
- **Street Address & County** (`streetAddress`, `county`)
- **Property Tax Rate & Tax History** (`propertyTaxRate`, `taxHistory` → tax paid, value increase rate)
- **Home Valuation Estimates** (`zestimate`, `zestimateHighPercent`, `zestimateLowPercent`)
- **Mortgage Rates** (`mortgageRates.thirtyYearFixedRate`, `mortgageRates.fifteenYearFixedRate`)
- **Nearby Homes for Sale** (`nearbyHomes` → price, homeType, homeStatus)
- **Climate Risk Assessment** (`climate.floodSources.primary.riskScore`, `climate.fireSources.primary.riskScore`)
- **School Ratings** (`schools` → name, rating, distance)

### **Market Data (Zillow API):**
- **Median Rent Price Over Time** (`medianRentPriceOverTime` → historical rent price trends by month/year)
- **Market Temperature** (`marketTemperature.temperature` → HOT, WARM, COLD)
- **Nearby Area Trends** (`nearbyAreaTrends` → trends in surrounding areas)
- **Zip Code Specific Data** (`zipcodesInCity` → ZIP codes available in a specific city, useful for granular analysis)
- **Nearby Cities and Trends** (`nearByAreas` → neighboring cities with real estate activity)

### Sample API Response Structure (Market Data - Zillow)
```json
{
  "medianRentPriceOverTime": {
    "prevYear": [
      {"price": 1275, "year": "2024", "month": "Apr"},
      {"price": 900, "year": "2024", "month": "Jul"},
      {"price": 1037.5, "year": "2024", "month": "Aug"}
    ]
  },
  "marketTemperature": {"temperature": "WARM"},
  "zipcodesInCity": [{"city": "Orlando", "name": "32825", "state": "FL"}]
}
```

## Analysis of Data Fields
### ✅ **Useful Data for the Project:**
| Field                                     | Description                      | Project Feature Usage                 |
|-------------------------------------------|----------------------------------|--------------------------------------|
| `city`, `state_code`, `county`            | Location details                 | Needed for property location analysis |
| `list_price`, `estimate.estimate`, `zestimate` | Property valuation          | Required for price prediction         |
| `beds`, `baths`, `sqft`, `lot_sqft`       | Property attributes              | Used for rental income optimization   |
| `flags.is_new_listing`                    | Property status                  | Helps detect trends in new listings   |
| `propertyTaxRate`, `taxHistory`           | Historical price trends          | Needed for property value forecasting |
| `schools.name`, `schools.rating`          | School Ratings                   | Important for property valuation      |
| `climate.floodSources.primary.riskScore`  | Risk assessment                  | Identifies flood-prone properties     |
| `medianRentPriceOverTime`                 | Market trends                    | Helps analyze rental income potential |
| `marketTemperature.temperature`           | Market activity level            | Useful for predicting investment risks|

### ❌ **Missing Data for the Project:**
| Required Field                              | Status              | Alternative Source Needed?               |
|---------------------------------------------|---------------------|------------------------------------------|
| Crime Rate                                  | ❌ Not Available    | Need external datasets                   |
| Market Trends (news/social media sentiment) | ❌ Not Available    | NLP on news & reports needed             |
| Neighborhood Growth Data                    | ❌ Not Available    | May require external sources             |

## **Conclusion & Next Steps**
- **✅ The Realtor API is useful for:** 
  - **Property listings & valuation data.**
  - **Basic property details (location, size, price).**
  - **Tracking new listings & real estate trends.**
- **✅ The Zillow API adds value with:**
  - **Tax history & mortgage rate trends.**
  - **Climate risk, school ratings, and rental market trends.**
- **❌ These APIs do NOT provide:**
  - **Crime rate & neighborhood appreciation trends.**
  - **Market trend analysis (news/social media sentiment).**

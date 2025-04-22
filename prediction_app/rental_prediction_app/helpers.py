import numpy as np
from datetime import datetime

def fallback_rent_prediction(data):
    """Fallback rental prediction method when model is unavailable"""
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
    predicted_rent *= (1 + 0.1 * float(data.get('bathrooms', 1)))
    
    # Adjust for square footage if available
    if 'livingArea' in data:
        sqft_factor = (int(data['livingArea']) / 1000) ** 0.7  # Non-linear scaling
        predicted_rent *= sqft_factor
    
    # Adjust for additional features
    if data.get('hasGarage', 0):
        predicted_rent *= 1.1
    if data.get('hasPool', 0):
        predicted_rent *= 1.15
    if data.get('hasFireplace', 0):
        predicted_rent *= 1.05
    if data.get('hasBasement', 0):
        predicted_rent *= 1.08
    if data.get('hasCentralAir', 0):
        predicted_rent *= 1.07
    if data.get('hasSecuritySystem', 0):
        predicted_rent *= 1.03
    if data.get('hasSprinklerSystem', 0):
        predicted_rent *= 1.02
    if data.get('hasSolarPanels', 0):
        predicted_rent *= 1.12
    
    # Adjust for year built
    year_factor = 1 + (2025 - int(data.get('yearBuilt', 1980))) * 0.001
    predicted_rent *= year_factor
    
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
    
    # Round to nearest $10
    return round(predicted_rent / 10) * 10

def fallback_sale_price_prediction(data):
    """Fallback sale price prediction when model is unavailable"""
    # Base price starts at $300,000
    base_price = 300000
    
    # Adjust for bedrooms
    bed_factor = 1 + (0.1 * int(data.get('bedrooms', 3)))
    
    # Adjust for bathrooms 
    bath_factor = 1 + (0.07 * float(data.get('bathrooms', 2)))
    
    # Adjust for square footage
    sqft_factor = (float(data.get('squareFootage', 1500)) / 1500) ** 1.1
    
    # Adjust for year built
    year_built = int(data.get('yearBuilt', 1980))
    age = 2025 - year_built
    age_factor = 1 - (age * 0.002)  # Newer properties worth more
    
    # Calculate the price
    price = base_price * bed_factor * bath_factor * sqft_factor * max(0.7, age_factor)
    
    # Return the result rounded to the nearest $1000
    return round(price / 1000) * 1000

def estimate_current_price(beds, baths, sqft):
    """Estimate current price based on basic metrics"""
    # Simple formula for estimating property price when not provided
    base_price = 250000
    bed_factor = 1 + (0.1 * beds)
    bath_factor = 1 + (0.07 * baths)
    sqft_factor = (sqft / 1500) ** 1.1
    
    price = base_price * bed_factor * bath_factor * sqft_factor
    return price

def calculate_investment_metrics(sale_price, monthly_rent, property_data):
    """Calculate various investment metrics based on predicted values"""
    # Get additional data from input or use defaults
    property_tax_rate = float(property_data.get('propertyTaxRate', 0.012))  # 1.2% annual
    insurance_rate = float(property_data.get('insuranceRate', 0.005))       # 0.5% annual
    maintenance_rate = float(property_data.get('maintenanceRate', 0.01))    # 1% annual
    vacancy_rate = float(property_data.get('vacancyRate', 0.05))            # 5% vacancy
    management_fee_rate = float(property_data.get('managementFeeRate', 0.1))  # 10% of rent
    closing_costs = float(property_data.get('closingCosts', 0.03))          # 3% of purchase price
    
    # Calculate derived values
    annual_rent = monthly_rent * 12
    property_tax = sale_price * property_tax_rate
    insurance = sale_price * insurance_rate
    maintenance = sale_price * maintenance_rate
    vacancy_loss = annual_rent * vacancy_rate
    management_fee = annual_rent * management_fee_rate
    
    # Calculate total annual expenses
    annual_expenses = property_tax + insurance + maintenance + vacancy_loss + management_fee
    
    # Calculate net operating income (NOI)
    noi = annual_rent - annual_expenses
    
    # Calculate cap rate
    cap_rate = (noi / sale_price) * 100 if sale_price > 0 else 0
    
    # Calculate cash-on-cash return (assuming 20% down payment)
    down_payment = sale_price * 0.2
    total_investment = down_payment + (sale_price * closing_costs)
    
    # Assume 30-year mortgage at 5.5% interest rate
    loan_amount = sale_price - down_payment
    interest_rate = float(property_data.get('interestRate', 0.055))
    loan_term_years = int(property_data.get('loanTermYears', 30))
    
    # Calculate monthly mortgage payment (P&I only)
    monthly_rate = interest_rate / 12
    num_payments = loan_term_years * 12
    mortgage_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    annual_mortgage = mortgage_payment * 12
    
    # Calculate cash flow
    annual_cash_flow = noi - annual_mortgage
    monthly_cash_flow = annual_cash_flow / 12
    
    # Calculate cash-on-cash return
    cash_on_cash = (annual_cash_flow / total_investment) * 100 if total_investment > 0 else 0
    
    # Calculate gross rent multiplier (GRM)
    grm = sale_price / annual_rent if annual_rent > 0 else 0
    
    # Calculate price to rent ratio
    price_to_rent = sale_price / annual_rent if annual_rent > 0 else 0
    
    # Calculate 1% rule metric (monthly rent as percentage of purchase price)
    one_percent_rule = (monthly_rent / sale_price) * 100 if sale_price > 0 else 0
    meets_1_percent = one_percent_rule >= 1.0
    
    # Calculate debt service coverage ratio (DSCR)
    dscr = noi / annual_mortgage if annual_mortgage > 0 else 0
    
    # Calculate 5-year metrics
    appreciation_rate = 0.03  # 3% annual appreciation
    year_5_value = sale_price * (1 + appreciation_rate) ** 5
    year_5_equity = year_5_value - loan_amount
    
    # Return all metrics
    return {
        'cap_rate': round(cap_rate, 2),
        'cash_on_cash': round(cash_on_cash, 2),
        'monthly_cash_flow': round(monthly_cash_flow, 2),
        'annual_cash_flow': round(annual_cash_flow, 2),
        'noi': round(noi, 2),
        'grm': round(grm, 2),
        'price_to_rent_ratio': round(price_to_rent, 2),
        'one_percent_rule': round(one_percent_rule, 2),
        'meets_1_percent_rule': meets_1_percent,
        'dscr': round(dscr, 2),
        'total_investment': round(total_investment, 2),
        'monthly_mortgage': round(mortgage_payment, 2),
        'year_5_projected_value': round(year_5_value, 2),
        'year_5_projected_equity': round(year_5_equity, 2),
        'roi_grade': get_investment_grade(cap_rate, cash_on_cash, monthly_cash_flow, dscr)
    }

def get_investment_grade(cap_rate, cash_on_cash, monthly_cash_flow, dscr):
    """Determine an investment grade based on key metrics"""
    # Points system to grade investment quality
    points = 0
    
    # Cap rate scoring
    if cap_rate >= 8:
        points += 3
    elif cap_rate >= 6:
        points += 2
    elif cap_rate >= 4:
        points += 1
    
    # Cash-on-cash scoring
    if cash_on_cash >= 10:
        points += 3
    elif cash_on_cash >= 7:
        points += 2
    elif cash_on_cash >= 4:
        points += 1
    
    # Monthly cash flow scoring
    if monthly_cash_flow >= 500:
        points += 3
    elif monthly_cash_flow >= 200:
        points += 2
    elif monthly_cash_flow >= 0:
        points += 1
    
    # DSCR scoring
    if dscr >= 1.5:
        points += 3
    elif dscr >= 1.2:
        points += 2
    elif dscr >= 1.0:
        points += 1
    
    # Determine grade based on points
    if points >= 10:
        return "A+ (Excellent Investment)"
    elif points >= 8:
        return "A (Very Good Investment)"
    elif points >= 6:
        return "B (Good Investment)"
    elif points >= 4:
        return "C (Fair Investment)"
    elif points >= 2:
        return "D (Marginal Investment)"
    else:
        return "F (Poor Investment)" 
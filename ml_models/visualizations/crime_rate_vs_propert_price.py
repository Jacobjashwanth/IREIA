import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Load dataset
file_path = "data/boston_housing.csv"  # Adjust to your actual file path
df = pd.read_csv(file_path)

# Ensure required columns exist
required_columns = {'CRIM', 'MEDV', 'RM', 'TAX', 'PTRATIO'}
if not required_columns.issubset(df.columns):
    raise ValueError("Dataset must contain 'CRIM' (crime rate), 'MEDV' (median property price), 'RM' (property size), 'TAX' (tax rate), and 'PTRATIO' (school score proxy).")

# Convert data types to numeric (if needed)
df[['CRIM', 'MEDV', 'RM', 'TAX', 'PTRATIO']] = df[['CRIM', 'MEDV', 'RM', 'TAX', 'PTRATIO']].apply(pd.to_numeric, errors='coerce')

# Drop rows with missing values
df_cleaned = df.dropna()

# Scatter Plot: Crime Rate vs. Property Prices (Overall Trend)
plt.figure(figsize=(12, 6))
sns.scatterplot(data=df_cleaned, x='CRIM', y='MEDV', alpha=0.6)
sns.regplot(data=df_cleaned, x='CRIM', y='MEDV', scatter=False, color='red')  # Trend line
plt.xlabel("Crime Rate")
plt.ylabel("Median Property Price (USD)")
plt.title("Crime Rate vs. Property Prices")
plt.grid(True)
plt.show()

# Heatmap: Correlation Between Crime Rate, Property Prices & Additional Factors
plt.figure(figsize=(10, 6))
corr_matrix = df_cleaned[['CRIM', 'MEDV', 'RM', 'TAX', 'PTRATIO']].corr()
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
plt.title("Correlation Between Crime Rate & Property Prices")
plt.show()

# Boxplot: Property Prices Based on Crime Rate Categories
crime_bins = ['Low Crime', 'Medium Crime', 'High Crime']
df_cleaned['Crime Category'] = pd.qcut(df_cleaned['CRIM'], q=3, labels=crime_bins)
plt.figure(figsize=(12, 6))
sns.boxplot(data=df_cleaned, x='Crime Category', y='MEDV')
plt.xlabel("Crime Rate Category")
plt.ylabel("Median Property Price (USD)")
plt.title("Property Prices Across Different Crime Levels")
plt.grid(True)
plt.show()

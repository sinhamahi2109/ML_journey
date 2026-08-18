# King County House Price Prediction — Regression Analysis

Predicts house sale prices in King County, WA using property features (sqft, waterfront 
status, grade, location, etc.)

**Techniques:** Data cleaning, EDA, correlation analysis, Simple & Multiple Linear Regression, 
Feature Scaling & Polynomial Transformation, Ridge Regression

**Key finding:** sqft_above is positively correlated with price. Waterfront properties show 
a higher median price, though non-waterfront homes have a wider range of high-price outliers.

**Model performance (R²):**
- Simple Linear Regression (sqft_living only): 0.493
- Multiple Linear Regression (11 features): 0.658
- Scaled + Polynomial Pipeline: 0.751
- Ridge Regression (alpha=0.1): 0.648
- Ridge + Polynomial Features: 0.700

**Best model:** The scaled polynomial pipeline performed best (R² = 0.751), showing that 
feature scaling and non-linear transformation captured price patterns better than plain 
linear or ridge regression.

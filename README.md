# Insurance Charges Prediction — Linear & Ridge Regression

Predicts medical insurance charges using patient attributes (age, BMI, smoker status, etc.)

**Techniques:** Data cleaning, EDA, correlation analysis, Simple & Multiple Linear Regression, Ridge Regression, Polynomial Features

**Key finding:** Smoker status showed by far the strongest correlation with charges (0.79), 
much higher than BMI (0.20) or age (0.30).

**Model performance (R²):**
- Linear Regression (scaled + polynomial pipeline): 0.845
- Ridge Regression (alpha=0.1): 0.676
- Ridge Regression + Polynomial Features: 0.784

**Best model:** Linear Regression with polynomial features performed best, slightly outperforming 
Ridge — indicating regularization wasn't strictly necessary for this dataset size/feature count.

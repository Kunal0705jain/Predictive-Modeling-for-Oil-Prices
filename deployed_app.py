# -*- coding: utf-8 -*-
"""mani17.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1a3dA027jYCU2YWFzUHNb-ZCuvm2aUgg7
"""

import streamlit as st
import pandas as pd
import pickle
from prophet import Prophet
import joblib
import matplotlib.pyplot as plt

# Load the Prophet model from the pickle file
model_path = 'prophet_refitted_model.pkl'

@st.cache_resource
def load_model():
    try:
        with open(model_path, 'rb') as file:
            return joblib.load(file)
    except Exception as e:
        st.error(f"Error loading model with joblib: {e}")
        with open(model_path, 'rb') as file:
            return pickle.load(file)

prophet_model = load_model()

# Title of the app
st.title("30-Day Forecast Using Prophet Model")

# Predict the next 30 days
future = prophet_model.make_future_dataframe(periods=30)
forecast = prophet_model.predict(future)

# Display the forecast dataframe
st.subheader('Forecast Data for the Next 30 Days')
st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30))

# Add a date selector for the next 30 days
st.subheader('Select a Date to View Predicted Closing Value')

# Get the list of dates available for prediction
forecast_dates = forecast['ds'].dt.date

# Date picker only allows dates within the forecast range
selected_date = st.selectbox('Select a date', forecast_dates)

# Convert selected date to string format
selected_date_str = pd.to_datetime(selected_date).strftime('%Y-%m-%d')

# Filter the forecast dataframe for the selected date
selected_forecast = forecast[forecast['ds'].dt.date == selected_date]

# Display the closing value for the selected date
if not selected_forecast.empty:
    closing_value = selected_forecast['yhat'].values[0]
    lower_bound = selected_forecast['yhat_lower'].values[0]
    upper_bound = selected_forecast['yhat_upper'].values[0]

    st.write(f"### Predicted Closing Value on {selected_date_str}:")
    st.write(f"**Closing Value**: {closing_value:.2f}")
    st.write(f"**Prediction Interval**: [{lower_bound:.2f}, {upper_bound:.2f}]")

    # Get daily high/low for the selected day
    daily_high = selected_forecast['yhat_upper'].values[0]
    daily_low = selected_forecast['yhat_lower'].values[0]

    st.write(f"**Highest Predicted Closing on {selected_date_str}**: {daily_high:.2f}")
    st.write(f"**Lowest Predicted Closing on {selected_date_str}**: {daily_low:.2f}")

    # Get monthly high/low
    start_of_month = pd.to_datetime(selected_date).replace(day=1)
    end_of_month = start_of_month + pd.offsets.MonthEnd(1)

    # Ensure start_of_month and end_of_month are Timestamps for comparison
    monthly_forecast = forecast[(forecast['ds'] >= start_of_month) & (forecast['ds'] <= end_of_month)]
    monthly_high = monthly_forecast['yhat'].max()
    monthly_low = monthly_forecast['yhat'].min()

    st.write(f"**Highest Predicted Closing for the Month**: {monthly_high:.2f}")
    st.write(f"**Lowest Predicted Closing for the Month**: {monthly_low:.2f}")

    # Plot the closing values for the selected month
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_forecast['ds'], monthly_forecast['yhat'], label='Predicted Closing', color='blue')
    plt.axhline(monthly_high, color='red', linestyle='--', label='Monthly High')
    plt.axhline(monthly_low, color='green', linestyle='--', label='Monthly Low')
    plt.axvline(pd.to_datetime(selected_date), color='orange', linestyle=':', label='Selected Date')
    plt.title('Predicted Closing Values for the Month')
    plt.xlabel('Date')
    plt.ylabel('Closing Value')
    plt.xticks(rotation=45)
    plt.legend()

    # Save the current figure to display in Streamlit
    st.pyplot(plt)

    # Clear the current figure to avoid overlap in future plots
    plt.clf()

else:
    st.write(f"No prediction available for the selected date: {selected_date_str}")
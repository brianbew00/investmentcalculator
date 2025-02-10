import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the dataset
file_path = 'Compare Actual vs CAGR vs Average vs Geometric Mean.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

def calculate_portfolio(initial_investment, start_year, allocation_sp500, allocation_bond):
    start_index = df[df.iloc[:, 0] == start_year].index[0]
    
    # Extract relevant data
    years = df.iloc[start_index:, 0].dropna().values
    sp500_returns = df.iloc[start_index:, 1].dropna().values  # Use column B
    bond_returns = df.iloc[start_index:, 2].dropna().values  # Use column C
    
    # Blended returns calculation
    blended_returns = (sp500_returns * (allocation_sp500 / 100)) + (bond_returns * (allocation_bond / 100))
    
    # Compute actual portfolio values
    actual_values = [initial_investment]
    for r in blended_returns:
        actual_values.append(actual_values[-1] * (1 + r))
    actual_values = actual_values[1:]  # Remove initial investment
    
    # Compute average return
    average_return = blended_returns.mean()
    avg_values = [initial_investment]
    for _ in range(len(years)):
        avg_values.append(avg_values[-1] * (1 + average_return))
    avg_values = avg_values[1:]
    
    # Compute CAGR
    cagr_rate = (actual_values[-1] / initial_investment) ** (1 / len(years)) - 1
    cagr_values = [initial_investment]
    for _ in range(len(years)):
        cagr_values.append(cagr_values[-1] * (1 + cagr_rate))
    cagr_values = cagr_values[1:]
    
    return years, actual_values, avg_values, cagr_values, average_return, cagr_rate

# Streamlit UI
st.title("Investment Growth Calculator")

# User Inputs
initial_investment = st.number_input("Initial Investment Amount", min_value=1000, value=10000, step=1000, format='%d')
start_year = st.selectbox("Select Starting Year", df.iloc[2:, 0].dropna().unique())
allocation_sp500 = st.slider("% Allocation to S&P 500", min_value=0, max_value=100, value=90)
allocation_bond = 100 - allocation_sp500

col1, col2 = st.columns([1, 1])
with col1:
    st.write(f"S&P 500 Allocation: {allocation_sp500}%")
with col2:
    st.write(f"US T. Bond Allocation: {allocation_bond}%")

if st.button("Calculate Portfolio Growth"):
    years, actual_values, avg_values, cagr_values, average_return, cagr_rate = calculate_portfolio(initial_investment, start_year, allocation_sp500, allocation_bond)
    
    # Ensure all arrays are the same length
    min_length = min(len(years), len(actual_values), len(avg_values), len(cagr_values))
    years, actual_values, avg_values, cagr_values = (
        years[:min_length], actual_values[:min_length], avg_values[:min_length], cagr_values[:min_length]
    )
    
    # Format values as currency
    formatted_results = pd.DataFrame({
        "Year": years,
        "Actual Performance": [f"${v:,.0f}" for v in actual_values],
        "Average Return": [f"${v:,.0f}" for v in avg_values],
        "CAGR / Geometric Return": [f"${v:,.0f}" for v in cagr_values]
    })
    
    # Create summary table with corrected labels and no row indices
    summary_data = pd.DataFrame({
        "Metric": ["Average Portfolio", "CAGR Portfolio"],
        "Return": [f"{average_return:.2%}", f"{cagr_rate:.2%}"]
    }).reset_index(drop=True)
    
    # Display Summary Table
    st.subheader("Portfolio Summary")
    st.dataframe(summary_data, width=500)
    
    # Display Results Table
    st.subheader("Detailed Yearly Portfolio Growth")
    st.dataframe(formatted_results, width=1000)
    
    # Plot Growth Chart
    plt.figure(figsize=(10, 5))
    plt.plot(years, actual_values, marker='o', linestyle='-', label="Actual Portfolio")
    plt.plot(years, avg_values, marker='s', linestyle='--', label="Average Portfolio")
    plt.plot(years, cagr_values, marker='d', linestyle=':', label="CAGR Portfolio")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value ($)")
    plt.title("Investment Growth Over Time")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

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
    sp500_returns = df.iloc[start_index:, 1].dropna().values  # Column B
    bond_returns = df.iloc[start_index:, 2].dropna().values   # Column C
    
    # Calculate blended returns
    blended_returns = (sp500_returns * (allocation_sp500 / 100)) + (bond_returns * (allocation_bond / 100))
    
    # Debug: Show first 10 blended returns
    st.write("Blended Returns Debugging:", blended_returns[:10])
    
    # Create a column showing the formula breakdown (for debugging)
    formula_column = [
        f"({s:.2f} * {allocation_sp500 / 100:.2f}) + ({b:.2f} * {allocation_bond / 100:.2f}) = {br:.2f}"
        for s, b, br in zip(sp500_returns, bond_returns, blended_returns)
    ]
    
    # Compute the actual portfolio values (compounding the blended returns)
    actual_values = [initial_investment]
    for r in blended_returns:
        actual_values.append(actual_values[-1] * (1 + r))
    actual_values = actual_values[1:]
    
    # Compute the arithmetic average return and the corresponding portfolio values
    average_return = blended_returns.mean()
    avg_values = [initial_investment]
    for _ in range(len(years)):
        avg_values.append(avg_values[-1] * (1 + average_return))
    avg_values = avg_values[1:]
    
    # Compute the geometric mean return using logarithms (more numerically stable)
    try:
        geo_mean_return = np.exp(np.mean(np.log(1 + blended_returns))) - 1
    except ValueError:
        st.error("Error: One or more blended returns are less than -100%, so the geometric mean cannot be computed.")
        geo_mean_return = None
    # Compute the portfolio values based on the geometric mean return.
    # (This series will not be displayed per the instructions.)
    geo_values = [initial_investment]
    if geo_mean_return is not None:
        for _ in range(len(years)):
            geo_values.append(geo_values[-1] * (1 + geo_mean_return))
        geo_values = geo_values[1:]
    else:
        geo_values = [np.nan] * len(years)
    
    # Compute the CAGR (which is equivalent to the geometric mean in this context)
    cagr_rate = (actual_values[-1] / initial_investment) ** (1 / len(years)) - 1
    cagr_values = [initial_investment]
    for _ in range(len(years)):
        cagr_values.append(cagr_values[-1] * (1 + cagr_rate))
    cagr_values = cagr_values[1:]
    
    return years, actual_values, avg_values, geo_values, cagr_values, formula_column, average_return, geo_mean_return, cagr_rate

# Streamlit UI
st.title("Investment Growth Calculator")

# User inputs
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
    (years, actual_values, avg_values, geo_values, cagr_values, formula_column,
     average_return, geo_mean_return, cagr_rate) = calculate_portfolio(initial_investment, start_year, allocation_sp500, allocation_bond)
    
    # Ensure all arrays are the same length
    min_length = min(len(years), len(actual_values), len(avg_values), len(cagr_values), len(formula_column))
    years = years[:min_length]
    actual_values = actual_values[:min_length]
    avg_values = avg_values[:min_length]
    cagr_values = cagr_values[:min_length]
    formula_column = formula_column[:min_length]
    
    # Create a summary table with no index column and an added final value column.
    # We now include only the two rates (arithmetic and compounded) used in the display.
    summary_data = pd.DataFrame({
         "Metric": ["Average Rate", "Geometric Mean / CAGR Rate"],
         "Return": [f"{average_return:.2%}", f"{cagr_rate:.2%}"],
         "Final Value": [f"${avg_values[-1]:,.0f}", f"${cagr_values[-1]:,.0f}"]
    })
    
    st.subheader("Portfolio Summary")
    st.dataframe(summary_data.style.hide_index(), width=500)
    
    # Create the detailed yearly growth table (remove the geo_values series)
    formatted_results = pd.DataFrame({
         "Year": years,
         "Actual Performance": [f"${v:,.0f}" for v in actual_values],
         "Average Rate": [f"${v:,.0f}" for v in avg_values],
         "Geometric Mean / CAGR Rate": [f"${v:,.0f}" for v in cagr_values],
         "Blended Return Formula": formula_column
    })
    
    st.subheader("Detailed Yearly Portfolio Growth")
    st.dataframe(formatted_results, width=1000)
    
    # Plot the growth chart using only the three displayed series.
    plt.figure(figsize=(10, 5))
    plt.plot(years, actual_values, marker='o', linestyle='-', label="Actual Performance")
    plt.plot(years, avg_values, marker='s', linestyle='--', label="Average Rate")
    plt.plot(years, cagr_values, marker='d', linestyle=':', label="Geometric Mean / CAGR Rate")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value ($)")
    plt.title("Investment Growth Over Time")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

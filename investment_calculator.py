import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = '/mnt/data/Compare Actual vs CAGR vs Average vs Geometric Mean.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

def calculate_portfolio(initial_investment, start_year, allocation_sp500, allocation_bond, method):
    start_index = df[df.iloc[:, 0] == start_year].index[0]
    returns = df.iloc[start_index:, 6] / 100  # Extract return percentages and convert to decimal
    years = df.iloc[start_index:, 0]
    
    portfolio_values = [initial_investment]
    for r in returns:
        blended_return = (allocation_sp500 * r) + (allocation_bond * df.iloc[start_index, 2] / 100)
        new_value = portfolio_values[-1] * (1 + blended_return)
        portfolio_values.append(new_value)
    
    return years.values, portfolio_values[:-1]

# Streamlit UI
st.title("Investment Growth Calculator")

# User Inputs
initial_investment = st.number_input("Initial Investment Amount", min_value=1000, value=10000, step=1000)
start_year = st.selectbox("Select Starting Year", df.iloc[2:, 0].unique())
allocation_sp500 = st.slider("% Allocation to S&P 500", min_value=0, max_value=100, value=90)
allocation_bond = 100 - allocation_sp500

st.write(f"% Allocation to US T. Bond: {allocation_bond}%")

method = st.selectbox("Select Calculation Method", ["Actual Returns", "Average Returns", "Geometric Mean", "CAGR"])

if st.button("Calculate Portfolio Growth"):
    years, portfolio_values = calculate_portfolio(initial_investment, start_year, allocation_sp500 / 100, allocation_bond / 100, method)
    
    # Display Results Table
    results_df = pd.DataFrame({"Year": years, "Portfolio Value": portfolio_values})
    st.table(results_df)
    
    # Plot Growth Chart
    plt.figure(figsize=(10, 5))
    plt.plot(years, portfolio_values, marker='o', linestyle='-', label="Portfolio Value")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value ($)")
    plt.title("Investment Growth Over Time")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

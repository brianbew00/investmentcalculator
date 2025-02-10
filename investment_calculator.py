import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = 'Compare Actual vs CAGR vs Average vs Geometric Mean.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

def calculate_portfolio(initial_investment, start_year, allocation_sp500, allocation_bond):
    start_index = df[df.iloc[:, 0] == start_year].index[0]
    years = df.iloc[start_index:, 0]
    
    actual_returns = df.iloc[start_index:, 6] / 100
    avg_returns = df.iloc[start_index:, 14] / 100
    geo_mean_returns = df.iloc[start_index:, 17] / 100
    cagr_returns = df.iloc[start_index:, 12] / 100
    
    def compute_values(returns):
        values = [initial_investment]
        for r in returns:
            blended_return = (allocation_sp500 * r) + (allocation_bond * df.iloc[start_index, 2] / 100)
            new_value = values[-1] * (1 + blended_return)
            values.append(new_value)
        return values[:-1]
    
    return years.values, compute_values(actual_returns), compute_values(avg_returns), compute_values(geo_mean_returns), compute_values(cagr_returns)

# Streamlit UI
st.title("Investment Growth Calculator")

# User Inputs
initial_investment = st.number_input("Initial Investment Amount", min_value=1000, value=10000, step=1000, format='%d')
start_year = st.selectbox("Select Starting Year", df.iloc[2:, 0].unique())
allocation_sp500 = st.slider("% Allocation to S&P 500", min_value=0, max_value=100, value=90)
allocation_bond = 100 - allocation_sp500

col1, col2 = st.columns([1, 1])
with col1:
    st.write(f"S&P 500 Allocation: {allocation_sp500}%")
with col2:
    st.write(f"US T. Bond Allocation: {allocation_bond}%")

if st.button("Calculate Portfolio Growth"):
    years, actual_values, avg_values, geo_values, cagr_values = calculate_portfolio(initial_investment, start_year, allocation_sp500 / 100, allocation_bond / 100)
    
    # Format values as currency
    formatted_results = pd.DataFrame({
        "Year": years,
        "Actual Portfolio": [f"${v:,.0f}" for v in actual_values],
        "Average Portfolio": [f"${v:,.0f}" for v in avg_values],
        "Geometric Mean Portfolio": [f"${v:,.0f}" for v in geo_values],
        "CAGR Portfolio": [f"${v:,.0f}" for v in cagr_values]
    })
    
    # Display Results Table with adjusted column widths
    st.dataframe(
        formatted_results.style.set_table_attributes("style='display:inline'"),
        column_config={
            "Year": st.column_config.TextColumn(width='50px'),
            "Actual Portfolio": st.column_config.TextColumn(width='150px'),
            "Average Portfolio": st.column_config.TextColumn(width='150px'),
            "Geometric Mean Portfolio": st.column_config.TextColumn(width='150px'),
            "CAGR Portfolio": st.column_config.TextColumn(width='150px')
        }
    )
    
    # Plot Growth Chart
    plt.figure(figsize=(10, 5))
    plt.plot(years, actual_values, marker='o', linestyle='-', label="Actual Portfolio")
    plt.plot(years, avg_values, marker='s', linestyle='--', label="Average Portfolio")
    plt.plot(years, geo_values, marker='^', linestyle='-.', label="Geometric Mean Portfolio")
    plt.plot(years, cagr_values, marker='d', linestyle=':', label="CAGR Portfolio")
    plt.xlabel("Year")
    plt.ylabel("Portfolio Value ($)")
    plt.title("Investment Growth Over Time")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

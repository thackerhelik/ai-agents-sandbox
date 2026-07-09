import streamlit as st
from financial_analysis import run_financial_crew

# Set up the page title and layout
st.set_page_config(page_title="AI Trading Crew Dashboard", page_icon="📈", layout="centered")

st.title("📈 AI Multi-Agent Trading Dashboard")
st.caption("Empower your trading crew to analyze markets and build strategies.")

st.markdown("---")

# Create the input form components
st.subheader("Configure Strategy Parameters")

# Sidebar or main form inputs
ticker = st.text_input("Stock Ticker Symbol", value="AAPL", max_chars=20)

col1, col2 = st.columns(2)
with col1:
    currency = st.selectbox("Currency", ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)", "JPY (¥)"])
    capital = st.number_input("Initial Capital", min_value=100, value=10000, step=500)
with col2:
    risk = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])
    strategy = st.selectbox("Strategy Preference", ["Day Trading", "Swing Trading", "Long-term Investment"])

# Format the currency string (e.g., "€10000")
formatted_capital = f"{currency.split()[1].strip('()')}{capital}"

# Run Button
if st.button("🚀 Launch Trading Crew", use_container_width=True):
    
    # Build the dictionary exactly how CrewAI expects
    ui_inputs = {
        "stock_selection": ticker,
        "initial_capital": formatted_capital,
        "risk_tolerance": risk,
        "trading_strategy_preference": strategy,
        "news_impact_consideration": True
    }

    # Show a loading spinner while the AI thinks
    with st.spinner(f"Agents are analyzing {ticker} and browsing the live internet... This may take a couple of minutes."):

        # Fire the engine
        final_report = run_financial_crew(ui_inputs)

        # Display the results
        st.success("✅ Trading Crew has completed their analysis!")
        st.markdown("### Final Trading Report")
        st.markdown(final_report)

        # # Temporary placeholder mocking final markdown output
        # st.markdown(f"""
        # ### Final Trading Report Preview
        # * **Asset:** {ticker}
        # * **Allocated Funds:** {currency.split()[0]}{capital:,}
        # * **Risk Profile:** {risk}
        # * **Approach:** {strategy}
        # """)
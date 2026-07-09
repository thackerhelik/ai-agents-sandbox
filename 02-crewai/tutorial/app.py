import streamlit as st

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

# Run Button
if st.button("🚀 Launch Trading Crew", use_container_width=True):
    # This is where we hook up main() function later
    st.success(f"Crew completed execution for {ticker}! (CrewAI connection coming next step)")

    # Temporary placeholder mocking final markdown output
    st.markdown(f"""
    ### Final Trading Report Preview
    * **Asset:** {ticker}
    * **Allocated Funds:** {currency.split()[0]}{capital:,}
    * **Risk Profile:** {risk}
    * **Approach:** {strategy}
    """)
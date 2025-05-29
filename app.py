import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import requests
import re
from database import create_user_table, add_user, get_users, verify_user

# Email validation
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Coin list to display
COINS = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Cardano": "cardano",
    "Solana": "solana",
    "Dogecoin": "dogecoin",
    "Polkadot": "polkadot",
    "Avalanche": "avalanche-2",
    "XRP": "ripple",
    "Litecoin": "litecoin",
    "Binance Coin": "binancecoin",
    "Polygon": "matic-network",
    "Chainlink": "chainlink",
    "Uniswap": "uniswap",
    "Shiba Inu": "shiba-inu"
}

# CoinGecko API URL
def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return None

# Plot chart
def plot_chart(data, coin_name):
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["price"],
        mode="lines+markers",
        name="Price (USD)"
    ))
    fig.update_layout(title=f"{coin_name} Price Chart (Last 7 Days)", xaxis_title="Time", yaxis_title="Price (USD)")
    st.plotly_chart(fig, use_container_width=True)

def login_page():
    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not is_valid_email(email):
            st.error("❌ Please enter a valid email.")
        elif verify_user(email, password):
            st.success(f"✅ Logged in as {email}")
            st.session_state.logged_in = True
            st.session_state.user_email = email
        else:
            st.error("❌ Invalid email or password.")

def register_page():
    st.subheader("📝 Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if not is_valid_email(email):
            st.error("❌ Invalid email address.")
        elif email in get_users():
            st.warning("⚠️ Email already registered.")
        else:
            add_user(email, password)
            st.success("✅ Account created. Please login.")

def dashboard():
    st.title("📊 Live Crypto Dashboard")

    selected_coin = st.selectbox("Select Cryptocurrency", list(COINS.keys()))
    coin_id = COINS[selected_coin]

    data = get_coin_data(coin_id)

    if data:
        st.metric("Current Price (USD)", f"${data['prices'][-1][1]:,.2f}")
        st.metric("7-Day High", f"${max([p[1] for p in data['prices']]):,.2f}")
        st.metric("7-Day Low", f"${min([p[1] for p in data['prices']]):,.2f}")
        plot_chart(data, selected_coin)
    else:
        st.error("⚠️ Failed to fetch data from API.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

def main():
    st.set_page_config(page_title="Crypto Tracker", layout="wide")
    create_user_table()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = None

    if st.session_state.logged_in:
        dashboard()
    else:
        page = st.sidebar.radio("Select Page", ["Login", "Register"])
        if page == "Login":
            login_page()
        elif page == "Register":
            register_page()

if __name__ == "__main__":
    main()

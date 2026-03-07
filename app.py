import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

# --- PAGE SETUP ---
st.set_page_config(page_title="AroundU | Admin Dashboard", layout="wide")

# --- CUSTOM CSS (To Match your UI Screenshot) ---
st.markdown("""
    <style>
    /* Main background */
    .main { background-color: #F8FAFC; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        color: white;
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* Metrics Card Styling */
    div[data-testid="stMetric"] {
        background-color: white;
        border-left: 5px solid #2563EB;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Chart Container */
    .plot-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Navigation Selected State */
    .nav-link-selected {
        background-color: #2563EB !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK ADMIN DATA ---
@st.cache_data
def load_admin_data():
    dates = pd.date_range(start="2023-01-01", periods=365, freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'New_Users': np.random.randint(20, 100, size=365),
        'Total_Places': np.random.randint(800, 1200, size=365),
        'Visits': np.random.randint(1000, 5000, size=365),
        'Saves': np.random.randint(100, 500, size=365),
        'Directions': np.random.randint(200, 800, size=365),
        'Calls': np.random.randint(50, 300, size=365),
        'Bot_Success': np.random.uniform(75, 95, size=365),
        'Reviews': np.random.randint(50, 200, size=365)
    })
    return data

df_raw = load_admin_data()

# =========================
# SIDEBAR (Exact Match to UI)
# =========================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3177/3177440.png", width=50) # Logo placeholder
    st.title("AroundU")
    st.caption("Beni Suef Platform Intelligence")
    st.markdown("<br>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Places Analytics", "User Analytics", "Reviews & Bot", "Moderation Center"],
        icons=['speedometer2', 'shop', 'people', 'chat-left-text', 'shield-check'],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"background-color": "transparent"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"5px"},
            "nav-link-selected": {"background-color": "#2563EB"},
        }
    )

    st.markdown("---")
    st.write("Logged in as: **Admin (Beni Suef)**")

    st.markdown("### 📅 Select Date Range")
    date_range = st.date_input(
        "Choose period:",
        value=(datetime.now() - timedelta(days=30), datetime.now())
    )

# --- FILTER LOGIC ---
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df_raw[(df_raw['Date'] >= start_date) & (df_raw['Date'] <= end_date)]
    # Previous period for Deltas
    period_days = (end_date - start_date).days + 1
    prev_df = df_raw[(df_raw['Date'] >= start_date - timedelta(days=period_days)) & (df_raw['Date'] < start_date)]
else:
    st.stop()

# =========================
# 1️⃣ MAIN DASHBOARD
# =========================
if selected == "Dashboard":
    st.title("📊 Platform Performance Overview")
    
    # --- Metrics Row ---
    m1, m2, m3, m4 = st.columns(4)
    
    def delta(col):
        curr, prev = filtered_df[col].sum(), prev_df[col].sum()
        if prev == 0: return "0%"
        return f"{int(((curr - prev) / prev) * 100)}%"

    m1.metric("Total Platform Visits", f"{filtered_df['Visits'].sum():,}", delta('Visits'))
    m2.metric("Total User Saves", f"{filtered_df['Saves'].sum():,}", delta('Saves'))
    m3.metric("Direction Clicks", f"{filtered_df['Directions'].sum():,}", delta('Directions'))
    m4.metric("Total Reviews", f"{filtered_df['Reviews'].sum():,}", delta('Reviews'))

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Charts Row ---
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🚀 Platform Growth Analysis")
        # Comparison logic
        metrics = ['Visits', 'Saves', 'Directions', 'Calls']
        growth_data = pd.DataFrame({
            'Metric': metrics * 2,
            'Value': [filtered_df[m].sum() for m in metrics] + [prev_df[m].sum() for m in metrics],
            'Period': ['Selected Period']*4 + ['Previous Period']*4
        })
        fig_growth = px.bar(growth_data, x='Metric', y='Value', color='Period', barmode='group',
                             color_discrete_map={'Selected Period': '#1E3A8A', 'Previous Period': '#93C5FD'})
        st.plotly_chart(fig_growth, use_container_width=True)

    with col_right:
        st.subheader("🤖 Bot Resolution")
        st.metric("Avg Resolution Rate", f"{filtered_df['Bot_Success'].mean():.1f}%")
        query_types = pd.DataFrame({'Type': ['Menu', 'Hours', 'Location', 'Pricing'], 'Val': [45, 25, 20, 10]})
        fig_pie = px.pie(query_types, values='Val', names='Type', hole=0.6, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_pie, use_container_width=True)

# =========================
# 2️⃣ PLACES ANALYTICS
# =========================
elif selected == "Places Analytics":
    st.title("🏘️ Places & Category Analytics")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Places per Category")
        cat_data = pd.DataFrame({'Category': ['Restaurants', 'Cafes', 'Pharmacies', 'Houses'], 'Count': [450, 320, 120, 600]})
        fig_cat = px.bar(cat_data, x='Count', y='Category', orientation='h', color='Count')
        st.plotly_chart(fig_cat, use_container_width=True)
    with c2:
        st.subheader("Recently Added Places")
        recent_places = pd.DataFrame({
            'Name': ['Beni Suef Grand Cafe', 'Nile View Pharmacy', 'El-Zohour House'],
            'Date Added': ['2024-03-01', '2024-03-03', '2024-03-05'],
            'Status': ['Active', 'Pending', 'Active']
        })
        st.table(recent_places)

# =========================
# 3️⃣ USER ANALYTICS & LOCATION
# =========================
elif selected == "User Analytics":
    st.title("📍 User & Location Logic")
    st.subheader("User Activity Heatmap: Beni Suef")
    # Coordinates for Beni Suef
    BS_LAT, BS_LON = 29.0661, 31.0994
    map_data = pd.DataFrame({
        'lat': np.random.uniform(BS_LAT - 0.01, BS_LAT + 0.01, size=100),
        'lon': np.random.uniform(BS_LON - 0.01, BS_LON + 0.01, size=100)
    })
    st.map(map_data)
    
    st.subheader("New Signups Trend")
    fig_users = px.line(filtered_df, x='Date', y='New_Users', title="New Registered Users per Day")
    st.plotly_chart(fig_users, use_container_width=True)

# =========================
# 4️⃣ MODERATION CENTER
# =========================
elif selected == "Moderation Center":
    st.title("🛡️ Admin Moderation Center")
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.subheader("New Owners Pending Approval")
        pending = pd.DataFrame({
            'Owner Name': ['Ahmed Aly', 'Sara Hassan', 'Mido Zaki'],
            'Business': ['Downtown Grill', 'HealthFirst Pharmacy', 'Moonlight Cafe'],
            'Requested': ['2 hrs ago', '5 hrs ago', '1 day ago']
        })
        st.dataframe(pending, use_container_width=True)
    
    with col_v2:
        st.subheader("Suspended Users / Places")
        st.error("Currently 12 users and 5 places are suspended for policy violations.")
        if st.button("View Audit Log"):
            st.info("Log: Admin deleted Review #8420 at 10:45 AM today.")
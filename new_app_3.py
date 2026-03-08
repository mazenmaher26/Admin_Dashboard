import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

# --- PAGE SETUP ---
st.set_page_config(page_title="AroundU | Admin Panel", layout="wide")

# --- UI CUSTOMIZATION (MATCHING YOUR UI SCREENSHOT) ---
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #1E293B !important; min-width: 280px; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Metric Cards with Blue Accents */
    div[data-testid="stMetric"] {
        background-color: white;
        border-left: 5px solid #2563EB;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Plotly Chart Containers */
    .plot-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA GENERATOR ---
@st.cache_data
def get_admin_data():
    dates = pd.date_range(start="2023-01-01", end="2024-03-01", freq='D')
    
    # Platform-wide Time Series
    df_ts = pd.DataFrame({
        'Date': dates,
        'Visits': np.random.randint(1000, 5000, size=len(dates)),
        'New_Users': np.random.randint(20, 100, size=len(dates)),
        'Saves': np.random.randint(50, 300, size=len(dates)),
        'Directions': np.random.randint(100, 600, size=len(dates)),
        'Calls': np.random.randint(30, 150, size=len(dates)),
        'Reviews': np.random.randint(10, 80, size=len(dates)),
        'Bot_Resolved': np.random.randint(70, 95, size=len(dates))
    })

    # Places Data
    cats = ['Restaurant', 'Cafe', 'Pharmacy', 'House', 'Super Market']
    df_places = pd.DataFrame({
        'Name': [f"Place {i}" for i in range(200)],
        'Category': np.random.choice(cats, 200),
        'Status': np.random.choice(['Active', 'Suspended'], p=[0.9, 0.1], size=200),
        'District': np.random.choice(['City Center', 'University', 'Nile Corniche'], 200)
    })
    
    return df_ts, df_places

df_ts, df_places = get_admin_data()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("🏙️ AroundU")
    st.caption("Admin Platform Intelligence")
    
    selected = option_menu(
        menu_title=None,
        options=["Overview", "Places Analytics", "User Analytics", "Reviews", "Chatbot", "Moderation", "Location Logic"],
        icons=['grid-1x2', 'shop', 'people', 'star', 'robot', 'shield-lock', 'geo-alt'],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2563EB"}}
    )
    
    st.divider()
    st.markdown("### 📅 Global Time Filter")
    date_range = st.date_input("Select Period:", value=(datetime(2024,1,1), datetime(2024,1,30)))

# Filtering Logic
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df_ts[(df_ts['Date'] >= start) & (df_ts['Date'] <= end)]
    
    # Previous period for Deltas
    period_days = (end - start).days + 1
    df_prev = df_ts[(df_ts['Date'] >= start - timedelta(days=period_days)) & (df_ts['Date'] < start)]
else:
    st.stop()

# =========================
# 1. PLATFORM OVERVIEW
# =========================
if selected == "Overview":
    st.title("📊 Platform Performance Overview")
    
    # --- ROW 1: KPI CARDS ---
    def delta(col):
        curr, prev = df_filtered[col].sum(), df_prev[col].sum()
        if prev == 0: return "0%"
        return f"{int(((curr - prev)/prev)*100)}%"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Platform Visits", f"{df_filtered['Visits'].sum():,}", delta('Visits'))
    k2.metric("New Registered Users", f"{df_filtered['New_Users'].sum():,}", delta('New_Users'))
    k3.metric("Total Saved Places", f"{df_filtered['Saves'].sum():,}", delta('Saves'))
    k4.metric("Direction Clicks", f"{df_filtered['Directions'].sum():,}", delta('Directions'))

    # --- ROW 2: KPI CARDS ---
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Call Button Clicks", f"{df_filtered['Calls'].sum():,}", delta('Calls'))
    k6.metric("Total Reviews", f"{df_filtered['Reviews'].sum():,}", delta('Reviews'))
    k7.metric("Active Places", len(df_places[df_places['Status']=='Active']))
    k8.metric("Bot Resolution Rate", f"{df_filtered['Bot_Resolved'].mean():.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROW 3: HEATMAP & GROWTH ---
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("⏰ Platform Visiting Hours (Heatmap)")
        # Mocking 7x24 heatmap data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = [f"{i}:00" for i in range(24)]
        # Generate data where evening hours are "hotter"
        base_heat = np.random.randint(10, 50, size=(7, 24))
        base_heat[:, 17:22] += 50  # Evening rush
        
        fig_heat = px.imshow(base_heat, x=hours, y=days, 
                             color_continuous_scale='Blues', aspect="auto",
                             labels=dict(x="Hour of Day", y="Day of Week", color="User Activity"))
        fig_heat.update_xaxes(side="top")
        st.plotly_chart(fig_heat, use_container_width=True)
        st.info("💡 Insight: Platform activity peaks in Beni Suef between 6:00 PM and 10:00 PM daily.")

    with col_b:
        st.subheader("🛡️ Platform Content Status")
        fig_status = px.pie(df_places, names='Status', hole=0.6,
                            color_discrete_map={'Active': '#10B981', 'Suspended': '#EF4444'})
        fig_status.update_layout(showlegend=False)
        st.plotly_chart(fig_status, use_container_width=True)
        
        st.subheader("📈 Category Distribution")
        cat_counts = df_places['Category'].value_counts().reset_index()
        st.plotly_chart(px.bar(cat_counts, x='count', y='Category', orientation='h', color_discrete_sequence=['#2563EB']), use_container_width=True)

# =========================
# REMAINING SECTIONS (PREVIOUS LOGIC PRESERVED)
# =========================
elif selected == "Places Analytics":
    st.title("🏘️ Places Analytics")
    st.plotly_chart(px.bar(df_places.groupby('Category').size().reset_index(name='count'), x='Category', y='count'))

elif selected == "User Analytics":
    st.title("👥 User Analytics")
    st.area_chart(df_filtered.set_index('Date')['New_Users'])

elif selected == "Reviews":
    st.title("⭐ Reviews Analytics")
    st.metric("Avg Rating", "4.2 / 5.0")

elif selected == "Chatbot":
    st.title("🤖 Chatbot Analytics")
    st.plotly_chart(px.line(df_filtered, x='Date', y='Bot_Resolved'))

elif selected == "Moderation":
    st.title("🛡️ Moderation Center")
    st.table(pd.DataFrame({'Admin': ['Admin_01'], 'Action': ['Approved Place #42'], 'Time': ['2 hrs ago']}))

elif selected == "Location Logic":
    st.title("📍 Location Analytics")
    BS_LAT, BS_LON = 29.0661, 31.0994
    st.map(pd.DataFrame({'lat': np.random.uniform(BS_LAT-0.01, BS_LAT+0.01, 50), 'lon': np.random.uniform(BS_LON-0.01, BS_LON+0.01, 50)}))
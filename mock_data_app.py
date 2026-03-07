import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

# --- PAGE SETUP ---
st.set_page_config(page_title="AroundU | Admin Dashboard", layout="wide")

# --- CUSTOM CSS (Matching your UI Screenshot) ---
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        min-width: 260px;
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* Metrics Card Styling */
    div[data-testid="stMetric"] {
        background-color: white;
        border-left: 5px solid #2563EB;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Chart Containers */
    .plot-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }

    /* Titles */
    h1, h2, h3 { color: #1E293B; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA GENERATOR ---
@st.cache_data
def generate_mock_data():
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", end="2024-03-01", freq='D')
    
    # Platform-wide Time Series Data
    df = pd.DataFrame({
        'Date': dates,
        'New_Users': np.random.randint(10, 80, size=len(dates)),
        'New_Owners': np.random.randint(1, 10, size=len(dates)),
        'Visits': np.random.randint(1000, 4500, size=len(dates)),
        'Saves': np.random.randint(200, 600, size=len(dates)),
        'Directions': np.random.randint(150, 700, size=len(dates)),
        'Calls': np.random.randint(40, 250, size=len(dates)),
        'Bot_Success_Rate': np.random.uniform(70, 96, size=len(dates)),
        'Reviews_Count': np.random.randint(20, 150, size=len(dates)),
        'Sentiment_Pos': np.random.randint(60, 90, size=len(dates)) # Percentage
    })

    # Places Data
    categories = ['Restaurant', 'Cafe', 'Pharmacy', 'House']
    districts = ['City Center', 'University Area', 'Nile Corniche', 'New Beni Suef', 'El Wasta']
    
    places_list = []
    for i in range(100):
        places_list.append({
            'Place_ID': f"P-{1000+i}",
            'Name': f"Business {i}",
            'Category': np.random.choice(categories),
            'District': np.random.choice(districts),
            'Rating': np.random.uniform(3.0, 5.0),
            'Visits': np.random.randint(500, 10000),
            'Saves': np.random.randint(50, 2000),
            'Status': np.random.choice(['Active', 'Pending', 'Suspended'], p=[0.8, 0.1, 0.1]),
            'Created_At': np.random.choice(dates)
        })
    df_places = pd.DataFrame(places_list)
    
    return df, df_places

df_raw, df_places = generate_mock_data()

# =========================
# SIDEBAR NAVIGATION
# =========================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3177/3177440.png", width=60)
    st.title("AroundU")
    st.caption("Beni Suef Admin Intelligence")
    st.markdown("<br>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Places Analytics", "User & Location", "Reviews & Bot", "Moderation"],
        icons=['speedometer2', 'shop', 'people', 'chat-left-text', 'shield-lock'],
        default_index=0,
        styles={
            "container": {"background-color": "transparent"},
            "nav-link": {"font-size": "14px", "text-align": "left", "color": "white"},
            "nav-link-selected": {"background-color": "#2563EB"},
        }
    )

    st.divider()
    
    # Date Filtering (Identical to your UI)
    st.markdown("### 📅 Select Date Range")
    date_range = st.date_input(
        "Choose period:",
        value=(datetime(2024, 1, 23), datetime(2024, 1, 30))
    )

# --- FILTER LOGIC ---
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df_raw[(df_raw['Date'] >= start_date) & (df_raw['Date'] <= end_date)]
    period_days = (end_date - start_date).days + 1
    prev_df = df_raw[(df_raw['Date'] >= start_date - timedelta(days=period_days)) & (df_raw['Date'] < start_date)]
else:
    st.stop()

# =========================
# 1️⃣ DASHBOARD (Overview)
# =========================
if selected == "Dashboard":
    st.markdown(f"<h1>📊 Platform Overview: {date_range[0]} - {date_range[1]}</h1>", unsafe_allow_html=True)
    
    # --- Metrics Row ---
    m1, m2, m3, m4 = st.columns(4)
    
    def get_delta(col):
        curr, prev = filtered_df[col].sum(), prev_df[col].sum()
        if prev == 0: return "0%"
        return f"{int(((curr - prev) / prev) * 100)}%"

    m1.metric("Total Platform Visits", f"{filtered_df['Visits'].sum():,}", get_delta('Visits'))
    m2.metric("Total User Saves", f"{filtered_df['Saves'].sum():,}", get_delta('Saves'))
    m3.metric("Direction Clicks", f"{filtered_df['Directions'].sum():,}", get_delta('Directions'))
    m4.metric("Total Reviews", f"{filtered_df['Reviews_Count'].sum():,}", get_delta('Reviews_Count'))

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Growth & Bot ---
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.subheader("🚀 Platform Growth Analysis")
        metrics = ['Visits', 'Saves', 'Directions', 'Calls']
        comp_df = pd.DataFrame({
            'Metric': metrics * 2,
            'Count': [filtered_df[m].sum() for m in metrics] + [prev_df[m].sum() for m in metrics],
            'Period': ['Selected Period']*4 + ['Previous Period']*4
        })
        fig = px.bar(comp_df, x='Metric', y='Count', color='Period', barmode='group',
                     color_discrete_map={'Selected Period': '#1E3A8A', 'Previous Period': '#93C5FD'},
                     template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("🤖 Chatbot Stats")
        st.metric("Bot Resolution Rate", f"{filtered_df['Bot_Success_Rate'].mean():.1f}%")
        q_types = pd.DataFrame({'Type': ['Menu', 'Hours', 'Location', 'Pricing'], 'Val': [40, 30, 20, 10]})
        fig_p = px.pie(q_types, values='Val', names='Type', hole=0.6, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_p, use_container_width=True)

# =========================
# 2️⃣ PLACES ANALYTICS
# =========================
elif selected == "Places Analytics":
    st.title("🏘️ Places & Category Analytics")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Total Places per Category")
        fig_cat = px.bar(df_places['Category'].value_counts().reset_index(), 
                         x='count', y='Category', orientation='h', color='Category')
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with c2:
        st.subheader("Top Rated Places (Beni Suef)")
        top_rated = df_places.sort_values('Rating', ascending=False).head(5)[['Name', 'Category', 'Rating']]
        st.table(top_rated)

    st.divider()
    st.subheader("Category Growth Over Time")
    # Simulation of growth
    growth_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'Restaurants': [10, 15, 22, 28, 35],
        'Houses': [5, 12, 18, 25, 45]
    })
    st.line_chart(growth_data.set_index('Month'))

# =========================
# 3️⃣ USER & LOCATION
# =========================
elif selected == "User & Location":
    st.title("📍 User Analytics & Location Logic")
    
    u1, u2 = st.columns([1, 2])
    with u1:
        st.metric("New Users (Selected Period)", filtered_df['New_Users'].sum())
        st.metric("Total Owners on Platform", df_places['Place_ID'].nunique())
        st.info("Most Active District: **University Area**")
        
    with u2:
        st.subheader("User Activity Heatmap (Beni Suef)")
        BS_LAT, BS_LON = 29.0661, 31.0994
        map_df = pd.DataFrame({
            'lat': np.random.uniform(BS_LAT - 0.015, BS_LAT + 0.015, size=150),
            'lon': np.random.uniform(BS_LON - 0.015, BS_LON + 0.015, size=150),
            'weight': np.random.randint(1, 10, 150)
        })
        fig_map = px.density_mapbox(map_df, lat='lat', lon='lon', z='weight', radius=20,
                                    center=dict(lat=BS_LAT, lon=BS_LON), zoom=12,
                                    mapbox_style="open-street-map", height=500)
        st.plotly_chart(fig_map, use_container_width=True)

# =========================
# 4️⃣ REVIEWS & BOT
# =========================
elif selected == "Reviews & Bot":
    st.title("💬 Sentiment & Chatbot Intelligence")
    
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("Sentiment Analysis (NLP)")
        avg_pos = filtered_df['Sentiment_Pos'].mean()
        fig_sent = px.pie(values=[avg_pos, 100-avg_pos], names=['Positive', 'Negative'], 
                          color_discrete_sequence=['#10B981', '#EF4444'], hole=0.5)
        st.plotly_chart(fig_sent, use_container_width=True)
        
    with r2:
        st.subheader("Unresolved Bot Queries")
        st.warning(f"There are {np.random.randint(5, 25)} unresolved queries from the last 24 hours.")
        unresolved = pd.DataFrame({
            'User_Query': ["Do you have vegan pizza?", "Is the pharmacy open now?", "House price in New BS?"],
            'Time': ["10:15 AM", "11:30 AM", "01:05 PM"]
        })
        st.table(unresolved)

# =========================
# 5️⃣ MODERATION
# =========================
elif selected == "Moderation":
    st.title("🛡️ Platform Moderation Center")
    
    t1, t2 = st.tabs(["Pending Approvals", "Audit Log & Suspensions"])
    
    with t1:
        st.subheader("Owners Awaiting Verification")
        pending = df_places[df_places['Status'] == 'Pending'][['Name', 'Category', 'Created_At']].head(5)
        st.dataframe(pending, use_container_width=True)
        if st.button("Approve Selected"):
            st.success("Selected places have been made live.")

    with t2:
        st.subheader("Recent Admin Actions")
        actions = pd.DataFrame({
            'Admin': ['Admin_01', 'Admin_01', 'SuperAdmin'],
            'Action': ['Suspended Place P-1022', 'Banned User U-992', 'Created Category: Pharmacy'],
            'Time': ['10 mins ago', '2 hrs ago', 'Yesterday']
        })
        st.table(actions)
        st.error(f"Total Suspended Places: {len(df_places[df_places['Status'] == 'Suspended'])}")
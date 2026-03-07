import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

# --- PAGE SETUP ---
st.set_page_config(page_title="AroundU | Admin Panel", layout="wide")

# --- UI CUSTOMIZATION (MATCHING OWNER DASHBOARD UI) ---
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #1E293B !important; min-width: 280px; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Blue-Accent Metric Cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border-left: 5px solid #2563EB;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* White Plot Containers */
    .plot-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- COMPREHENSIVE MOCK DATA GENERATOR ---
@st.cache_data
def get_all_admin_data():
    dates = pd.date_range(start="2023-01-01", end="2024-03-01", freq='D')
    
    # Platform Over Time
    df_ts = pd.DataFrame({
        'Date': dates,
        'Signups': np.random.randint(5, 50, size=len(dates)),
        'Visits': np.random.randint(1000, 5000, size=len(dates)),
        'Reviews': np.random.randint(10, 100, size=len(dates)),
        'Chats': np.random.randint(50, 300, size=len(dates)),
        'Directions': np.random.randint(20, 200, size=len(dates))
    })

    # Places / Categories
    cats = ['Restaurant', 'Cafe', 'Pharmacy', 'House', 'Super Market']
    districts = ['City Center', 'University', 'Nile Corniche', 'New Beni Suef', 'El Wasta']
    
    places = []
    for i in range(200):
        places.append({
            'Name': f"Place {i}",
            'Category': np.random.choice(cats),
            'District': np.random.choice(districts),
            'Visits': np.random.randint(100, 5000),
            'Saves': np.random.randint(10, 1000),
            'Rating': np.random.uniform(1.5, 5.0),
            'Status': np.random.choice(['Active', 'Suspended', 'Pending'], p=[0.85, 0.05, 0.1]),
            'Bot_Resolved': np.random.choice([True, False], p=[0.8, 0.2]),
            'Date_Added': np.random.choice(dates)
        })
    df_places = pd.DataFrame(places)
    
    return df_ts, df_places

df_ts, df_places = get_all_admin_data()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("🏙️ AroundU")
    st.caption("Beni Suef Admin Intelligence")
    
    selected = option_menu(
        menu_title=None,
        options=["Overview", "Places Analytics", "User Analytics", "Reviews", "Chatbot", "Category Logic", "Moderation", "Location Logic"],
        icons=['grid-1x2', 'shop', 'people', 'star', 'robot', 'list-task', 'shield-lock', 'geo-alt'],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2563EB"}}
    )
    
    st.divider()
    st.markdown("### 📅 Time Period Filter")
    date_range = st.date_input("Filter results:", value=(datetime(2024,1,1), datetime(2024,1,30)))

# Filter Logic
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask = (df_ts['Date'] >= start) & (df_ts['Date'] <= end)
    df_filtered = df_ts.loc[mask]
    
    period_days = (end - start).days + 1
    prev_mask = (df_ts['Date'] >= start - timedelta(days=period_days)) & (df_ts['Date'] < start)
    df_prev = df_ts.loc[prev_mask]
else:
    st.stop()

# =========================
# 1. PLATFORM OVERVIEW
# =========================
if selected == "Overview":
    st.title("📊 Platform Overview")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Places", len(df_places))
    k2.metric("Total Users", 12540)
    k3.metric("Total Owners", 184)
    k4.metric("Total Reviews", df_ts['Reviews'].sum())
    
    k5, k6, k7, k8 = st.columns(4)
    new_signups = df_filtered['Signups'].sum()
    k5.metric("New Signups", new_signups, f"{int(((new_signups - df_prev['Signups'].sum())/max(1,df_prev['Signups'].sum()))*100)}%")
    k6.metric("Active Places", len(df_places[df_places['Status'] == 'Active']))
    k7.metric("Suspended Places", len(df_places[df_places['Status'] == 'Suspended']))
    k8.metric("Total Categories", df_places['Category'].nunique())

# =========================
# 2. PLACES ANALYTICS
# =========================
elif selected == "Places Analytics":
    st.title("🏘️ Places Analytics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Places per Category")
        fig = px.pie(df_places, names='Category', hole=0.5)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Lowest Rated Places (Needs Attention)")
        st.dataframe(df_places.sort_values('Rating').head(5)[['Name', 'Rating', 'Category']])

    with col2:
        st.subheader("Most Visited Places")
        st.bar_chart(df_places.nlargest(5, 'Visits').set_index('Name')['Visits'])
        
        st.subheader("Pending Approvals")
        st.warning(f"There are {len(df_places[df_places['Status']=='Pending'])} places waiting for review.")

# =========================
# 3. USER ANALYTICS
# =========================
elif selected == "User Analytics":
    st.title("👥 User Analytics")
    st.subheader("Total Users Over Time")
    st.line_chart(df_ts.set_index('Date')['Signups'].cumsum())
    
    c1, c2 = st.columns(2)
    c1.metric("Suspended Users", 42)
    c1.metric("Banned Users", 12)
    c2.subheader("Users by Location (Heatmap Focus)")
    st.info("User concentration is highest in Beni Suef City Center (64%).")

# =========================
# 4. REVIEWS ANALYTICS
# =========================
elif selected == "Reviews":
    st.title("⭐ Reviews Analytics")
    r1, r2, r3 = st.columns(3)
    r1.metric("Positive vs Negative", "82% Positive")
    r2.metric("Review Growth Rate", "+12%")
    r3.metric("Flagged Reviews", 14)
    
    st.subheader("Average Rating per Category")
    avg_rate = df_places.groupby('Category')['Rating'].mean().reset_index()
    st.plotly_chart(px.bar(avg_rate, x='Category', y='Rating', color='Rating'))

# =========================
# 5. CHATBOT ANALYTICS
# =========================
elif selected == "Chatbot":
    st.title("🤖 Chatbot Analytics")
    ch1, ch2, ch3 = st.columns(3)
    ch1.metric("Total Chat Sessions", df_filtered['Chats'].sum())
    ch2.metric("Avg Resolution Rate", "84.2%")
    ch3.metric("Unresolved Queries", 28)
    
    st.subheader("Most Common Query Types")
    q_data = pd.DataFrame({'Type': ['Menu', 'Hours', 'Location', 'Pricing', 'Other'], 'Val': [45, 20, 15, 12, 8]})
    st.plotly_chart(px.pie(q_data, values='Val', names='Type', hole=0.4))

# =========================
# 6. CATEGORY LOGIC
# =========================
elif selected == "Category Logic":
    st.title("📑 Category Growth & Popularity")
    st.subheader("Most Popular Category (By Visits)")
    pop_cat = df_places.groupby('Category')['Visits'].sum().sort_values(ascending=False)
    st.bar_chart(pop_cat)
    
    st.subheader("Least Active Category")
    st.error(f"Least Active: {pop_cat.index[-1]} (Requires Marketing)")

# =========================
# 7. MODERATION CENTER
# =========================
elif selected == "Moderation":
    st.title("🛡️ Moderation Center")
    tab1, tab2 = st.tabs(["Admin Action History", "Pending Owners"])
    with tab1:
        st.table(pd.DataFrame({
            'Admin': ['Admin_1', 'Super_Admin', 'Admin_1'],
            'Action': ['Deleted Review #442', 'Suspended Place: Cafe Nile', 'Approved Owner: Sara'],
            'Timestamp': ['2024-03-01 10:00', '2024-03-01 11:30', '2024-03-01 12:45']
        }))
    with tab2:
        st.info("Verification Queue: 3 New Owners waiting for license approval.")

# =========================
# 8. LOCATION ANALYTICS
# =========================
elif selected == "Location Logic":
    st.title("📍 Location Intelligence (Beni Suef)")
    
    # Coordinates
    BS_LAT, BS_LON = 29.0661, 31.0994
    
    st.subheader("User Activity Heatmap")
    map_data = pd.DataFrame({
        'lat': np.random.uniform(BS_LAT-0.01, BS_LAT+0.01, 100),
        'lon': np.random.uniform(BS_LON-0.01, BS_LON+0.01, 100)
    })
    st.map(map_data)
    
    st.divider()
    
    cl1, cl2 = st.columns(2)
    with cl1:
        st.subheader("Direction Clicks Heatmap")
        st.info("Highest navigation requests are targeting the 'Nile Corniche' restaurants.")
    with cl2:
        st.subheader("Opportunity Map (No Competition)")
        st.success("Opportunity Found: 'New Beni Suef' lacks Pharmacies.")
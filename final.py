import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

# --- PAGE SETUP ---
st.set_page_config(page_title="AroundU | Admin Dashboard", layout="wide")

# --- UI CUSTOMIZATION (EXACT MATCH TO YOUR UI SCREENSHOT) ---
st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #F8FAFC; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        min-width: 280px !important;
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* Metric Cards with Blue Accents (Matching Screenshot) */
    div[data-testid="stMetric"] {
        background-color: white;
        border-left: 5px solid #2563EB;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* White Chart Containers */
    .plot-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 25px;
    }

    /* Target headers */
    h1, h2, h3 { color: #1E293B; font-family: 'Inter', sans-serif; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- ADVANCED MOCK DATA ENGINE ---
@st.cache_data
def load_all_platform_data():
    dates = pd.date_range(start="2023-01-01", end="2024-03-01", freq='D')
    
    # Platform-wide Time Series
    df_ts = pd.DataFrame({
        'Date': dates,
        'Visits': np.random.randint(2000, 8000, size=len(dates)),
        'New_Users': np.random.randint(30, 150, size=len(dates)),
        'New_Owners': np.random.randint(1, 8, size=len(dates)),
        'Saves': np.random.randint(100, 500, size=len(dates)),
        'Directions': np.random.randint(200, 900, size=len(dates)),
        'Calls': np.random.randint(50, 250, size=len(dates)),
        'Reviews': np.random.randint(20, 120, size=len(dates)),
        'Chats': np.random.randint(100, 500, size=len(dates)),
        'Resolved_Chats': np.random.randint(80, 450, size=len(dates))
    })

    # Places Database
    cats = ['Restaurant', 'Cafe', 'Pharmacy', 'House', 'Super Market']
    districts = ['City Center', 'University Area', 'Nile Corniche', 'New Beni Suef', 'El Wasta', 'Biba']
    
    places = []
    for i in range(250):
        places.append({
            'Name': f"Place {1000+i}",
            'Category': np.random.choice(cats),
            'District': np.random.choice(districts),
            'Visits': np.random.randint(100, 10000),
            'Saves': np.random.randint(10, 2000),
            'Rating': np.random.uniform(1.5, 5.0),
            'Status': np.random.choice(['Active', 'Suspended', 'Pending Approval'], p=[0.8, 0.1, 0.1])
        })
    df_places = pd.DataFrame(places)
    
    return df_ts, df_places

df_ts, df_places = load_all_platform_data()

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
        options=["Overview", "Places Analytics", "User Analytics", "Reviews", "Chatbot", "Moderation", "Location Logic"],
        icons=['grid-1x2', 'shop', 'people', 'star', 'robot', 'shield-lock', 'geo-alt'],
        default_index=0,
        styles={
            "container": {"background-color": "transparent"},
            "nav-link": {"font-size": "14px", "text-align": "left", "color": "white"},
            "nav-link-selected": {"background-color": "#2563EB"},
        }
    )

    st.divider()
    
    # GLOBAL TIME FILTER
    st.markdown("### 📅 Select Date Range")
    date_range = st.date_input(
        "Choose period:",
        value=(datetime(2024, 1, 1), datetime(2024, 1, 30))
    )

# --- FILTER LOGIC ---
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df_ts[(df_ts['Date'] >= start) & (df_ts['Date'] <= end)]
    # Comparison Period
    days_diff = (end - start).days + 1
    df_prev = df_ts[(df_ts['Date'] >= start - timedelta(days=days_diff)) & (df_ts['Date'] < start)]
else:
    st.stop()

# =========================
# 1. OVERVIEW (PLATFORM-WIDE)
# =========================
if selected == "Overview":
    st.title("📊 Platform Performance Overview")
    
    # Delta Helper
    def get_delta(col):
        curr, prev = df_filtered[col].sum(), df_prev[col].sum()
        if prev == 0: return "0%"
        return f"{int(((curr - prev)/prev)*100)}%"

    # KPI ROW 1
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Visits", f"{df_filtered['Visits'].sum():,}", get_delta('Visits'))
    k2.metric("New Users", f"{df_filtered['New_Users'].sum():,}", get_delta('New_Users'))
    k3.metric("Saved Places", f"{df_filtered['Saves'].sum():,}", get_delta('Saves'))
    k4.metric("Direction Clicks", f"{df_filtered['Directions'].sum():,}", get_delta('Directions'))

    # KPI ROW 2
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Call Clicks", f"{df_filtered['Calls'].sum():,}", get_delta('Calls'))
    k6.metric("Total Reviews", f"{df_filtered['Reviews'].sum():,}", get_delta('Reviews'))
    k7.metric("Active Places", len(df_places[df_places['Status']=='Active']))
    k8.metric("Bot Resolution", f"{(df_filtered['Resolved_Chats'].sum()/df_filtered['Chats'].sum())*100:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("⏰ Platform Visiting Hours (Beni Suef Activity)")
        hours = [f"{i}:00" for i in range(24)]
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        heat_data = np.random.randint(10, 100, size=(7, 24))
        heat_data[:, 18:22] += 60 # Peak evening activity
        fig_heat = px.imshow(heat_data, x=hours, y=days, color_continuous_scale='Blues', aspect="auto")
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_b:
        st.subheader("🚀 Signup Velocity")
        fig_v = px.bar(df_filtered, x='Date', y=['New_Users', 'New_Owners'], barmode='group', color_discrete_sequence=['#2563EB', '#F59E0B'])
        st.plotly_chart(fig_v, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_c = st.columns([1])[0]
    with col_c:
        st.subheader("🛡️ Content Status")
        fig_st = px.pie(df_places, names='Status', hole=0.6, color_discrete_sequence=['#10B981', '#EF4444', '#F59E0B'])
        st.plotly_chart(fig_st, use_container_width=True)

# =========================
# 2. PLACES ANALYTICS
# =========================
elif selected == "Places Analytics":
    st.title("🏘️ Places Analytics")
    
    p1, p2, p3 = st.columns(3)
    p1.metric("Pending Approval", len(df_places[df_places['Status']=='Pending Approval']))
    p2.metric("Suspended Places", len(df_places[df_places['Status']=='Suspended']))
    p3.metric("Most Visited Category", "Restaurants")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Most Visited Places")
        top_v = df_places.nlargest(5, 'Visits')
        st.plotly_chart(px.bar(top_v, x='Visits', y='Name', orientation='h', color='Visits'), use_container_width=True)
        
        st.subheader("Highest Rated Places")
        st.dataframe(df_places.nlargest(5, 'Rating')[['Name', 'Category', 'Rating']], use_container_width=True)

    with c2:
        st.subheader("Most Saved Places")
        top_s = df_places.nlargest(5, 'Saves')
        st.plotly_chart(px.bar(top_s, x='Saves', y='Name', orientation='h', color='Saves', color_continuous_scale='Greens'), use_container_width=True)
        
        st.subheader("Lowest Rated Places (Admin Action Needed)")
        st.dataframe(df_places.nsmallest(5, 'Rating')[['Name', 'Category', 'Rating']], use_container_width=True)

# =========================
# 3. USER ANALYTICS
# =========================
elif selected == "User Analytics":
    st.title("👥 User Analytics")
    
    u1, u2 = st.columns(2)
    u1.metric("New Users (This Period)", df_filtered['New_Users'].sum())
    u2.metric("Suspended/Banned Users", 84)
    
    st.subheader("Platform User Growth Trend")
    fig_u = px.area(df_filtered, x='Date', y='New_Users', color_discrete_sequence=['#2563EB'])
    st.plotly_chart(fig_u, use_container_width=True)
    

# =========================
# 4. REVIEWS
# =========================
elif selected == "Reviews":
    st.title("⭐ Reviews & Sentiment Analysis")
    r1, r2, r3 = st.columns(3)
    r1.metric("Total Reviews", df_filtered['Reviews'].sum())
    r2.metric("Positive Sentiment", "78%", "3%")
    r3.metric("Deleted", 12)
    
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("Positive vs Negative Ratio")
        fig_r = px.pie(values=[75, 25], names=['Positive', 'Negative'], hole=0.5, color_discrete_sequence=['#10B981', '#EF4444'])
        st.plotly_chart(fig_r, use_container_width=True)
    with r2:
        st.subheader("Average Rating per Category")
        avg_c = df_places.groupby('Category')['Rating'].mean().reset_index()
        st.plotly_chart(px.bar(avg_c, x='Category', y='Rating', color='Rating'), use_container_width=True)

# =========================
# 5. CHATBOT
# =========================
elif selected == "Chatbot":
    st.title("🤖 Chatbot Intelligence")
    ch1, ch2, ch3 = st.columns(3)
    ch1.metric("Total Chat Sessions", df_filtered['Chat_Sessions'].sum())
    ch2.metric("Avg Resolution Rate", f"{(df_filtered['Resolved_Chats'].sum()/df_filtered['Chat_Sessions'].sum())*100:.1f}%")
    ch3.metric("Unresolved Queries", 42)
    
    st.subheader("Most Common Query Types")
    q_data = pd.DataFrame({'Type': ['Menu', 'Hours', 'Location', 'Pricing', 'Other'], 'Val': [45, 25, 15, 10, 5]})
    st.plotly_chart(px.pie(q_data, values='Val', names='Type', hole=0.5), use_container_width=True)
    

# =========================
# 6. MODERATION
# =========================
elif selected == "Moderation":
    st.title("🛡️ Moderation Center")
    st.subheader("Admin Action History")
    actions = pd.DataFrame({
        'Admin': ['Admin_01', 'Admin_01', 'SuperAdmin'],
        'Action': ['Approved Place P-1002', 'Suspended User U-882', 'Deleted Review #442'],
        'Timestamp': ['10 mins ago', '1 hr ago', 'Yesterday']
    })
    st.table(actions)
    
    st.subheader("New Owners Pending Verification")
    st.warning("There are 5 owners awaiting identity verification.")

# =========================
# 7. LOCATION LOGIC (Beni Suef Focus)
# =========================
elif selected == "Location Logic":
    st.title("📍 Location Intelligence: Beni Suef")
    BS_LAT, BS_LON = 29.0661, 31.0994
    
    # Map Heatmap
    map_data = pd.DataFrame({
        'lat': np.random.uniform(BS_LAT-0.015, BS_LAT+0.015, 150),
        'lon': np.random.uniform(BS_LON-0.015, BS_LON+0.015, 150),
        'intensity': np.random.randint(1, 100, 150)
    })
    
    fig_map = px.density_mapbox(map_data, lat='lat', lon='lon', z='intensity', radius=15,
                                center=dict(lat=BS_LAT, lon=BS_LON), zoom=12.5,
                                mapbox_style="open-street-map", height=600)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.divider()
    
    st.subheader("🗺️ District Analysis & Opportunity Map")
    col1, col2 = st.columns(2)
    with col1:
        dist_counts = df_places['District'].value_counts().reset_index()
        st.plotly_chart(px.bar(dist_counts, x='count', y='District', orientation='h', title="Most Active Districts"), use_container_width=True)
    with col2:
        st.success("📍 Opportunity Found: 'New Beni Suef' district has high search volume for Pharmacies but 0 registered.")
        st.info("📍 Activity Alert: 'Nile Corniche' area has the highest concentration of Direction Clicks.")
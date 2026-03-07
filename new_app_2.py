import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

# --- PAGE SETUP ---
st.set_page_config(page_title="AroundU | Admin Dashboard", layout="wide")

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
    
    /* White Plot Containers */
    .plot-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ADVANCED MOCK DATA GENERATOR ---
@st.cache_data
def get_full_platform_data():
    dates = pd.date_range(start="2023-01-01", end="2024-03-01", freq='D')
    
    # Time Series Data (Users, Signups, Chats)
    df_ts = pd.DataFrame({
        'Date': dates,
        'New_Users': np.random.randint(20, 100, size=len(dates)),
        'New_Owners': np.random.randint(2, 12, size=len(dates)),
        'Visits': np.random.randint(2000, 8000, size=len(dates)),
        'Reviews': np.random.randint(50, 200, size=len(dates)),
        'Chat_Sessions': np.random.randint(100, 400, size=len(dates)),
        'Resolved_Chats': np.random.randint(80, 350, size=len(dates)),
        'Direction_Clicks': np.random.randint(300, 1000, size=len(dates))
    })

    # Places / Categories Data
    cats = ['Restaurant', 'Cafe', 'Pharmacy', 'House', 'Super Market']
    districts = ['City Center', 'University', 'Nile Corniche', 'New Beni Suef', 'El Wasta', 'Biba']
    
    places = []
    for i in range(300):
        places.append({
            'Name': np.random.choice(['Nile Cafe', 'Beni Suef Grill', 'Grand Pharmacy', 'Modern Villa', 'Metro Mart']) + f" {i}",
            'Category': np.random.choice(cats),
            'District': np.random.choice(districts),
            'Visits': np.random.randint(500, 50000),
            'Saves': np.random.randint(50, 5000),
            'Rating': np.random.uniform(1.2, 5.0),
            'Status': np.random.choice(['Active', 'Suspended', 'Pending Approval'], p=[0.8, 0.1, 0.1]),
            'Created_At': np.random.choice(dates)
        })
    df_places = pd.DataFrame(places)
    
    return df_ts, df_places

df_ts, df_places = get_full_platform_data()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("🏙️ AroundU")
    st.caption("Beni Suef Platform Intelligence")
    
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
    period_days = (end - start).days + 1
    df_prev = df_ts[(df_ts['Date'] >= start - timedelta(days=period_days)) & (df_ts['Date'] < start)]
else:
    st.stop()

# =========================
# 1. PLATFORM OVERVIEW
# =========================
if selected == "Overview":
    st.title("📊 Platform Overview")
    k1, k2, k3, k4 = st.columns(4)
    
    def delta(col):
        curr, prev = df_filtered[col].sum(), df_prev[col].sum()
        return f"{int(((curr - prev)/max(1,prev))*100)}%"

    k1.metric("Total Places", len(df_places))
    k2.metric("Total Registered Users", 15420)
    k3.metric("Total Reviews", df_ts['Reviews'].sum())
    k4.metric("Platform Growth", "+14.2%", delta('New_Users'))

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("📈 User & Owner Signup Velocity")
        fig_sig = px.line(df_filtered, x='Date', y=['New_Users', 'New_Owners'], color_discrete_sequence=["#2563EB", "#F59E0B"])
        st.plotly_chart(fig_sig, use_container_width=True)
    with col_b:
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

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Top 5 Most Visited Places")
        top_v = df_places.nlargest(5, 'Visits')
        st.plotly_chart(px.bar(top_v, x='Visits', y='Name', orientation='h', color='Visits'), use_container_width=True)
        
        st.subheader("Lowest Rated Places")
        st.dataframe(df_places.nsmallest(5, 'Rating')[['Name', 'Rating', 'Category']], use_container_width=True)
    
    with col_d:
        st.subheader("Most Saved Places")
        top_s = df_places.nlargest(5, 'Saves')
        st.plotly_chart(px.bar(top_s, x='Saves', y='Name', orientation='h', color='Saves', color_continuous_scale='Greens'), use_container_width=True)
        
        st.subheader("Highest Rated Places")
        st.dataframe(df_places.nlargest(5, 'Rating')[['Name', 'Rating', 'Category']], use_container_width=True)

# =========================
# 3. USER ANALYTICS
# =========================
elif selected == "User Analytics":
    st.title("👥 User Analytics")
    u1, u2 = st.columns(2)
    u1.metric("New Users (This Period)", df_filtered['New_Users'].sum())
    u2.metric("Suspended/Banned Users", 84)

    st.subheader("User Registration Rate Over Time")
    st.plotly_chart(px.area(df_filtered, x='Date', y='New_Users', color_discrete_sequence=['#2563EB']), use_container_width=True)

# =========================
# 4. REVIEWS ANALYTICS
# =========================
elif selected == "Reviews":
    st.title("⭐ Reviews & Sentiment")
    r1, r2, r3 = st.columns(3)
    r1.metric("Total Reviews", df_filtered['Reviews'].sum())
    r2.metric("Positive Sentiment", "78%", "3%")
    r3.metric("Flagged/Deleted", 12)

    c_e, c_f = st.columns(2)
    with c_e:
        st.subheader("Sentiment Split (NLP Analysis)")
        fig_sent = px.pie(values=[78, 22], names=['Positive', 'Negative'], hole=0.5, color_discrete_sequence=['#10B981', '#EF4444'])
        st.plotly_chart(fig_sent, use_container_width=True)
    with c_f:
        st.subheader("Average Rating per Category")
        avg_r = df_places.groupby('Category')['Rating'].mean().reset_index()
        st.plotly_chart(px.bar(avg_r, x='Category', y='Rating', color='Rating'), use_container_width=True)

# =========================
# 5. CHATBOT ANALYTICS
# =========================
elif selected == "Chatbot":
    st.title("🤖 Chatbot Analytics")
    ch1, ch2, ch3 = st.columns(3)
    ch1.metric("Total Chat Sessions", df_filtered['Chat_Sessions'].sum())
    ch2.metric("Avg Resolution Rate", f"{(df_filtered['Resolved_Chats'].sum()/df_filtered['Chat_Sessions'].sum())*100:.1f}%")
    ch3.metric("Unresolved Queries", 42)

    c_g, c_h = st.columns(2)
    with c_g:
        st.subheader("Most Common Query Types")
        q_types = pd.DataFrame({'Type': ['Menu', 'Hours', 'Location', 'Pricing', 'Other'], 'Val': [40, 25, 15, 12, 8]})
        st.plotly_chart(px.pie(q_types, values='Val', names='Type', hole=0.5), use_container_width=True)
    with c_h:
        st.subheader("Chat Volume per Day")
        st.plotly_chart(px.line(df_filtered, x='Date', y='Chat_Sessions', color_discrete_sequence=['#636EFA']), use_container_width=True)

# =========================
# 6. MODERATION CENTER
# =========================
elif selected == "Moderation":
    st.title("🛡️ Moderation & Audit Log")
    m_a, m_b = st.columns(2)
    with m_a:
        st.subheader("New Owners Pending Verification")
        pending_o = pd.DataFrame({
            'Owner': ['Ahmed Mansour', 'Hassan Ali', 'Sara Gad'],
            'Business': ['Nile View Cafe', 'Beni Suef Pharmacy', 'The Grand Villa'],
            'Requested': ['2 hrs ago', '5 hrs ago', 'Yesterday']
        })
        st.table(pending_o)
    with m_b:
        st.subheader("Admin Action History")
        actions = pd.DataFrame({
            'Admin': ['Admin_01', 'SuperAdmin', 'Admin_01'],
            'Action': ['Banned User U-99', 'Suspended Place P-44', 'Deleted Review #882'],
            'Time': ['10:15 AM', 'Yesterday', '2 days ago']
        })
        st.dataframe(actions, use_container_width=True)

# =========================
# 7. LOCATION ANALYTICS
# =========================
elif selected == "Location Logic":
    st.title("📍 Location Intelligence (Beni Suef)")
    BS_LAT, BS_LON = 29.0661, 31.0994
    
    # Map Visualization
    st.subheader("User Activity Heatmap & Direction Clicks")
    map_data = pd.DataFrame({
        'lat': np.random.uniform(BS_LAT-0.02, BS_LAT+0.02, 200),
        'lon': np.random.uniform(BS_LON-0.02, BS_LON+0.02, 200),
        'weight': np.random.randint(1, 100, 200)
    })
    fig_map = px.density_mapbox(map_data, lat='lat', lon='lon', z='weight', radius=15,
                                center=dict(lat=BS_LAT, lon=BS_LON), zoom=12,
                                mapbox_style="open-street-map", height=600)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    
    l_c1, l_c2 = st.columns(2)
    with l_c1:
        st.subheader("Most Active Districts")
        dist_counts = df_places['District'].value_counts().reset_index()
        st.plotly_chart(px.bar(dist_counts, x='count', y='District', orientation='h', color='District'), use_container_width=True)
    with l_c2:
        st.subheader("🗺️ Opportunity Map (No Competition)")
        st.success("Opportunity Detected: 'New Beni Suef' district has high user activity but 0 Pharmacies.")
        st.warning("Opportunity Detected: 'El Wasta' area has high house searches but only 2 listings.")
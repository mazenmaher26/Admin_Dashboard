import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta

# --- PAGE SETUP ---
st.set_page_config(page_title="AroundU | Admin Panel", layout="wide")

# --- UI CUSTOMIZATION (EXACT MATCH TO OWNER UI) ---
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
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENHANCED MOCK DATA GENERATOR ---
@st.cache_data
def get_admin_data():
    dates = pd.date_range(start="2023-01-01", end="2024-03-01", freq='D')
    
    # Time Series Data
    df_ts = pd.DataFrame({
        'Date': dates,
        'New_Users': np.random.randint(10, 60, size=len(dates)),
        'New_Places': np.random.randint(2, 15, size=len(dates)),
        'Reviews': np.random.randint(20, 150, size=len(dates)),
        'Visits': np.random.randint(1000, 6000, size=len(dates))
    })
    
    # Categorical Data
    cats = ['Restaurant', 'Cafe', 'Pharmacy', 'House', 'Super Market']
    df_places = pd.DataFrame({
        'Name': [f"Place {i}" for i in range(250)],
        'Category': np.random.choice(cats, 250),
        'Status': np.random.choice(['Active', 'Suspended'], p=[0.9, 0.1], size=250),
        'Rating': np.random.uniform(2.0, 5.0, 250),
        'Visits': np.random.randint(100, 10000, 250)
    })
    
    return df_ts, df_places

df_ts, df_places = get_admin_data()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("🏙️ AroundU")
    st.caption("Admin Business Intelligence")
    
    selected = option_menu(
        menu_title=None,
        options=["Overview", "Places Analytics", "User Analytics", "Reviews", "Chatbot", "Moderation", "Location Logic"],
        icons=['grid-1x2', 'shop', 'people', 'star', 'robot', 'shield-lock', 'geo-alt'],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2563EB"}}
    )
    
    st.divider()
    st.markdown("### 📅 Global Time Filter")
    date_range = st.date_input("Select Period:", value=(datetime(2024,1,1), datetime(2024,2,1)))

# Global Filtering Logic
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df_ts[(df_ts['Date'] >= start) & (df_ts['Date'] <= end)]
    
    # Prev period for Deltas
    period_days = (end - start).days + 1
    df_prev = df_ts[(df_ts['Date'] >= start - timedelta(days=period_days)) & (df_ts['Date'] < start)]
else:
    st.stop()

# =========================
# 1. PLATFORM OVERVIEW (ENHANCED)
# =========================
if selected == "Overview":
    st.title("📊 Platform Performance Overview")
    
    # --- ROW 1: KPI CARDS ---
    m1, m2, m3, m4 = st.columns(4)
    
    def calc_delta(col, df_curr, df_p):
        curr_total = df_curr[col].sum()
        prev_total = df_p[col].sum()
        if prev_total == 0: return "0%"
        return f"{int(((curr_total - prev_total)/prev_total)*100)}%"

    m1.metric("Total Platform Visits", f"{df_filtered['Visits'].sum():,}", calc_delta('Visits', df_filtered, df_prev))
    m2.metric("New Registered Users", f"{df_filtered['New_Users'].sum():,}", calc_delta('New_Users', df_filtered, df_prev))
    m3.metric("Total Active Places", len(df_places[df_places['Status']=='Active']))
    m4.metric("Platform Reviews", f"{df_filtered['Reviews'].sum():,}", calc_delta('Reviews', df_filtered, df_prev))

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROW 2: GROWTH & STATUS ---
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("📈 Platform Growth Trend")
        # Creating a cumulative growth view
        growth_df = df_filtered.copy()
        growth_df['Total_Users'] = growth_df['New_Users'].cumsum()
        growth_df['Total_Places'] = growth_df['New_Places'].cumsum()
        
        fig_growth = px.line(growth_df, x='Date', y=['Total_Users', 'Total_Places'], 
                             labels={'value': 'Count', 'variable': 'Metric'},
                             color_discrete_sequence=["#2563EB", "#10B981"],
                             template="plotly_white")
        fig_growth.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_growth, use_container_width=True)

    with col_b:
        st.subheader("🛡️ Platform Health")
        status_counts = df_places['Status'].value_counts().reset_index()
        fig_status = px.pie(status_counts, values='count', names='Status', hole=0.6,
                            color_discrete_map={'Active': '#10B981', 'Suspended': '#EF4444'})
        fig_status.update_layout(showlegend=False)
        st.plotly_chart(fig_status, use_container_width=True)
        st.caption("Ratio of Live vs. Suspended Content")

    # --- ROW 3: CATEGORIES & SIGNUP VELOCITY ---
    col_c, col_d = st.columns([1, 1])
    
    with col_c:
        st.subheader("🗂️ Places by Category")
        cat_fig = px.bar(df_places['Category'].value_counts().reset_index(), 
                         x='count', y='Category', orientation='h',
                         color='count', color_continuous_scale='Blues')
        cat_fig.update_layout(showlegend=False)
        st.plotly_chart(cat_fig, use_container_width=True)

    with col_d:
        st.subheader("🚀 Signup Velocity (New Users vs Owners)")
        velocity_df = df_filtered.copy()
        # Mocking owner signups as 10% of users
        velocity_df['New_Owners'] = (velocity_df['New_Users'] * 0.1).astype(int)
        
        fig_velocity = px.bar(velocity_df, x='Date', y=['New_Users', 'New_Owners'],
                              barmode='group', color_discrete_sequence=["#3B82F6", "#F59E0B"])
        fig_velocity.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_velocity, use_container_width=True)

# =================================================================
# REMAINING SECTIONS (PLACEHOLDERS FOR YOUR FULL ADMIN LOGIC)
# =================================================================
elif selected == "Places Analytics":
    st.title("🏘️ Places Analytics")
    # Add metrics: Most Visited, Most Saved, Highest/Lowest Rated...
    st.info("Visualizations for visit count platform-wide and user save rankings.")

elif selected == "User Analytics":
    st.title("👥 User Analytics")
    # Add metrics: Growth charts, New users per day, heatmap info...
    st.line_chart(df_filtered.set_index('Date')['New_Users'])

elif selected == "Reviews":
    st.title("⭐ Reviews Analytics")
    # Add metrics: Sentiment ratio, reviews per week, Avg rating per category...
    st.plotly_chart(px.histogram(df_places, x='Rating', nbins=10, title="Review Rating Distribution"))

elif selected == "Chatbot":
    st.title("🤖 Chatbot Analytics")
    # Add metrics: Resolution rate, Most common queries, unresolved counts...
    st.metric("Avg Resolution Rate", "84.5%", "+2%")

elif selected == "Moderation":
    st.title("🛡️ Moderation Center")
    # Add metrics: Flagged content, Pending owners, Audit history...
    st.warning("3 New Owners awaiting verification.")

elif selected == "Location Logic":
    st.title("📍 Location Analytics (Beni Suef)")
    # Add metrics: User Heatmap, District analysis, Opportunity Map...
    BS_LAT, BS_LON = 29.0661, 31.0994
    st.map(pd.DataFrame({'lat': [BS_LAT], 'lon': [BS_LON]}))
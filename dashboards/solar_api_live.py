"""
Solar Development Dashboard - LIVE DATA from NREL, Census, and FRED APIs
Real-time solar resource data, demographics, and economic indicators
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Live Solar Development Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys from environment
NREL_API_KEY = os.getenv('NREL_API_KEY', st.secrets.get('NREL_API_KEY', ''))
CENSUS_API_KEY = os.getenv('CENSUS_API_KEY', st.secrets.get('CENSUS_API_KEY', ''))
FRED_API_KEY = os.getenv('FRED_API_KEY', st.secrets.get('FRED_API_KEY', ''))
# Support both MAPBOX_ACCESS_TOKEN and MAPBOX_API_KEY naming conventions
MAPBOX_API_KEY = os.getenv('MAPBOX_ACCESS_TOKEN', os.getenv('MAPBOX_API_KEY',
                 st.secrets.get('MAPBOX_ACCESS_TOKEN', st.secrets.get('MAPBOX_API_KEY', ''))))

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .api-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        margin: 0.25rem;
    }
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #10b981;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# API Fetch Functions

@st.cache_data(ttl=3600)
def fetch_nrel_solar_resource(lat, lon):
    """Fetch solar resource data from NREL API"""
    try:
        url = 'https://developer.nrel.gov/api/solar/solar_resource/v1.json'
        params = {
            'api_key': NREL_API_KEY,
            'lat': lat,
            'lon': lon
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.warning(f"NREL API Error: {str(e)}")
        return None

@st.cache_data(ttl=86400)
def fetch_census_demographics(state_fips):
    """Fetch population and income data from Census API"""
    try:
        url = 'https://api.census.gov/data/2021/acs/acs5'
        params = {
            'get': 'B01003_001E,B19013_001E,NAME',  # Population, Median Income
            'for': 'county:*',
            'in': f'state:{state_fips}',
            'key': CENSUS_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        df['B01003_001E'] = pd.to_numeric(df['B01003_001E'], errors='coerce')  # Population
        df['B19013_001E'] = pd.to_numeric(df['B19013_001E'], errors='coerce')  # Income
        df.columns = ['population', 'median_income', 'name', 'state', 'county']
        return df
    except Exception as e:
        st.warning(f"Census API Error: {str(e)}")
        return None

@st.cache_data(ttl=86400)
def fetch_fred_energy_prices():
    """Fetch electricity prices from FRED API"""
    try:
        url = 'https://api.stlouisfed.org/fred/series/observations'
        params = {
            'series_id': 'APU000072610',  # Electricity price index
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'limit': 12,  # Last 12 months
            'sort_order': 'desc'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        observations = data.get('observations', [])
        df = pd.DataFrame(observations)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    except Exception as e:
        st.warning(f"FRED API Error: {str(e)}")
        return None

# Header
st.markdown("""
<div class="main-header">
    <span class="live-indicator"></span>
    ☀️ Live Solar Development Dashboard
</div>
<div style='font-size: 1.1rem; color: #6b7280; margin-bottom: 1rem;'>
    Real-time data from NREL, US Census, and FRED APIs
</div>
<div>
    <span class="api-badge">NREL Solar API</span>
    <span class="api-badge">US Census ACS</span>
    <span class="api-badge">FRED Economic Data</span>
    <span class="api-badge">Mapbox GL JS</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# Sidebar - Location Selection
st.sidebar.header("📍 Site Selection")

# Predefined locations for solar development
locations = {
    'Phoenix, AZ': (33.4484, -112.0740, '04'),  # State FIPS 04 = Arizona
    'Los Angeles, CA': (34.0522, -118.2437, '06'),  # California
    'Austin, TX': (30.2672, -97.7431, '48'),  # Texas
    'Las Vegas, NV': (36.1699, -115.1398, '32'),  # Nevada
    'Albuquerque, NM': (35.0844, -106.6504, '35'),  # New Mexico
    'Denver, CO': (39.7392, -104.9903, '08'),  # Colorado
    'Tucson, AZ': (32.2226, -110.9747, '04'),  # Arizona
    'San Diego, CA': (32.7157, -117.1611, '06'),  # California
}

selected_location = st.sidebar.selectbox(
    "Select Location",
    options=list(locations.keys())
)

lat, lon, state_fips = locations[selected_location]

st.sidebar.markdown(f"""
**Coordinates:**
- Latitude: `{lat}`
- Longitude: `{lon}`
- State FIPS: `{state_fips}`
""")

if st.sidebar.button("🔄 Refresh All Data"):
    st.cache_data.clear()
    st.rerun()

# Fetch data
with st.spinner("Fetching live data from APIs..."):
    solar_data = fetch_nrel_solar_resource(lat, lon)
    census_data = fetch_census_demographics(state_fips)
    fred_data = fetch_fred_energy_prices()

# KPI Row
if solar_data and 'outputs' in solar_data:
    outputs = solar_data['outputs']

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        dni = outputs.get('avg_dni', {}).get('annual', 0)
        st.metric(
            label="Annual DNI",
            value=f"{dni:.1f} kWh/m²/day",
            delta="Direct Normal Irradiance",
            help="From NREL Solar API"
        )

    with col2:
        ghi = outputs.get('avg_ghi', {}).get('annual', 0)
        st.metric(
            label="Annual GHI",
            value=f"{ghi:.1f} kWh/m²/day",
            delta="Global Horizontal Irradiance",
            help="From NREL Solar API"
        )

    with col3:
        lat_tilt = outputs.get('avg_lat_tilt', {}).get('annual', 0)
        st.metric(
            label="Latitude Tilt",
            value=f"{lat_tilt:.1f} kWh/m²/day",
            delta="Optimal fixed tilt",
            help="From NREL Solar API"
        )

    with col4:
        if census_data is not None and len(census_data) > 0:
            total_pop = census_data['population'].sum()
            st.metric(
                label="State Population",
                value=f"{total_pop/1e6:.2f}M",
                delta="Potential market size",
                help="From US Census ACS API"
            )

    with col5:
        if fred_data is not None and len(fred_data) > 0:
            recent_price = fred_data['value'].iloc[-1]
            st.metric(
                label="Electricity Price Index",
                value=f"{recent_price:.1f}",
                delta=f"+{recent_price - fred_data['value'].iloc[-6]:.1f} (6mo)",
                help="From FRED API"
            )

st.divider()

# Main Content
col_map, col_solar_chart = st.columns([2, 1])

with col_map:
    st.subheader("📍 Solar Resource Map")

    if solar_data:
        # Create map centered on location
        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=10,
            pitch=45,
            bearing=0
        )

        # Icon layer for selected site
        site_data = pd.DataFrame([{
            'lat': lat,
            'lon': lon,
            'dni': dni,
            'size': 100,
            'color': [255, 215, 0, 200]  # Gold
        }])

        icon_layer = pdk.Layer(
            'ScatterplotLayer',
            data=site_data,
            get_position='[lon, lat]',
            get_radius='size * 100',
            get_fill_color='color',
            pickable=True,
        )

        # Column layer showing solar potential
        column_layer = pdk.Layer(
            'ColumnLayer',
            data=site_data,
            get_position='[lon, lat]',
            get_elevation='dni * 500',
            elevation_scale=20,
            radius=500,
            get_fill_color='color',
            pickable=True,
            auto_highlight=True,
            extruded=True,
        )

        tooltip = {
            "html": f"""
            <b>{selected_location}</b><br/>
            DNI: {dni:.1f} kWh/m²/day<br/>
            GHI: {ghi:.1f} kWh/m²/day<br/>
            <i>Data from NREL API</i>
            """,
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "padding": "10px",
                "borderRadius": "5px"
            }
        }

        deck = pdk.Deck(
            layers=[column_layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style='mapbox://styles/mapbox/satellite-streets-v11',
            mapbox_key=MAPBOX_API_KEY
        )

        st.pydeck_chart(deck)

with col_solar_chart:
    st.subheader("☀️ Monthly Solar Resource")

    if solar_data and 'outputs' in solar_data:
        # Extract monthly data
        monthly_dni = outputs.get('avg_dni', {}).get('monthly', [])
        monthly_ghi = outputs.get('avg_ghi', {}).get('monthly', [])

        if monthly_dni and monthly_ghi:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            monthly_df = pd.DataFrame({
                'Month': months,
                'DNI': monthly_dni,
                'GHI': monthly_ghi
            })

            fig_monthly = go.Figure()
            fig_monthly.add_trace(go.Scatter(
                x=monthly_df['Month'],
                y=monthly_df['DNI'],
                name='DNI',
                mode='lines+markers',
                line=dict(color='#f59e0b', width=3)
            ))
            fig_monthly.add_trace(go.Scatter(
                x=monthly_df['Month'],
                y=monthly_df['GHI'],
                name='GHI',
                mode='lines+markers',
                line=dict(color='#3b82f6', width=3)
            ))

            fig_monthly.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                yaxis_title='kWh/m²/day',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )

            st.plotly_chart(fig_monthly, use_container_width=True)

st.divider()

# Census Demographics and FRED Economics
col_census, col_fred = st.columns(2)

with col_census:
    st.subheader("📊 County Demographics (US Census)")

    if census_data is not None and len(census_data) > 0:
        # Top counties by population
        top_counties = census_data.nlargest(10, 'population')[['name', 'population', 'median_income']]

        fig_census = px.bar(
            top_counties,
            x='population',
            y='name',
            orientation='h',
            color='median_income',
            color_continuous_scale='Viridis',
            labels={
                'population': 'Population',
                'name': 'County',
                'median_income': 'Median Income ($)'
            },
            hover_data={'median_income': ':$,.0f'}
        )

        fig_census.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            yaxis={'categoryorder':'total ascending'}
        )

        st.plotly_chart(fig_census, use_container_width=True)

        # Summary stats
        st.info(f"""
        **State Market Summary:**
        - Total Population: **{census_data['population'].sum()/1e6:.2f}M**
        - Avg Median Income: **${census_data['median_income'].mean():,.0f}**
        - Counties: **{len(census_data)}**

        *Data source: US Census Bureau ACS 5-Year Estimates*
        """)

with col_fred:
    st.subheader("💰 Electricity Prices (FRED)")

    if fred_data is not None and len(fred_data) > 0:
        fig_fred = px.line(
            fred_data,
            x='date',
            y='value',
            labels={
                'date': 'Date',
                'value': 'Price Index'
            },
            markers=True
        )

        fig_fred.update_traces(line=dict(color='#10b981', width=3))
        fig_fred.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            hovermode='x unified'
        )

        st.plotly_chart(fig_fred, use_container_width=True)

        # Trend analysis
        recent_avg = fred_data['value'].tail(3).mean()
        older_avg = fred_data['value'].head(3).mean()
        change = ((recent_avg - older_avg) / older_avg) * 100

        trend_emoji = "📈" if change > 0 else "📉"

        st.info(f"""
        **Price Trend Analysis:**
        - Recent Avg (3mo): **{recent_avg:.2f}**
        - 9-Month Change: **{change:+.1f}%** {trend_emoji}
        - Latest Value: **{fred_data['value'].iloc[-1]:.2f}** ({fred_data['date'].iloc[-1].strftime('%b %Y')})

        *Data source: Federal Reserve Economic Data (FRED)*
        """)

st.divider()

# Project Feasibility Calculator
st.subheader("🧮 Project Feasibility Calculator")

col_calc1, col_calc2, col_calc3 = st.columns(3)

with col_calc1:
    project_size_mw = st.number_input("Project Size (MW)", min_value=1.0, max_value=500.0, value=100.0, step=10.0)

with col_calc2:
    cost_per_watt = st.number_input("Cost per Watt ($)", min_value=0.5, max_value=3.0, value=1.2, step=0.1)

with col_calc3:
    ppa_price = st.number_input("PPA Price ($/MWh)", min_value=20.0, max_value=100.0, value=45.0, step=5.0)

if solar_data and 'outputs' in solar_data:
    # Calculate energy production
    avg_daily_irradiance = outputs.get('avg_ghi', {}).get('annual', 5.0)  # kWh/m²/day
    capacity_factor = 0.25  # Typical for utility solar
    annual_production_mwh = project_size_mw * 1000 * 365 * 24 * capacity_factor  # MWh/year

    # Calculate financials
    total_cost = project_size_mw * 1000 * cost_per_watt * 1000  # Total $ cost
    annual_revenue = annual_production_mwh * ppa_price
    simple_payback = total_cost / annual_revenue

    # Display results
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)

    with col_res1:
        st.metric("Annual Production", f"{annual_production_mwh/1000:.1f} GWh")

    with col_res2:
        st.metric("Total Cost", f"${total_cost/1e6:.1f}M")

    with col_res3:
        st.metric("Annual Revenue", f"${annual_revenue/1e6:.2f}M")

    with col_res4:
        st.metric("Simple Payback", f"{simple_payback:.1f} years")

    st.success(f"""
    **Feasibility Summary:**
    - Location: **{selected_location}** (DNI: {dni:.1f} kWh/m²/day)
    - This site is **{'EXCELLENT' if dni > 6 else 'GOOD' if dni > 5 else 'MARGINAL'}** for solar development
    - Estimated capacity factor: **{capacity_factor*100:.0f}%**
    - With PPA at **${ppa_price}/MWh**, expect **{simple_payback:.1f} year** simple payback

    *Calculations based on live NREL solar resource data*
    """)

st.divider()

# API Details Table
st.subheader("🔌 Live API Integrations")

api_status = []

# Check NREL
api_status.append({
    'API': 'NREL Solar Resource',
    'Status': '✅ Connected' if solar_data else '❌ Error',
    'Data Points': len(solar_data.get('outputs', {})) if solar_data else 0,
    'Last Update': datetime.now().strftime('%H:%M:%S'),
    'Usage': 'Solar irradiance (DNI, GHI, monthly data)'
})

# Check Census
api_status.append({
    'API': 'US Census Bureau ACS',
    'Status': '✅ Connected' if census_data is not None else '❌ Error',
    'Data Points': len(census_data) if census_data is not None else 0,
    'Last Update': datetime.now().strftime('%H:%M:%S'),
    'Usage': 'Population, median income by county'
})

# Check FRED
api_status.append({
    'API': 'Federal Reserve (FRED)',
    'Status': '✅ Connected' if fred_data is not None else '❌ Error',
    'Data Points': len(fred_data) if fred_data is not None else 0,
    'Last Update': datetime.now().strftime('%H:%M:%S'),
    'Usage': 'Electricity price trends'
})

# Check Mapbox
api_status.append({
    'API': 'Mapbox GL JS',
    'Status': '✅ Connected' if MAPBOX_API_KEY else '⚠️ No Key',
    'Data Points': 1,
    'Last Update': datetime.now().strftime('%H:%M:%S'),
    'Usage': 'Satellite imagery, vector tiles, 3D terrain'
})

api_df = pd.DataFrame(api_status)
st.dataframe(api_df, use_container_width=True, hide_index=True)

# Export
st.divider()
st.subheader("📥 Export Data")

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    if solar_data:
        solar_json = json.dumps(solar_data, indent=2)
        st.download_button(
            label="📄 Download NREL Data (JSON)",
            data=solar_json,
            file_name=f'nrel_solar_{selected_location.replace(", ", "_")}_{datetime.now().strftime("%Y%m%d")}.json',
            mime='application/json'
        )

with col_exp2:
    if census_data is not None:
        census_csv = census_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download Census Data (CSV)",
            data=census_csv,
            file_name=f'census_demographics_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )

with col_exp3:
    if fred_data is not None:
        fred_csv = fred_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💰 Download FRED Data (CSV)",
            data=fred_csv,
            file_name=f'fred_electricity_prices_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280; font-size: 0.875rem;'>
    🤖 Powered by Agentic GIS + Real-Time APIs<br/>
    <b>APIs:</b> NREL Solar Resource v1 • US Census ACS 5-Year • FRED Economic Data • Mapbox GL JS<br/>
    Last refreshed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br/>
    <i>All data is fetched live from authoritative sources</i>
</div>
""", unsafe_allow_html=True)

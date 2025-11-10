"""
Interconnection Queue Dashboard - Track Solar Projects by Substation
Visualize projects in the interconnection queue with transmission lines and substations
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(
    page_title="Interconnection Queue Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys
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
    .substation-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        margin: 0.25rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-active { background: #10b981; color: white; }
    .status-pending { background: #f59e0b; color: white; }
    .status-withdrawn { background: #ef4444; color: white; }
    .status-ia { background: #3b82f6; color: white; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    ⚡ Interconnection Queue Dashboard
</div>
<div style='font-size: 1.1rem; color: #6b7280; margin-bottom: 1rem;'>
    Track solar projects in the interconnection queue by substation
</div>
<div>
    <span class="substation-badge">Transmission Lines</span>
    <span class="substation-badge">Substations</span>
    <span class="substation-badge">Queue Status</span>
    <span class="substation-badge">Interactive Map</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# Sidebar - Filters
st.sidebar.header("🔌 Queue Filters")

# Sample data structure - USER WILL PROVIDE ACTUAL DATA
# This demonstrates the expected data format
sample_substations = {
    'Substation A': {'lat': 33.4484, 'lon': -112.0740, 'voltage_kv': 230, 'operator': 'APS'},
    'Substation B': {'lat': 34.0522, 'lon': -118.2437, 'voltage_kv': 500, 'operator': 'SCE'},
    'Substation C': {'lat': 30.2672, 'lon': -97.7431, 'voltage_kv': 345, 'operator': 'ERCOT'},
    'Substation D': {'lat': 36.1699, 'lon': -115.1398, 'voltage_kv': 230, 'operator': 'NV Energy'},
}

sample_transmission_lines = [
    {'name': 'Line 1', 'start': 'Substation A', 'end': 'Substation B', 'voltage_kv': 500},
    {'name': 'Line 2', 'start': 'Substation B', 'end': 'Substation C', 'voltage_kv': 345},
    {'name': 'Line 3', 'start': 'Substation C', 'end': 'Substation D', 'voltage_kv': 230},
]

# Sample interconnection queue projects
sample_projects = pd.DataFrame([
    {
        'project_name': 'Solar Farm Alpha',
        'developer': 'Energix',
        'capacity_mw': 250,
        'substation': 'Substation A',
        'queue_date': '2023-01-15',
        'status': 'IA Executed',
        'cod_date': '2025-06-01',
        'project_type': 'Solar',
        'lat': 33.4500,
        'lon': -112.0800
    },
    {
        'project_name': 'Solar Farm Beta',
        'developer': 'NextEra Energy',
        'capacity_mw': 180,
        'substation': 'Substation B',
        'queue_date': '2023-03-20',
        'status': 'Feasibility Study',
        'cod_date': '2025-12-01',
        'project_type': 'Solar',
        'lat': 34.0550,
        'lon': -118.2500
    },
    {
        'project_name': 'Solar Farm Gamma',
        'developer': 'First Solar',
        'capacity_mw': 300,
        'substation': 'Substation C',
        'queue_date': '2023-05-10',
        'status': 'Active',
        'cod_date': '2026-03-01',
        'project_type': 'Solar + Storage',
        'lat': 30.2700,
        'lon': -97.7500
    },
    {
        'project_name': 'Solar Farm Delta',
        'developer': 'SunPower',
        'capacity_mw': 200,
        'substation': 'Substation D',
        'queue_date': '2023-07-01',
        'status': 'System Impact Study',
        'cod_date': '2026-09-01',
        'project_type': 'Solar',
        'lat': 36.1720,
        'lon': -115.1450
    },
    {
        'project_name': 'Solar Farm Epsilon',
        'developer': 'Cypress Creek',
        'capacity_mw': 150,
        'substation': 'Substation A',
        'queue_date': '2023-09-15',
        'status': 'Withdrawn',
        'cod_date': None,
        'project_type': 'Solar',
        'lat': 33.4450,
        'lon': -112.0700
    },
])

# File uploader for user data
st.sidebar.subheader("📁 Upload Your Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload Queue Data (CSV/Excel)",
    type=['csv', 'xlsx'],
    help="Upload your interconnection queue data with columns: project_name, developer, capacity_mw, substation, status, lat, lon"
)

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        projects_df = pd.read_csv(uploaded_file)
    else:
        projects_df = pd.read_excel(uploaded_file)
    st.sidebar.success(f"✅ Loaded {len(projects_df)} projects")
else:
    projects_df = sample_projects
    st.sidebar.info("Using sample data. Upload your file to see real queue data.")

# Filters
st.sidebar.divider()

# Substation filter
selected_substations = st.sidebar.multiselect(
    "Filter by Substation",
    options=projects_df['substation'].unique().tolist(),
    default=projects_df['substation'].unique().tolist()
)

# Status filter
status_options = projects_df['status'].unique().tolist()
selected_statuses = st.sidebar.multiselect(
    "Filter by Status",
    options=status_options,
    default=status_options
)

# Developer filter
developer_options = projects_df['developer'].unique().tolist()
selected_developers = st.sidebar.multiselect(
    "Filter by Developer",
    options=developer_options,
    default=developer_options
)

# Capacity filter
min_capacity = st.sidebar.slider(
    "Minimum Capacity (MW)",
    min_value=0,
    max_value=int(projects_df['capacity_mw'].max()),
    value=0
)

# Apply filters
filtered_df = projects_df[
    (projects_df['substation'].isin(selected_substations)) &
    (projects_df['status'].isin(selected_statuses)) &
    (projects_df['developer'].isin(selected_developers)) &
    (projects_df['capacity_mw'] >= min_capacity)
]

st.sidebar.divider()
st.sidebar.metric("Filtered Projects", len(filtered_df))
st.sidebar.metric("Total Capacity", f"{filtered_df['capacity_mw'].sum():.0f} MW")

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_projects = len(filtered_df)
    st.metric("Total Projects", total_projects)

with col2:
    total_capacity = filtered_df['capacity_mw'].sum()
    st.metric("Total Capacity", f"{total_capacity:.0f} MW")

with col3:
    active_projects = len(filtered_df[filtered_df['status'].isin(['Active', 'IA Executed'])])
    st.metric("Active/IA", active_projects)

with col4:
    avg_capacity = filtered_df['capacity_mw'].mean() if len(filtered_df) > 0 else 0
    st.metric("Avg Capacity", f"{avg_capacity:.0f} MW")

st.divider()

# Map visualization
st.subheader("🗺️ Projects by Substation - Interactive Map")

if len(filtered_df) > 0 and MAPBOX_API_KEY:
    # Prepare data for PyDeck
    map_data = filtered_df.copy()

    # Color coding by status
    status_colors = {
        'Active': [16, 185, 129],  # Green
        'IA Executed': [59, 130, 246],  # Blue
        'Feasibility Study': [245, 158, 11],  # Orange
        'System Impact Study': [251, 146, 60],  # Light Orange
        'Withdrawn': [239, 68, 68],  # Red
    }

    map_data['color'] = map_data['status'].apply(lambda x: status_colors.get(x, [128, 128, 128]))
    map_data['radius'] = map_data['capacity_mw'] * 50  # Scale by capacity

    # Create map view
    view_state = pdk.ViewState(
        latitude=map_data['lat'].mean(),
        longitude=map_data['lon'].mean(),
        zoom=5,
        pitch=45,
    )

    # Project layer (colored columns)
    project_layer = pdk.Layer(
        'ColumnLayer',
        data=map_data,
        get_position='[lon, lat]',
        get_elevation='capacity_mw * 100',
        elevation_scale=10,
        radius=2000,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
    )

    # Substation layer (icons)
    substations_data = []
    for sub_name, sub_info in sample_substations.items():
        if sub_name in selected_substations:
            substations_data.append({
                'name': sub_name,
                'lat': sub_info['lat'],
                'lon': sub_info['lon'],
                'voltage_kv': sub_info['voltage_kv'],
                'operator': sub_info['operator']
            })

    substation_layer = pdk.Layer(
        'ScatterplotLayer',
        data=pd.DataFrame(substations_data),
        get_position='[lon, lat]',
        get_fill_color='[255, 140, 0]',  # Orange
        get_radius=5000,
        pickable=True,
    )

    # Create deck
    deck = pdk.Deck(
        layers=[project_layer, substation_layer],
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/satellite-streets-v11',
        mapbox_key=MAPBOX_API_KEY,
        tooltip={
            'html': '<b>{project_name}</b><br/>'
                   'Developer: {developer}<br/>'
                   'Capacity: {capacity_mw} MW<br/>'
                   'Status: {status}<br/>'
                   'Substation: {substation}',
            'style': {
                'backgroundColor': 'steelblue',
                'color': 'white'
            }
        }
    )

    st.pydeck_chart(deck)
else:
    st.warning("⚠️ Map requires Mapbox API key. Add MAPBOX_ACCESS_TOKEN to secrets.")

st.divider()

# Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 Capacity by Substation")
    capacity_by_sub = filtered_df.groupby('substation')['capacity_mw'].sum().reset_index()
    fig1 = px.bar(
        capacity_by_sub,
        x='substation',
        y='capacity_mw',
        title='Total Capacity by Substation',
        labels={'capacity_mw': 'Capacity (MW)', 'substation': 'Substation'},
        color='capacity_mw',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    st.subheader("📈 Projects by Status")
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    fig2 = px.pie(
        status_counts,
        values='count',
        names='status',
        title='Queue Status Distribution',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Timeline chart
st.subheader("📅 Project Timeline")

# Filter out withdrawn projects for timeline
timeline_df = filtered_df[filtered_df['cod_date'].notna()].copy()

if len(timeline_df) > 0:
    timeline_df['queue_date'] = pd.to_datetime(timeline_df['queue_date'])
    timeline_df['cod_date'] = pd.to_datetime(timeline_df['cod_date'])

    fig3 = px.timeline(
        timeline_df,
        x_start='queue_date',
        x_end='cod_date',
        y='project_name',
        color='status',
        title='Project Queue to COD Timeline',
        labels={'project_name': 'Project'},
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Data table
st.subheader("📋 Queue Data Table")

display_df = filtered_df[[
    'project_name', 'developer', 'capacity_mw', 'substation',
    'status', 'queue_date', 'cod_date', 'project_type'
]].copy()

display_df['capacity_mw'] = display_df['capacity_mw'].apply(lambda x: f"{x:.0f} MW")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        'project_name': 'Project Name',
        'developer': 'Developer',
        'capacity_mw': 'Capacity',
        'substation': 'Substation',
        'status': 'Status',
        'queue_date': 'Queue Date',
        'cod_date': 'COD Date',
        'project_type': 'Type'
    }
)

# Export
st.divider()
st.subheader("📥 Export Data")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name=f'interconnection_queue_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )

with col_exp2:
    st.info("""
    **Data Upload Format:**
    - Required columns: `project_name`, `developer`, `capacity_mw`, `substation`, `status`, `lat`, `lon`
    - Optional columns: `queue_date`, `cod_date`, `project_type`
    - Upload CSV or Excel file
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem; padding: 2rem;'>
    <b>Interconnection Queue Dashboard</b> | Track solar projects by substation<br/>
    Built with Streamlit + PyDeck + Plotly<br/>
    <i>🚀 Powered by Geospatial Solutions LLC</i>
</div>
""", unsafe_allow_html=True)

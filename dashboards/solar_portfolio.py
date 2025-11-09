"""
Solar Portfolio Dashboard - Streamlit Example
Interactive geospatial dashboard showing solar project portfolio with real-time metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Solar Portfolio Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
    }
    .status-green {
        background-color: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }
    .status-yellow {
        background-color: #f59e0b;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }
    .status-red {
        background-color: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data
@st.cache_data
def load_project_data():
    """Generate sample solar project data"""
    np.random.seed(42)

    states = ['CA', 'TX', 'AZ', 'NV', 'FL', 'NC', 'NY', 'MA', 'OR', 'WA', 'CO', 'NM']
    phases = ['Planning', 'Permitting', 'Construction', 'Operational', 'Delayed']

    # State centroids (approximate)
    state_coords = {
        'CA': (36.7783, -119.4179),
        'TX': (31.9686, -99.9018),
        'AZ': (34.0489, -111.0937),
        'NV': (38.8026, -116.4194),
        'FL': (27.6648, -81.5158),
        'NC': (35.7596, -79.0193),
        'NY': (43.2994, -74.2179),
        'MA': (42.4072, -71.3824),
        'OR': (43.8041, -120.5542),
        'WA': (47.7511, -120.7401),
        'CO': (39.5501, -105.7821),
        'NM': (34.5199, -105.8701)
    }

    projects = []
    for i in range(50):
        state = np.random.choice(states)
        lat, lon = state_coords[state]

        # Add random offset for individual projects
        lat_offset = np.random.uniform(-2, 2)
        lon_offset = np.random.uniform(-2, 2)

        phase = np.random.choice(phases, p=[0.15, 0.25, 0.20, 0.35, 0.05])
        capacity_mw = np.random.uniform(10, 200)

        # Status based on phase
        if phase == 'Delayed':
            status = 'High Risk'
            color = [239, 68, 68, 200]  # Red
        elif phase in ['Planning', 'Permitting']:
            status = 'On Track' if np.random.random() > 0.3 else 'At Risk'
            color = [16, 185, 129, 200] if status == 'On Track' else [245, 158, 11, 200]
        else:
            status = 'On Track'
            color = [16, 185, 129, 200]  # Green

        # Generate timeline
        start_date = datetime.now() - timedelta(days=np.random.randint(30, 365))
        expected_completion = start_date + timedelta(days=np.random.randint(180, 540))

        projects.append({
            'id': f'PRJ-{i+1:03d}',
            'name': f'{state} Solar {i+1}',
            'state': state,
            'latitude': lat + lat_offset,
            'longitude': lon + lon_offset,
            'phase': phase,
            'status': status,
            'capacity_mw': round(capacity_mw, 1),
            'buildable_acres': round(capacity_mw * 5.5, 1),  # ~5.5 acres per MW
            'permit_status': np.random.choice(['Pending', 'Approved', 'Under Review']),
            'weather_risk': np.random.choice(['None', 'Low', 'Moderate', 'High'], p=[0.5, 0.3, 0.15, 0.05]),
            'start_date': start_date,
            'expected_completion': expected_completion,
            'color': color,
            'elevation': np.random.randint(50, 300)
        })

    return pd.DataFrame(projects)

# Load data
df = load_project_data()

# Header
st.markdown('<div class="main-header">☀️ Solar Portfolio Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-time monitoring of 50+ solar projects across 12 states</div>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_states = st.sidebar.multiselect(
    "States",
    options=sorted(df['state'].unique()),
    default=sorted(df['state'].unique())
)

selected_phases = st.sidebar.multiselect(
    "Project Phase",
    options=df['phase'].unique(),
    default=df['phase'].unique()
)

selected_status = st.sidebar.multiselect(
    "Status",
    options=df['status'].unique(),
    default=df['status'].unique()
)

capacity_range = st.sidebar.slider(
    "Capacity Range (MW)",
    min_value=float(df['capacity_mw'].min()),
    max_value=float(df['capacity_mw'].max()),
    value=(float(df['capacity_mw'].min()), float(df['capacity_mw'].max()))
)

# Apply filters
filtered_df = df[
    (df['state'].isin(selected_states)) &
    (df['phase'].isin(selected_phases)) &
    (df['status'].isin(selected_status)) &
    (df['capacity_mw'] >= capacity_range[0]) &
    (df['capacity_mw'] <= capacity_range[1])
]

# KPI Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Projects",
        value=len(filtered_df),
        delta=f"{len(filtered_df) - 40} from target"
    )

with col2:
    total_capacity = filtered_df['capacity_mw'].sum()
    st.metric(
        label="Total Capacity",
        value=f"{total_capacity:.1f} MW",
        delta="↑ 12.5%"
    )

with col3:
    on_track = len(filtered_df[filtered_df['status'] == 'On Track'])
    st.metric(
        label="On Track",
        value=f"{on_track}/{len(filtered_df)}",
        delta=f"{(on_track/len(filtered_df)*100):.1f}%"
    )

with col4:
    delayed = len(filtered_df[filtered_df['status'] == 'High Risk'])
    st.metric(
        label="High Risk",
        value=delayed,
        delta=f"-{delayed} from last month",
        delta_color="inverse"
    )

with col5:
    avg_capacity = filtered_df['capacity_mw'].mean()
    st.metric(
        label="Avg Capacity",
        value=f"{avg_capacity:.1f} MW",
        delta="+5.2 MW"
    )

st.divider()

# Main content: Map and Charts
col_map, col_chart = st.columns([2, 1])

with col_map:
    st.subheader("📍 Project Locations")

    # Create PyDeck map with 3D columns
    view_state = pdk.ViewState(
        latitude=filtered_df['latitude'].mean(),
        longitude=filtered_df['longitude'].mean(),
        zoom=3.5,
        pitch=45,
        bearing=0
    )

    # Column layer for 3D bars (height = capacity)
    column_layer = pdk.Layer(
        'ColumnLayer',
        data=filtered_df,
        get_position='[longitude, latitude]',
        get_elevation='capacity_mw * 1000',  # Scale for visibility
        elevation_scale=50,
        radius=25000,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    # Scatterplot layer for markers
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_df,
        get_position='[longitude, latitude]',
        get_radius='capacity_mw * 500',
        get_fill_color='color',
        pickable=True,
        opacity=0.8,
    )

    tooltip = {
        "html": """
        <b>{name}</b><br/>
        Phase: {phase}<br/>
        Status: {status}<br/>
        Capacity: {capacity_mw} MW<br/>
        Permit: {permit_status}<br/>
        Weather Risk: {weather_risk}
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
        map_style='mapbox://styles/mapbox/light-v10'
    )

    st.pydeck_chart(deck)

with col_chart:
    st.subheader("📊 Capacity by State")

    # Capacity by state bar chart
    state_capacity = filtered_df.groupby('state')['capacity_mw'].sum().sort_values(ascending=False).head(10)

    fig_bar = px.bar(
        x=state_capacity.values,
        y=state_capacity.index,
        orientation='h',
        labels={'x': 'Total Capacity (MW)', 'y': 'State'},
        color=state_capacity.values,
        color_continuous_scale='Viridis'
    )
    fig_bar.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Second row: Phase funnel and Timeline
col_funnel, col_timeline = st.columns(2)

with col_funnel:
    st.subheader("🔄 Project Pipeline")

    # Phase distribution funnel
    phase_counts = filtered_df['phase'].value_counts()
    phase_order = ['Planning', 'Permitting', 'Construction', 'Operational', 'Delayed']
    phase_counts = phase_counts.reindex(phase_order, fill_value=0)

    fig_funnel = go.Figure(go.Funnel(
        y=phase_counts.index,
        x=phase_counts.values,
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(
            color=['#60a5fa', '#34d399', '#fbbf24', '#10b981', '#ef4444']
        )
    ))
    fig_funnel.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_timeline:
    st.subheader("📅 Completion Timeline")

    # Timeline scatter plot
    timeline_df = filtered_df[['name', 'expected_completion', 'capacity_mw', 'status']].copy()
    timeline_df['days_to_completion'] = (timeline_df['expected_completion'] - datetime.now()).dt.days
    timeline_df = timeline_df[timeline_df['days_to_completion'] > 0].sort_values('expected_completion').head(15)

    fig_timeline = px.scatter(
        timeline_df,
        x='expected_completion',
        y='name',
        size='capacity_mw',
        color='status',
        color_discrete_map={
            'On Track': '#10b981',
            'At Risk': '#f59e0b',
            'High Risk': '#ef4444'
        },
        labels={'expected_completion': 'Expected Completion', 'name': 'Project'}
    )
    fig_timeline.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis={'categoryorder':'total ascending'}
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

st.divider()

# Project Details Table
st.subheader("📋 Project Details")

# Add status indicators with HTML
def status_badge(status):
    if status == 'On Track':
        return '<span class="status-green">On Track</span>'
    elif status == 'At Risk':
        return '<span class="status-yellow">At Risk</span>'
    else:
        return '<span class="status-red">High Risk</span>'

# Display table
display_df = filtered_df[[
    'id', 'name', 'state', 'phase', 'status',
    'capacity_mw', 'buildable_acres', 'permit_status', 'weather_risk'
]].copy()

display_df = display_df.sort_values('capacity_mw', ascending=False)

st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
    column_config={
        'id': st.column_config.TextColumn('Project ID', width='small'),
        'name': st.column_config.TextColumn('Project Name', width='medium'),
        'state': st.column_config.TextColumn('State', width='small'),
        'phase': st.column_config.TextColumn('Phase', width='medium'),
        'status': st.column_config.TextColumn('Status', width='small'),
        'capacity_mw': st.column_config.NumberColumn('Capacity (MW)', format='%.1f'),
        'buildable_acres': st.column_config.NumberColumn('Buildable Acres', format='%.1f'),
        'permit_status': st.column_config.TextColumn('Permit Status', width='small'),
        'weather_risk': st.column_config.TextColumn('Weather Risk', width='small')
    },
    hide_index=True
)

# Export functionality
st.divider()
col_export1, col_export2, col_export3 = st.columns(3)

with col_export1:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f'solar_portfolio_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )

with col_export2:
    st.button("📧 Email Report", help="Send this dashboard as PDF via email")

with col_export3:
    st.button("🔄 Refresh Data", help="Pull latest data from APIs")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.875rem;'>
    🤖 Generated with Agentic GIS | Last updated: {}<br/>
    Data sources: PostGIS, NOAA API, County Permitting Portals, Survey123
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

"""
Real Estate Site Suitability Dashboard - Streamlit Example
Buildable land analysis with constraint overlays and multi-criteria scoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Site Suitability Dashboard",
    page_icon="🏗️",
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
    .constraint-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        margin: 0.25rem;
    }
    .constraint-flood { background-color: #3b82f6; color: white; }
    .constraint-wetland { background-color: #10b981; color: white; }
    .constraint-slope { background-color: #f59e0b; color: white; }
    .constraint-zoning { background-color: #8b5cf6; color: white; }
</style>
""", unsafe_allow_html=True)

# Generate sample parcel data
@st.cache_data
def load_parcel_data():
    """Generate sample parcel suitability data"""
    np.random.seed(42)

    # Mock data for 200 parcels
    parcels = []
    for i in range(200):
        # Random location in central California
        lat = np.random.uniform(36.5, 37.5)
        lon = np.random.uniform(-121.5, -120.5)

        # Total acreage
        total_acres = np.random.uniform(2, 15)

        # Constraints (randomly assign)
        flood_acres = np.random.uniform(0, min(2, total_acres * 0.3)) if np.random.random() < 0.25 else 0
        wetland_acres = np.random.uniform(0, min(1.5, total_acres * 0.2)) if np.random.random() < 0.20 else 0
        steep_slope_acres = np.random.uniform(0, min(1, total_acres * 0.15)) if np.random.random() < 0.30 else 0
        setback_acres = np.random.uniform(0.3, min(0.8, total_acres * 0.1))

        # Calculate buildable area
        constrained_acres = flood_acres + wetland_acres + steep_slope_acres + setback_acres
        buildable_acres = max(0, total_acres - constrained_acres)

        # Suitability score (0-100)
        buildable_ratio = buildable_acres / total_acres
        score = int(buildable_ratio * 100)

        # Recommendation
        if buildable_acres >= 5:
            recommendation = 'GO'
            color = [16, 185, 129, 200]  # Green
        elif buildable_acres >= 2:
            recommendation = 'CONDITIONAL'
            color = [245, 158, 11, 200]  # Yellow/Orange
        else:
            recommendation = 'NO-GO'
            color = [239, 68, 68, 200]  # Red

        # Zoning
        zoning = np.random.choice(['R-1', 'R-2', 'R-3', 'MU', 'C-1'], p=[0.3, 0.25, 0.2, 0.15, 0.1])

        # Land cost per acre
        cost_per_acre = np.random.uniform(50000, 200000)

        parcels.append({
            'parcel_id': f'APN-{1000+i}',
            'latitude': lat,
            'longitude': lon,
            'total_acres': round(total_acres, 2),
            'flood_acres': round(flood_acres, 2),
            'wetland_acres': round(wetland_acres, 2),
            'slope_acres': round(steep_slope_acres, 2),
            'setback_acres': round(setback_acres, 2),
            'buildable_acres': round(buildable_acres, 2),
            'suitability_score': score,
            'recommendation': recommendation,
            'zoning': zoning,
            'cost_per_acre': round(cost_per_acre, 0),
            'total_cost': round(total_acres * cost_per_acre, 0),
            'color': color,
            'elevation': np.random.randint(100, 500)
        })

    return pd.DataFrame(parcels)

# Load data
df = load_parcel_data()

# Header
st.markdown('<div class="main-header">🏗️ Real Estate Site Suitability Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
<div style='font-size: 1.1rem; color: #6b7280; margin-bottom: 2rem;'>
    Buildable land analysis for 200 parcels with automated constraint detection
</div>
""", unsafe_allow_html=True)

# Sidebar - Filters
st.sidebar.header("🔍 Suitability Filters")

min_buildable = st.sidebar.slider(
    "Minimum Buildable Acres",
    min_value=0.0,
    max_value=float(df['buildable_acres'].max()),
    value=2.0,
    step=0.5
)

max_cost = st.sidebar.slider(
    "Maximum Total Cost ($)",
    min_value=int(df['total_cost'].min()),
    max_value=int(df['total_cost'].max()),
    value=int(df['total_cost'].max()),
    step=50000,
    format="$%d"
)

selected_zoning = st.sidebar.multiselect(
    "Zoning Designations",
    options=sorted(df['zoning'].unique()),
    default=sorted(df['zoning'].unique())
)

selected_recommendations = st.sidebar.multiselect(
    "Recommendations",
    options=['GO', 'CONDITIONAL', 'NO-GO'],
    default=['GO', 'CONDITIONAL']
)

# Apply filters
filtered_df = df[
    (df['buildable_acres'] >= min_buildable) &
    (df['total_cost'] <= max_cost) &
    (df['zoning'].isin(selected_zoning)) &
    (df['recommendation'].isin(selected_recommendations))
].copy()

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Qualified Parcels",
        value=len(filtered_df),
        delta=f"{len(filtered_df[filtered_df['recommendation']=='GO'])} GO parcels"
    )

with col2:
    avg_buildable = filtered_df['buildable_acres'].mean()
    st.metric(
        label="Avg Buildable Acres",
        value=f"{avg_buildable:.1f}",
        delta=f"{(avg_buildable/filtered_df['total_acres'].mean()*100):.0f}% of total"
    )

with col3:
    total_buildable = filtered_df['buildable_acres'].sum()
    st.metric(
        label="Total Buildable Area",
        value=f"{total_buildable:.1f} ac",
        delta=f"~{int(total_buildable * 43560)} sq ft"
    )

with col4:
    go_parcels = len(filtered_df[filtered_df['recommendation'] == 'GO'])
    st.metric(
        label="GO Parcels",
        value=go_parcels,
        delta=f"{(go_parcels/len(filtered_df)*100):.0f}% of qualified"
    )

with col5:
    avg_score = filtered_df['suitability_score'].mean()
    st.metric(
        label="Avg Suitability",
        value=f"{avg_score:.0f}/100",
        delta="High confidence"
    )

st.divider()

# Main content
col_map, col_analysis = st.columns([2, 1])

with col_map:
    st.subheader("📍 Parcel Suitability Map")

    # Layer selector
    layer_type = st.radio(
        "Map View",
        options=['Suitability Score', 'Constraints'],
        horizontal=True
    )

    if layer_type == 'Suitability Score':
        # 3D column layer
        view_state = pdk.ViewState(
            latitude=filtered_df['latitude'].mean(),
            longitude=filtered_df['longitude'].mean(),
            zoom=9,
            pitch=45,
            bearing=0
        )

        column_layer = pdk.Layer(
            'ColumnLayer',
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_elevation='suitability_score * 100',
            elevation_scale=10,
            radius=200,
            get_fill_color='color',
            pickable=True,
            auto_highlight=True,
            extruded=True,
        )

        tooltip = {
            "html": """
            <b>{parcel_id}</b><br/>
            <b>Suitability: {suitability_score}/100</b><br/>
            Recommendation: <b>{recommendation}</b><br/>
            Buildable: {buildable_acres} acres<br/>
            Total: {total_acres} acres<br/>
            Zoning: {zoning}<br/>
            Cost: ${total_cost:,.0f}
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
            map_style='mapbox://styles/mapbox/satellite-streets-v11'
        )

        st.pydeck_chart(deck)

    else:
        # Heatmap for constraints
        view_state = pdk.ViewState(
            latitude=filtered_df['latitude'].mean(),
            longitude=filtered_df['longitude'].mean(),
            zoom=9,
            pitch=0,
            bearing=0
        )

        # Calculate total constraint acres
        filtered_df['total_constraints'] = (
            filtered_df['flood_acres'] +
            filtered_df['wetland_acres'] +
            filtered_df['slope_acres'] +
            filtered_df['setback_acres']
        )

        heatmap_layer = pdk.Layer(
            'HeatmapLayer',
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_weight='total_constraints',
            radius_pixels=50,
            intensity=1,
            threshold=0.05,
        )

        scatter_layer = pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_radius=100,
            get_fill_color=[255, 255, 255, 100],
            pickable=True,
        )

        deck = pdk.Deck(
            layers=[heatmap_layer, scatter_layer],
            initial_view_state=view_state,
            map_style='mapbox://styles/mapbox/dark-v10'
        )

        st.pydeck_chart(deck)

with col_analysis:
    st.subheader("🎯 Suitability Distribution")

    # Score histogram
    fig_hist = px.histogram(
        filtered_df,
        x='suitability_score',
        nbins=20,
        color='recommendation',
        color_discrete_map={
            'GO': '#10b981',
            'CONDITIONAL': '#f59e0b',
            'NO-GO': '#ef4444'
        },
        labels={'suitability_score': 'Suitability Score', 'count': 'Parcels'}
    )
    fig_hist.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=True
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# Constraint Analysis
col_const1, col_const2 = st.columns(2)

with col_const1:
    st.subheader("⚠️ Constraint Breakdown")

    # Stacked bar chart of constraints
    constraint_summary = pd.DataFrame({
        'Constraint Type': ['Flood Zone', 'Wetlands', 'Steep Slope', 'Setbacks'],
        'Total Acres': [
            filtered_df['flood_acres'].sum(),
            filtered_df['wetland_acres'].sum(),
            filtered_df['slope_acres'].sum(),
            filtered_df['setback_acres'].sum()
        ],
        'Parcels Affected': [
            len(filtered_df[filtered_df['flood_acres'] > 0]),
            len(filtered_df[filtered_df['wetland_acres'] > 0]),
            len(filtered_df[filtered_df['slope_acres'] > 0]),
            len(filtered_df[filtered_df['setback_acres'] > 0])
        ]
    })

    fig_constraints = px.bar(
        constraint_summary,
        x='Constraint Type',
        y='Total Acres',
        color='Constraint Type',
        text='Parcels Affected',
        color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
    )
    fig_constraints.update_traces(texttemplate='%{text} parcels', textposition='outside')
    fig_constraints.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig_constraints, use_container_width=True)

with col_const2:
    st.subheader("💰 Cost vs. Buildable Area")

    # Scatter plot
    fig_scatter = px.scatter(
        filtered_df,
        x='buildable_acres',
        y='total_cost',
        size='suitability_score',
        color='recommendation',
        color_discrete_map={
            'GO': '#10b981',
            'CONDITIONAL': '#f59e0b',
            'NO-GO': '#ef4444'
        },
        hover_data=['parcel_id', 'zoning'],
        labels={
            'buildable_acres': 'Buildable Acres',
            'total_cost': 'Total Cost ($)',
            'suitability_score': 'Score'
        }
    )
    fig_scatter.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# Top Parcels Table
st.subheader("🏆 Top Qualified Parcels")

top_parcels = filtered_df.sort_values('suitability_score', ascending=False).head(20)

st.dataframe(
    top_parcels[[
        'parcel_id', 'total_acres', 'buildable_acres',
        'suitability_score', 'recommendation', 'zoning',
        'flood_acres', 'wetland_acres', 'slope_acres',
        'total_cost'
    ]],
    use_container_width=True,
    height=400,
    column_config={
        'parcel_id': st.column_config.TextColumn('Parcel ID', width='small'),
        'total_acres': st.column_config.NumberColumn('Total (ac)', format='%.2f'),
        'buildable_acres': st.column_config.NumberColumn('Buildable (ac)', format='%.2f'),
        'suitability_score': st.column_config.ProgressColumn(
            'Score',
            min_value=0,
            max_value=100,
            format='%d'
        ),
        'recommendation': st.column_config.TextColumn('Rec.', width='small'),
        'zoning': st.column_config.TextColumn('Zone', width='small'),
        'flood_acres': st.column_config.NumberColumn('Flood', format='%.2f'),
        'wetland_acres': st.column_config.NumberColumn('Wetland', format='%.2f'),
        'slope_acres': st.column_config.NumberColumn('Slope', format='%.2f'),
        'total_cost': st.column_config.NumberColumn('Cost', format='$%d')
    },
    hide_index=True
)

# AI Summary Section
st.divider()
st.subheader("🤖 AI-Generated Summary")

go_count = len(filtered_df[filtered_df['recommendation'] == 'GO'])
conditional_count = len(filtered_df[filtered_df['recommendation'] == 'CONDITIONAL'])
avg_buildable = filtered_df['buildable_acres'].mean()
top_parcel = filtered_df.sort_values('suitability_score', ascending=False).iloc[0]

summary_text = f"""
**Analysis Complete: {len(filtered_df)} Parcels Screened**

Based on the constraint analysis, **{go_count} parcels** receive a **GO recommendation** with an average buildable area of **{avg_buildable:.1f} acres**. An additional **{conditional_count} parcels** are marked as **CONDITIONAL**, requiring further site-specific analysis.

**Top Recommendation:**
Parcel **{top_parcel['parcel_id']}** shows the highest suitability with **{top_parcel['buildable_acres']:.1f} buildable acres** out of {top_parcel['total_acres']:.1f} total acres. This parcel has minimal constraints ({top_parcel['flood_acres']:.1f} ac flood, {top_parcel['wetland_acres']:.1f} ac wetland, {top_parcel['slope_acres']:.1f} ac slope) and is zoned **{top_parcel['zoning']}** at a total cost of **${top_parcel['total_cost']:,.0f}**.

**Key Constraints:**
- Flood zones impact {len(filtered_df[filtered_df['flood_acres'] > 0])} parcels
- Wetlands impact {len(filtered_df[filtered_df['wetland_acres'] > 0])} parcels
- Steep slopes (>15%) impact {len(filtered_df[filtered_df['slope_acres'] > 0])} parcels

**Next Steps:**
Recommend proceeding with due diligence on the top 10 GO-rated parcels. Consider clustering development on parcels with >5 buildable acres to reduce infrastructure costs.
"""

st.info(summary_text)

# Export
st.divider()
col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)

with col_exp1:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f'suitability_analysis_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )

with col_exp2:
    st.button("🗺️ Export Shapefile", help="Download parcels as Shapefile for GIS")

with col_exp3:
    st.button("📄 Generate PDF Report", help="Create detailed PDF with maps and analysis")

with col_exp4:
    st.button("📧 Email to Stakeholders", help="Send summary via email")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.875rem;'>
    🤖 Powered by Agentic GIS | Analysis run: {}<br/>
    Data sources: County Assessor API, FEMA NFHL, USFWS Wetlands, USGS 3DEP Slope Analysis<br/>
    Processing time: 12 minutes for 200 parcels
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

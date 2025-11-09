# Streamlit GIS Dashboards

Interactive geospatial dashboards powered by Streamlit, integrated with Geospatial Solutions website.

## 🚀 Live Dashboards

- **Solar API Live:** [solar-api-live.streamlit.app](https://solar-api-live.streamlit.app/)
- **Solar Portfolio:** [solar-portfolio.streamlit.app](https://solar-portfolio.streamlit.app/)
- **Real Estate Suitability:** [real-estate-suitability.streamlit.app](https://real-estate-suitability.streamlit.app/)
- **Interconnection Queue:** (Deploy with your substation data)

**Embedded in website:** [geospatialsolutions.co/solutions/interactive-dashboards/demo](https://geospatialsolutions.co/solutions/interactive-dashboards/demo)

## Available Dashboards

### 1. Solar API Live (`dashboards/solar_api_live.py`) ✅ LIVE
   - **Real-time data** from NREL, Census, FRED APIs
   - **Operator/Owner dropdown** (Energix, NextEra, etc.)
   - **Project stage tracking** (Pre-Dev to Operational)
   - **3D PyDeck maps** with satellite imagery
   - **Financial feasibility calculator**
   - **Live API status monitoring**

### 2. Solar Portfolio Dashboard (`dashboards/solar_portfolio.py`) ✅ LIVE
   - Portfolio-level project monitoring
   - 50+ solar projects across 12 states
   - AI-powered insights with Claude
   - Weather risk alerts
   - Permit status tracking

### 3. Real Estate Suitability (`dashboards/real_estate_suitability.py`) ✅ LIVE
   - Automated buildable land analysis
   - 200 parcels analyzed in 12 minutes
   - Constraint detection (flood, wetlands, slope, zoning)
   - AI-powered recommendations
   - Multi-criteria suitability scoring

### 4. Interconnection Queue (`dashboards/interconnection_queue.py`) 🆕
   - **Track solar projects by substation**
   - **Transmission line visualization**
   - **Filter by operator, status, capacity**
   - **3D column charts scaled by MW**
   - **Timeline view: Queue date → COD**
   - **Upload your own CSV/Excel queue data**
   - **Export filtered results**

## Setup

### Prerequisites
- Python 3.9+
- Vercel account (for deployment)
- API keys (automatically loaded from Vercel environment variables)

### Local Development

1. **Install dependencies:**
   ```bash
   cd streamlit
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   # Copy from Vercel environment variables
   NREL_API_KEY=your_key_here
   CENSUS_API_KEY=your_key_here
   MAPBOX_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   GOOGLE_MAPS_API_KEY=your_key_here
   ```

3. **Run dashboard:**
   ```bash
   streamlit run dashboards/solar_portfolio.py
   ```

   Or:
   ```bash
   streamlit run dashboards/real_estate_suitability.py
   ```

## Deployment

### Option 1: Streamlit Community Cloud (Recommended)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from repository
4. Add secrets (API keys) in Streamlit Cloud settings

### Option 2: Docker + Vercel

1. Build Docker image:
   ```bash
   docker build -t streamlit-gis .
   ```

2. Deploy to Vercel:
   ```bash
   vercel deploy
   ```

## Integration with Next.js Website

Embed dashboards in Next.js pages using iframe:

```typescript
// app/(services)/solutions/interactive-dashboards/demo/page.tsx

export default function DashboardDemoPage() {
  return (
    <div className="h-screen">
      <iframe
        src="https://your-streamlit-app.streamlit.app"
        className="w-full h-full border-0"
        title="Interactive Dashboard Demo"
      />
    </div>
  );
}
```

## API Usage

### NREL Solar API
```python
import requests
import os

NREL_API_KEY = os.getenv('NREL_API_KEY')

# Solar resource data
response = requests.get(
    f'https://developer.nrel.gov/api/solar/solar_resource/v1.json',
    params={
        'api_key': NREL_API_KEY,
        'lat': 40.7128,
        'lon': -74.0060
    }
)
solar_data = response.json()
```

### Census API
```python
import requests
import os

CENSUS_API_KEY = os.getenv('CENSUS_API_KEY')

# Get population by county
response = requests.get(
    f'https://api.census.gov/data/2021/acs/acs5',
    params={
        'get': 'B01003_001E,NAME',
        'for': 'county:*',
        'in': 'state:06',  # California
        'key': CENSUS_API_KEY
    }
)
population_data = response.json()
```

### Anthropic Claude API (for AI summaries)
```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Analyze this solar project data and provide recommendations..."}
    ]
)

summary = message.content[0].text
```

## Dashboard Features

- ✅ Real-time API data fetching
- ✅ 3D geospatial visualizations (PyDeck)
- ✅ Interactive charts (Plotly)
- ✅ AI-generated summaries (Anthropic Claude)
- ✅ Export to CSV, PDF, Shapefile
- ✅ Email report functionality
- ✅ Responsive design

## Customization

To create a new dashboard:

1. Create new file in `dashboards/your_dashboard.py`
2. Follow the template structure from existing dashboards
3. Add to navigation in `Home.py` (if using multi-page app)
4. Deploy and get shareable URL

## Performance

- Caching with `@st.cache_data` for API calls
- Lazy loading for large datasets
- Debounced filters to reduce re-renders
- Optimized map rendering with PyDeck

## Support

For issues or questions:
- GitHub Issues: [your-repo]/issues
- Email: support@geospatialsolutions.co

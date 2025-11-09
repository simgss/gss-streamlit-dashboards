# Streamlit GIS Dashboards

Interactive geospatial dashboards powered by Streamlit, integrated with Geospatial Solutions website.

## Available Dashboards

1. **Solar Portfolio Dashboard** (`dashboards/solar_portfolio.py`)
   - Real-time solar project monitoring
   - Uses: NREL Solar API, Mapbox, Census API
   - 3D map visualization with PyDeck

2. **Real Estate Suitability** (`dashboards/real_estate_suitability.py`)
   - Buildable land constraint analysis
   - Uses: Census API, Mapbox, Google Maps API
   - Multi-criteria suitability scoring

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

# Deploy to Streamlit Cloud

Quick deployment guide for these Streamlit dashboards.

## Quick Start

1. **Sign in to Streamlit Cloud** with GitHub: [share.streamlit.io](https://share.streamlit.io)

2. **Click "New app"** and fill in:
   - Repository: `simgss/gss-streamlit-dashboards`
   - Branch: `main`
   - Main file path: Choose one below

## Available Dashboards

### 1. Solar API Live Dashboard
**Main file path:** `dashboards/solar_api_live.py`

Real-time solar resource data from NREL API, demographics from Census Bureau, and economic indicators.

**Required Secrets:**
```toml
NREL_API_KEY = "your_nrel_api_key"
CENSUS_API_KEY = "your_census_api_key"
FRED_API_KEY = "your_fred_api_key"
MAPBOX_ACCESS_TOKEN = "your_mapbox_token"
```

### 2. Solar Portfolio Dashboard
**Main file path:** `dashboards/solar_portfolio.py`

Portfolio-level solar monitoring with AI-powered insights.

**Required Secrets:**
```toml
NREL_API_KEY = "your_nrel_api_key"
CENSUS_API_KEY = "your_census_api_key"
MAPBOX_ACCESS_TOKEN = "your_mapbox_token"
ANTHROPIC_API_KEY = "your_anthropic_key"
```

### 3. Real Estate Suitability Dashboard
**Main file path:** `dashboards/real_estate_suitability.py`

Real estate development suitability analysis with demographic overlay.

**Required Secrets:**
```toml
CENSUS_API_KEY = "your_census_api_key"
MAPBOX_ACCESS_TOKEN = "your_mapbox_token"
GOOGLE_MAPS_API_KEY = "your_google_maps_key"
ANTHROPIC_API_KEY = "your_anthropic_key"
```

## Get API Keys

### NREL Solar API (FREE)
- Sign up: [developer.nrel.gov/signup](https://developer.nrel.gov/signup/)
- Instant key via email

### US Census Bureau (FREE)
- Sign up: [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)
- Key sent via email

### FRED Economic Data (FREE)
- Sign up: [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
- Create account and request API key

### Mapbox (FREE tier)
- Sign up: [account.mapbox.com](https://account.mapbox.com)
- Copy default public token

### Google Maps API (FREE tier)
- Console: [console.cloud.google.com](https://console.cloud.google.com)
- Enable Maps JavaScript API
- Create credentials

### Anthropic Claude (Pay-per-use)
- Console: [console.anthropic.com](https://console.anthropic.com)
- Generate API key
- ~$0.003 per request

## Adding Secrets to Streamlit Cloud

When deploying:

1. Click **"Advanced settings"** before deploying
2. Paste your secrets in TOML format
3. Click **"Deploy"**

To update secrets later:
1. Go to app settings
2. Select **"Secrets"**
3. Edit and save

## Local Testing (Optional)

```bash
# Clone repository
git clone https://github.com/simgss/gss-streamlit-dashboards.git
cd gss-streamlit-dashboards

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .streamlit/secrets.toml with your API keys
mkdir .streamlit
# Add your API keys to .streamlit/secrets.toml

# Run dashboard
streamlit run dashboards/solar_api_live.py
```

## Embed in Website

After deployment, embed in your website using iframes:

```html
<iframe
  src="https://your-app-name.streamlit.app"
  width="100%"
  height="800px"
  frameborder="0"
></iframe>
```

## Auto-Deployment

Any push to `main` branch automatically redeploys all apps on Streamlit Cloud!

## Support

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Main Website**: [geospatialsolutions.co](https://geospatialsolutions.co)

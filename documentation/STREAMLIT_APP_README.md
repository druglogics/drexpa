# DREXPA Streamlit Web Application

A user-friendly web interface for the DREXPA bioinformatics pipeline.

## Features

- 📤 **Easy File Upload** - Upload drug names, screening data, and gene mappings
- ⚙️ **Flexible Configuration** - Choose pipeline steps and customize options
- 🚀 **Pipeline Execution** - Run the pipeline with progress tracking
- 📊 **Interactive Results** - View tables, statistics, and visualizations
- ⬇️ **Download All** - Export all results as CSV files and ZIP archives

## Quick Start (Local)

### Prerequisites
- Python 3.8+
- pip or conda

### Installation & Run

```bash
# 1. Navigate to the DREXPA directory
cd DREXPA

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit app
streamlit run drexpa/streamlit_app.py
```

The app will open at `http://localhost:8501`

## Deployment Options

### Option 1: Streamlit Cloud (Public, Simplest)

**Pros:** Auto-deploys on push, free tier, public URL
**Cons:** Data processed on Streamlit servers

1. Push this repo to GitHub
2. Create account at [streamlit.io](https://streamlit.io)
3. Click "New app" → Select your GitHub repo and `streamlit_app.py`
4. App auto-deploys and gets a public URL like `https://yourname-drexpa.streamlit.app`

Public URL will be automatically generated and can be shared.

### Option 2: Docker (Private, Reproducible)

**Pros:** Full control, data stays private, reproducible environment
**Cons:** Requires Docker, local or self-hosted deployment

```bash
# Build Docker image
docker build -t drexpa-app .

# Run container
docker run -p 8501:8501 drexpa-app

# Access at http://localhost:8501
```

Or deploy to free platforms:
- **Render**: Push Dockerfile to GitHub, deploy from Render dashboard
- **Railway**: Similar to Render, free tier available

### Option 3: GitHub Pages (Static, Advanced)

For a static export (less interactive):

```bash
streamlit run streamlit_app.py --server.headless true --server.fileWatcherType none
```

Requires custom GitHub Actions workflow (advanced setup).

## Usage

1. **Upload Data** - Provide required files:
   - `drug_names.txt` - One drug per line
   - `synergy_data.csv` - Drug screening results
   - `node_dict.csv` - Gene → Node mapping
   - Optional: `tissue_cline.csv`, `manual_chembl.csv`

2. **Configure** - Select pipeline steps and options:
   - Choose which steps to run
   - Adjust thresholds and parameters
   - Map custom column names if needed

3. **Execute** - Click "Run Pipeline" and monitor progress

4. **Download** - View results as tables and download all files

## File Structure

```
DREXPA/
├── streamlit_app.py              # Main app
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── .streamlit/config.toml        # Streamlit settings
├── app_utils/                    # Helper modules
│   ├── __init__.py
│   ├── file_handlers.py         # Upload validation
│   ├── pipeline_runner.py       # Pipeline execution
│   └── visualizations.py        # Charts and plots
└── README.md                     # This file
```

## Troubleshooting

**Issue: "ModuleNotFoundError: No module named 'drexpa'"**
- Ensure you're in the DREXPA directory when running: `pwd` should end with `/DREXPA`
- Install dependencies: `pip install -r requirements.txt`

**Issue: "Permission denied" when running Docker**
- On Windows: Use `docker run` (PowerShell or CMD)
- On Mac/Linux: May need `sudo docker run`

**Issue: Streamlit Cloud deployment fails**
- Check `requirements.txt` is in repo root
- Ensure GitHub repo is public (or grant Streamlit Cloud access)
- Check for any private dependencies in imports

## Configuration

### Streamlit Settings

Edit `.streamlit/config.toml` to customize:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"

[client]
maxUploadSize = 200  # MB

[logger]
level = "info"
```

### DREXPA Pipeline

All DREXPA configuration options are exposed in the app's "Configuration" page:
- Pipeline steps
- Synergy thresholds
- Column name mappings
- Target merge strategies

See [DREXPA docs](./README.md) for detailed configuration.

## Development

### Adding Features

1. **New Visualization**: Add function to `app_utils/visualizations.py`, import in `streamlit_app.py`
2. **New Configuration Option**: Add to Configuration page, update `app_utils/pipeline_runner.py`
3. **New Results Display**: Add tab in Results page, load from output directory

### Testing Locally

```bash
# Run with sample data
streamlit run streamlit_app.py

# Upload files from data/input/oncologics/ or create minimal test files
```

## Support

- **DREXPA Documentation**: See main `README.md`
- **Streamlit Docs**: https://docs.streamlit.io
- **Issues**: GitHub Issues (if using GitHub for deployment)

## License

Same as DREXPA package.

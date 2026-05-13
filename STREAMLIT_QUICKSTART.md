# 🚀 DREXPA Streamlit App - Quick Start Guide

Your DREXPA web application is ready! Here's how to get started.

## 📋 What Was Built

A complete Streamlit web application with:

✅ **File Upload Interface** - Users upload drug data and configurations  
✅ **Advanced Configuration Panel** - Control every pipeline parameter  
✅ **Pipeline Execution** - Run DREXPA with progress tracking  
✅ **Interactive Results** - View tables, stats, and visualizations  
✅ **Easy Downloads** - Export all outputs as CSV files  
✅ **Multiple Deployment Options** - Local, Docker, or cloud  

## 🎯 Files Created

```
DREXPA/
├── streamlit_app.py              ← Main application
├── requirements.txt              ← Python dependencies  
├── Dockerfile                    ← For Docker deployment
├── .streamlit/config.toml        ← Streamlit settings
├── app_utils/                    ← Helper modules
│   ├── __init__.py
│   ├── file_handlers.py         ← Upload validation
│   ├── pipeline_runner.py       ← Execute pipeline
│   └── visualizations.py        ← Generate charts
├── test_data/                    ← Sample data for testing
│   ├── drug_names.txt
│   ├── synergy_data.csv
│   ├── node_dict.csv
│   └── tissue_cline.csv
├── STREAMLIT_APP_README.md       ← App documentation
└── DEPLOYMENT_GUIDE.md           ← Complete deployment instructions
```

## ⚡ Run Locally (5 seconds)

```bash
cd "path/to/DREXPA"
streamlit run drexpa/streamlit_app.py
```

Opens automatically at `http://localhost:8501`

**Test with sample data:** Use files in `test_data/` folder

## 🌐 Deploy to Public Web (Choose One)

### **Option 1: Streamlit Cloud (Easiest - 5 minutes)**

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Select your repo and `streamlit_app.py`
4. Deploy
5. Get public URL: `https://username-drexpa.streamlit.app`

➜ **See DEPLOYMENT_GUIDE.md for detailed steps**

### **Option 2: Docker (Private - 15 minutes)**

```bash
docker build -t drexpa-app .
docker run -p 8501:8501 drexpa-app
```

Deploy to Render, Railway, or AWS with auto-deployment from GitHub.

➜ **See DEPLOYMENT_GUIDE.md for detailed steps**

### **Option 3: GitHub (Manual - 30 minutes)**

For advanced users: Static export to GitHub Pages with custom domain.

➜ **See DEPLOYMENT_GUIDE.md for detailed steps**

## 🎮 Using the App

1. **Upload Data** Tab
   - `drug_names.txt` (required)
   - `synergy_data.csv` (required)
   - `node_dict.csv` (required)
   - Optional: `tissue_cline.csv`, `manual_chembl.csv`

2. **Configuration** Tab
   - Select which pipeline steps to run
   - Adjust parameters (thresholds, options)
   - Customize column names if needed
   - Output files go to `drexpa/` folder (by default) to keep organized

3. **Execute Pipeline** Tab
   - Click "Run Pipeline"
   - Monitor progress in real-time
   - View logs as pipeline executes

4. **Results** Tab
   - See summary statistics
   - Browse interactive tables
   - View charts and network diagram
   - Download individual files or all as ZIP

## 📊 Key Features

### Interactive Tables
- Drug profiles with unique IDs
- Drug-target mappings
- Drug panel in DrugLogics format
- All columns sortable and searchable

### Visualizations
- 📊 **Bar chart** - Targets per drug
- 🔥 **Heatmap** - Drug-target interactions  
- 🕸️ **Network diagram** - Interaction graph

### Advanced Configuration
- Full control over all DREXPA pipeline steps
- Custom column name mapping
- Threshold adjustments
- Target merge strategies

## 🔧 Technical Details

**Built with:**
- Streamlit - Web framework
- Pandas - Data handling
- Plotly - Interactive charts
- DREXPA - Bioinformatics pipeline

**Python Version:** 3.8+  
**Dependencies:** See `requirements.txt`  
**License:** Same as DREXPA package

## 📚 Documentation

- **STREAMLIT_APP_README.md** - Complete app documentation
- **DEPLOYMENT_GUIDE.md** - Deployment instructions for all platforms
- **DREXPA README.md** - Original DREXPA documentation

## ⚠️ Important Notes

### Data Privacy
- **Local/Docker**: Data never leaves your computer ✅
- **Streamlit Cloud**: Files stored temporarily on Streamlit servers (auto-deleted)

Choose Docker if handling sensitive data.

### Requirements for Running
- Python 3.8+ installed
- pip or conda package manager
- For Docker: Docker installed

### First Run
- First run may take longer (installing dependencies, loading data)
- Subsequent runs are faster

## 🐛 Troubleshooting

**"ModuleNotFoundError: No module named 'drexpa'"**
- Ensure you're in the DREXPA directory: `pwd`
- Install dependencies: `pip install -r requirements.txt`

**Port 8501 already in use**
- Use different port: `streamlit run streamlit_app.py --server.port 8502`

**File upload fails**
- Check file format matches expected (CSV, TXT)
- Verify required columns are present

**Streamlit Cloud deployment fails**
- Ensure `requirements.txt` is in repo root
- Check GitHub repo is public or grant Streamlit access
- Look at deployment logs in Streamlit dashboard

## 🚀 Next Steps

1. **Test locally** with sample data in `test_data/`
2. **Choose deployment option** (Cloud is easiest)
3. **Follow deployment instructions** in DEPLOYMENT_GUIDE.md
4. **Share your public link!** 🎉

## 📞 Support

- **App issues?** Check STREAMLIT_APP_README.md
- **Deployment help?** See DEPLOYMENT_GUIDE.md
- **DREXPA pipeline?** Check main DREXPA documentation
- **Streamlit docs:** https://docs.streamlit.io

---

**Ready to go?** Run: `streamlit run streamlit_app.py` 🎯

Questions? See the detailed documentation files!

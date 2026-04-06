# ✈️ Aerospace Alloy Raw Material Cost Tracker — Cloud Version

Cloud-deployed Streamlit app for tracking aerospace aluminum alloy raw material costs.
Access from any device (PC, iPhone, iPad) via web browser.

## Deployment Guide (Step by Step)

### Prerequisites (already done)
- ✅ GitHub account: `achim-amc`
- ✅ Turso database: `alloy-tracker` (EU West)
- ✅ Turso URL and auth token saved

### Step 1: Create the GitHub Repository

1. Go to https://github.com/new
2. Repository name: `alloy-cost-tracker`
3. Set to **Private**
4. Click "Create repository"
5. You'll see a page with setup instructions — keep it open

### Step 2: Upload the Code

**Option A — via GitHub web interface (easiest):**
1. On your new repo page, click "uploading an existing file"
2. Drag ALL files from this folder into the upload area
3. Click "Commit changes"
4. ALSO create the `.streamlit` folder:
   - Click "Add file" → "Create new file"
   - Name it: `.streamlit/secrets.toml.example`
   - Paste the contents of the example file
   - Click "Commit changes"

**Option B — via command line:**
```bash
cd path/to/this/folder
git init
git add .
git commit -m "Initial deploy"
git branch -M main
git remote add origin https://github.com/achim-amc/alloy-cost-tracker.git
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - Repository: `achim-amc/alloy-cost-tracker`
   - Branch: `main`
   - Main file: `app.py`
5. Click **"Advanced settings"** → **"Secrets"**
6. Paste this (with YOUR real values):

```toml
[turso]
url = "libsql://alloy-tracker-achim-amc.aws-eu-west-1.turso.io"
token = "YOUR_FULL_TURSO_TOKEN"

[app]
password = "CHOOSE_YOUR_PASSWORD"
```

7. Click "Deploy"
8. Wait 2-3 minutes — your app will be live at:
   `https://alloy-cost-tracker-achim-amc.streamlit.app`

### Step 4: Seed Historical Data

After deployment, open a terminal and run:
```bash
pip install libsql-experimental
export TURSO_URL="libsql://alloy-tracker-achim-amc.aws-eu-west-1.turso.io"
export TURSO_TOKEN="YOUR_FULL_TURSO_TOKEN"
python seed_history.py
```

This loads 35 historical data points (Jan 2024 — Mar 2026) into the cloud database.

### Step 5: Add to iPhone Home Screen

1. Open Safari on your iPhone
2. Go to your app URL
3. Enter your password
4. Tap the **Share** button (square with arrow)
5. Tap **"Add to Home Screen"**
6. Name it "Alloy Tracker"
7. Tap "Add"

Now it appears as an app icon on your iPhone.

## File Structure

```
alloy-cost-tracker/
├── app.py                          # Main Streamlit app (Turso cloud DB)
├── config.py                       # Alloy compositions, conversion params
├── cost_engine.py                  # Cost calculation logic
├── price_fetcher.py                # Live price scraping
├── excel_export.py                 # Excel workbook generator
├── seed_history.py                 # Historical data seeder
├── requirements.txt                # Python dependencies
├── .gitignore                      # Excludes secrets from git
├── .streamlit/
│   └── secrets.toml.example        # Template for credentials
└── README.md                       # This file
```

## Local App

Your local version at `C:\Users\achim\Downloads\alloy_cost_tracker\` is
completely independent and unaffected. It continues to use local SQLite.

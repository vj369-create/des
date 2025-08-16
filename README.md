# Desander Dashboard (Streamlit PWA)

Installable Streamlit dashboard using Matplotlib/Seaborn, packaged as a Progressive Web App.

## Quickstart (Python 3.12 recommended)
```bash
python3.12 -m venv venv
venv\Scripts\activate        # Windows
# or: source venv/bin/activate # macOS/Linux
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` then use **Install app** (Chrome/Edge) or **Add to Home Screen** on mobile.

### Notes
- `manifest.json` and `service-worker.js` are registered from the app root.
- If you serve behind a subpath, adjust the SW registration path in `app.py`.

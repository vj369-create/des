# Industrial Monitoring Dashboard — PWA (v2)

Flask PWA with **file upload** and **date picker**.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080

### Use cases
- **Upload route**: choose your `.xlsx` and a date (`YYYY-MM-DD`). The image renders inline on the page.
- **Server file route (optional)**: place `f.xlsx` beside `app.py` and hit `/dashboard?date=dd-mm-yyyy` or use the classic link on the homepage.

## Deploy
Any Python host (Render, Railway, Azure App Service, EC2). Ensure `static/` and `templates/` directories are served and that service worker paths match.

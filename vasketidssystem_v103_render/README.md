# Vasketidssystem (version 103)

Dette projekt er klar til deployment på Render.com.

## Deploy-trin

1. Gå til https://render.com
2. Opret nyt Web Service projekt
3. Upload ZIP-filen
4. Sørg for at:
   - `startCommand` er `python start.py`
   - Python version og `requirements.txt` automatisk genkendes
5. Tilføj `DATABASE_URL` som miljøvariabel i Render-dashboardet
6. Start deployment – siden vil køre med Flask backend

## Katalogstruktur

- `app.py` – hovedapplikationen (Flask)
- `start.py` – entrypoint
- `templates/` – HTML-filer
- `static/` – baggrundsbilleder og CSS
- `requirements.txt` – afhængigheder
# Vasketidssystem for Tåsingegade 16 🧼

Dette er et fuldt funktionelt vasketidssystem bygget i Flask med PostgreSQL, udviklet til brug i boligkomplekser. Systemet er responsivt, brugervenligt og tilbyder både brugere og administratorer mulighed for at styre vasketidsbookinger, kommentarer og adgangskontrolleret brugeradministration.

## 🔧 Funktioner

### Brugere
- Login med brugernavn og kodeord
- Mulighed for at ændre adgangskode
- Maks 2 bookinger per dag
- Kommentar-funktion
- Valgfri e-mail og SMS-notifikation
- Responsiv kalender (14 dage frem, opdelt i 4 daglige blokke)
- Visuel feedback på bookinger:
  - Grøn = ledig
  - Rød = booket
  - Gul = service (admin-booking)

### Admin
- Opret, rediger og slet brugere
- Rediger adgangskoder og kontaktoplysninger
- Book tider som “service” (gul knap)
- Slet alle bookinger og kommentarer
- Overblik over alle bookinger og brugere
- Adgang til adminpanel med visuel oversigt

## 📦 Deploy via Render.com
Du skal bruge:
- `requirements.txt` til Python afhængigheder
- `start.py` til at starte appen
- `render.yaml` til at specificere build og startkommando

**Database**: PostgreSQL. Brug `DATABASE_URL` som environment variable.

## 🖼 Design
- Fælles baggrund (Bg.jpg) for alle sider
- Udtonede knapper og ensartet layout
- Mobilvenligt og brugervenligt

## 📁 Mappestruktur
- `/templates` → HTML-sider (`login.html`, `index.html`, `admin.html`, `skiftkode.html`)
- `/static/Bg.jpg` → Baggrundsbillede
- `app.py` → Applikationens logik
- `start.py` → Indgangspunkt
- `requirements.txt` → Afhængigheder

---

© Tåsingegade 16 – udviklet med omtanke for beboere og vasketider.
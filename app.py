# v97: Render commit marker
dummy_render_trigger = 5  # v106 commit trigger  # v97 commit trigger

# v87: Render commit marker
# v85: Render commit marker

from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'hemmelig_nøgle'

UGEDAGE_DK = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag']

DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://vasketid_db_user:rGVcD7xXGPrltSmj4AtKqoNcfwEe71bm@dpg-d1i3i09r0fns73bs6j4g-a.frankfurt-postgres.render.com/vasketid_db"

@app.route('/bookinger_json')
def bookinger_json():
    bookinger_14 = {}
    conn = get_db_connection()
    cur = conn.cursor()
    idag = datetime.today()
    cur.execute(
        "SELECT * FROM bookinger WHERE dato >= %s AND dato <= %s",
        (idag.strftime('%Y-%m-%d'), (idag + timedelta(days=14)).strftime('%Y-%m-%d'))
    )
    alle_14 = cur.fetchall()
    conn.close()
    for b in alle_14:
        dato_raw = str(b[2])
        try:
            datetime.strptime(dato_raw, '%d-%m-%Y')
            dato_str = dato_raw
        except ValueError:
            dato_str = datetime.strptime(dato_raw, '%Y-%m-%d').strftime('%d-%m-%Y')
        bookinger_14[(dato_str, b[3])] = b[1]
    return jsonify([
        {"dato": k[0], "tid": k[1], "navn": v}
        for k, v in bookinger_14.items()
    ])

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL") or "postgresql://vasketid_db_user:rGVcD7xXGPrltSmj4AtKqoNcfwEe71bm@dpg-d1i3i09r0fns73bs6j4g-a.frankfurt-postgres.render.com/vasketid_db"
    return psycopg2.connect(db_url, sslmode='require')

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    fejl = request.args.get("fejl", "")
    if request.method == 'POST':
        brugernavn = request.form['brugernavn']
        kode = request.form['kode']
        conn = get_db_connection()
        cur = conn.cursor()

        # AUTO-OPRET ADMIN HVIS MANGLER
        cur.execute("SELECT * FROM brugere WHERE brugernavn = 'admin'")
        if not cur.fetchone():
            cur.execute("INSERT INTO brugere (brugernavn, kode) VALUES ('admin', 'admin123')")
            conn.commit()

        cur.execute("SELECT * FROM brugere WHERE brugernavn = %s AND kode = %s", (brugernavn.lower(), kode))
        bruger = cur.fetchone()
        conn.close()
        if bruger:
            session['brugernavn'] = brugernavn
            if brugernavn.lower() == 'admin':
                return redirect('/admin')
            else:
                return redirect('/index')
        else:
            return redirect('/login?fejl=Forkert+brugernavn+eller+adgangskode')
    return render_template('login.html', fejl=fejl)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin():
    if 'brugernavn' not in session or session['brugernavn'].lower() != 'admin':
        return redirect('/login')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM brugere")
    brugere = [dict(username=row[0], password=row[1], email=row[2], sms=row[3]) for row in cur.fetchall()]
    

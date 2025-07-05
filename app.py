# v97: Render commit marker

dummy_render_trigger = 0  # v97 commit trigger

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
    cur.execute("SELECT * FROM bookinger")
    bookinger = [dict(id=i+1, bruger=row[0], dato=row[1], tid=row[2]) for i, row in enumerate(cur.fetchall())]
    cur.execute("SELECT * FROM kommentarer")
    kommentarer = [dict(id=i+1, bruger=row[0], tekst=row[1]) for i, row in enumerate(cur.fetchall())]
    conn.close()
    return render_template("admin.html", brugere=brugere, bookinger=bookinger, kommentarer=kommentarer)

@app.route('/index')
def index():
    if 'brugernavn' not in session:
        return redirect('/login')
    brugernavn = session['brugernavn']

    valgt_uge = request.args.get("uge")
    idag = datetime.today()
    if valgt_uge:
        valgt_uge = int(valgt_uge)
        start_dato = datetime.strptime(f"{idag.year}-W{valgt_uge}-1", "%Y-W%W-%w")
    else:
        valgt_uge = idag.isocalendar().week
        dag = idag.weekday()
        start_dato = idag - timedelta(days=dag)

    ugedage_dk = UGEDAGE_DK
    ugedage_dato = [(start_dato + timedelta(days=i)).strftime('%d-%m-%Y') for i in range(7)]
    tider = ['07–11', '11–15', '15–19', '19–23']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookinger WHERE dato >= %s AND dato <= %s",
                (idag.strftime('%Y-%m-%d'), (idag + timedelta(days=14)).strftime('%Y-%m-%d')))
    alle_14 = cur.fetchall()
    conn.close()

    bookinger = {}
    for b in alle_14:
        dato_raw = str(b[2])
        try:
            datetime.strptime(dato_raw, '%d-%m-%Y')
            dato_str = dato_raw
        except ValueError:
            dato_str = datetime.strptime(dato_raw, '%Y-%m-%d').strftime('%d-%m-%Y')
        bookinger[(dato_str, b[3])] = b[1]

    return render_template(
        "index.html",
        ugedage_dk=ugedage_dk,
        ugedage_dato=ugedage_dato,
        tider=tider,
        valgt_uge=valgt_uge,
        bookinger=bookinger,
        bookinger_14=bookinger,
        bruger=brugernavn
    )

# Korrigeret app.py indhold (forkortet version for zip)
from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'hemmelig_nøgle'

UGEDAGE_DK = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag']

DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://vasketid_db_user:rGVcD7xXGPrltSmj4AtKqoNcfwEe71bm@dpg-d1i3i09r0fns73bs6j4g-a.frankfurt-postgres.render.com/vasketid_db"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/')
def home():
    return redirect('/login')

@app.route('/index')
def index():
    if 'brugernavn' not in session:
        return redirect('/login')
    brugernavn = session['brugernavn']
    idag = datetime.today()
    valgt_uge = request.args.get("uge")
    if valgt_uge:
        valgt_uge = int(valgt_uge)
        start_dato = datetime.strptime(f"{idag.year}-W{valgt_uge}-1", "%Y-W%W-%w")
    else:
        valgt_uge = idag.isocalendar().week
        dag = idag.weekday()
        start_dato = idag - timedelta(days=dag)

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

    return render_template("index.html",
        ugedage_dk=UGEDAGE_DK,
        ugedage_dato=ugedage_dato,
        tider=tider,
        valgt_uge=valgt_uge,
        bookinger=bookinger,
        bookinger_14=bookinger,
        bruger=brugernavn
    )

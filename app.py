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
    cur.execute("SELECT * FROM bookinger")
    alle = cur.fetchall()

    cur.execute("SELECT * FROM bookinger WHERE dato >= %s AND dato <= %s",
                (idag.strftime('%Y-%m-%d'), (idag + timedelta(days=14)).strftime('%Y-%m-%d')))
    alle_14 = cur.fetchall()
    conn.close()

    bookinger = {}
    bookinger_14 = {}
    for b in alle_14:
        dato_raw = str(b[2])
        try:
            datetime.strptime(dato_raw, '%d-%m-%Y')
            dato_str = dato_raw
        except ValueError:
            dato_str = datetime.strptime(dato_raw, '%Y-%m-%d').strftime('%d-%m-%Y')
        bookinger_14[(dato_str, b[3])] = b[1]

cur.execute("SELECT * FROM bookinger")
alle = cur.fetchall()

cur.execute("SELECT * FROM bookinger WHERE dato >= %s AND dato <= %s",
            (idag.strftime('%Y-%m-%d'), (idag + timedelta(days=14)).strftime('%Y-%m-%d')))
alle_14 = cur.fetchall()
conn.close()

bookinger = {}
for b in alle:
    dato_raw = str(b[2])
    try:
        datetime.strptime(dato_raw, '%d-%m-%Y')
        dato_str = dato_raw
    except ValueError:
        dato_str = datetime.strptime(dato_raw, '%Y-%m-%d').strftime('%d-%m-%Y')
    bookinger[(dato_str, b[3])] = b[1]

bookinger_14 = {}
for b in alle_14:
    dato_raw = str(b[2])
    try:
        datetime.strptime(dato_raw, '%d-%m-%Y')
        dato_str = dato_raw
    except ValueError:
        dato_str = datetime.strptime(dato_raw, '%Y-%m-%d').strftime('%d-%m-%Y')
    bookinger_14[(dato_str, b[3])] = b[1]

    return render_template(
        "index.html",
        ugedage_dk=ugedage_dk,
        ugedage_dato=ugedage_dato,
        tider=tider,
        valgt_uge=valgt_uge,
        bookinger=bookinger,
        bookinger_14=bookinger_14,
        bruger=brugernavn
    )
@app.route('/book', methods=['POST'])
def book():
    if 'brugernavn' not in session:
        return redirect('/login')
    valgt_uge = request.form.get('valgt_uge') or datetime.today().isocalendar().week
    bruger = 'service' if session['brugernavn'] == 'admin' else session['brugernavn']
    dato = request.form['dato']
    tid = request.form['tid']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bookinger WHERE dato = %s AND brugernavn = %s", (dato, bruger))
    count = cur.fetchone()[0]
    if count >= 2 and bruger != 'service':
        cur.close()
        conn.close()
        return redirect(f"/index?uge={valgt_uge}")
    cur.execute("INSERT INTO bookinger (brugernavn, dato, tid) VALUES (%s, %s, %s)", (bruger, dato, tid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(f"/index?uge={valgt_uge}")
    cur.execute("INSERT INTO bookinger (brugernavn, dato, tid) VALUES (%s, %s, %s)", (bruger, dato, tid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(f"/index?uge={valgt_uge}")

@app.route('/slet', methods=['POST'])
def slet():
    if 'brugernavn' not in session:
        return redirect('/login')
    valgt_uge = request.form.get('valgt_uge') or datetime.today().isocalendar().week
    bruger = session['brugernavn']
    dato = request.form['dato']
    tid = request.form['tid']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM bookinger WHERE brugernavn = %s AND dato = %s AND tid = %s", (bruger, dato, tid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(f"/index?uge={valgt_uge}")

# v32 – admin visning gendannet

@app.route('/admin/skift_adgangskode', methods=['POST'])
def skift_admin_kode():
    if 'brugernavn' not in session or session['brugernavn'].lower() != 'admin':
        return redirect('/login')
    ny_kode = request.form.get("ny_kode", "")
    if not ny_kode:
        return redirect('/admin')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE brugere SET kode = %s WHERE brugernavn = 'admin'", (ny_kode,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')
# v33 – admin kan ændre adgangskode

@app.route('/admin/book_service', methods=['POST'])
def admin_book_service():
    if 'brugernavn' not in session or session['brugernavn'].lower() != 'admin':
        return redirect('/login')
    dato = request.form['dato']
    tid = request.form['tid']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO bookinger (brugernavn, dato, tid) VALUES ('service', %s, %s)", (dato, tid))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')
# v34 – book_service tilføjet

@app.route('/admin/delete_booking', methods=['POST'])
def admin_delete_booking():
    if 'brugernavn' not in session or session['brugernavn'].lower() != 'admin':
        return redirect('/login')
    booking_id = request.form.get('booking_id')
    if not booking_id:
        return redirect('/admin')
    booking_id = int(booking_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT brugernavn, dato, tid FROM bookinger")
    alle = cur.fetchall()
    if 0 <= booking_id - 1 < len(alle):
        b = alle[booking_id - 1]
        cur.execute("DELETE FROM bookinger WHERE brugernavn = %s AND dato = %s AND tid = %s",
                    (str(b[0]), str(b[1]), str(b[2])))
        conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')
    b = alle[int(booking_id)-1]
    cur.execute("DELETE FROM bookinger WHERE brugernavn = %s AND dato = %s AND tid = %s", (b[0], b[1], b[2]))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')
# v36 – admin delete_booking tilføjet
# v37 – fixet psycopg2 typefejl ved booking delete

@app.route('/opret', methods=['POST'])
def opret():
    brugernavn = request.form['brugernavn'].lower()
    kode = request.form['kode']
    email = request.form.get('email', '')
    sms = request.form.get('sms', '')
    notifikation = 'ja' if request.form.get('notifikation') == 'ja' else 'nej'

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO brugere (brugernavn, kode, email, sms, notifikation) VALUES (%s, %s, %s, %s, %s)",
                (brugernavn, kode, email, sms, notifikation))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/login')
# v47 – tilføjet brugeroprettelse

@app.route('/admin/update_user', methods=['POST'])
def update_user():
    if 'brugernavn' not in session or session['brugernavn'].lower() != 'admin':
        return redirect('/login')
    username = request.form['username']
    new_username = request.form['new_username']
    password = request.form['password']
    email = request.form.get('email', '')
    sms = request.form.get('sms', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE brugere SET brugernavn = %s, kode = %s, email = %s, sms = %s WHERE brugernavn = %s",
                (new_username, password, email, sms, username))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'brugernavn' not in session or session['brugernavn'].lower() != 'admin':
        return redirect('/login')
    username = request.form['username']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM brugere WHERE brugernavn = %s", (username,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')

@app.route('/skiftkode', methods=['POST'])
def skiftkode_post():
    brugernavn = request.form['brugernavn'].strip().lower()
    gammel_kode = request.form['gammel_kode']
    ny_kode1 = request.form['ny_kode1']
    ny_kode2 = request.form['ny_kode2']

    if ny_kode1 != ny_kode2:
        return redirect('/skiftkode?fejl=Kodeord+matcher+ikke')

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT kode FROM brugere WHERE LOWER(brugernavn) = %s", (brugernavn,))
    result = cur.fetchone()

    if not result or result[0] != gammel_kode:
        conn.close()
        return redirect('/skiftkode?fejl=Forkert+brugernavn+eller+kodeord')

    if brugernavn == 'admin':
        conn.close()
        return redirect('/skiftkode?fejl=Admin+kan+kun+ændres+af+admin')

    cur.execute("UPDATE brugere SET kode = %s WHERE LOWER(brugernavn) = %s", (ny_kode1, brugernavn))
    conn.commit()
    conn.close()
    return redirect('/login?besked=Adgangskode+opdateret')

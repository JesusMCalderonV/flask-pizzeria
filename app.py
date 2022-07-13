from flask import Flask, render_template, request, redirect, jsonify
from config import config
from Usuarios import get_db
from funciones import registrarUsuario

app = Flask('Administrado de ventas')

@app.route('/')
def index():
    return redirect('login')
    
@app.route('/signup', methods=['GET', 'POST'])
def singup():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT user FROM usuarios"
    cursor.execute(query)
    usuarios = cursor.fetchall()
    registro = True
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        name = request.form['name']
        if registrarUsuario(user, password, name) == True:
            return redirect('/inicio')
        else:
            return redirect('/signup')
    elif request.method == 'GET':
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT user, password FROM usuarios"
    cursor.execute(query)
    usuarios = cursor.fetchall()
    db.close()
    ingreso = False
    if request.method == 'POST':
        if 'ingresar' in request.form:
            user = request.form['username']
            password = request.form['password']
            print(f'Usuario: {user} Clave: {password}')
            print(usuarios)
            for i in range(len(usuarios)):
                if user == usuarios[i][0] and password == usuarios[i][1]:
                    ingreso = True
                    break
            print(ingreso)
            if ingreso == True:
                db = get_db()
                db.execute("""CREATE TABLE IF NOT EXISTS registros(
                id  INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT NOT NULL,
                unidades INTERGER NOT NULL,
                nombre TEXT NOT NULL,
                valor INTERGER NOT NULL
                )
                """)
                cur = db.cursor()
                cur.execute("SELECT id, producto, unidades, nombre, valor FROM registros ORDER BY id DESC")
                data = cur.fetchall()
                db.close()
                print(data)
                return render_template('inicio.html', pedidos = data)
            else:
                return redirect('/login')
        elif 'registrar' in request.form:
            return redirect('/signup')
    elif request.method == 'GET':
        return render_template('login.html')

@app.route('/inicio', methods=['POST', 'GET'])
def inicio():
    if request.method == 'POST':
        db = get_db()
        db.execute("""CREATE TABLE IF NOT EXISTS registros(
        id  INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT NOT NULL,
        unidades INTERGER NOT NULL,
        nombre TEXT NOT NULL,
        valor INTERGER NOT NULL
        )
        """)
        cur = db.cursor()
        cur.execute("SELECT id, producto, unidades, nombre, valor FROM registros ORDER BY id DESC")
        data = cur.fetchall()
        db.close()
        print(data)
        return render_template('inicio.html', pedidos = data)
    else:
        return redirect('login')
        
@app.route('/pedido', methods=['POST', 'GET'])
def pedido():
    if request.method == 'POST':
        producto = request.form['producto']
        unidades = request.form['unidades']
        name = request.form['name']
        valor = request.form['valor']
        db = get_db()
        db.execute("""CREATE TABLE IF NOT EXISTS registros(
        id  INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT NOT NULL,
        unidades INTERGER NOT NULL,
        nombre TEXT NOT NULL,
        valor INTERGER NOT NULL
        )
        """)
        db.execute("INSERT INTO registros(producto, unidades, nombre, valor) VALUES(?,?,?,?)", (producto, unidades, name, valor))
        cur = db.cursor()
        db.commit()
        cur.execute("SELECT id, producto, unidades, nombre, valor FROM registros ORDER BY id DESC")
        data = cur.fetchall()
        db.close()
        print(data)
        return render_template('inicio.html', pedidos = data)
    else:
        return redirect('login')

@app.route('/ventas', methods=['POST', 'GET'])
def mostrarVentas():
    return render_template('ventas.html')

@app.route('/edicionExcitosa', methods=['POST', 'GET'])
def editar():
    if request.method == 'POST':
        identificador = request.form['id']
        producto = request.form['producto']
        unidades = request.form['unidades']
        name = request.form['name']
        valor = request.form['valor']
        db = get_db()
        cur = db.cursor()
        query = f"update registros set producto='{producto}', unidades='{unidades}', nombre='{name}', valor='{valor}' where id='{identificador}';"
        cur.execute(query)
        db.commit()
        cur.execute("SELECT id, producto, unidades, nombre, valor FROM registros ORDER BY id DESC")
        registro = cur.fetchall()
        db.close()
        return render_template('inicio.html', pedidos=registro)

@app.route('/edicion', methods=['POST', 'GET'])
def editarOeliminar():
    if request.method == 'POST':
        identificador = request.form['id']
        producto = request.form['producto']
        unidades = request.form['unidades']
        name = request.form['name']
        valor = request.form['valor']
        pedido = [identificador, producto, unidades, name, valor]
        if 'editar' in request.form:
            return render_template('edit.html', editar= pedido)
        elif 'eliminar' in request.form:
            db = get_db()
            cur = db.cursor()
            cur.execute("DELETE from registros where ID="+identificador)
            db.commit()
            cur.execute("SELECT id, producto, unidades, nombre, valor FROM registros ORDER BY id DESC")
            registro = cur.fetchall()
            db.close()
            return render_template('inicio.html', pedidos=registro)
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()
from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import conectar


# Cria o Blueprint de autenticação
auth_bp = Blueprint('auth', __name__)


# Decorator movido para cá para poder ser usado em outros módulos
def login_required(f):
    @wraps(f) 
    def decorated(*args, **kwargs):

        if "usuario"not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated


# Api cadastro de usuario
@auth_bp.route("/cadastro", methods=["GET", "POST"])
def pagina_cadastro():
    if request.method =="POST":

        usuario = request.form["usuario"].strip()
        email = request.form["email"].strip()
        senha = request.form["senha"].strip()


        senha_hash = generate_password_hash(senha)
     
        conn = conectar()
    
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO usuarios
        (
            usuario,
            email,
            senha
        )
        VALUES (?,?,?)
        """,
        (
            usuario,
            email,
            senha_hash
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('auth.pagina_login'))

    return render_template("cadastro.html")


# API do Login
@auth_bp.route("/login", methods=["GET","POST"])
def pagina_login():
    if request.method =="POST":

        email = request.form["email"].strip()    
        senha = request.form["senha"].strip()   

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute("select * from usuarios where email = ?", (email,))

        usuario = cursor.fetchone()
        
        conn.close()

        if usuario and check_password_hash ( usuario[3], senha):
            print("LOGIN OK")

            session["usuario"] = usuario[0]

            return redirect(url_for('views.pagina_dashboard'))
        
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for('auth.pagina_login'))
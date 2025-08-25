from ast import Store
import sqlite3
from PyQt6 import QtWidgets, uic, QtCore

app = QtWidgets.QApplication([])

# Carga de las interfaces gráficas
login = uic.loadUi("login.ui")
admi = uic.loadUi("menu_admi.ui")
cajero = uic.loadUi("menu_cajero.ui")
mesero = uic.loadUi("menu_mesero.ui")
abrir_mesa = uic.loadUi("abrir_mesa.ui")


# Conexión a la base de datos SQLite
conexion = sqlite3.connect('usuarios.db')
cursor = conexion.cursor()


# Guarda los cambios
conexion.commit()

def gui_admi():
    login.hide()
    admi.show()

def gui_cajero():
    login.hide()
    cajero.show()

def gui_mesero():
    login.hide()
    mesero.show()

def regresar_admi():
    admi.hide()
    login.show()
    login.lineEdit1.clear()
    login.lineEdit2.clear()

def regresar_cajero():
    cajero.hide()
    login.show()
    login.lineEdit1.clear()
    login.lineEdit2.clear()


def regresar_mesero():
    mesero.hide()
    login.show()
    login.lineEdit1.clear()
    login.lineEdit2.clear()


def gui_login():
    usuario = login.lineEdit1.text()
    contraseña = login.lineEdit2.text()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contraseña=?", (usuario, contraseña))
    usuario_encontrado = cursor.fetchone()
    if usuario_encontrado:
        rol = usuario_encontrado[3]  # El índice 3 corresponde al campo 'rol' en la consulta
        if rol == "admin":
            gui_admi()
        elif rol == "cajero":
            gui_cajero()
        elif rol == "mesero":
            gui_mesero()
    else:
        login.lineEdit1.clear()
        login.lineEdit2.clear()


def abrir_cuenta(numero_mesa):
    abrir_mesa.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    abrir_mesa.lb_mesa.setText(f"Mesa {numero_mesa}")
    abrir_mesa.show()

def cancelar_cuenta():
    pass

def reservar_mesa():
    pass

def cancelar_mesa():
    abrir_mesa.hide()

# Conectar los eventos de clic de los botones de mesa a abrir_cuenta con argumentos
mesero.bt_mesa1.clicked.connect(lambda: abrir_cuenta(1))
mesero.bt_mesa2.clicked.connect(lambda: abrir_cuenta(2))
mesero.bt_mesa3.clicked.connect(lambda: abrir_cuenta(3))
mesero.bt_mesa4.clicked.connect(lambda: abrir_cuenta(4))
mesero.bt_mesa5.clicked.connect(lambda: abrir_cuenta(5))
mesero.bt_mesa6.clicked.connect(lambda: abrir_cuenta(6))
abrir_mesa.bt_cancelar.clicked.connect(cancelar_mesa)


login.pushButton.clicked.connect(gui_login)
admi.bt_salir.clicked.connect(regresar_admi)
cajero.bt_salir.clicked.connect(regresar_cajero)
mesero.bt_salir.clicked.connect(regresar_mesero)

login.show()
app.exec()

# Cierra la conexión al salir
conexion.close()

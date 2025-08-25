import sys
import sqlite3
from PyQt6 import QtWidgets, uic, QtCore
from prueba import MainWindow as MenuPlatillos    

class App(QtWidgets.QApplication):
    cuenta_impresa_signal = QtCore.pyqtSignal(int)
    
    def __init__(self, args):
        super().__init__(args)
        # Carga de las interfaces gráficas
        self.login = uic.loadUi("login.ui")
        self.admi = uic.loadUi("menu_admi.ui")
        self.cajero = uic.loadUi("menu_cajero.ui")
        self.mesero = uic.loadUi("menu_mesero.ui")
        self.abrir_mesa = uic.loadUi("abrir_mesa.ui")
        self.menu_cajero = uic.loadUi("menu_cajero.ui")  
        self.menu_platillos_window = None  
        self.mesas_impresas = []  # Lista para llevar registro de mesas impresas
        self.mesas_activas = []  # Lista para llevar registro de mesas activas
   
        # Inicializar las variables de mesa
        self.Mesa_1 = False
        self.Mesa_2 = False
        self.Mesa_3 = False
        self.Mesa_4 = False
        self.Mesa_5 = False
        self.Mesa_6 = False
        
        # Conexión a la base de datos SQLite
        self.conexion = sqlite3.connect('usuarios.db')
        self.cursor = self.conexion.cursor()
        
        self.setup_ui()
        
    def setup_ui(self):
        self.login.pushButton.clicked.connect(self.gui_login)
        self.admi.bt_salir.clicked.connect(self.regresar_admi)
        self.cajero.bt_salir.clicked.connect(self.regresar_cajero)
        self.mesero.bt_salir.clicked.connect(self.regresar_mesero)

        # Conexión del botón "Abrir Mesa" en la interfaz abrir_mesa
        self.abrir_mesa.bt_abrir.clicked.connect(self.abrir_mesa_clicked)
        self.abrir_mesa.bt_imprimir_cuenta.clicked.connect(self.imprimir_cuenta)
        self.menu_cajero.bt_pagar_cuenta.clicked.connect(self.abrir_ventana_pagar_cuenta)

        # Conexiones de los botones de las mesas
        self.mesero.bt_mesa1.clicked.connect(lambda: self.abrir_cuenta(1))
        self.mesero.bt_mesa2.clicked.connect(lambda: self.abrir_cuenta(2))
        self.mesero.bt_mesa3.clicked.connect(lambda: self.abrir_cuenta(3))
        self.mesero.bt_mesa4.clicked.connect(lambda: self.abrir_cuenta(4))
        self.mesero.bt_mesa5.clicked.connect(lambda: self.abrir_cuenta(5))
        self.mesero.bt_mesa6.clicked.connect(lambda: self.abrir_cuenta(6))
        self.abrir_mesa.bt_cancelar.clicked.connect(self.cancelar_mesa)
        
        self.cajero.bt_salir.clicked.connect(self.regresar_cajero)
        self.menu_cajero.bt_salir.clicked.connect(self.regresar_menu_cajero)
        self.menu_cajero.bt_pagar_cuenta.clicked.connect(self.pagar_cuenta_cajero)

        # Conexión del botón "Agregar Productos" en la interfaz abrir_mesa
        self.abrir_mesa.bt_agregar_productos.clicked.connect(self.abrir_menu_platillos)
        self.cuenta_impresa_signal.connect(self.actualizar_cuentas_disponibles)

        # Mostrar la ventana de login al iniciar la aplicación
        self.login.show()

    def gui_admi(self):
        self.login.hide()
        self.admi.show()

    def gui_cajero(self):
        self.login.hide()
        self.cajero.show()

    def gui_mesero(self):
        self.login.hide()
        self.mesero.show()

    def regresar_admi(self):
        self.admi.hide()
        self.login.show()
        self.login.lineEdit1.clear()
        self.login.lineEdit2.clear()

    def regresar_cajero(self):
        self.cajero.hide()
        self.login.show()
        self.login.lineEdit1.clear()
        self.login.lineEdit2.clear()

    def regresar_mesero(self):
        self.mesero.hide()
        self.login.show()
        self.login.lineEdit1.clear()
        self.login.lineEdit2.clear()

    def gui_login(self):
        usuario = self.login.lineEdit1.text()
        contraseña = self.login.lineEdit2.text()
        self.cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contraseña=?", (usuario, contraseña))
        usuario_encontrado = self.cursor.fetchone()
        if usuario_encontrado:
            rol = usuario_encontrado[3]  # El índice 3 corresponde al campo 'rol' en la consulta
            if rol == "admin":
                self.gui_admi()
            elif rol == "cajero":
                self.gui_cajero()
            elif rol == "mesero":
                self.gui_mesero()
        else:
            self.login.lineEdit1.clear()
            self.login.lineEdit2.clear()

    def abrir_cuenta(self, numero_mesa):
        # Verificar si la mesa está activa
        if self.verificar_mesa_activa(numero_mesa):
            # Verificar si la mesa ha sido impresa
            if numero_mesa in self.mesas_impresas:
                self.abrir_mesa.bt_abrir.setEnabled(False)
                self.abrir_mesa.bt_reservar.setEnabled(False)
                self.abrir_mesa.bt_agregar_productos.setEnabled(False)
                self.abrir_mesa.bt_imprimir_cuenta.setEnabled(False)  # Habilitar la impresión si ya fue impresa
            else:
                self.abrir_mesa.bt_abrir.setEnabled(False)
                self.abrir_mesa.bt_reservar.setEnabled(False)
                self.abrir_mesa.bt_agregar_productos.setEnabled(True)
                self.abrir_mesa.bt_imprimir_cuenta.setEnabled(True)
        else:
            # La mesa no está activa, mostrar el botón de abrir mesa, reservar y cancelar
            self.abrir_mesa.bt_abrir.setEnabled(True)
            self.abrir_mesa.bt_reservar.setEnabled(True)
            self.abrir_mesa.bt_agregar_productos.setEnabled(False)
            self.abrir_mesa.bt_imprimir_cuenta.setEnabled(False)
            
        self.abrir_mesa.lb_mesa.setText(f"Mesa {numero_mesa}")
        self.abrir_mesa.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.abrir_mesa.show()

    def abrir_menu_platillos(self):
        if self.menu_platillos_window is None:
            self.menu_platillos_window = MenuPlatillos()
        self.menu_platillos_window.show()
        # Cerrar la ventana abrir_mesa
        self.abrir_mesa.close()

    def verificar_mesa_activa(self, numero_mesa):
        # Verificar si la mesa está activa 
        if numero_mesa == 1:
            return self.Mesa_1
        elif numero_mesa == 2:
            return self.Mesa_2
        elif numero_mesa == 3:
            return self.Mesa_3
        elif numero_mesa == 4:
            return self.Mesa_4
        elif numero_mesa == 5:
            return self.Mesa_5
        elif numero_mesa == 6:
            return self.Mesa_6
        else:
            return False

    def abrir_mesa_clicked(self):
        # Obtener el número de mesa desde el texto del QLabel
        numero_mesa = int(self.abrir_mesa.lb_mesa.text().split()[-1])

        # Verificar si la mesa está activa, si no lo está, cambiar su estado a activa
        if not self.verificar_mesa_activa(numero_mesa):
            if numero_mesa == 1:
                self.Mesa_1 = True
            elif numero_mesa == 2:
                self.Mesa_2 = True
            elif numero_mesa == 3:
                self.Mesa_3 = True
            elif numero_mesa == 4:
                self.Mesa_4 = True
            elif numero_mesa == 5:
                self.Mesa_5 = True
            elif numero_mesa == 6:
                self.Mesa_6 = True

        # Ocultar la ventana abrir_mesa
        self.abrir_mesa.hide()

        # Verificar si la ventana menu_platillos ya está abierta
        if self.menu_platillos_window is None:
            self.menu_platillos_window = MenuPlatillos()
        self.menu_platillos_window.show()

         # Verificar si se ha impreso la cuenta y mostrar el mensaje
        if numero_mesa in self.mesas_impresas:
            self.imprimir_cuenta(numero_mesa)

    def cancelar_mesa(self):
        self.abrir_mesa.hide()

    def imprimir_cuenta(self):
        # Obtener el número de mesa desde el texto del QLabel
        numero_mesa = int(self.abrir_mesa.lb_mesa.text().split()[-1])

        # Registrar la mesa como impresa y activa
        self.mesas_impresas.append(numero_mesa)
        self.mesas_activas.append(numero_mesa)

        # Deshabilitar todos los botones excepto el de cancelar
        self.abrir_mesa.bt_abrir.setEnabled(False)
        self.abrir_mesa.bt_reservar.setEnabled(False)
        self.abrir_mesa.bt_agregar_productos.setEnabled(False)
        self.abrir_mesa.bt_imprimir_cuenta.setEnabled(False)
        self.abrir_mesa.bt_cancelar.setEnabled(True)

        # Mostrar un mensaje de que la cuenta ha sido impresa
        QtWidgets.QMessageBox.information(None, "Información", f"Se ha impreso la cuenta de la Mesa {numero_mesa}")

        # Verificar si la ventana menu_platillos ya está abierta
        if self.menu_platillos_window is None:
            self.menu_platillos_window = MenuPlatillos()
        self.menu_platillos_window.hide()

        self.cuenta_impresa_signal.emit(numero_mesa)
        self.abrir_mesa.hide()
        
    def actualizar_cuentas_disponibles(self, numero_mesa):
        if numero_mesa in self.mesas_impresas and numero_mesa not in self.mesas_activas:
            self.mesas_activas.append(numero_mesa)

    def abrir_ventana_pagar_cuenta(self):
        pass
           
    def pagar_cuenta_cajero(self):
        pass
    
    def regresar_menu_cajero(self):
        self.menu_cajero.hide()

if __name__ == "__main__":
    app = App(sys.argv)
    sys.exit(app.exec())

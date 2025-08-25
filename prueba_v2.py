import sys
import sqlite3
from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QMainWindow, QMessageBox, QGridLayout
from PyQt6.QtCore import QSize
from datetime import datetime
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtWidgets import QApplication, QPushButton, QMainWindow, QMessageBox, QGridLayout, QDialog, QLabel, QLineEdit, QVBoxLayout

class MenuPlatillos(QMainWindow):
    def __init__(self):
        super().__init__()

        # Cargar la interfaz gráfica desde un archivo .ui
        self.setWindowTitle("Platillos y Bebidas")
        self.ui = uic.loadUi("menu_platillos.ui", self)  # Carga la interfaz desde un archivo .ui

        # Realizar conexión con la base de datos
        self.db_connection_menu = sqlite3.connect('menu.db')  # Conexión a la base de datos de menú
        self.db_connection_pedidos = sqlite3.connect('pedidos.db')  # Conexión a la base de datos de pedidos
        self.cursor = self.db_connection_pedidos.cursor()  
        self.cargar_productos()  
        self.platillos_seleccionados = []  # Lista para llevar registro de platillos seleccionados
        self.bebidas_seleccionadas = []  # Lista para llevar registro de bebidas seleccionadas

 
    # Método para cargar los productos desde la base de datos y mostrarlos en la interfaz
    def cargar_productos(self):
        cursor_platillos = self.db_connection_menu.cursor()
        cursor_platillos.execute("SELECT Nombre, Precio FROM Platillos")
        productos_platillos = cursor_platillos.fetchall()
        self.cargar_productos_en_page(productos_platillos, self.ui.pg_platillos)

        cursor_snacks = self.db_connection_menu.cursor()
        cursor_snacks.execute("SELECT Nombre, Precio FROM Snacks")
        productos_snacks = cursor_snacks.fetchall()
        self.cargar_productos_en_page(productos_snacks, self.ui.pg_snacks)

        cursor_bebidas = self.db_connection_menu.cursor()
        cursor_bebidas.execute("SELECT Nombre, Precio FROM Bebidas")
        productos_bebidas = cursor_bebidas.fetchall()
        self.cargar_productos_en_page(productos_bebidas, self.ui.pg_bebidas)

        cursor_bebidas_alcohol = self.db_connection_menu.cursor()
        cursor_bebidas_alcohol.execute("SELECT Nombre, Precio FROM Bebidas_con_alcohol")
        productos_bebidas_alchol = cursor_bebidas_alcohol.fetchall()
        self.cargar_productos_en_page(productos_bebidas_alchol, self.ui.pg_bebidas_alcohol)

        cursor_postres = self.db_connection_menu.cursor()
        cursor_postres.execute("SELECT Nombre, Precio FROM Postres")
        productos_postres = cursor_postres.fetchall()
        self.cargar_productos_en_page(productos_postres, self.ui.pg_postres)

    # Método para cargar los productos en un page widget de la interfaz
    def cargar_productos_en_page(self, productos, page_widget):
        layout = QGridLayout(page_widget)
        layout.setSpacing(10)
        
        fila = 0
        columna = 0
        for nombre, Precio in productos:
            boton = QPushButton(nombre)
            boton.setFixedSize(QSize(100, 50))
            boton.clicked.connect(lambda _, producto=nombre, precio=Precio: self.agregar_producto(producto, precio))
            layout.addWidget(boton, fila, columna)
            
            fila += 1
            if fila == 6:  # Cuando llegamos a 6 columnas, pasamos a la siguiente fila
                columna += 1
                fila = 0

    # Método para agregar un producto a la lista de selección
    def agregar_producto(self, nombre_producto, precio_producto):
        self.ui.listWidget.addItem(f"{nombre_producto} - ${precio_producto:.2f}")

        if any(nombre_producto == p[0] for p in self.platillos_seleccionados) or any(nombre_producto == p[0] for p in self.bebidas_seleccionadas):
            return

        tipo_producto = "platillo"
        if nombre_producto in [p[0] for p in self.platillos_seleccionados]:
            tipo_producto = "platillo"
        elif nombre_producto in [p[0] for p in self.bebidas_seleccionadas]:
            tipo_producto = "bebida"

        if tipo_producto == "platillo":
            self.platillos_seleccionados.append((nombre_producto, precio_producto))
        elif tipo_producto == "bebida":
            self.bebidas_seleccionadas.append((nombre_producto, precio_producto))


    # Método para limpiar la selección de productos
    def limpiar_seleccion(self):
        self.platillos_seleccionados.clear()
        self.bebidas_seleccionadas.clear()
        self.ui.listWidget.clear()

    # Método para eliminar un producto de la lista de selección
    def eliminar_producto(self):
        item = self.ui.listWidget.currentItem()
        if item is not None:
            producto = item.text()
            self.ui.listWidget.takeItem(self.ui.listWidget.row(item))
            if producto in self.platillos_seleccionados:
                self.platillos_seleccionados.remove(producto)
            elif producto in self.bebidas_seleccionadas:
                self.bebidas_seleccionadas.remove(producto)


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
        self.interfaz_pagar = uic.loadUi("interfaz_pagar.ui")
        self.interfaz_corte_caja = uic.loadUi("interfaz_corte_caja.ui")
        self.menu_platillos_window = None  
        self.mesas_impresas = []  # Lista para llevar registro de mesas impresas
        self.mesas_activas = []  # Lista para llevar registro de mesas activas
        self.mesa_seleccionada = None  # Variable de instancia para almacenar el número de mesa seleccionado
        self.dialogo_corte = None  # Inicializamos el diálogo aquí como una variable de instancia


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
        self.cajero.bt_pagar_cuenta.clicked.connect(self.abrir_interfaz_pagar)

        # Conexiones de los botones de las mesas
        self.mesero.bt_mesa1.clicked.connect(lambda: self.abrir_cuenta(1))
        self.mesero.bt_mesa2.clicked.connect(lambda: self.abrir_cuenta(2))
        self.mesero.bt_mesa3.clicked.connect(lambda: self.abrir_cuenta(3))
        self.mesero.bt_mesa4.clicked.connect(lambda: self.abrir_cuenta(4))
        self.mesero.bt_mesa5.clicked.connect(lambda: self.abrir_cuenta(5))
        self.mesero.bt_mesa6.clicked.connect(lambda: self.abrir_cuenta(6))
        self.abrir_mesa.bt_cancelar.clicked.connect(self.cancelar_mesa)
        
        self.cajero.bt_salir.clicked.connect(self.regresar_cajero)
        self.cajero.bt_corte_caja.clicked.connect(self.mostrar_corte_caja)
        self.cajero.bt_imprimir.clicked.connect(self.gui_mesero)

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
        if not isinstance(numero_mesa, int):
            print("Número de mesa inválido:", numero_mesa)
            return

        # Almacenar el número de mesa en la variable de instancia
        self.mesa_seleccionada = numero_mesa

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
        self.mesa_activa = numero_mesa  # Establecer la mesa activa en la instancia de la aplicación
        self.abrir_mesa.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.abrir_mesa.show()
        print("Número de mesa antes de guardar_pedido:", numero_mesa)

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

        # Cambiar el color del botón de la mesa a verde
        self.cambiar_color_mesa(numero_mesa, "verde")
        print("Número de mesa después de abrir mesa:", numero_mesa)

    def cambiar_color_mesa(self, numero_mesa, color):
        # Mapear los colores a los códigos de color correspondientes
        colores = {
           "verde": "background-color: rgb(0, 255, 0);",  # Verde
            "rojo": "background-color: rgb(255, 0, 0);",   # Rojo
            "violeta": "background-color: rgb(255, 0, 255);",  # Vielota
            "original":"background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 170, 255, 255), stop:1 rgba(255, 255, 255, 255));"
        }
        if color not in colores:
            print("Color no válido:", color)
            return

        # Obtener el botón de la mesa correspondiente
        boton_mesa = getattr(self.mesero, f"bt_mesa{numero_mesa}")
        
        # Aplicar el estilo CSS al botón
        boton_mesa.setStyleSheet(colores[color])

    def cancelar_mesa(self):
        self.abrir_mesa.hide()

    def imprimir_cuenta(self):
        numero_mesa = int(self.abrir_mesa.lb_mesa.text().split()[-1])
        self.cambiar_color_mesa(numero_mesa, "rojo")

        # Conectar a la base de datos pedidos.db
        conexion = sqlite3.connect("pedidos.db")
        cursor = conexion.cursor()

        try:
            # Consultar los productos y precios de la mesa correspondiente
            cursor.execute(f"SELECT Producto, Precio FROM mesa_{numero_mesa}_activa")
            productos = cursor.fetchall()
        except sqlite3.OperationalError as e:
            QtWidgets.QMessageBox.critical(None, "Error", f"Error al consultar la base de datos: {e}")
            conexion.close()
            return
        conexion.close()

        # Calcular el total sin IVA
        total_sin_iva = sum(precio for _, precio in productos)

        # Calcular el IVA 
        iva = total_sin_iva * 0.16

        # Calcular el total con IVA
        total_con_iva = total_sin_iva + iva

        # Crear el ticket
        ticket = f"                     Py Restaurant\n"
        ticket += "-----------------------------------------------------------------\n"
        ticket += f"Rectoría General de la Universidad Autónoma Metropolitana.\n"
        ticket += f"      Prolongación Canal de Miramontes No. 3855\n"
        ticket += f"         Col. Exhacienda de San Juan de Dios.\n"
        ticket += f"   Alcaldía de Tlalpan, C.P. 14387, Ciudad de México.\n"
        ticket += f"          Edificio A - Oriente, 1er. Piso.\n"
        ticket += "-----------------------------------------------------------------\n"
        ticket += f"                   UAM Cuajimalpa\n"
        ticket += f" Av. Vasco de Quiroga 4871, Col. Santa Fe Cuajimalpa,CDMX\n"
        ticket += "-----------------------------------------------------------------\n"
        ticket += f"              Ticket - Mesa {numero_mesa}\n"
        ticket += "-----------------------------------------------------------------\n"
        for producto, precio in productos:
            ticket += f"{producto} - ${precio:.2f}\n"
        ticket += "-----------------------------------------------------------------\n"
        ticket += f"          Total sin IVA: ${total_sin_iva:.2f}\n"
        ticket += f"          IVA (16%): ${iva:.2f}\n"
        ticket += "-----------------------------------------------------------------\n"
        ticket += f"          Total: ${total_con_iva:.2f}\n"

        # Guardar el ticket en un archivo de texto
        with open(f"ticket_mesa_{numero_mesa}.txt", "w") as file:
            file.write(ticket)

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

        self.cuenta_impresa_signal.emit(numero_mesa)
        self.abrir_mesa.hide()
   
    def actualizar_cuentas_disponibles(self, numero_mesa):
        if numero_mesa in self.mesas_impresas and numero_mesa not in self.mesas_activas:
            self.mesas_activas.append(numero_mesa)

    def abrir_interfaz_pagar(self):
        self.interfaz_pagar.show()
        # Limpiar los botones anteriores
        for button in self.interfaz_pagar.findChildren(QtWidgets.QPushButton):
            button.deleteLater()  # Eliminar los botones anteriores
        # Crear botones para mesas impresas
        for mesa in self.mesas_impresas:
            button = QtWidgets.QPushButton(f"Mesa {mesa}")
            button.clicked.connect(lambda checked, mesa=mesa: self.mostrar_detalle_pago(mesa))
            self.interfaz_pagar.verticalLayout.addWidget(button)

    def mostrar_detalle_pago(self, numero_mesa):
        # Conectar a la base de datos pedidos.db
        conexion = sqlite3.connect("pedidos.db")
        cursor = conexion.cursor()

        try:
            # Consultar los productos y precios de la mesa correspondiente
            cursor.execute(f"SELECT Producto, Precio FROM mesa_{numero_mesa}_activa")
            productos = cursor.fetchall()

            # Calcular el total sin IVA
            total_sin_iva = sum(precio for _, precio in productos)

            # Calcular el IVA 
            iva = total_sin_iva * 0.16

            # Calcular el total con IVA
            total_con_iva = total_sin_iva + iva

            # Crear el ticket
            ticket = f"Ticket - Mesa {numero_mesa}\n"
            ticket += "----------------------------------\n"
            total = 0
            for producto, precio in productos:
                ticket += f"{producto} - ${precio:.2f}\n"
            ticket += "-----------------------------------------------------------------\n"
            ticket += f"          Total sin IVA: ${total_sin_iva:.2f}\n"
            ticket += f"          IVA (16%): ${iva:.2f}\n"
            ticket += "-----------------------------------------------------------------\n"
            ticket += f"          Total: ${total_con_iva:.2f}\n"
    
            

            # Crear una ventana emergente para el pago
            self.dialogo_pago = QtWidgets.QDialog(self.interfaz_pagar)
            self.dialogo_pago.setWindowTitle(f"Pago - Mesa {numero_mesa}")

            layout = QVBoxLayout()

            label_ticket = QtWidgets.QLabel(ticket)
            layout.addWidget(label_ticket)

            label_total = QtWidgets.QLabel(f"Total: ${total_con_iva:.2f}")
            layout.addWidget(label_total)

            self.lineEdit_pago = QtWidgets.QLineEdit()
            self.lineEdit_pago.setPlaceholderText("Monto con el que paga el cliente")
            layout.addWidget(self.lineEdit_pago)

            self.label_cambio = QtWidgets.QLabel("Cambio: $0.00")
            layout.addWidget(self.label_cambio)

            button_efectivo = QtWidgets.QPushButton("Pago en Efectivo")
            button_efectivo.clicked.connect(lambda: self.calcular_cambio(total_con_iva))
            layout.addWidget(button_efectivo)

            button_tarjeta = QtWidgets.QPushButton("Pago con Tarjeta")
            button_tarjeta.clicked.connect(lambda: self.procesar_pago(total_con_iva, "tarjeta"))
            layout.addWidget(button_tarjeta)

            button_pagar = QtWidgets.QPushButton("Pagar Cuenta")
            button_pagar.clicked.connect(lambda: self.procesar_pago(total_con_iva))
            layout.addWidget(button_pagar)

            self.dialogo_pago.setLayout(layout)
            self.dialogo_pago.exec()
        except sqlite3.OperationalError as e:
            QtWidgets.QMessageBox.critical(None, "Error", f"Error al consultar la base de datos: {e}")
        finally:
            conexion.close()

    def calcular_cambio(self, total):
        try:
            monto_pago = float(self.lineEdit_pago.text())
            cambio = monto_pago - total
            self.label_cambio.setText(f"Cambio: ${cambio:.2f}")
        except ValueError:
            QtWidgets.QMessageBox.warning(None, "Advertencia", "Por favor, ingrese un monto válido.")

    def procesar_pago(self, total, metodo_pago="efectivo"):
        numero_mesa = int(self.dialogo_pago.windowTitle().split()[-1])
        if metodo_pago == "efectivo":
            try:
                monto_pago = float(self.lineEdit_pago.text())
                cambio = monto_pago - total
                self.label_cambio.setText(f"Cambio: ${cambio:.2f}")
            except ValueError:
                QtWidgets.QMessageBox.warning(None, "Advertencia", "Por favor, ingrese un monto válido.")
                return
        else:
            self.label_cambio.setText("Pago con tarjeta - No hay cambio")
        self.cambiar_color_mesa(numero_mesa, "original")

        if numero_mesa == 1:
            self.Mesa_1 = False
        elif numero_mesa == 2:
            self.Mesa_2 = False
        elif numero_mesa == 3:
            self.Mesa_3 = False
        elif numero_mesa == 4:
            self.Mesa_4 = False
        elif numero_mesa == 5:
            self.Mesa_5 = False
        elif numero_mesa == 6:
            self.Mesa_6 = False

        QtWidgets.QMessageBox.information(None, "Información", f"Pago procesado para la Mesa {numero_mesa}")
        self.dialogo_pago.close()
        self.interfaz_pagar.hide()

        conexion = sqlite3.connect("pedidos.db")
        cursor = conexion.cursor()

        try:
            # Consultar productos de la mesa activa
            cursor.execute(f"SELECT Producto, Precio FROM mesa_{numero_mesa}_activa")
            productos = cursor.fetchall()

            fecha_actual = datetime.now().date()
            hora_pago = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Obtener la hora actual en formato adecuado

            # Insertar productos en la tabla Mesa_#
            for producto, precio in productos:
                cursor.execute(f"INSERT INTO Mesa_{numero_mesa} (fecha, hora_apertura, hora_cierre, mesero, producto, precio) VALUES (?, ?, ?, ?, ?, ?)",
                               (fecha_actual, None, None, 'Nombre Mesero', producto, precio))

            # Eliminar registros de la mesa activa
            cursor.execute(f"DELETE FROM mesa_{numero_mesa}_activa")

            # Insertar el registro de venta en la tabla Ventas
            cursor.execute("INSERT INTO Ventas (Hora_pago, Mesa, Total, Tipo_pago) VALUES (?, ?, ?, ?)",
                           (hora_pago, numero_mesa, total, metodo_pago))

            conexion.commit()  # Confirmar los cambios en la base de datos

            # Actualizar listas y variables de instancia
            self.mesas_impresas.remove(numero_mesa)
            self.mesas_activas.remove(numero_mesa)
            setattr(self, f"Mesa_{numero_mesa}", False)

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(None, "Error", f"Error al procesar el pago: {e}")

        finally:
            # Cerrar conexión y ocultar interfaz
            conexion.close()
            self.dialogo_pago.close()
            self.interfaz_pagar.hide()

    def regresar_menu_cajero(self):
        self.menu_cajero.hide()

    # Método para guardar el pedido en la base de datos 
    def guardar_pedido(self):
        numero_mesa = self.mesa_seleccionada
        
        if not isinstance(numero_mesa, int):
            
            return
        if self.menu_platillos_window:
            platillos_seleccionados = self.menu_platillos_window.platillos_seleccionados
            bebidas_seleccionadas = self.menu_platillos_window.bebidas_seleccionadas
            try:
                cursor = self.menu_platillos_window.db_connection_pedidos.cursor()
                nombre_tabla = f"mesa_{numero_mesa}_activa"
                for nombre, precio in platillos_seleccionados + bebidas_seleccionadas:
                    cursor.execute(f"INSERT INTO {nombre_tabla} (Producto, Precio) VALUES (?, ?)", (nombre, precio))
                self.menu_platillos_window.db_connection_pedidos.commit()
                QMessageBox.information(self.menu_platillos_window, "Información", "El pedido ha sido enviado a cocina")
                self.menu_platillos_window.limpiar_seleccion()
                self.mesa_seleccionada = None
                self.menu_platillos_window.close()
            except sqlite3.Error as error:
                print("Error al guardar en la base de datos:", error)
                QMessageBox.warning(self.menu_platillos_window, "Error", "Error al guardar en la base de datos.")
            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()

    # Conexiones de los botones de la interfaz (trasladadas desde MenuPlatillos)
    def conectar_botones_menu_platillos(self, menu_platillos_window):
        if menu_platillos_window:
            menu_platillos_window.ui.bt_mandar_orden.clicked.connect(self.guardar_pedido)
            menu_platillos_window.ui.bt_eliminar_producto.clicked.connect(menu_platillos_window.eliminar_producto)


    def validar_campos(self):
        efectivo = self.lineEdit_efectivo.text()
        tarjeta = self.lineEdit_tarjeta.text()
        gastos = self.lineEdit_gastos.text()

        if efectivo and tarjeta and gastos:
            try:
                efectivo = float(efectivo)
                tarjeta = float(tarjeta)
                gastos = float(gastos)
                
                cursor = self.db_connection_pedidos.cursor()
                cursor.execute("SELECT SUM(Total) FROM Ventas")
                venta_total = cursor.fetchone()[0]
                if venta_total is None:
                    venta_total = 0.0

                calculo_venta_total = (efectivo + gastos) + tarjeta

                if calculo_venta_total < venta_total:
                    faltante = venta_total - calculo_venta_total
                    self.label_resultado.setText(f"Existe un faltante de: ${faltante:.2f}")
                elif calculo_venta_total > venta_total:
                    sobrante = calculo_venta_total - venta_total
                    self.label_resultado.setText(f"Existe un sobrante de: ${sobrante:.2f}")
                else:
                    self.label_resultado.setText("Datos correctos, puedes terminar el corte de caja")
            except ValueError:
                self.label_resultado.setText("Por favor, ingrese montos válidos.")
        else:
            self.label_resultado.setText("Por favor, complete todos los campos.")

    def mostrar_corte_caja(self):
        dialogo_corte = QtWidgets.QDialog(self.interfaz_corte_caja)
        dialogo_corte.setWindowTitle("Corte de Caja")
        layout = QVBoxLayout()

        label_corte = QLabel("Corte de Caja", dialogo_corte)
        layout.addWidget(label_corte)

        self.db_connection_pedidos = sqlite3.connect('pedidos.db')
        # Obtener la venta del día
        cursor = self.db_connection_pedidos.cursor()
        cursor.execute("SELECT SUM(Total) FROM Ventas")
        venta_total = cursor.fetchone()[0]
        if venta_total is None:
            venta_total = 0.0

        label_venta_total = QLabel(f"Venta del día = ${venta_total:.2f}", dialogo_corte)
        layout.addWidget(label_venta_total)

        label_efectivo = QLabel("Total de efectivo en caja", dialogo_corte)
        layout.addWidget(label_efectivo)
        self.lineEdit_efectivo = QLineEdit(dialogo_corte)
        layout.addWidget(self.lineEdit_efectivo)

        label_tarjeta = QLabel("Total de pagos en tarjeta", dialogo_corte)
        layout.addWidget(label_tarjeta)
        self.lineEdit_tarjeta = QLineEdit(dialogo_corte)
        layout.addWidget(self.lineEdit_tarjeta)

        label_gastos = QLabel("Gastos del día", dialogo_corte)
        layout.addWidget(label_gastos)
        self.lineEdit_gastos = QLineEdit(dialogo_corte)
        layout.addWidget(self.lineEdit_gastos)

        self.label_resultado = QLabel("", dialogo_corte)
        layout.addWidget(self.label_resultado)

        btn_confirmar = QPushButton("Confirmar corte de caja", dialogo_corte)
        btn_confirmar.clicked.connect(self.confirmar_corte_caja)
        layout.addWidget(btn_confirmar)

        dialogo_corte.setLayout(layout)

        # Conectar la validación dinámica de campos
        self.lineEdit_efectivo.textChanged.connect(self.validar_campos)
        self.lineEdit_tarjeta.textChanged.connect(self.validar_campos)
        self.lineEdit_gastos.textChanged.connect(self.validar_campos)

        # Asignar el diálogo al atributo de la clase para que podamos cerrarlo más tarde
        self.dialogo_corte = dialogo_corte

        dialogo_corte.exec()

    
    def confirmar_corte_caja(self):
        efectivo = self.lineEdit_efectivo.text()
        tarjeta = self.lineEdit_tarjeta.text()

        try:
            efectivo = float(efectivo)
            tarjeta = float(tarjeta) if tarjeta else 0.0  # Convertir a float si hay algo, o 0.0 si está vacío
            gastos = float(self.lineEdit_gastos.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Advertencia", "Por favor, ingrese montos válidos.")
            return

        cursor = self.db_connection_pedidos.cursor()
        cursor.execute("SELECT SUM(Total) FROM Ventas")
        venta_total = cursor.fetchone()[0]
        if venta_total is None:
            venta_total = 0.0

        calculo_venta_total = (efectivo + gastos) + tarjeta

        if calculo_venta_total < venta_total:
            faltante = venta_total - calculo_venta_total
            self.label_resultado.setText(f"Existe un faltante de: ${faltante:.2f}")
        elif calculo_venta_total > venta_total:
            sobrante = calculo_venta_total - venta_total
            self.label_resultado.setText(f"Existe un sobrante de: ${sobrante:.2f}")
        else:
            self.label_resultado.setText("Datos correctos, puedes terminar el corte de caja")

        # Guardar el corte de caja en un archivo .txt
        with open("corte_de_caja.txt", "w") as file:
            file.write(f"Corte de Caja\n")
            file.write(f"Venta del día = ${venta_total:.2f}\n")
            file.write(f"Total de efectivo en caja = ${efectivo:.2f}\n")
            file.write(f"Total de pagos en tarjeta = ${tarjeta:.2f}\n")
            file.write(f"Gastos del día = ${gastos:.2f}\n")
            if calculo_venta_total < venta_total:
                file.write(f"Existe un faltante de: ${faltante:.2f}\n")
            elif calculo_venta_total > venta_total:
                file.write(f"Existe un sobrante de: ${sobrante:.2f}\n")
            else:
                file.write("Datos correctos, puedes terminar el corte de caja\n")

        # Borrar los datos de la tabla Ventas
        cursor.execute("DELETE FROM Ventas")
        self.db_connection_pedidos.commit()
        
        # Cerrar la ventana de corte de caja
        self.dialogo_corte.accept()

        

if __name__ == "__main__":
    app = App(sys.argv)
    # Inicialización de la ventana MenuPlatillos
    app.menu_platillos_window = MenuPlatillos()
    # Conexión de los botones de MenuPlatillos
    app.conectar_botones_menu_platillos(app.menu_platillos_window)
    sys.exit(app.exec())


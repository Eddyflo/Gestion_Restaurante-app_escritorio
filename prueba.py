import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QMainWindow, QMessageBox
import sqlite3
from PyQt6 import uic
from PyQt6.QtCore import QSize
from datetime import datetime

class MainWindow(QMainWindow):
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

        # Conexión de eventos a botones de la interfaz
        self.ui.bt_mandar_orden.clicked.connect(self.guardar_pedido)  
        self.ui.bt_eliminar_producto.clicked.connect(self.eliminar_producto)  
        
    # Método para cargar los productos desde la base de datos y mostrarlos en la interfaz
    def cargar_productos(self):
        cursor_platillos = self.db_connection_menu.cursor()
        cursor_platillos.execute("SELECT Nombre, Precio FROM Platillos")
        productos_platillos = cursor_platillos.fetchall()
        self.cargar_productos_en_page(productos_platillos, self.ui.pg_platillos)

        cursor_bebidas = self.db_connection_menu.cursor()
        cursor_bebidas.execute("SELECT Nombre, Precio FROM Bebidas")
        productos_bebidas = cursor_bebidas.fetchall()
        self.cargar_productos_en_page(productos_bebidas, self.ui.pg_bebidas)

    # Método para cargar los productos en un page widget de la interfaz
    def cargar_productos_en_page(self, productos, page_widget):
        layout = QVBoxLayout(page_widget)
        layout.setSpacing(10)

        for nombre, descripcion in productos:
            boton = QPushButton(nombre)
            boton.setFixedSize(QSize(100, 30))
            boton.clicked.connect(lambda _, producto=nombre: self.agregar_producto(producto))
            layout.addWidget(boton)

    # Método para agregar un producto a la lista de selección
    def agregar_producto(self, nombre_producto):
        self.ui.listWidget.addItem(nombre_producto)

        if nombre_producto in self.platillos_seleccionados or nombre_producto in self.bebidas_seleccionadas:
            return

        tipo_producto = "platillo"
        if nombre_producto in [p[0] for p in self.platillos_seleccionados]:
            tipo_producto = "platillo"
        elif nombre_producto in [p[0] for p in self.bebidas_seleccionadas]:
            tipo_producto = "bebida"

        if tipo_producto == "platillo":
            self.platillos_seleccionados.append(nombre_producto)
        elif tipo_producto == "bebida":
            self.bebidas_seleccionadas.append(nombre_producto)

    # Método para guardar el pedido en la base de datos
    def guardar_pedido(self):
        desglose = "\n".join(self.platillos_seleccionados + self.bebidas_seleccionadas)
        self.guardar_pedido_en_bd(desglose)
        self.limpiar_seleccion()
        self.close()

    # Método para limpiar la selección de productos
    def limpiar_seleccion(self):
        self.platillos_seleccionados.clear()
        self.bebidas_seleccionadas.clear()
        self.ui.listWidget.clear()

    # Método para guardar el pedido en la base de datos de pedidos
    def guardar_pedido_en_bd(self, desglose):
        try:
            fecha_actual = datetime.now().date()
            cursor = self.db_connection_pedidos.cursor()
            cursor.execute("INSERT INTO Mesa_1 (fecha, hora_apertura, hora_cierre, mesero, producto, precio) VALUES (?, ?, ?, ?, ?, ?)",
                           (fecha_actual, None, None, 'Nombre Mesero', desglose, None))
            self.db_connection_pedidos.commit()
            QMessageBox.information(self, "Información", "El pedido ha sido enviado a cocina")
        except sqlite3.Error as error:
            print("Error al guardar en la base de datos:", error)
            QMessageBox.warning(self, "Error", "Error al guardar en la base de datos.")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

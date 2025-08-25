import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QMainWindow, QMessageBox
import sqlite3
from PyQt6 import uic
from PyQt6.QtCore import QSize

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Platillos y Bebidas")
        self.ui = uic.loadUi("menu_platillos.ui", self)  # Cargar la interfaz desde el archivo .ui
        self.db_connection_menu = sqlite3.connect('menu.db')  # Conexión a la base de datos de menú
        self.db_connection_pedidos = sqlite3.connect('pedidos.db')  # Conexión a la base de datos de pedidos
        self.cursor = self.db_connection_pedidos.cursor()
        self.cargar_productos()
        self.platillos_seleccionados = []  # Lista para almacenar los platillos seleccionados
        self.bebidas_seleccionadas = []  # Lista para almacenar las bebidas seleccionadas

        # Conectar los botones
        self.ui.bt_mandar_orden.clicked.connect(self.guardar_pedido)
        self.ui.bt_eliminar_producto.clicked.connect(self.eliminar_producto)

    def cargar_productos(self):
        # Cargar productos de Platillos
        cursor_platillos = self.db_connection_menu.cursor()
        cursor_platillos.execute("SELECT Nombre, Descripcion FROM Platillos")
        productos_platillos = cursor_platillos.fetchall()
        self.cargar_productos_en_page(productos_platillos, self.ui.pg_platillos)

        # Cargar productos de Bebidas
        cursor_bebidas = self.db_connection_menu.cursor()
        cursor_bebidas.execute("SELECT Nombre, Descripcion FROM Bebidas")
        productos_bebidas = cursor_bebidas.fetchall()
        self.cargar_productos_en_page(productos_bebidas, self.ui.pg_bebidas)

    def cargar_productos_en_page(self, productos, page_widget):
        # Crear layout vertical para los botones
        layout = QVBoxLayout(page_widget)
        layout.setSpacing(10)

        for nombre, descripcion in productos:
            boton = QPushButton(nombre)
            boton.setFixedSize(QSize(100, 30))
            boton.clicked.connect(lambda _, producto=nombre: self.agregar_producto(producto))
            layout.addWidget(boton)

    def agregar_producto(self, nombre_producto):
        # Agregar el nombre del producto al QListWidget
        self.ui.listWidget.addItem(nombre_producto)

        # Agregar el producto seleccionado a la lista correspondiente
        if nombre_producto in self.platillos_seleccionados or nombre_producto in self.bebidas_seleccionadas:
            return  # Evitar duplicados

        tipo_producto = "platillo"  # Por defecto
        if nombre_producto in [p[0] for p in self.platillos_seleccionados]:
            tipo_producto = "platillo"
        elif nombre_producto in [p[0] for p in self.bebidas_seleccionadas]:
            tipo_producto = "bebida"

        if tipo_producto == "platillo":
            self.platillos_seleccionados.append(nombre_producto)
        elif tipo_producto == "bebida":
            self.bebidas_seleccionadas.append(nombre_producto)

    def guardar_pedido(self):
        desglose = "\n".join(self.platillos_seleccionados + self.bebidas_seleccionadas)
        self.guardar_pedido_en_bd(desglose)
        self.limpiar_seleccion()
        self.close()

    def limpiar_seleccion(self):
        # Limpiar las listas de productos seleccionados
        self.platillos_seleccionados.clear()
        self.bebidas_seleccionadas.clear()
        # Limpiar la interfaz gráfica para reflejar la selección vacía
        self.ui.listWidget.clear()

    def guardar_pedido_en_bd(self, desglose):
        try:
            # Verificar si la conexión está abierta antes de ejecutar la consulta
            if self.db_connection_pedidos is not None and self.db_connection_pedidos:
                cursor = self.db_connection_pedidos.cursor()
                cursor.execute("INSERT INTO Pedidos (Desglose) VALUES (?)", (desglose,))
                self.db_connection_pedidos.commit()
                QMessageBox.information(self, "Información", "El pedido ha sido enviado a cocina")
            else:
                QMessageBox.warning(self, "Advertencia", "No se pudo guardar el pedido. Conexión no disponible.")
        except sqlite3.Error as error:
            print("Error al guardar en la base de datos:", error)
            QMessageBox.warning(self, "Error", "Error al guardar en la base de datos.")
        finally:
            # Cerrar el cursor después de ejecutar la consulta
            if 'cursor' in locals() and cursor:
                cursor.close()

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
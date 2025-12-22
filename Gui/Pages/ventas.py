import tkinter as tk
from tkinter import ttk, messagebox
from Gui.Pages.Styles.ventas_styles import VentasStyles
from Core.ventas_backend import VentasBackend
from Core.logger import setup_logger

class VentasFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = VentasBackend()
        self.logger = setup_logger()
        self.styles = VentasStyles()
        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.precios_tab = PreciosTab(self.notebook)
        self.notebook.add(self.precios_tab, text="Precios de Venta")

        self.registrar_tab = RegistrarVentaTab(self.notebook)
        self.notebook.add(self.registrar_tab, text="Registrar Venta")

        self.historial_tab = HistorialTab(self.notebook)
        self.notebook.add(self.historial_tab, text="Historial de Ventas")


class PreciosTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        precios_frame = ttk.Frame(self)
        precios_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(precios_frame, text="Precios de venta de Productos", font=("Segoe UI", 14, "bold")).pack(pady=5)

        columns = ("Productos", "Precio Costo", "Precio Venta", "Ganancia")
        self.precios_tree = ttk.Treeview(precios_frame, columns=columns, show="headings", height=10, style="Modern.Treeview")
        self.precios_tree.heading("Productos", text="Productos")
        self.precios_tree.heading("Precio Costo", text="Precio Costo")
        self.precios_tree.heading("Precio Venta", text="Precio Venta")
        self.precios_tree.heading("Ganancia", text="Ganancia")
        self.precios_tree.column("Productos", width=150)
        self.precios_tree.column("Precio Costo", width=100)
        self.precios_tree.column("Precio Venta", width=100)
        self.precios_tree.column("Ganancia", width=100)
        self.precios_tree.pack(fill=tk.BOTH, expand=True)


class RegistrarVentaTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Registrar Venta", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(form_frame, text="Producto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.producto_combo = ttk.Combobox(form_frame, values=["Producto1", "Producto2", "Producto3"])  # Placeholder
        self.producto_combo.grid(row=1, column=1, pady=5, sticky=tk.EW)

        ttk.Label(form_frame, text="Cantidad:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.cantidad_entry = ttk.Entry(form_frame)
        self.cantidad_entry.grid(row=2, column=1, pady=5, sticky=tk.EW)

        ttk.Label(form_frame, text="Precio Unitario:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.precio_entry = ttk.Entry(form_frame)
        self.precio_entry.grid(row=3, column=1, pady=5, sticky=tk.EW)

        ttk.Label(form_frame, text="Cliente:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.cliente_entry = ttk.Entry(form_frame)
        self.cliente_entry.grid(row=4, column=1, pady=5, sticky=tk.EW)

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Registrar Venta", style="Primary.TButton").pack(side=tk.LEFT, padx=10)


class HistorialTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        historial_frame = ttk.Frame(self)
        historial_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(historial_frame, text="Historial de Ventas", font=("Segoe UI", 14, "bold")).pack(pady=5)

        columns = ("Producto", "Cantidad", "Precio Unitario", "Total", "Cliente", "Fecha")
        self.historial_tree = ttk.Treeview(historial_frame, columns=columns, show="headings", height=10, style="Modern.Treeview")
        for col in columns:
            self.historial_tree.heading(col, text=col)
            self.historial_tree.column(col, width=100)
        self.historial_tree.pack(fill=tk.BOTH, expand=True)


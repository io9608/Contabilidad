# Gui/Pages/produccion.py (New File)

import tkinter as tk
from tkinter import ttk, messagebox
from Core.produccion_backend import ProduccionBackend
from Core.inventario_backend import InventarioBackend
from Core.logger import setup_logger
from Gui.Pages.Styles.produccion_styles import ProduccionStyles

class ProduccionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = ProduccionBackend()
        self.inv_backend = InventarioBackend() # To get available ingredients
        self.logger = setup_logger()
        self.styles = ProduccionStyles(self)
        self.ingredientes_list = [] # Temporary list for ingredients being added
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Left Frame: Subproductos ---
        sub_frame = ttk.LabelFrame(main_container, text="1. Crear Subproducto", padding=10, style="Card.TLabelframe")
        sub_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Subproduct Name
        ttk.Label(sub_frame, text="Nombre del Subproducto:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.sub_nombre_entry = ttk.Entry(sub_frame, width=30, style="Modern.TEntry")
        self.sub_nombre_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)

        # Ingredients Section
        ttk.Label(sub_frame, text="Ingredientes:").grid(row=1, column=0, sticky=tk.W, pady=(10, 2))

        ing_frame = ttk.Frame(sub_frame)
        ing_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=2)

        self.ing_producto_combo = ttk.Combobox(ing_frame, width=20)
        self.ing_producto_combo.grid(row=0, column=0, padx=2)
        self.ing_cantidad_entry = ttk.Entry(ing_frame, width=10)
        self.ing_cantidad_entry.grid(row=0, column=1, padx=2)
        self.ing_unidad_combo = ttk.Combobox(ing_frame, values=["g", "kg", "ml", "l", "units"], width=10)
        self.ing_unidad_combo.grid(row=0, column=2, padx=2)

        ttk.Button(ing_frame, text="Añadir Ingrediente", command=self.add_ingredient, style="Primary.TButton").grid(row=0, column=3, padx=5)

        # Ingredients Treeview
        columns = ("Producto", "Cantidad", "Unidad")
        self.ingredientes_tree = ttk.Treeview(sub_frame, columns=columns, show="headings", height=6, style="Modern.Treeview")
        self.ingredientes_tree.heading("Producto", text="Producto")
        self.ingredientes_tree.heading("Cantidad", text="Cantidad")
        self.ingredientes_tree.heading("Unidad", text="Unidad")
        self.ingredientes_tree.column("Producto", width=150)
        self.ingredientes_tree.column("Cantidad", width=100)
        self.ingredientes_tree.column("Unidad", width=100)
        self.ingredientes_tree.grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.EW)

        ttk.Button(sub_frame, text="Crear Subproducto", command=self.crear_subproducto, style="Primary.TButton").grid(row=4, column=0, columnspan=2, pady=10)

        # --- Right Frame: Productos Finales ---
        final_frame = ttk.LabelFrame(main_container, text="2. Crear Producto Final", padding=10, style="Card.TLabelframe")
        final_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Final Product Name
        ttk.Label(final_frame, text="Nombre del Producto Final:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.final_nombre_entry = ttk.Entry(final_frame, width=30, style="Modern.TEntry")
        self.final_nombre_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)

        # Subproduct Selector
        ttk.Label(final_frame, text="Subproducto a usar:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.subproducto_selector = ttk.Combobox(final_frame, width=28, style="Modern.TCombobox")
        self.subproducto_selector.grid(row=1, column=1, sticky=tk.EW, pady=2)
        self.subproducto_selector.bind("<<ComboboxSelected>>", self.on_subproducto_selected)

        # Units Produced
        ttk.Label(final_frame, text="Unidades Producidas:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.unidades_entry = ttk.Entry(final_frame, width=30, style="Modern.TEntry")
        self.unidades_entry.grid(row=2, column=1, sticky=tk.EW, pady=2)

        ttk.Button(final_frame, text="Crear Producto Final", command=self.crear_producto_final, style="Primary.TButton").grid(row=3, column=0, columnspan=2, pady=10)

        # Subproducts Treeview
        sub_columns = ("Nombre", "Costo Total")
        self.subproductos_tree = ttk.Treeview(final_frame, columns=sub_columns, show="headings", height=8, style="Modern.Treeview")
        self.subproductos_tree.heading("Nombre", text="Nombre")
        self.subproductos_tree.heading("Costo Total", text="Costo Total")
        self.subproductos_tree.column("Nombre", width=150)
        self.subproductos_tree.column("Costo Total", width=100)
        self.subproductos_tree.grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.EW)

        # Ingredients of selected subproduct Treeview
        ttk.Label(final_frame, text="Ingredientes del Subproducto:").grid(row=5, column=0, sticky=tk.W, pady=(10, 2))
        ing_sub_columns = ("Producto", "Cantidad", "Unidad")
        self.ing_sub_tree = ttk.Treeview(final_frame, columns=ing_sub_columns, show="headings", height=6)
        self.ing_sub_tree.heading("Producto", text="Producto")
        self.ing_sub_tree.heading("Cantidad", text="Cantidad")
        self.ing_sub_tree.heading("Unidad", text="Unidad")
        self.ing_sub_tree.column("Producto", width=150)
        self.ing_sub_tree.column("Cantidad", width=100)
        self.ing_sub_tree.column("Unidad", width=100)
        self.ing_sub_tree.grid(row=6, column=0, columnspan=2, pady=5, sticky=tk.EW)

        # Configure grid weights
        sub_frame.columnconfigure(1, weight=1)
        final_frame.columnconfigure(1, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)

        # Initial load
        self.load_ingredients()
        self.load_subproductos()

    def load_ingredients(self):
        """Populates the ingredient combobox with products from inventory."""
        inventario = self.inv_backend.get_inventario_para_resumen()
        productos = [item['producto'] for item in inventario]
        self.ing_producto_combo['values'] = productos
        if productos:
            self.ing_producto_combo.current(0)

    def load_subproductos(self):
        """Populates the subproduct combobox and treeview with available subproducts."""
        subproductos = self.backend.get_subproductos_disponibles()
        self.subproducto_selector['values'] = [sub['nombre'] for sub in subproductos]
        self.subproducto_dict = {sub['nombre']: sub['id'] for sub in subproductos}  # Map name to ID

        # Clear and populate subproducts treeview
        for item in self.subproductos_tree.get_children():
            self.subproductos_tree.delete(item)
        for sub in subproductos:
            self.subproductos_tree.insert("", tk.END, values=(sub['nombre'], f"${sub['costo_total_subproducto']:.2f}"))

    def add_ingredient(self):
        """Adds an ingredient to the temporary list."""
        producto = self.ing_producto_combo.get()
        cantidad = self.ing_cantidad_entry.get()
        unidad = self.ing_unidad_combo.get()

        if not producto or not cantidad or not unidad:
            messagebox.showerror("Error", "Por favor complete todos los campos del ingrediente.")
            return

        try:
            cantidad = float(cantidad)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")
            return

        # Add to list
        self.ingredientes_list.append({'producto': producto, 'cantidad': cantidad, 'unidad': unidad})
        self.ingredientes_tree.insert("", tk.END, values=(producto, cantidad, unidad))

        # Clear fields
        self.ing_cantidad_entry.delete(0, tk.END)
        self.ing_unidad_combo.set('')

    def crear_subproducto(self):
        """Creates a subproduct using the backend."""
        nombre = self.sub_nombre_entry.get()
        if not nombre:
            messagebox.showerror("Error", "Por favor ingrese el nombre del subproducto.")
            return
        if not self.ingredientes_list:
            messagebox.showerror("Error", "Por favor añada al menos un ingrediente.")
            return

        try:
            costo = self.backend.crear_subproducto(nombre, self.ingredientes_list)
            messagebox.showinfo("Éxito", f"Subproducto '{nombre}' creado con costo total: ${costo:.2f}")
            # Clear fields
            self.sub_nombre_entry.delete(0, tk.END)
            self.ingredientes_list = []
            for item in self.ingredientes_tree.get_children():
                self.ingredientes_tree.delete(item)
            self.load_subproductos()  # Refresh subproducts
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear subproducto: {str(e)}")

    def crear_producto_final(self):
        """Creates a final product using the backend."""
        nombre = self.final_nombre_entry.get()
        subproducto_nombre = self.subproducto_selector.get()
        unidades = self.unidades_entry.get()

        if not nombre or not subproducto_nombre or not unidades:
            messagebox.showerror("Error", "Por favor complete todos los campos.")
            return

        try:
            unidades = int(unidades)
            subproducto_id = self.subproducto_dict[subproducto_nombre]
            self.backend.crear_producto_final(nombre, subproducto_id, unidades)
            messagebox.showinfo("Éxito", f"Producto final '{nombre}' creado.")
            # Clear fields
            self.final_nombre_entry.delete(0, tk.END)
            self.subproducto_selector.set('')
            self.unidades_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Las unidades deben ser un número entero.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear producto final: {str(e)}")

    def on_subproducto_selected(self, event):
        """Displays the ingredients of the selected subproduct."""
        subproducto_nombre = self.subproducto_selector.get()
        if subproducto_nombre in self.subproducto_dict:
            subproducto_id = self.subproducto_dict[subproducto_nombre]
            ingredientes = self.backend.get_ingredientes_subproducto(subproducto_id)

            # Clear previous ingredients
            for item in self.ing_sub_tree.get_children():
                self.ing_sub_tree.delete(item)

            # Populate ingredients treeview
            for ing in ingredientes:
                self.ing_sub_tree.insert("", tk.END, values=(ing['producto_ingrediente'], ing['cantidad_usada'], ing['unidad_usada']))

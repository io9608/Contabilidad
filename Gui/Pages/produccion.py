"""
Página de Producción con interfaz mejorada. 
- Treeview de subproductos
- Treeview de productos finales
- Botón para producir
"""

import tkinter as tk
from tkinter import ttk, messagebox
from Core.produccion_backend import ProduccionBackend
from Core.inventario_backend import InventarioBackend
from Core.logger import setup_logger


class ProduccionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.backend = ProduccionBackend()
        self.inv_backend = InventarioBackend()
        self.logger = setup_logger()
        
        # Estado actual
        self.ingredientes_list = []
        self.selected_subproducto_id = None
        self.selected_subproducto_name = None
        self.subproductos_map = {}  # id -> subproducto data
        self.productos_finales_map = {}  # id -> producto final data
        
        self.setup_ui()
        self.load_subproductos()
        self.load_productos_finales()
        self.logger.info("ProduccionFrame initialized")

    def setup_ui(self):
        """Configurar la interfaz de usuario."""
        
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ===== HEADER =====
        header_frame = tk.Frame(main, bg="#ffc107", height=70)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="⚙️ Gestión de Producción",
            font=("Segoe UI", 20, "bold"),
            bg="#ffc107",
            fg="white",
            padx=10,
            pady=10
        )
        title.pack(side=tk.LEFT, fill=tk. BOTH, expand=True)
        
        # ===== CONTENEDOR PRINCIPAL (2 COLUMNAS) =====
        content = ttk.Frame(main)
        content.pack(fill=tk.BOTH, expand=True)
        
        # ===== COLUMNA IZQUIERDA:  Crear Subproducto =====
        left_panel = tk.LabelFrame(
            content,
            text="1️⃣ Crear Subproducto",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#ffc107"
        )
        left_panel.pack(side=tk.LEFT, fill=tk. BOTH, expand=True, padx=(0, 10))
        
        # Nombre del subproducto
        tk.Label(
            left_panel,
            text="Nombre del Subproducto:",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        self.sub_nombre_entry = tk.Entry(
            left_panel,
            font=("Segoe UI", 10),
            width=40
        )
        self.sub_nombre_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Ingredientes
        tk.Label(
            left_panel,
            text="Ingredientes:",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(10, 5))
        
        # Frame para agregar ingredientes
        ing_frame = ttk.Frame(left_panel)
        ing_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ing_frame, text="Producto: ").grid(row=0, column=0, sticky="w", padx=2)
        self.ing_producto_combo = ttk.Combobox(ing_frame, width=15, state="readonly")
        self.ing_producto_combo.grid(row=0, column=1, padx=2)
        
        ttk.Label(ing_frame, text="Cantidad:").grid(row=0, column=2, sticky="w", padx=2)
        self.ing_cantidad_entry = tk.Entry(ing_frame, width=10, font=("Segoe UI", 9))
        self.ing_cantidad_entry.grid(row=0, column=3, padx=2)
        
        ttk.Label(ing_frame, text="Unidad:").grid(row=0, column=4, sticky="w", padx=2)
        self.ing_unidad_combo = ttk.Combobox(
            ing_frame,
            values=["g", "kg", "ml", "L", "units"],
            state="readonly",
            width=10
        )
        self.ing_unidad_combo.grid(row=0, column=5, padx=2)
        
        add_ing_btn = tk.Button(
            ing_frame,
            text="➕ Agregar",
            command=self.add_ingredient,
            bg="#0078d4",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            cursor="hand2"
        )
        add_ing_btn. grid(row=0, column=6, padx=5)
        
        # Tabla de ingredientes
        cols = ("Producto", "Cantidad", "Unidad", "Acción")
        self.ingredientes_tree = ttk.Treeview(
            left_panel,
            columns=cols,
            show="headings",
            height=6
        )
        self.ingredientes_tree.heading("Producto", text="Producto")
        self.ingredientes_tree.heading("Cantidad", text="Cantidad")
        self.ingredientes_tree.heading("Unidad", text="Unidad")
        self.ingredientes_tree.heading("Acción", text="Eliminar")
        
        self. ingredientes_tree.column("Producto", width=150)
        self.ingredientes_tree.column("Cantidad", width=80, anchor=tk.CENTER)
        self.ingredientes_tree.column("Unidad", width=70, anchor=tk.CENTER)
        self.ingredientes_tree. column("Acción", width=60, anchor=tk.CENTER)
        
        self.ingredientes_tree.pack(fill=tk. BOTH, expand=True, pady=(0, 15))
        self.ingredientes_tree.bind("<Button-3>", self.on_ingrediente_right_click)
        
        # Botones crear subproducto
        action_frame = tk.Frame(left_panel, bg="white")
        action_frame. pack(fill=tk.X)
        
        create_sub_btn = tk.Button(
            action_frame,
            text="✅ Crear Subproducto",
            command=self. create_subproducto,
            bg="#198754",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            relief=tk. FLAT,
            cursor="hand2"
        )
        create_sub_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            action_frame,
            text="🔄 Limpiar",
            command=self.clear_subproducto,
            bg="#6c757d",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # ===== COLUMNA DERECHA: Subproductos y Productos Finales =====
        right_panel = ttk. Frame(content)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # --- Subproductos ---
        sub_card = tk.LabelFrame(
            right_panel,
            text="2️⃣ Subproductos Disponibles",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#0078d4"
        )
        sub_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tabla de subproductos
        sub_cols = ("Nombre", "Costo Total", "Acción")
        self.subproductos_tree = ttk.Treeview(
            sub_card,
            columns=sub_cols,
            show="headings",
            height=6
        )
        self.subproductos_tree.heading("Nombre", text="📦 Nombre")
        self.subproductos_tree. heading("Costo Total", text="Costo Total")
        self.subproductos_tree.heading("Acción", text="Acción")
        
        self. subproductos_tree.column("Nombre", width=200)
        self.subproductos_tree.column("Costo Total", width=100, anchor=tk.E)
        self.subproductos_tree.column("Acción", width=70, anchor=tk.CENTER)
        
        self.subproductos_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.subproductos_tree.bind("<<TreeviewSelect>>", self. on_subproducto_select)
        self.subproductos_tree. bind("<Button-3>", self.on_subproducto_right_click)
        
        # Info subproducto seleccionado
        info_frame = tk.Frame(sub_card, bg="white")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            info_frame,
            text="Seleccionado:",
            font=("Segoe UI", 9, "bold"),
            bg="white"
        ).pack(anchor="w")
        
        self.selected_sub_label = tk.Label(
            info_frame,
            text="(Ninguno)",
            font=("Segoe UI", 10),
            bg="white",
            fg="#0078d4",
            padx=10
        )
        self.selected_sub_label.pack(anchor="w")
        
        # --- Productos Finales ---
        prod_card = tk.LabelFrame(
            right_panel,
            text="3️⃣ Productos Finales",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            padx=10,
            pady=10,
            fg="#198754"
        )
        prod_card.pack(fill=tk.BOTH, expand=True)
        
        # Tabla de productos finales
        prod_cols = ("Nombre", "Subproducto", "Costo Unit.", "Precio Venta", "Ganancia", "Acción")
        self.productos_finales_tree = ttk.Treeview(
            prod_card,
            columns=prod_cols,
            show="headings",
            height=6
        )
        self.productos_finales_tree.heading("Nombre", text="📦 Nombre")
        self.productos_finales_tree.heading("Subproducto", text="Subproducto")
        self.productos_finales_tree.heading("Costo Unit.", text="Costo Unit.")
        self.productos_finales_tree.heading("Precio Venta", text="Precio Venta")
        self.productos_finales_tree.heading("Ganancia", text="Ganancia")
        self.productos_finales_tree.heading("Acción", text="Acción")
        
        self.productos_finales_tree.column("Nombre", width=120)
        self.productos_finales_tree.column("Subproducto", width=100)
        self.productos_finales_tree.column("Costo Unit.", width=80, anchor=tk.E)
        self.productos_finales_tree.column("Precio Venta", width=80, anchor=tk.E)
        self.productos_finales_tree.column("Ganancia", width=80, anchor=tk.E)
        self.productos_finales_tree.column("Acción", width=70, anchor=tk.CENTER)
        
        self.productos_finales_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.productos_finales_tree.bind("<Button-3>", self.on_producto_right_click)
        
        # ===== FOOTER:  Botón Producir =====
        footer = tk.Frame(right_panel, bg="white")
        footer.pack(fill=tk.X, pady=(10, 0))
        
        produce_btn = tk.Button(
            footer,
            text="🚀 Producir Subproducto",
            command=self.produce_subproducto,
            bg="#d13438",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk. FLAT,
            cursor="hand2"
        )
        produce_btn.pack(fill=tk.X)
        
        # Cargar datos de inventario para combobox de ingredientes
        self.load_ingredient_combo()

    def load_ingredient_combo(self):
        """Cargar productos del inventario para el combobox."""
        try:
            inventario = self.inv_backend. get_inventario_para_resumen()
            productos = [item['producto'] for item in inventario]
            self.ing_producto_combo['values'] = productos
            self.logger.info(f"Cargados {len(productos)} productos para ingredientes")
        except Exception as e:
            self.logger.error(f"Error cargando ingredientes: {e}")

    def load_subproductos(self):
        """Cargar subproductos disponibles."""
        try:
            for item in self.subproductos_tree.get_children():
                self.subproductos_tree. delete(item)
            
            subproductos = self.backend.get_subproductos_disponibles()
            self.subproductos_map. clear()
            
            for sub in subproductos:
                sub_id = sub. get('id')
                self.subproductos_map[sub_id] = sub
                
                self.subproductos_tree. insert(
                    "",
                    tk.END,
                    iid=str(sub_id),
                    values=(
                        sub.get('nombre', ''),
                        f"${sub.get('costo_total_subproducto', 0):.2f}",
                        "🗑️"
                    )
                )
            
            self. logger.info(f"Cargados {len(subproductos)} subproductos")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar subproductos: {e}")
            self.logger.error(f"Error cargando subproductos: {e}")

    def load_productos_finales(self):
        """Cargar productos finales."""
        try:
            for item in self.productos_finales_tree.get_children():
                self.productos_finales_tree.delete(item)
            
            productos = self.backend.get_productos_finales_con_precios()
            self.productos_finales_map.clear()
            
            for prod in productos: 
                prod_id = prod. get('id')
                self. productos_finales_map[prod_id] = prod
                
                costo = float(prod.get('costo_unitario', 0))
                precio_venta = float(prod. get('precio_venta', 0) or 0)
                ganancia = precio_venta - costo
                
                self.productos_finales_tree.insert(
                    "",
                    tk.END,
                    iid=str(prod_id),
                    values=(
                        prod.get('nombre', ''),
                        prod.get('subproducto_nombre', ''),
                        f"${costo:.2f}",
                        f"${precio_venta:.2f}",
                        f"${ganancia:. 2f}",
                        "🗑️"
                    )
                )
            
            self.logger.info(f"Cargados {len(productos)} productos finales")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar productos finales: {e}")
            self.logger.error(f"Error cargando productos finales: {e}")

    def on_subproducto_select(self, event):
        """Manejar selección de subproducto."""
        selection = self.subproductos_tree.selection()
        
        if selection:
            try:
                sub_id = int(selection[0])
                self.selected_subproducto_id = sub_id
                sub_data = self.subproductos_map.get(sub_id)
                
                if sub_data:
                    self.selected_subproducto_name = sub_data. get('nombre')
                    costo = sub_data.get('costo_total_subproducto', 0)
                    self.selected_sub_label.config(
                        text=f"📦 {self.selected_subproducto_name} - ${costo:.2f}"
                    )
                    self.logger.info(f"Subproducto seleccionado:  {self.selected_subproducto_name}")
                    
            except Exception as e:
                self.logger.error(f"Error al seleccionar subproducto: {e}")

    def add_ingredient(self):
        """Agregar ingrediente a la tabla."""
        try:
            producto = self.ing_producto_combo. get()
            cantidad = self.ing_cantidad_entry.get().strip()
            unidad = self.ing_unidad_combo. get()
            
            if not all([producto, cantidad, unidad]):
                messagebox.showwarning("Aviso", "Completa todos los campos")
                return
            
            try:
                float(cantidad)
            except ValueError:
                messagebox. showerror("Error", "La cantidad debe ser un número")
                return
            
            self.ingredientes_tree.insert(
                "",
                tk.END,
                values=(producto, cantidad, unidad)
            )
            
            self.ingredientes_list.append({
                'producto':  producto,
                'cantidad': float(cantidad),
                'unidad': unidad
            })
            
            # Limpiar campos
            self.ing_producto_combo.set("")
            self.ing_cantidad_entry.delete(0, tk.END)
            self.ing_unidad_combo.set("")
            
            self.logger.info(f"Ingrediente agregado: {producto}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error:  {e}")
            self.logger.error(f"Error agregando ingrediente: {e}")

    def on_ingrediente_right_click(self, event):
        """Click derecho para eliminar ingrediente."""
        item = self.ingredientes_tree. identify('item', event.x, event.y)
        
        if not item:
            return
        
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(
            label="❌ Eliminar",
            command=lambda: self.remove_ingrediente(item),
            foreground="red"
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def remove_ingrediente(self, item_id):
        """Eliminar ingrediente."""
        try:
            values = self.ingredientes_tree. item(item_id, 'values')
            self.ingredientes_tree.delete(item_id)
            
            # Eliminar de lista
            self.ingredientes_list = [
                ing for ing in self.ingredientes_list 
                if ing['producto'] != values[0]
            ]
            
            self.logger.info(f"Ingrediente eliminado: {values[0]}")
            
        except Exception as e:
            self. logger.error(f"Error eliminando ingrediente: {e}")

    def create_subproducto(self):
        """Crear nuevo subproducto."""
        try:
            nombre = self.sub_nombre_entry.get().strip()
            
            if not nombre or not self.ingredientes_list:
                messagebox.showwarning("Aviso", "Ingresa nombre y al menos un ingrediente")
                return
            
            costo = self.backend.crear_subproducto(nombre, self.ingredientes_list)
            
            messagebox.showinfo(
                "✅ Éxito",
                f"Subproducto '{nombre}' creado\nCosto Total: ${costo:.2f}"
            )
            
            self.clear_subproducto()
            self.load_subproductos()
            self.logger.info(f"Subproducto creado: {nombre}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            self.logger.error(f"Error creando subproducto: {e}")

    def produce_subproducto(self):
        """Producir subproducto (consumir ingredientes del inventario)."""
        if not self.selected_subproducto_id: 
            messagebox.showwarning("Aviso", "Selecciona un subproducto")
            return
        
        try:
            sub_data = self.subproductos_map.get(self.selected_subproducto_id)
            if not sub_data: 
                messagebox.showerror("Error", "Subproducto no encontrado")
                return
            
            # Obtener ingredientes del subproducto
            ingredientes = self.backend.get_subproducto_ingredientes(self.selected_subproducto_id)
            
            if not ingredientes:
                messagebox. showwarning("Aviso", "El subproducto no tiene ingredientes")
                return
            
            # Consumir stock
            for ing in ingredientes:
                self. inv_backend.consumir_stock(
                    ing['producto_ingrediente'],
                    ing['cantidad_usada'],
                    ing['unidad_usada']
                )
            
            messagebox.showinfo(
                "✅ Éxito",
                f"Ingredientes consumidos para:\n{self.selected_subproducto_name}"
            )
            
            self.load_subproductos()
            self.logger.info(f"Subproducto producido:  {self.selected_subproducto_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            self.logger.error(f"Error produciendo subproducto: {e}")

    def on_subproducto_right_click(self, event):
        """Click derecho en subproducto."""
        item = self.subproductos_tree.identify('item', event.x, event.y)
        
        if not item:
            return
        
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(
            label="❌ Eliminar",
            command=lambda: self. delete_subproducto(int(item)),
            foreground="red"
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def delete_subproducto(self, sub_id):
        """Eliminar subproducto."""
        if not messagebox.askyesno("Confirmar", "¿Eliminar este subproducto?"):
            return
        
        try:
            # TODO: Implementar eliminación en backend
            self.load_subproductos()
            messagebox.showinfo("✅ Éxito", "Subproducto eliminado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def on_producto_right_click(self, event):
        """Click derecho en producto final."""
        item = self.productos_finales_tree.identify('item', event.x, event.y)
        
        if not item: 
            return
        
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(
            label="❌ Eliminar",
            command=lambda: self.delete_producto(int(item)),
            foreground="red"
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def delete_producto(self, prod_id):
        """Eliminar producto final."""
        if not messagebox.askyesno("Confirmar", "¿Eliminar este producto? "):
            return
        
        try:
            # TODO:  Implementar eliminación en backend
            self.load_productos_finales()
            messagebox.showinfo("✅ Éxito", "Producto eliminado")
            
        except Exception as e: 
            messagebox.showerror("Error", f"Error: {e}")

    def clear_subproducto(self):
        """Limpiar formulario."""
        self.sub_nombre_entry.delete(0, tk. END)
        for item in self.ingredientes_tree.get_children():
            self.ingredientes_tree.delete(item)
        self.ingredientes_list. clear()
        self.ing_producto_combo.set("")
        self.ing_cantidad_entry.delete(0, tk.END)
        self.ing_unidad_combo.set("")
        self.logger.info("Formulario de subproducto limpiado")
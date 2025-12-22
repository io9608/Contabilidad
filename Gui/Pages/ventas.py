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

        self.precios_tab = PreciosTab(self.notebook, self.backend)
        self.notebook.add(self.precios_tab, text="Precios de Venta")

        self.clientes_tab = ClientesTab(self.notebook, self.backend)
        self.notebook.add(self.clientes_tab, text="Clientes")

        self.registrar_tab = RegistrarVentaTab(self.notebook, self.backend)
        self.notebook.add(self.registrar_tab, text="Registrar Venta")

        self.historial_tab = HistorialTab(self.notebook, self.backend)
        self.notebook.add(self.historial_tab, text="Historial de Ventas")


class PreciosTab(ttk.Frame):
    def __init__(self, parent, backend: VentasBackend):
        super().__init__(parent)
        self.backend = backend
        self.editing_entry = None
        self.setup_ui()
        self.load_precios()

    def setup_ui(self):
        precios_frame = ttk.Frame(self)
        precios_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(precios_frame, text="Precios de venta de Productos", font=("Segoe UI", 14, "bold")).pack(pady=5)

        columns = ("Productos", "Precio Costo", "Precio Venta", "Ganancia", "% Gan.")
        self.column_ids = columns
        self.precios_tree = ttk.Treeview(precios_frame, columns=columns, show="headings", height=12, style="Modern.Treeview")
        for c in columns:
            self.precios_tree.heading(c, text=c)
        self.precios_tree.column("Productos", width=220)
        self.precios_tree.column("Precio Costo", width=100, anchor=tk.E)
        self.precios_tree.column("Precio Venta", width=120, anchor=tk.E)
        self.precios_tree.column("Ganancia", width=100, anchor=tk.E)
        self.precios_tree.column("% Gan.", width=80, anchor=tk.E)
        self.precios_tree.pack(fill=tk.BOTH, expand=True)

        # Bind double click to start editing Precio Venta cell
        self.precios_tree.bind("<Double-1>", self.on_double_click)

    def load_precios(self):
        try:
            productos = self.backend.get_productos_con_costo()
            # Clear
            for i in self.precios_tree.get_children():
                self.precios_tree.delete(i)
            for p in productos:
                pid = p.get("id")
                costo = p.get("costo_unitario", 0.0)
                venta = p.get("precio_venta", 0.0) or 0.0
                gan = p.get("ganancia_unitaria", 0.0)
                pct = p.get("ganancia_pct", None)
                pct_display = f"{pct:.2f}%" if pct is not None else "-"
                # Use product id as iid so we can retrieve it later
                self.precios_tree.insert("", tk.END, iid=str(pid), values=(p.get("nombre"), f"${costo:.2f}", f"${venta:.2f}", f"${gan:.2f}", pct_display))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los precios: {e}")

    def _start_edit_cell(self, item_id, col_name, bbox):
        # Remove previous editing entry if any
        if self.editing_entry:
            try:
                self.editing_entry.destroy()
            except Exception:
                pass
            self.editing_entry = None

        # Get current value and strip $ if present
        cur_values = self.precios_tree.item(item_id, "values")
        # Map column index
        col_index = self.column_ids.index(col_name)
        cur_text = cur_values[col_index] if col_index < len(cur_values) else ""
        if isinstance(cur_text, str) and cur_text.startswith("$"):
            cur_text = cur_text[1:].strip()
        # Create entry over the tree cell
        x, y, width, height = bbox
        entry = tk.Entry(self.precios_tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, cur_text)
        entry.focus_set()

        def finish_edit(event=None):
            new_text = entry.get().strip()
            try:
                new_price = float(new_text) if new_text != "" else 0.0
            except Exception:
                messagebox.showwarning("Valor inválido", "Ingresa un número válido para precio")
                entry.focus_set()
                return
            # save to DB via backend
            try:
                self.backend.set_precio_venta(int(item_id), new_price)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el precio: {e}")
                entry.destroy()
                self.editing_entry = None
                return
            # update tree display
            vals = list(self.precios_tree.item(item_id, "values"))
            # precio venta is column "Precio Venta"
            try:
                col_idx = self.column_ids.index("Precio Venta")
                vals[col_idx] = f"${new_price:.2f}"
                self.precios_tree.item(item_id, values=vals)
            except Exception:
                pass
            # notify other tabs that price changed
            try:
                # generate virtual event on the notebook (parent) so RegistrarVentaTab can reload
                if hasattr(self.master, "event_generate"):
                    self.master.event_generate("<<PrecioActualizado>>")
            except Exception:
                pass
            entry.destroy()
            self.editing_entry = None

        entry.bind("<Return>", finish_edit)
        entry.bind("<FocusOut>", finish_edit)
        self.editing_entry = entry

    def on_double_click(self, event):
        region = self.precios_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = self.precios_tree.identify_column(event.x)  # e.g., '#3'
        # map to column name
        col_index = int(col.replace("#", "")) - 1
        if col_index < 0 or col_index >= len(self.column_ids):
            return
        col_name = self.column_ids[col_index]
        # Only allow editing the "Precio Venta" column
        if col_name != "Precio Venta":
            return
        rowid = self.precios_tree.identify_row(event.y)
        if not rowid:
            return
        bbox = self.precios_tree.bbox(rowid, column=col)
        if not bbox:
            return
        # bbox returns (x, y, width, height)
        self._start_edit_cell(rowid, col_name, bbox)


class ClientesTab(ttk.Frame):
    def __init__(self, parent, backend: VentasBackend):
        super().__init__(parent)
        self.backend = backend
        self.setup_ui()
        self.load_clients()

    def setup_ui(self):
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top: crear cliente
        create_frame = ttk.Frame(main)
        create_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Label(create_frame, text="Nuevo cliente:").pack(side=tk.LEFT)
        self.new_client_entry = ttk.Entry(create_frame)
        self.new_client_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(create_frame, text="Crear", command=self.create_client, style="Primary.TButton").pack(side=tk.LEFT, padx=5)

        # Middle: clientes list + acciones
        mid = ttk.Frame(main)
        mid.pack(fill=tk.BOTH, expand=True)

        # Clients list
        cols = ("Nombre", "Activo")
        self.clients_tree = ttk.Treeview(mid, columns=cols, show="headings", height=10, style="Modern.Treeview")
        self.clients_tree.heading("Nombre", text="Nombre")
        self.clients_tree.heading("Activo", text="Activo")
        self.clients_tree.column("Nombre", width=220)
        self.clients_tree.column("Activo", width=80, anchor=tk.CENTER)
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clients_tree.bind("<<TreeviewSelect>>", self.on_client_select)

        scrollbar = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Right: stats and toggle
        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        ttk.Label(right, text="Estadísticas", font=("Segoe UI", 12, "bold")).pack(pady=(0,5))
        self.stats_label = ttk.Label(right, text="Selecciona un cliente")
        self.stats_label.pack(pady=5)
        self.toggle_btn = ttk.Button(right, text="Activar/Inactivar", command=self.toggle_active, state=tk.DISABLED)
        self.toggle_btn.pack(pady=5)

        ttk.Label(right, text="Ventas por día", font=("Segoe UI", 11, "bold")).pack(pady=(10,5))
        self.ventas_tree = ttk.Treeview(right, columns=("Fecha","Ventas","Total"), show="headings", height=8)
        self.ventas_tree.heading("Fecha", text="Fecha")
        self.ventas_tree.heading("Ventas", text="Ventas")
        self.ventas_tree.heading("Total", text="Total")
        self.ventas_tree.column("Fecha", width=120)
        self.ventas_tree.column("Ventas", width=60, anchor=tk.E)
        self.ventas_tree.column("Total", width=80, anchor=tk.E)
        self.ventas_tree.pack(fill=tk.BOTH, expand=True)

    def load_clients(self):
        try:
            rows = self.backend.get_clientes()
            # Clear
            for i in self.clients_tree.get_children():
                self.clients_tree.delete(i)
            for r in rows:
                active = r.get("active", 1)
                self.clients_tree.insert("", tk.END, iid=str(r["id"]), values=(r["nombre"], "Sí" if active else "No"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar clientes: {e}")

    def create_client(self):
        name = self.new_client_entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Ingresa el nombre del cliente")
            return
        try:
            self.backend.add_cliente(name)
            self.new_client_entry.delete(0, tk.END)
            self.load_clients()
            messagebox.showinfo("OK", "Cliente creado")
        except ValueError as ve:
            messagebox.showwarning("Aviso", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear cliente: {e}")

    def on_client_select(self, _evt):
        selected = self.clients_tree.selection()
        if not selected:
            self.toggle_btn.config(state=tk.DISABLED)
            self.stats_label.config(text="Selecciona un cliente")
            return
        cliente_id = int(selected[0])
        self.toggle_btn.config(state=tk.NORMAL)
        # load stats
        stats = self.backend.get_cliente_stats(cliente_id)
        self.stats_label.config(text=f"Compras: {stats['purchases_count']}  —  Ganancias: ${stats['total_revenue']:.2f}")
        # ventas por día
        ventas = self.backend.get_ventas_por_dia(cliente_id)
        for i in self.ventas_tree.get_children():
            self.ventas_tree.delete(i)
        for v in ventas:
            self.ventas_tree.insert("", tk.END, values=(v["day"], v["sales_count"], f"${v['total_sum']:.2f}"))

    def toggle_active(self):
        selected = self.clients_tree.selection()
        if not selected:
            return
        cliente_id = int(selected[0])
        try:
            new_state = self.backend.toggle_cliente_active(cliente_id)
            self.load_clients()
            state_text = "Activo" if new_state == 1 else "Inactivo"
            messagebox.showinfo("OK", f"Cliente ahora: {state_text}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar estado: {e}")


class RegistrarVentaTab(ttk.Frame):
    def __init__(self, parent, backend: VentasBackend):
        super().__init__(parent)
        self.backend = backend
        self.product_map = {}  # name -> product dict
        self.item_rows = []  # list of frames for items
        self.setup_ui()
        # Bind to price-updated event so we reload product list when PreciosTab changes a price
        try:
            if hasattr(self.master, "bind"):
                self.master.bind("<<PrecioActualizado>>", lambda e: self.load_products())
        except Exception:
            pass
        self.load_products()
        self.load_clients()

    def setup_ui(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(container, text="Registrar Venta", font=("Segoe UI", 16, "bold")).pack(pady=5)

        top = ttk.Frame(container)
        top.pack(fill=tk.X, pady=5)
        ttk.Label(top, text="Cliente:").pack(side=tk.LEFT)
        self.client_combo = ttk.Combobox(top, state="readonly")
        self.client_combo.pack(side=tk.LEFT, padx=5)

        # Items area
        self.items_frame = ttk.Frame(container)
        self.items_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        btns = ttk.Frame(container)
        btns.pack(fill=tk.X, pady=5)
        ttk.Button(btns, text="Agregar producto", command=self.add_item, style="Secondary.TButton").pack(side=tk.LEFT)
        ttk.Button(btns, text="Registrar Venta", command=self.submit_sale, style="Primary.TButton").pack(side=tk.RIGHT)

        total_frame = ttk.Frame(container)
        total_frame.pack(fill=tk.X, pady=5)
        ttk.Label(total_frame, text="Total:").pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="$0.00", font=("Segoe UI", 12, "bold"))
        self.total_label.pack(side=tk.LEFT, padx=5)

    def load_products(self):
        try:
            prods = self.backend.get_productos_con_costo()
            self.product_map.clear()
            self.product_display_list = []
            self.display_to_name = {}
            for p in prods:
                name = p.get("nombre")
                self.product_map[name] = p
                display = f"{name} — ${p.get('precio_venta',0):.2f}"
                self.product_display_list.append(display)
                self.display_to_name[display] = name
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar productos: {e}")

    def load_clients(self):
        try:
            rows = self.backend.get_clientes_activos()
            vals = [r["nombre"] for r in rows]
            self.client_name_to_id = {r["nombre"]: r["id"] for r in rows}
            self.client_combo['values'] = vals
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar clientes: {e}")

    def add_item(self):
        row = ttk.Frame(self.items_frame)
        row.pack(fill=tk.X, pady=3)

        prod_cb = ttk.Combobox(row, values=self.product_display_list, width=40, state="readonly")
        prod_cb.pack(side=tk.LEFT, padx=3)
        qty_entry = ttk.Entry(row, width=8)
        qty_entry.insert(0, "1")
        qty_entry.pack(side=tk.LEFT, padx=3)
        # price entry (editable)
        price_entry = ttk.Entry(row, width=12)
        price_entry.insert(0, "$0.00")
        price_entry.pack(side=tk.LEFT, padx=3)
        rem_btn = ttk.Button(row, text="Eliminar", command=lambda r=row: self.remove_item(r), style="Secondary.TButton")
        rem_btn.pack(side=tk.LEFT, padx=3)

        def on_change(_ev=None):
            self.update_row_price(prod_cb, price_entry)
            self.update_total()

        prod_cb.bind("<<ComboboxSelected>>", on_change)
        qty_entry.bind("<KeyRelease>", lambda e: self.update_total())
        price_entry.bind("<KeyRelease>", lambda e: self.update_total())

        # set default first product if exists
        if self.product_display_list:
            prod_cb.set(self.product_display_list[0])
            self.update_row_price(prod_cb, price_entry)
            self.update_total()

        self.item_rows.append((row, prod_cb, qty_entry, price_entry))

    def remove_item(self, row_frame):
        # find and remove entry from item_rows
        for tup in list(self.item_rows):
            if tup[0] == row_frame:
                self.item_rows.remove(tup)
                break
        row_frame.destroy()
        self.update_total()

    def update_row_price(self, prod_cb, price_entry):
        disp = prod_cb.get()
        if not disp:
            price_entry.delete(0, tk.END)
            price_entry.insert(0, "$0.00")
            return
        prod_name = self.display_to_name.get(disp)
        prod = self.product_map.get(prod_name, {})
        precio = float(prod.get("precio_venta", 0) or 0)
        price_entry.delete(0, tk.END)
        price_entry.insert(0, f"{precio:.2f}")

    def _parse_price_text(self, text):
        if text is None:
            return 0.0
        txt = str(text).strip()
        if txt.startswith("$"):
            txt = txt[1:].strip()
        try:
            return float(txt) if txt != "" else 0.0
        except Exception:
            return 0.0

    def update_total(self):
        total = 0.0
        for (_, prod_cb, qty_entry, price_entry) in self.item_rows:
            disp = prod_cb.get()
            if not disp:
                continue
            try:
                qty = float(qty_entry.get() or 0)
            except Exception:
                qty = 0
            precio = self._parse_price_text(price_entry.get())
            total += precio * qty
        self.total_label.config(text=f"${total:.2f}")

    def submit_sale(self):
        client_name = self.client_combo.get()
        if not client_name:
            messagebox.showwarning("Aviso", "Selecciona un cliente activo")
            return
        client_id = self.client_name_to_id.get(client_name)
        items = []
        for (_, prod_cb, qty_entry, price_entry) in self.item_rows:
            disp = prod_cb.get()
            if not disp:
                continue
            prod_name = self.display_to_name.get(disp)
            prod = self.product_map.get(prod_name)
            if not prod:
                continue
            try:
                qty = int(float(qty_entry.get()))
                if qty <= 0:
                    continue
            except Exception:
                messagebox.showwarning("Aviso", "Cantidad inválida")
                return
            unit_price = self._parse_price_text(price_entry.get())
            items.append({
                "product_id": prod.get("id"),
                "quantity": qty,
                "unit_price": unit_price
            })
        if not items:
            messagebox.showwarning("Aviso", "Agrega al menos un producto")
            return
        try:
            res = self.backend.crear_venta_multiple(client_id, items)
            messagebox.showinfo("OK", f"Venta registrada. Total: ${res['total']:.2f}")
            # reset UI
            for (r, *_ ) in list(self.item_rows):
                r.destroy()
            self.item_rows.clear()
            self.update_total()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la venta: {e}")


class HistorialTab(ttk.Frame):
    def __init__(self, parent, backend: VentasBackend):
        super().__init__(parent)
        self.backend = backend
        self.setup_ui()
        self.load_historial()

    def setup_ui(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        cols = ("Fecha", "Cliente", "Producto", "Cantidad", "Precio/u", "Total")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=15, style="Modern.Treeview")
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.column("Fecha", width=140)
        self.tree.column("Cliente", width=160)
        self.tree.column("Producto", width=160)
        self.tree.column("Cantidad", width=80, anchor=tk.E)
        self.tree.column("Precio/u", width=100, anchor=tk.E)
        self.tree.column("Total", width=100, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_historial(self):
        try:
            rows = self.backend.get_historial_ventas()
            for i in self.tree.get_children():
                self.tree.delete(i)
            for r in rows:
                self.tree.insert("", tk.END, values=(
                    str(r.get("fecha_venta")),
                    r.get("cliente"),
                    r.get("producto"),
                    r.get("cantidad_vendida"),
                    f"${float(r.get('precio_unitario_venta') or 0):.2f}",
                    f"${float(r.get('total_venta') or 0):.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar historial: {e}")
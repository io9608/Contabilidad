import tkinter as tk
from tkinter import ttk, messagebox
from Core.ventas_backend import VentasBackend

class RegistrarVentaTab(ttk.Frame):
    tab_name = "Registro Venta"

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

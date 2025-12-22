import tkinter as tk
from tkinter import ttk
from Gui.Pages.ResumenesTabs.inventario_tab import InventarioTab
from Core.inventario_backend import InventarioBackend

from Core.logger import setup_logger

class ResumenesFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = setup_logger()
        self.backend = InventarioBackend()
        self.setup_ui()

        # Inventario tab
        self.inv_tab = InventarioTab(self.notebook, self.backend)
        self.notebook.add(self.inv_tab, text="Inventario")

        # Recetas tab
        #self.recetas_tab = RecetasTab(self.notebook, self.subproductos_backend)
        #self.notebook.add(self.recetas_tab, text="Recetas")

        self.logger.info("ResumenesFrame initialized with Inventario and Recetas tabs")

    def setup_ui(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

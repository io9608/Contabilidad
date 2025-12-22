# Core/produccion_backend.py (Completed File)

import pymysql
from decimal import Decimal
from Core.database import get_connection
from Core.logger import setup_logger
from Core.inventario_backend import InventarioBackend

logger = setup_logger()

class ProduccionBackend:
    def __init__(self):
        self.db = get_connection()
        self.inventory_manager = InventarioBackend() # We need this to consume stock
        logger.info("ProduccionBackend initialized")

    def crear_subproducto(self, nombre_subproducto, ingredientes):
        """
        Creates a subproduct and consumes the required ingredients from inventory.
        
        :param nombre_subproducto: Name of the subproduct (e.g., "Masa de Donas")
        :param ingredientes: A list of dictionaries, e.g.,
            [
                {'producto': 'Harina', 'cantidad': 200, 'unidad': 'g'},
                {'producto': 'Levadura', 'cantidad': 10, 'unidad': 'g'}
            ]
        :return: The total cost of the created subproduct.
        """
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        
        total_costo = Decimal(0)
        try:
            # --- Phase 1: Calculate Cost and Validate Stock ---
            with conn.cursor() as cursor:
                for ing in ingredientes:
                    producto = ing['producto']
                    cantidad = ing['cantidad']
                    unidad = ing['unidad']

                    # Get cost per base unit from inventory
                    cursor.execute("SELECT costo_promedio_ponderado FROM inventario WHERE producto = %s", (producto,))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError(f"El ingrediente '{producto}' no se encuentra en el inventario.")
                    
                    costo_por_base = result['costo_promedio_ponderado']
                    # Convert used amount to base unit to calculate cost
                    from Core.units import convert_to_base
                    cantidad_base, _ = convert_to_base(cantidad, unidad)
                    if not cantidad_base:
                        raise ValueError(f"No se pudo convertir la cantidad para '{producto}'")
                    
                    total_costo += Decimal(cantidad_base) * costo_por_base

            # --- Phase 2: Consume Stock (All or Nothing) ---
            for ing in ingredientes:
                self.inventory_manager.consumir_stock(ing['producto'], ing['cantidad'], ing['unidad'])

            # --- Phase 3: Save Subproduct to Database ---
            with conn.cursor() as cursor:
                # Insert the main subproduct record
                cursor.execute(
                    "INSERT INTO subproductos (nombre, costo_total_subproducto) VALUES (%s, %s)",
                    (nombre_subproducto, total_costo)
                )
                subproducto_id = cursor.lastrowid

                # Insert each ingredient
                for ing in ingredientes:
                    cursor.execute(
                        "INSERT INTO subproducto_ingredientes (subproducto_id, producto_ingrediente, cantidad_usada, unidad_usada) VALUES (%s, %s, %s, %s)",
                        (subproducto_id, ing['producto'], ing['cantidad'], ing['unidad'])
                    )
            
            conn.commit()
            logger.info(f"Subproducto '{nombre_subproducto}' creado con éxito. Costo: ${total_costo:.2f}")
            return total_costo

        except Exception as e:
            logger.error(f"Error al crear subproducto: {e}")
            conn.rollback()
            raise # Re-raise the error to be caught by the GUI
        finally:
            conn.close()

    def get_subproductos_disponibles(self):
        """Returns a list of all created subproducts for use in final products."""
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre, costo_total_subproducto FROM subproductos ORDER BY nombre")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al obtener subproductos: {e}")
            return []
        finally:
            conn.close()

    def get_ingredientes_subproducto(self, subproducto_id):
        """Returns the ingredients of a specific subproduct."""
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT producto_ingrediente, cantidad_usada, unidad_usada FROM subproducto_ingredientes WHERE subproducto_id = %s",
                    (subproducto_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al obtener ingredientes del subproducto: {e}")
            return []
        finally:
            conn.close()

    def crear_producto_final(self, nombre_producto, subproducto_id, unidades_producidas):
        """
        Creates a final product record based on a subproduct.
        
        :param nombre_producto: Name of the final product (e.g., "Donas")
        :param subproducto_id: The ID of the subproduct used (e.g., ID of "Masa de Donas")
        :param unidades_producidas: How many final units were made (e.g., 30 donas)
        """
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO productos_finales (nombre, subproducto_id, unidades_producidas) VALUES (%s, %s, %s)",
                    (nombre_producto, subproducto_id, unidades_producidas)
                )
            conn.commit()
            logger.info(f"Producto Final '{nombre_producto}' creado con éxito.")
        except Exception as e:
            logger.error(f"Error al crear producto final: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_productos_finales_info(self):
        """
        Returns a list of final products with their cost per unit.
        This is crucial for the sales page.
        """
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT
                    pf.id,
                    pf.nombre,
                    pf.unidades_producidas,
                    sp.costo_total_subproducto,
                    (sp.costo_total_subproducto / pf.unidades_producidas) AS costo_por_unidad
                FROM productos_finales pf
                JOIN subproductos sp ON pf.subproducto_id = sp.id
                ORDER BY pf.nombre
                """
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al obtener info de productos finales: {e}")
            return []
        finally:
            conn.close()

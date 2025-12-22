# Core/ventas_backend.py (Completed File)

import pymysql
from Core.database import get_connection
from Core.logger import setup_logger
from Core.produccion_backend import ProduccionBackend

logger = setup_logger()

class VentasBackend:
    def __init__(self):
        self.db = get_connection()
        self.prod_backend = ProduccionBackend() # To get product costs
        logger.info("VentasBackend initialized")

    def add_cliente(self, nombre_cliente):
        """Adds a new client to the database."""
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO clientes (nombre) VALUES (%s)", (nombre_cliente,))
            conn.commit()
            logger.info(f"Cliente '{nombre_cliente}' añadido.")
        except pymysql.IntegrityError:
            # This error happens if the client name already exists (due to UNIQUE constraint)
            logger.warning(f"El cliente '{nombre_cliente}' ya existe.")
            raise ValueError("Este cliente ya existe.")
        except Exception as e:
            logger.error(f"Error al añadir cliente: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_clientes(self):
        """Returns a list of all clients."""
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al obtener clientes: {e}")
            return []
        finally:
            conn.close()

    def get_productos_con_costo(self):
        """
        Gets final products and adds their calculated cost for the sales UI.
        """
        productos_info = self.prod_backend.get_productos_finales_info()
        # The data is already in a good format from the production backend
        return productos_info

    def registrar_venta(self, cliente_id, producto_final_id, cantidad_vendida, precio_unitario_venta):
        """
        Records a single sale transaction.
        """
        conn = get_connection()
        if not conn: raise Exception("No database connection")
        try:
            with conn.cursor() as cursor:
                # Calculate the total sale value
                total_venta = cantidad_vendida * precio_unitario_venta
                
                cursor.execute(
                    "INSERT INTO ventas (cliente_id, producto_final_id, cantidad_vendida, precio_unitario_venta, total_venta) VALUES (%s, %s, %s, %s, %s)",
                    (cliente_id, producto_final_id, cantidad_vendida, precio_unitario_venta, total_venta)
                )
            conn.commit()
            logger.info(f"Venta registrada: ClienteID {cliente_id}, ProductoID {producto_final_id}, Cantidad {cantidad_vendida}")
        except Exception as e:
            logger.error(f"Error al registrar venta: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_historial_ventas(self):
        """Returns the full sales history with client and product names."""
        conn = get_connection()
        if not conn: return []
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT
                    v.fecha_venta,
                    c.nombre AS cliente,
                    pf.nombre AS producto,
                    v.cantidad_vendida,
                    v.precio_unitario_venta,
                    v.total_venta,
                    sp.costo_total_subproducto,
                    pf.unidades_producidas,
                    (sp.costo_total_subproducto / pf.unidades_producidas) AS costo_unitario,
                    (v.precio_unitario_venta - (sp.costo_total_subproducto / pf.unidades_producidas)) * v.cantidad_vendida AS ganancia_total
                FROM ventas v
                JOIN clientes c ON v.cliente_id = c.id
                JOIN productos_finales pf ON v.producto_final_id = pf.id
                JOIN subproductos sp ON pf.subproducto_id = sp.id
                ORDER BY v.fecha_venta DESC
                """
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error al obtener historial de ventas: {e}")
            return []
        finally:
            conn.close()
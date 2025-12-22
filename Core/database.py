import pymysql
from datetime import datetime
from Core.logger import setup_logger

logger = setup_logger()

def get_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="pp",
            database="pruebas",
            password="1234",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        # Tabla para compras 
        with conn.cursor() as cursor:
            sql = """
                CREATE TABLE IF NOT EXISTS compras (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    producto VARCHAR(255) NOT NULL,
                    cantidad VARCHAR(255) NOT NULL,
                    unidad VARCHAR(255) NOT NULL,
                    precio_compra DECIMAL(10,2) NOT NULL,
                    precio_total DECIMAL(10,2) NOT NULL,
                    proveedor VARCHAR(255) NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            cursor.execute(sql)
            sql_inv = """
                CREATE TABLE IF NOT EXISTS inventario (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    producto VARCHAR(100) UNIQUE NOT NULL,
                    cantidad_stock DECIMAL(15,4) NOT NULL DEFAULT 0,
                    unidad_base VARCHAR(20) NOT NULL,
                    costo_promedio_ponderado DECIMAL(10,4) NOT NULL DEFAULT 0
                )
                """
            cursor.execute(sql_inv)
            sql_sub = """
                CREATE TABLE IF NOT EXISTS subproductos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) UNIQUE NOT NULL,
                    costo_total_subproducto DECIMAL(10,2) NOT NULL
                )
                """
            cursor.execute(sql_sub)
            sql_ing = """
                CREATE TABLE IF NOT EXISTS subproducto_ingredientes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subproducto_id INT NOT NULL,
                    producto_ingrediente VARCHAR(255) NOT NULL,
                    cantidad_usada DECIMAL(10,4) NOT NULL,
                    unidad_usada VARCHAR(20) NOT NULL,
                    FOREIGN KEY (subproducto_id) REFERENCES subproductos(id) ON DELETE CASCADE
                )
                """
            cursor.execute(sql_ing)

            sql_prod_final = """
                CREATE TABLE IF NOT EXISTS productos_finales (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) UNIQUE NOT NULL,
                    subproducto_id INT NOT NULL,
                    unidades_producidas INT NOT NULL,
                    FOREIGN KEY (subproducto_id) REFERENCES subproductos(id) ON DELETE CASCADE
                )
                """
            cursor.execute(sql_prod_final)

            sql_clientes = """
                CREATE TABLE IF NOT EXISTS clientes(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) UNIQUE NOT NULL
                )
                """
            cursor.execute(sql_clientes)
            sql_ventas = """
                CREATE TABLE IF NOT EXISTS ventas(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cliente_id INT NOT NULL,
                    producto_final_id INT NOT NULL,
                    cantidad_vendida INT NOT NULL,
                    precio_unitario_venta DECIMAL(10,2) NOT NULL,
                    total_venta DECIMAL(10,2) NOT NULL,
                    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                    FOREIGN KEY (producto_final_id) REFERENCES productos_finales(id)
                )
                """
            cursor.execute(sql_ventas)

            conn.commit()
            logger.info("Tables 'compras', 'inventario', 'subproductos', 'subproducto_ingredientes', 'productos_finales', 'clientes', and 'ventas' created or already exist")
        return conn
    except pymysql.Error as e:
        logger.error(f"Error obteniendo coneccion a MariaDb:{e}")
        return None

def insert_compra(producto, cantidad, unidad, precio_compra, precio_total, proveedor, tipo):
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO compras (producto, cantidad, unidad, precio_compra, precio_total, proveedor, tipo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (producto, cantidad, unidad, precio_compra, precio_total, proveedor, tipo))
                conn.commit()
                logger.info(f"Inserted purchase: {producto}")
        except Exception as e:
            logger.error(f"Error inserting purchase: {e}")
        finally:
            conn.close()

def get_compras():
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT producto, cantidad, unidad, precio_compra, precio_total, proveedor, tipo, fecha FROM compras ORDER BY fecha DESC")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error retrieving purchases: {e}")
        finally:
            conn.close()
    return []







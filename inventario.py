import sqlite3

DB_NAME = "inventario.db"


def inicializar_db():
    """Crea la tabla si no existe y agrega las columnas nuevas si faltan."""
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE COLLATE NOCASE
        )
    """)

    cursor.execute("PRAGMA table_info(productos)")
    columnas = [columna[1] for columna in cursor.fetchall()]

    if "precio" not in columnas:
        cursor.execute("ALTER TABLE productos ADD COLUMN precio REAL")

    if "categoria" not in columnas:
        cursor.execute("ALTER TABLE productos ADD COLUMN categoria TEXT")

    conexion.commit()
    conexion.close()


def agregar_producto():
    nombre = input("Ingrese el nombre del producto: ").strip().capitalize()

    if nombre == "":
        print("Fallo: el nombre no puede estar vacío.")
        return

    try:
        precio = float(input("Ingrese el precio: "))
        if precio < 0:
            print("Fallo: el precio no puede ser negativo.")
            return

        categoria = input("Ingrese la categoría: ").strip().capitalize()
        if categoria == "":
            print("Fallo: la categoría no puede estar vacía.")
            return

    except ValueError:
        print("Fallo: el precio debe ser un número.")
        return

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO productos (nombre, precio, categoria)
            VALUES (?, ?, ?)
            """,
            (nombre, precio, categoria)
        )
        conexion.commit()
        print(f"Producto '{nombre}' agregado correctamente.")

    except sqlite3.IntegrityError:
        print(f"El producto '{nombre}' ya existe.")

    finally:
        conexion.close()


def eliminar_producto_menu():

    print("\n--- ELIMINAR PRODUCTO ---")
    print("1 - Eliminar por nombre")
    print("2 - Eliminar por ID")
    print("3 - Volver al menú principal")

    opcion = input("Seleccione cómo desea eliminar: ").strip()

    if opcion == "1":
        eliminar_producto()

    elif opcion == "2":
        eliminar_por_id()

    elif opcion == "3":
        print("Volviendo al menú principal...")

    else:
        print("Opción inválida.")


def listar_productos():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, precio, categoria
        FROM productos
        ORDER BY nombre COLLATE NOCASE
    """)

    productos = cursor.fetchall()

    if len(productos) == 0:
        print("No hay productos registrados.")
    else:
        print(f"\nLISTA DE PRODUCTOS ({len(productos)})")
        print("-" * 80)

        print(f"{'ID':<6} {'PRODUCTO':<25} {'PRECIO':>12} {'CATEGORIA':<20}")
        print("-" * 80)

        for id_producto, nombre, precio, categoria in productos:

            precio_texto = f"${precio:.2f}" if precio is not None else "Sin asignar"
            categoria_texto = categoria if categoria is not None else "Sin asignar"

            print(
                f"{id_producto:<6} "
                f"{nombre:<25} "
                f"{precio_texto:>12} "
                f"{categoria_texto:<20}"
            )

        print("-" * 80)

    conexion.close()

def buscar_producto():
    nombre = input("Ingrese el producto a buscar: ").strip()

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, precio, categoria
        FROM productos
        WHERE nombre = ? COLLATE NOCASE
    """, (nombre,))

    producto = cursor.fetchone()

    if producto:
        id_producto, nombre, precio, categoria = producto
        print(f"El producto '{nombre}' se encuentra en la lista.")
        print(f"Identificador: {id_producto}")

        if precio is None:
            print("Precio: Sin asignar")
        else:
            print(f"Precio: ${precio:.2f}")

        if categoria is None:
            print("Categoría: Sin asignar")
        else:
            print(f"Categoría: {categoria}")
    else:
        print(f"El producto '{nombre}' no está en la lista.")

    conexion.close()


def modificar_producto():
    nombre = input("Ingrese el producto que desea modificar: ").strip()

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, precio, categoria
        FROM productos
        WHERE nombre = ? COLLATE NOCASE
    """, (nombre,))

    producto = cursor.fetchone()

    if producto is None:
        print(f"El producto '{nombre}' no existe.")
        conexion.close()
        return

    id_producto, nombre, precio_actual, categoria_actual = producto

    print("\nDATOS ACTUALES")
    print(f"Producto: {nombre}")
    print(f"Precio: {precio_actual if precio_actual is not None else 'Sin asignar'}")
    print(f"Categoría: {categoria_actual if categoria_actual is not None else 'Sin asignar'}")

    nuevo_precio = input("\nIngrese el nuevo precio (Enter para conservar): ").strip()

    if nuevo_precio == "":
        precio_final = precio_actual
    else:
        try:
            precio_final = float(nuevo_precio)

            if precio_final < 0:
                print("El precio no puede ser negativo.")
                conexion.close()
                return

        except ValueError:
            print("Error: debe ingresar un precio numérico.")
            conexion.close()
            return

    nueva_categoria = input("Ingrese la nueva categoría (Enter para conservar): ").strip()

    if nueva_categoria == "":
        categoria_final = categoria_actual
    else:
        categoria_final = nueva_categoria.capitalize()

    cursor.execute("""
        UPDATE productos
        SET precio = ?, categoria = ?
        WHERE id = ?
    """, (precio_final, categoria_final, id_producto))

    conexion.commit()
    conexion.close()

    print("\n¡Producto modificado correctamente!")
    

def eliminar_por_id():

    try:
        id_producto = int(input("Ingrese el ID del producto que desea eliminar: "))
    except ValueError:
        print("Error: debe ingresar un ID numérico.")
        return

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT nombre FROM productos WHERE id = ?",
        (id_producto,)
    )

    producto = cursor.fetchone()

    if producto is None:
        print(f"No existe un producto con el ID {id_producto}.")
    else:
        confirmar = input(
            f"¿Desea eliminar '{producto[0]}'? (s/n): "
        ).strip().lower()

        if confirmar == "s":
            cursor.execute(
                "DELETE FROM productos WHERE id = ?",
                (id_producto,)
            )
            conexion.commit()
            print("Producto eliminado correctamente.")
        else:
            print("Operación cancelada.")

    conexion.close()


def menu():

    opcion = ""

    while opcion != "6":

        print("\n************************")
        print("1 - Agregar producto")
        print("2 - Eliminar producto")
        print("3 - Lista de productos")
        print("4 - Buscar un producto")
        print("5 - Modificar producto")
        print("6 - SALIR")
        print("************************")

        opcion = input("\nIngrese la opción deseada: ").strip()

        if opcion == "1":
            agregar_producto()

        elif opcion == "2":
            eliminar_producto_menu()

        elif opcion == "3":
            listar_productos()

        elif opcion == "4":
            buscar_producto()

        elif opcion == "5":
            modificar_producto()

        elif opcion == "6":
            print("Saliendo del programa... ¡Hasta luego!")

        else:
            print("Opción inválida. Elija un número del 1 al 6.")


inicializar_db()
menu()

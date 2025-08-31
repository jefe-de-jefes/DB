import mysql.connector
from mysql.connector import errors
import os
import sys
import re

def pedir_correo(messagge:str):
    formato_correo = r'^[\w\.-]+@[\w]+\.\w{2,}$'
    while True:
        correo = input(messagge)
        if re.match(formato_correo, correo):
            return correo
        else:
            print('Formato de correo invalido.')


def cleaner():
    os.system('cls' if os.name == 'nt' else 'clear')

def pedir_int(messagge:str, min:int, max:int) -> int:
    while True:
        try:
            value:int = int(input(messagge))
            if min <= value <= max:
                return value
        except ValueError:
            print(f"Por favor, introduzca un numero entero valido entre {min} y {max}")

def pedir_float(messagge:str, min:float, max:float) -> float:
    while True:
        try:
            value:float = float(input(messagge))
            if min <= value <= max:
                return value
        except ValueError:
            print(f"Por favor, introduzca un numero entero valido entre {min} y {max}")

def print_user(datos_user)->str: #datos user esta conformado por nombre y sexo
    if(datos_user[1] == 'M'):
        return f'Mr {datos_user[0].upper()}'
    else:
        return f'Msr {datos_user[0].upper()}'

def print_reportes(option, venta, usuario, stock):
    while(option != 6):
        if option == 1:
            venta.reporte_ventas()
            break
        elif option == 2:
            usuario.reporte_usuarios()
            break
        elif option == 3:
            stock.reporte_stock()
            break
        elif option == 4:
            print('Vuelva pronto.')
            break


def menu_principal()->int:
    cleaner()
    print('BIENVENIDO AL MENU PRINCIPAL DE INTERACCION CON FIRST')
    print('1.-Nueva venta')
    print('2.-Dar de alta usuario')
    print('3.-Modificar usuario')
    print('4.-Actualizar stock')
    print('5.-Reportes')
    print('6.-Salir')
    return pedir_int('Seleccione la opcion deseada: ', 0, 6)

def menu_reportes()->int:
    cleaner()
    print('BIENVENIDO AL MENU DE REPORTES')
    print('1.-Reporte de ventas')
    print('2.-Reporte de usuarios')
    print('3.-Reporte de inventario')
    print('4.-Regresar al menu principal')
    return pedir_int('Seleccione la opcion deseada: ', 0, 4)

def menu_actualizar()->int:
    cleaner()
    print('Seleccione apartado del usuario a modificar:')
    print('1.-Nombre')
    print('2.-Correo')
    print('3.-Edad')
    print('4.-Sexo')
    print('5.-Salir')
    return pedir_int('Introduzca la opcion deseada: ', 1, 5)

def menu_actualizar_produ()->int:
    cleaner()
    print('Seleccione apartado del usuario a modificar:')
    print('1.-Nombre')
    print('2.-Stock')
    print('3.-Precio')
    print('4.-Salir')
    return pedir_int('Introduzca la opcion deseada: ', 1, 4)

def pedir_sexo():
    while True:
        sex = input('Introduzca el sexo del usuario [M o F]: ').upper()
        if sex in ['M', 'F']:
            return sex
        else:
            print('Opcion no valida. Intente nuevamente')

class User:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
    def insertar_user(self):
        try:
            cleaner()
            while True:
                print('**NUEVO USUARIO**')
                nombre = input('Introduzca el nombre del usuario: ')
                email = pedir_correo('Introduzca el correo electronico: ')
                edad = pedir_int('Introduzca su edad: ', 18, 75)
                sexo = pedir_sexo()

                print(f'Nombre: {nombre}')
                print(f'Correo: {email}')
                print(f'Edad: {edad}')
                print(f'Sexo: Masculino') if sexo == 'M' else print('Sexo: Femenino')
                option = pedir_int('Para confirmar presione 1. Para cancelar presione 2: ',1,2 )
                if option == 2:
                    print('***Operacion cancelada. ***')
                    return
                sql_insert = ('INSERT INTO users (nombre, email, edad, sexo) VALUES (%s, %s, %s, %s)')
                values = (nombre, email, edad, sexo)
                self.cursor.execute(sql_insert, values)
                self.conn.commit()

                print(f'*** Usuario #{self.cursor.lastrowid} registrado con exito. ***')
                input()
                return
        except errors.IntegrityError as e:
            print('Error: Usuario no encontrado en la base de datos. {e}')
            self.conn.rollback()

        except errors.DatabaseError as e:
            print(f'Error en la base de datos: {e}')
            self.conn.rollback()

        except Exception as e:
            print(f'Error inesperado al insertar usuario: {e}')
            self.conn.rollback()
        finally:
            input('Presione cualquier tecla para volver al menu principal.')


    def actualizar_user(self, id_user):
        try:
            cleaner()
            while True:
                print(f'** ACTUALIZAR USUARIO #{id_user} **')

                sql_user = ('SELECT * FROM users WHERE IdUser = %s')
                self.cursor.execute(sql_user, (id_user,))
                datos = self.cursor.fetchone()

                # Que datos voy a actualizar
                if self.validar_usuario(datos) == 2:
                    input('Presione enter para volver al menu principal...')
                    return

                cleaner()
                option = menu_actualizar()

                if option == 1:
                    var = 'nombre'
                    new_dato = input('Introduzca el nuevo nombre: ')
                elif option == 2:
                    var = 'email'
                    new_dato = pedir_correo()
                elif option == 3:
                    var = 'edad'
                    new_dato = pedir_int('Introduce la nueva edad del usuario: ', 1, 75)
                elif option == 4:
                    var = 'sexo'
                    new_dato = pedir_sexo()
                elif option == 5:
                    print('Cancelando modificacion...')
                    input('Presione enter para volver al menu principal...')
                    return

                sql_actualizar = (f'UPDATE users SET {var} = %s WHERE IdUser = %s')
                values = (new_dato, id_user)
                self.cursor.execute(sql_actualizar, values)
                self.conn.commit()

                print('** Datos actualizados **')
                sql_user = ('SELECT * FROM users WHERE IdUser = %s')
                self.cursor.execute(sql_user, (id_user,))
                datos = self.cursor.fetchone()
                if self.validar_usuario(datos) == 2:
                    print('Deshaciendo ultimo movimiento...')
                    self.conn.rollback()
                    input('Ultimo movimiento eliminado exitosamente...')
                    return
                print(f'*** Usuario #{id_user} actualizado con exito con exito. ***')
                input()
                return
        except errors.IntegrityError as e:
            print(f'Error: Usuario no encontrado en la base de datos. {e}')
            self.conn.rollback()

        except errors.DatabaseError as e:
            print(f'Error en la base de datos: {e}')
            self.conn.rollback()

        except Exception as e:
            print(f'Error inesperado al actualizar usuario: {e}')
            self.conn.rollback()
        finally:
            input('Presione cualquier tecla para volver al menu principal.')

    def validar_usuario(self, datos)->int:
        try:
            print('Datos del usuario:')
            print(f'{"Id_Usuario":<15} {"Nombre":<15} {"Correo":<15} {"Edad":<15} {"Total_pedidos":<15} {"Sexo":<15}')

            for i in datos:
                print(f'{i:<15}', end = ' | ')
            print()

            option = pedir_int('Para confirmar usuario a modificar presione 1. Para cancelar presione 2: ', 1, 2)
            if option == 2:
                print('*** Operacion cancelada. ***')
            return option
        except Exception as e:
            print(f'Error en validar_usuario.: {e}')

    def reporte_usuarios(self):
        try:
            cleaner()
            print('*** REPORTE DE USUARIOS ACTIVOS ***')
            self.cursor.execute('SELECT * FROM users;')
            datos = self.cursor.fetchall()

            if not datos:
                print("No hay usuarios registrados.")
                return

            headers = [desc[0] for desc in self.cursor.description]
            print(" | ".join(f"{h:<17}" for h in headers))
            print("-" * 90)

            for row in datos:
                print(" | ".join(f"{str(col):<17}" for col in row))

            input("\nPresione cualquier tecla para volver al menú...")

        except Exception as e:
            print('Error inesperado: ', e)



class Ventas:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    def new_venta(self):
        try:
            id_user = pedir_int('Introduzca el Id del usuario: ', 1, sys.maxsize)

            #obtener nombre con id
            sql_user = 'SELECT nombre, sexo FROM users WHERE IdUser = %s'
            self.cursor.execute(sql_user, (id_user,))
            datos_user = self.cursor.fetchone()

            #bienvenida personalizada a usuario
            print(f'Bienvenido {print_user(datos_user)} al sistema gestionador de la DB ventas-clientes-stock')
            id_article = pedir_int('Introduzca el codigo del articulo> ', 1, sys.maxsize)
            sql_precio = 'SELECT precio, article, stock FROM Stock WHERE IdArticle = %s'
            self.cursor.execute(sql_precio, (id_article,))
            datos_articulo:tuple = self.cursor.fetchone()

            tot_articles:int = pedir_int(f'Introduzca el total de piezas a comprar del articulo {datos_articulo[1]}: ', 1, datos_articulo[2])

            tot_sale = datos_articulo[0] * tot_articles
            print(f'Seria un total de {tot_sale}, acepta la compra [1.-Si/2.-No]?')
            agree = pedir_int('> ', 1, 2)
            if agree == 2:
                print('*** Agregado como cliente codo ***')
                print('Bye bye')
                return
            #HACE LA CONSULTA Y LA GUARDA EN sql_insert
            sql_insert = 'INSERT INTO Sales (IdArticle, IdUser, TotArticle, TotSale) VALUES (%s, %s, %s, %s)'
            values = (id_article, id_user, tot_articles, tot_sale)

            #hace la ejecucion de la consulta osea inserta los datos
            self.cursor.execute(sql_insert, values)

            #guarda los datos en la BD
            self.conn.commit()
            print(f'*** Venta #{self.cursor.lastrowid} de {datos_articulo[1]} por un total de ${tot_sale} realizada con exito. ***')

        except Error as e:
            if e.errno == 1044:
                print("El usuario no tiene privilegios sobre la base de datos.")

        except errors.IntegrityError as e:
            print(f'Error: Usuario o artículo no encontrado en la base de datos. {e}')
            self.conn.rollback()

        except errors.DatabaseError as e:
            print(f'Error en la base de datos: {e}')
            self.conn.rollback()

        except Exception as e:
            print(f'Error inesperado al ingresar venta: {e}')
            self.conn.rollback()
        finally:
            input('Presione cualquier tecla para volver al menu principal.')

    def reporte_ventas(self):
        try:
            cleaner()
            print('*** REPORTE DE VENTAS ***')
            self.cursor.execute('SELECT * FROM Sales;')
            datos = self.cursor.fetchall()

            if not datos:
                print("No hay ventas por el momento, hablenle a marketing.")
                return

            headers = [desc[0] for desc in self.cursor.description]
            print(" | ".join(f"{h:<17}" for h in headers))
            print("-" * 90)

            for row in datos:
                print(" | ".join(f"{str(col):<17}" for col in row))

            input("\nPresione cualquier tecla para volver al menú...")

        except Exception as e:
            print('Error inesperado: ', e)

class Inventario:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    def actualizar_stock(self, id_produ):
            try:
                cleaner()
                while True:
                    print(f'** ACTUALIZAR PRODUCTO #{id_produ} **')

                    sql_produ = ('SELECT * FROM Stock WHERE IdArticle = %s')
                    self.cursor.execute(sql_produ, (id_produ,))
                    datos_produ = self.cursor.fetchone()

                    if self.validar_produ(datos_produ) == 2:
                        input('Presione enter para volver al menu principal...')
                        return

                    cleaner()
                    option = menu_actualizar_produ()

                    if option == 1:
                        var = 'article'
                        new_dato = input('Introduzca el nuevo nombre: ')
                    elif option == 2:
                        var = 'stock'
                        new_dato = pedir_int('Introduzca la nueva cantidad en inventario: ', 0, sys.maxsize)
                    elif option == 3:
                        var = 'precio'
                        new_dato = pedir_float('Introduce el nuevo precio del producto: ', 1, float('inf'))
                    elif option == 4:
                        print('Cancelando modificacion...')
                        input('Presione enter para volver al menu principal...')
                        return

                    sql_actualizar = (f'UPDATE Stock SET {var} = %s WHERE IdArticle = %s')
                    values = (new_dato, id_produ)
                    self.cursor.execute(sql_actualizar, values)
                    self.conn.commit()

                    print('** Datos actualizados **')
                    sql_produ = ('SELECT * FROM Stock WHERE IdArticle = %s')
                    self.cursor.execute(sql_produ, (id_produ,))
                    datos = self.cursor.fetchone()
                    if self.validar_produ(datos) == 2:
                        print('Deshaciendo ultimo movimiento...')
                        self.conn.rollback()
                        input('Ultimo movimiento eliminado exitosamente...')
                        return
                    print(f'*** Producto #{id_produ} actualizado con exito con exito. ***')
                    input()
                    return
            except errors.IntegrityError as e:
                print('Error: Usuario no encontrado en la base de datos. {e}')
                self.conn.rollback()

            except errors.DatabaseError as e:
                print(f'Error en la base de datos: {e}')
                self.conn.rollback()

            except Exception as e:
                print(f'Error inesperado al actualizar usuario: {e}')
                self.conn.rollback()
            finally:
                input('Presione cualquier tecla para volver al menu principal.')

    def validar_produ(self, datos)->int:
        try:
            print('Datos del producto:')
            print(f'{"Id_Articulo":<15} {"Nombre":<15} {"Stock":<15} {"Precio":<15}')

            for i in datos:
                print(f'{i:<15}', end = ' | ')
            print()

            option = pedir_int('Para confirmar producto a modificar presione 1. Para cancelar presione 2: ', 1, 2)
            if option == 2:
                print('*** Operacion cancelada. ***')
            return option
        except Exception as e:
            print(f'Error en validar_usuario.: {e}')

    def reporte_stock(self):
        try:
            cleaner()
            print('*** REPORTE DE INVENTARIO ***')
            self.cursor.execute('SELECT * FROM Stock;')
            datos = self.cursor.fetchall()

            if not datos:
                print("No hay inventario, favor de marcar a proveedores.")
                return

            headers = [desc[0] for desc in self.cursor.description]
            print(" | ".join(f"{h:<17}" for h in headers))
            print("-" * 90)

            for row in datos:
                print(" | ".join(f"{str(col):<17}" for col in row))

            input("\nPresione cualquier tecla para volver al menú...")

        except Exception as e:
            print('Error inesperado: ', e)



#excepciones para errores en la bd
def main():
    try:
        conn = mysql.connector.connect(
            host='192.168.0.15',
            port=3306,
            user=input('Introduzca su usuario> '),
            password=input('Introduzca la contraseña> '),
            database=input('Introduzca el nombre de la DB> ')
            )

        if conn.is_connected():
            print('Conectado a la BD')
            cursor =  conn.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(record[0])


        venta = Ventas(conn, cursor)
        usuario = User(conn, cursor)
        stock = Inventario(conn, cursor)

        option_menu:int = 0

        while(option_menu != 6):
            option_menu = menu_principal()
            if option_menu == 1:
                venta.new_venta()
                continue
            elif option_menu == 2:
                usuario.insertar_user()
                continue
            elif option_menu == 3:
                usuario.actualizar_user(pedir_int('Introduce el id del usuario: ', 1, sys.maxsize))
                continue
            elif option_menu == 4:
                stock.actualizar_stock(pedir_int('Introduce el id del produco: ', 1, sys.maxsize))
            elif option_menu == 5:
                op_reportes = menu_reportes()
                print_reportes(op_reportes, venta, usuario, stock)
            elif option_menu == 6:
                print('Vuelva pronto.')
                break



    except Error as e:
        if e.errno == 1044:
            print("Busca otra BD porque no eres bienvenido aqui (por el momento): ", e)
        elif e.errno == 1045:
            print("Escribe bien tu contraseña o usuario animal: ", e)
        elif e.errno == 2003:
            print("Porfavor revisa que no tenga fallas el server", e)
        else:
            print('Error muy inesperado, que andas haciendo maik', e)

    except Exception as e:
        print('Error ', e)

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error inesperado por favor contactese con los chidos', e)


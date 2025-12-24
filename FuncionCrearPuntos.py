

def linear_interpolation(p_start, p_end, v):
    return p_start * (1 - v) + p_end * v

def chess_to_mm(square):
    """
    Calcula X, Y y Z según la zona.
    Z = 143.0 para el tablero principal (a-h)
    Z = 118.0 para las zonas externas (i-n)
    """
    square = square.lower().strip()
    col_char = square[0]
    row_num = int(square[1])

    # Factor V (Filas)
    v = (row_num - 1) / 7.0
    
    # Definir alturas
    z_tablero = 143.0
    z_externo = 118.0
    
    # --- ZONA 1: TABLERO PRINCIPAL (a-h) ---
    if 'a' <= col_char <= 'h':
        p_a1 = np.array([228.5, 839.5]) 
        p_h1 = np.array([-41.0, 850.0]) 
        p_a8 = np.array([220.0, 572.0]) 
        p_h8 = np.array([-49.5, 580.5]) 

        col_idx = ord(col_char) - ord('a')
        u = col_idx / 7.0
        
        xy = bilinear_interpolation(p_a1, p_h1, p_a8, p_h8, u, v)
        return np.array([xy[0], xy[1], z_tablero]) # Agregamos Z tablero

    # --- ZONA 2: BASURERO BLANCAS (i-j) ---
    elif col_char in ['i', 'j']:
        p_i1 = np.array([411.0, 854.0])
        p_j1 = np.array([365.0, 844.0])
        p_i8 = np.array([411.0, 556.0])
        p_j8 = np.array([365.0, 561.0])

        col_idx = ord(col_char) - ord('i') 
        u = col_idx / 1.0 
        
        xy = bilinear_interpolation(p_i1, p_j1, p_i8, p_j8, u, v)
        return np.array([xy[0], xy[1], z_externo]) # Agregamos Z externo

    # --- ZONA 3: BASURERO NEGRAS (l-m) ---
    elif col_char in ['l', 'm']:
        p_l1 = np.array([-172.0, 859.0])
        p_m1 = np.array([-222.0, 851.0])
        p_l8 = np.array([-172.0, 574.5])
        p_m8 = np.array([-222.0, 575.0])

        col_idx = ord(col_char) - ord('l')
        u = col_idx / 1.0
        
        xy = bilinear_interpolation(p_l1, p_m1, p_l8, p_m8, u, v)
        return np.array([xy[0], xy[1], z_externo]) # Agregamos Z externo

    # --- ZONA 4: REINAS BLANCAS (k) ---
    elif col_char == 'k':
        p_k1 = np.array([464.0, 846.0])
        p_k8 = np.array([464.0, 555.0])
        
        xy = linear_interpolation(p_k1, p_k8, v)
        return np.array([xy[0], xy[1], z_externo]) # Agregamos Z externo

    # --- ZONA 5: REINAS NEGRAS (n) ---
    elif col_char == 'n':
        p_n1 = np.array([-269.0, 857.0])
        p_n8 = np.array([-269.0, 577.0])
        
        xy = linear_interpolation(p_n1, p_n8, v)
        return np.array([xy[0], xy[1], z_externo]) # Agregamos Z externo

    else:
        raise ValueError(f"Columna '{col_char}' no reconocida.")

def generar_archivo_robot(cadena_movimientos, tipo_movimiento):
    # Ruta base
    ruta_base = r"X:\EpsonRC70\Projects\chess_arm_robot"

    if not os.path.exists(ruta_base):
        try:
            os.makedirs(ruta_base)
        except:
            print(f"Error: No se pudo crear la carpeta {ruta_base}")
            return

    nombres = {
        0: "move.txt",
        1: "capture.txt",
        2: "promotion.txt",
        3: "capture_promotion.txt"
    }

    if tipo_movimiento not in nombres:
        print("Error: Tipo inválido.")
        return

    nombre_archivo = nombres[tipo_movimiento]
    ruta_completa = os.path.join(ruta_base, nombre_archivo)
    lista_coordenadas = []

    for i in range(0, len(cadena_movimientos), 2):
        casilla = cadena_movimientos[i : i+2]
        try:
            punto = chess_to_mm(casilla)
            # Escribimos X, Y, Z (3 valores)
            lista_coordenadas.append(f"{punto[0]:.2f},{punto[1]:.2f},{punto[2]:.2f}")
        except Exception as e:
            print(f"Error procesando '{casilla}': {e}")
            return

    try:
        with open(ruta_completa, "w") as f:
            f.write("\n".join(lista_coordenadas))
        print(f"--- Archivo generado: {nombre_archivo} ---")
    except Exception as e:
        print(f"Error escribiendo archivo: {e}")

if __name__ == "__main__":
    # Prueba: Movimiento del tablero (z=143) a zona externa (z=118)
    generar_archivo_robot("f2l1n8f1", 2)

import numpy as np
import os


class RobotMoveWriter:
    """
    Convierte casillas de ajedrez a coordenadas (X,Y,Z)
    y genera archivos para el robot.
    """

    def __init__(self):
        # Ruta base
        self.ruta_base = r"X:\EpsonRC70\Projects\chess_arm_robot"

        # Alturas
        self.z_tablero = 143.0
        self.z_externo = 118.0

        # --- TABLERO PRINCIPAL ---
        self.p_a1 = np.array([228.5, 839.5])
        self.p_h1 = np.array([-41.0, 850.0])
        self.p_a8 = np.array([220.0, 572.0])
        self.p_h8 = np.array([-49.5, 580.5])

        # --- BASURERO BLANCAS ---
        self.p_i1 = np.array([411.0, 854.0])
        self.p_j1 = np.array([365.0, 844.0])
        self.p_i8 = np.array([411.0, 556.0])
        self.p_j8 = np.array([365.0, 561.0])

        # --- BASURERO NEGRAS ---
        self.p_l1 = np.array([-172.0, 859.0])
        self.p_m1 = np.array([-222.0, 851.0])
        self.p_l8 = np.array([-172.0, 574.5])
        self.p_m8 = np.array([-222.0, 575.0])

        # --- REINAS ---
        self.p_k1 = np.array([464.0, 846.0])
        self.p_k8 = np.array([464.0, 555.0])
        self.p_n1 = np.array([-269.0, 857.0])
        self.p_n8 = np.array([-269.0, 577.0])

        # Tipos de archivo
        self.nombres = {
            0: "move.txt",
            1: "capture.txt",
            2: "promotion.txt",
            3: "capture_promotion.txt"
        }

    # --------------------------------------------------
    # Interpolaciones (MISMAS funciones, ahora métodos)
    # --------------------------------------------------
    def bilinear_interpolation(self, c1, c2, c3, c4, u, v):
        return (c1 * (1 - u) * (1 - v) +
                c2 * u * (1 - v) +
                c3 * (1 - u) * v +
                c4 * u * v)

    def linear_interpolation(self, p_start, p_end, v):
        return p_start * (1 - v) + p_end * v

    # --------------------------------------------------
    # Conversión chess → mm (MISMA lógica)
    # --------------------------------------------------
    def chess_to_mm(self, square):
        square = square.lower().strip()
        col_char = square[0]
        row_num = int(square[1])

        # Factor filas
        v = (row_num - 1) / 7.0

        # --- TABLERO PRINCIPAL ---
        if 'a' <= col_char <= 'h':
            col_idx = ord(col_char) - ord('a')
            u = col_idx / 7.0
            xy = self.bilinear_interpolation(
                self.p_a1, self.p_h1, self.p_a8, self.p_h8, u, v
            )
            return np.array([xy[0], xy[1], self.z_tablero])

        # --- BASURERO BLANCAS ---
        elif col_char in ['i', 'j']:
            col_idx = ord(col_char) - ord('i')
            u = col_idx / 1.0
            xy = self.bilinear_interpolation(
                self.p_i1, self.p_j1, self.p_i8, self.p_j8, u, v
            )
            return np.array([xy[0], xy[1], self.z_externo])

        # --- BASURERO NEGRAS ---
        elif col_char in ['l', 'm']:
            col_idx = ord(col_char) - ord('l')
            u = col_idx / 1.0
            xy = self.bilinear_interpolation(
                self.p_l1, self.p_m1, self.p_l8, self.p_m8, u, v
            )
            return np.array([xy[0], xy[1], self.z_externo])

        # --- REINAS BLANCAS ---
        elif col_char == 'k':
            xy = self.linear_interpolation(self.p_k1, self.p_k8, v)
            return np.array([xy[0], xy[1], self.z_externo])

        # --- REINAS NEGRAS ---
        elif col_char == 'n':
            xy = self.linear_interpolation(self.p_n1, self.p_n8, v)
            return np.array([xy[0], xy[1], self.z_externo])

        else:
            raise ValueError(f"Columna '{col_char}' no reconocida.")

    # --------------------------------------------------
    # Generación del archivo (MISMA función, ahora método)
    # --------------------------------------------------
    def generar_archivo_robot(self, cadena_movimientos, tipo_movimiento):

        if not os.path.exists(self.ruta_base):
            try:
                os.makedirs(self.ruta_base)
            except:
                print(f"Error: No se pudo crear la carpeta {self.ruta_base}")
                return

        if tipo_movimiento not in self.nombres:
            print("Error: Tipo inválido.")
            return

        nombre_archivo = self.nombres[tipo_movimiento]
        ruta_completa = os.path.join(self.ruta_base, nombre_archivo)
        lista_coordenadas = []

        for i in range(0, len(cadena_movimientos), 2):
            casilla = cadena_movimientos[i:i+2]
            punto = self.chess_to_mm(casilla)
            lista_coordenadas.append(
                f"{punto[0]:.2f},{punto[1]:.2f},{punto[2]:.2f}"
            )

        try:
            with open(ruta_completa, "w") as f:
                f.write("\n".join(lista_coordenadas))
            print(f"--- Archivo generado: {nombre_archivo} ---")
        except Exception as e:
            print(f"Error escribiendo archivo: {e}")

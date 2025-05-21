import pdb
import numpy as np

class ChaoticBitGenerator:
    def __init__(self):
        pass

    def _logistic_map_func(self, x, mu):
        """Función interna para una iteración del mapa logístico."""
        if not (0 < x < 1):
            raise ValueError("x debe estar en el intervalo (0, 1)")
        if not (0 <= mu <= 4):
            raise ValueError("mu debe estar en el intervalo [0, 4]")
        return mu * x * (1 - x)

    def _tent_map_func(self, x, r):
        """Función interna para una iteración del mapa de la tienda."""
        # Validaciones añadidas
        if not (0 <= x <= 1):
            raise ValueError("Valor de x para el mapa de la tienda debe estar en [0, 1].")
        if not (1 < r <= 2): # Rango común para comportamiento caótico.
            raise ValueError("Valor de r para el mapa de la tienda debe estar en (1, 2].")

        if x < 0.5:
            return r * x
        else: # 0.5 <= x <= 1
            return r * (1 - x)

    def _sine_map_func(self, x): # Eliminamos *args ya que no es necesario y puede causar confusión
        """Función interna para una iteración del mapa seno.
        El mapa seno 'estándar' es S(x) = sin(pi * x). No tiene un parámetro 'r' o 'mu'.
        """
        # Validaciones añadidas
        if not (0 <= x <= 1):
            raise ValueError("Valor de x para el mapa seno debe estar en [0, 1].")
        return np.sin(np.pi * x)

    def _get_map_function(self, map_type):
        """Retorna la función del mapa caótico basada en el tipo."""
        if map_type == 'logistic':
            return self._logistic_map_func
        elif map_type == 'tent':
            return self._tent_map_func
        elif map_type == 'sine':
            return self._sine_map_func
        else:
            raise ValueError(f"Tipo de mapa caótico no soportado: {map_type}. Elija 'logistic', 'tent' o 'sine'.")

    def generate_cccbg_bits(self, map_type1: str, x0_1: float, param1: float,
                       map_type2: str, x0_2: float, param2: float,
                       num_bits: int) -> np.ndarray:
        # Validación de parámetros
        if map_type1 == 'logistic' and not (3.57 <= param1 <= 4.0):
            raise ValueError("Para Logistic Map, mu debe estar en [3.57, 4.0]")
        if map_type2 == 'tent' and not (1.999 <= param2 <= 2.0):
            raise ValueError("Para Tent Map, r debe estar en [1.999, 2.0]")
        """
        Implementa el Cross-Coupled Chaotic Bit Generator (CCCBG) descrito en el paper.
        Genera una secuencia de bits utilizando dos mapas caóticos acoplados.

        Args:
            map_type1 (str): Tipo del primer mapa ('logistic', 'tent', 'sine').
            x0_1 (float): Condición inicial para el primer mapa (x_a^0). Debe estar en (0, 1).
            param1 (float): Parámetro para el primer mapa (mu para logistic, r para tent). No usado para sine map.
            map_type2 (str): Tipo del segundo mapa ('logistic', 'tent', 'sine').
            x0_2 (float): Condición inicial para el segundo mapa (x_b^0). Debe estar en (0, 1).
            param2 (float): Parámetro para el segundo mapa (mu para logistic, r para tent). No usado para sine map.
            num_bits (int): El número de bits a generar.

        Returns:
            np.ndarray: Una secuencia de bits (0s y 1s) generada por el CCCBG.
        """
        if not (0 < x0_1 < 1 and 0 < x0_2 < 1):
            raise ValueError("Las condiciones iniciales (x0_1, x0_2) deben estar estrictamente en el rango (0, 1) para un comportamiento caótico adecuado.")
        if not num_bits > 0:
            raise ValueError("El número de bits a generar debe ser un entero positivo.")
            
        F1 = self._get_map_function(map_type1)
        F2 = self._get_map_function(map_type2)

        bits = []
        x_a = x0_1
        x_b = x0_2

        for i in range(num_bits):
            # Paso 2: Iterar los mapas con sus parámetros individuales
            # Para sine map, el parámetro no se pasa.
            f1_xa = F1(x_a, param1) if map_type1 != 'sine' else F1(x_a)
            f2_xb = F2(x_b, param2) if map_type2 != 'sine' else F2(x_b)

            # Paso 3: Acoplar los mapas (Ecuaciones 11 y 12 del paper)
            x_a_next = (f1_xa + x_b) % 1
            x_b_next = (f2_xb + x_a) % 1
            
            # Paso 4: Generación del bit (Rule for bit generation)
            bit = 1 if x_a_next > 0.5 else 0
            bits.append(bit)

            # Actualizar los valores para la próxima iteración
            x_a = x_a_next
            x_b = x_b_next

        return np.array(bits)
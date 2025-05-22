import numpy as np

class ChaoticBitGenerator:
    def __init__(self):
        pass

    def _skew_tent_map(self, x, alpha):
        """
        Skew Tent Map: 
        f(x) = x/alpha        si 0 <= x < alpha
             = (1-x)/(1-alpha) si alpha <= x <= 1
        """
        if not (0.49 <= alpha <= 0.50):
            raise ValueError("El parámetro alpha debe estar en el rango [0.49, 0.50].")
        if not (0 <= x <= 1):
            raise ValueError("x debe estar en el intervalo [0, 1].")
        if x < alpha:
            return x / alpha
        else:
            return (1 - x) / (1 - alpha)

    def generate_cccbg_bits(self, alpha: float, x0: float, y0: float, num_bits: int) -> np.ndarray:
        """
        Genera una secuencia de bits usando dos mapas Skew Tent acoplados cruzadamente.

        Args:
            alpha (float): Parámetro del sistema Skew Tent (0.49 <= alpha <= 0.50).
            x0 (float): Condición inicial del primer mapa (en [0, 1]).
            y0 (float): Condición inicial del segundo mapa (en [0, 1]).
            num_bits (int): Número de bits a generar.

        Returns:
            np.ndarray: Secuencia de bits (0s y 1s).
        """
        if not (0.49 <= alpha <= 0.50):
            raise ValueError("El parámetro alpha debe estar en el rango [0.49, 0.50].")
        if not (0 <= x0 <= 1 and 0 <= y0 <= 1):
            raise ValueError("Las condiciones iniciales x0, y0 deben estar en [0, 1].")
        if not num_bits > 0:
            raise ValueError("El número de bits a generar debe ser un entero positivo.")

        bits = []
        x = x0
        y = y0

        for _ in range(num_bits):
            # Paso 1: Iterar ambos mapas Skew Tent
            fx = self._skew_tent_map(x, alpha)
            fy = self._skew_tent_map(y, alpha)
            # Paso 2: Acoplamiento cruzado
            x_next = (fx + y) % 1
            y_next = (fy + x) % 1
            # Paso 3: Generación del bit
            bit = 1 if x_next > 0.5 else 0
            bits.append(bit)
            x = x_next
            y = y_next

        return np.array(bits)
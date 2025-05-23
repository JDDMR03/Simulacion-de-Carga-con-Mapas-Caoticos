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

    def generate_cccbg_bits(self, alpha: float, x0: float, y0: float, num_bits: int) -> tuple:
        """
        Genera una secuencia de bits usando dos mapas Skew Tent acoplados cruzadamente.
        Devuelve: bits, x_values, periodo_ok

        Args:
            alpha (float): Parámetro del sistema Skew Tent (0.49 <= alpha <= 0.50).
            x0 (float): Condición inicial del primer mapa (en [0, 1]).
            y0 (float): Condición inicial del segundo mapa (en [0, 1]).
            num_bits (int): Número de bits a generar.

        Returns:
            tuple: (Secuencia de bits (0s y 1s), lista de valores x generados, resultado de periodo)
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
        x_values = []
        y_values = []
        seen = set()
        period_ok = True

        for i in range(num_bits):
            # Paso 1: Iterar ambos mapas Skew Tent
            fx = self._skew_tent_map(x, alpha)
            fy = self._skew_tent_map(y, alpha)
            # Paso 2: Acoplamiento cruzado
            x_next = (fx + y) % 1
            y_next = (fy + x) % 1

            # Guardar el número real antes de decidir el bit
            x_values.append(x_next)
            y_values.append(y_next)

            # Verificar periodo: si x_next o y_next ya se vieron, no cumple periodo
            key = (round(x_next, 10), round(y_next, 10))
            if key in seen:
                period_ok = False
                break
            seen.add(key)

            # Paso 3: Generación del bit
            bit = 1 if x_next > 0.5 else 0
            bits.append(bit)
            x = x_next
            y = y_next

        # Si se terminó el ciclo sin romper, cumple periodo
        if len(bits) == num_bits:
            period_ok = True
        else:
            period_ok = False

        return np.array(bits), np.array(x_values), period_ok
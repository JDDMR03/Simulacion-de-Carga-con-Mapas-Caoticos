import numpy as np
from scipy.stats import chi2
from scipy.special import erfc

class RandomnessTests:
    def __init__(self):
        pass

    def monobit_test(self, bit_sequence: np.ndarray) -> dict:
        """
        Monobit Test (Frequency Test): Verifica si la cantidad de 0s y 1s es aproximadamente igual.
        """
        n = len(bit_sequence)
        if n < 100:
            return {"p_value": np.nan, "statistic": np.nan, "message": f"Secuencia demasiado corta (n={n}). Se requiere n >= 100."}
        # Convertir bits a +1/-1
        bits_pm = 2 * bit_sequence - 1
        s_obs = np.sum(bits_pm)
        s_obs_norm = abs(s_obs) / np.sqrt(n)
        p_value = erfc(s_obs_norm / np.sqrt(2))
        return {"p_value": p_value, "statistic": s_obs_norm, "message": "OK"}

    def serial_test(self, bit_sequence: np.ndarray, m: int = 2) -> dict:
        """
        Serial Test: Verifica la frecuencia de aparición de todos los patrones de longitud m.
        Para m=2, compara la frecuencia de 00, 01, 10, 11.
        """
        n = len(bit_sequence)
        if n < 1000:
            return {"p_value": np.nan, "statistic": np.nan, "message": f"Secuencia de bits demasiado corta (n={n}). Se recomienda n >= 1000."}
        if m != 2:
            return {"p_value": np.nan, "statistic": np.nan, "message": "Solo m=2 soportado."}
        # Contar ocurrencias de cada díada
        pairs = [str(int(bit_sequence[i])) + str(int(bit_sequence[i+1])) for i in range(n-1)]
        counts = {k: 0 for k in ['00', '01', '10', '11']}
        for p in pairs:
            counts[p] += 1
        observed = np.array([counts['00'], counts['01'], counts['10'], counts['11']])
        expected = (n-1) / 4
        chi2_stat = np.sum((observed - expected) ** 2 / expected)
        df = 3
        p_value = 1 - chi2.cdf(chi2_stat, df)
        return {"p_value": p_value, "statistic": chi2_stat, "message": "OK"}

    def auto_correlation_test(self, bit_sequence: np.ndarray, d: int = 1) -> dict:
        """
        Auto-correlation Test: Verifica la correlación entre bits separados por d posiciones.
        """
        n = len(bit_sequence)
        if n < 1000 or d >= n:
            return {"p_value": np.nan, "statistic": np.nan, "message": "Secuencia demasiado corta o d inválido."}
        matches = np.sum(bit_sequence[:n-d] == bit_sequence[d:])
        v = matches
        stat = 2 * (v - (n-d)/2) / np.sqrt(n-d)
        p_value = erfc(abs(stat)/np.sqrt(2))
        return {"p_value": p_value, "statistic": stat, "message": "OK"}

    def poker_test(self, bit_sequence: np.ndarray, m: int = 4) -> dict:
        """
        Poker Test: Divide la secuencia en bloques de m bits y verifica la frecuencia de cada patrón.
        """
        n = len(bit_sequence)
        k = n // m
        if n < 5000 or k < 5 * (2**m):
            return {"p_value": np.nan, "statistic": np.nan, "message": f"Secuencia demasiado corta o m muy grande (n={n}, m={m})."}
        blocks = [''.join(str(int(b)) for b in bit_sequence[i*m:(i+1)*m]) for i in range(k)]
        unique, counts = np.unique(blocks, return_counts=True)
        freq = np.zeros(2**m)
        for u, c in zip(unique, counts):
            freq[int(u, 2)] = c
        stat = ((2**m) / k) * np.sum(freq**2) - k
        df = 2**m - 1
        p_value = 1 - chi2.cdf(stat, df)
        return {"p_value": p_value, "statistic": stat, "message": "OK"}

    def run_all_tests(self, bit_sequence: np.ndarray) -> dict:
        results = {}
        results['Monobit Test'] = self.monobit_test(bit_sequence)
        results['Serial Test'] = self.serial_test(bit_sequence, m=2)
        results['Auto-correlation Test (d=1)'] = self.auto_correlation_test(bit_sequence, d=1)
        results['Poker Test (m=4)'] = self.poker_test(bit_sequence, m=4)
        return results
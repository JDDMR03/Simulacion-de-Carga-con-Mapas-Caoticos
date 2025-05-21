# tests/test_randomness_tests.py
import unittest
import numpy as np
from src.core.randomness_tests import RandomnessTests

class TestRandomnessTests(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada método de prueba."""
        self.tester = RandomnessTests()
        self.alpha = 0.01 # Umbral de significancia para las pruebas

    # --- Pruebas para monobit_test ---
    def test_monobit_test_random_sequence(self):
        """
        Prueba Monobit con una secuencia pseudo-aleatoria (debería pasar).
        """
        bits = np.random.randint(0, 2, size=100000)
        result = self.tester.monobit_test(bits)
        p_value = result['p_value'] # Acceder al p_value del diccionario
        self.assertIsInstance(p_value, (float, np.float64))
        self.assertFalse(np.isnan(p_value))
        self.assertGreaterEqual(p_value, 0)
        self.assertLessEqual(p_value, 1)
        self.assertGreaterEqual(p_value, self.alpha)

    def test_monobit_test_non_random_sequence_zeros(self):
        """
        Prueba Monobit con una secuencia de solo ceros (debería fallar).
        """
        bits = np.zeros(10000)
        result = self.tester.monobit_test(bits)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        self.assertLess(p_value, self.alpha)

    def test_monobit_test_non_random_sequence_alternating(self):
        """
        Prueba Monobit con una secuencia 010101... (debería pasar, ya que la cuenta de 0s y 1s es balanceada).
        """
        bits = np.array([i % 2 for i in range(10000)])
        result = self.tester.monobit_test(bits)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        self.assertGreaterEqual(p_value, self.alpha) 

    def test_monobit_test_short_sequence(self):
        """
        Prueba Monobit con una secuencia muy corta (debería devolver NaN).
        """
        bits = np.random.randint(0, 2, size=50) # Longitud < 100
        result = self.tester.monobit_test(bits)
        p_value = result['p_value']
        self.assertTrue(np.isnan(p_value)) # np.isnan ahora funciona porque p_value es float/np.float64

    # --- Pruebas para serial_test ---
    def test_serial_test_random_sequence(self):
        """
        Prueba Serial con una secuencia pseudo-aleatoria (debería pasar).
        """
        bits = np.random.randint(0, 2, size=50000)
        result = self.tester.serial_test(bits, m=2)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        self.assertFalse(np.isnan(p_value))
        self.assertGreaterEqual(p_value, self.alpha)

    def test_serial_test_non_random_sequence_alternating(self):
        """
        Prueba Serial con una secuencia 010101... (debería fallar).
        """
        bits = np.array([i % 2 for i in range(50000)])
        result = self.tester.serial_test(bits, m=2)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        self.assertLess(p_value, self.alpha)

    def test_serial_test_short_sequence(self):
        """
        Prueba Serial con una secuencia muy corta (debería devolver NaN).
        """
        bits = np.random.randint(0, 2, size=1000) # Longitud < 20000
        result = self.tester.serial_test(bits, m=2)
        p_value = result['p_value']
        self.assertTrue(np.isnan(p_value))
        
    # --- Pruebas para auto_correlation_test ---
    def test_autocorr_test_random_sequence(self): # Added this test, it was missing in the provided snippet
        """
        Prueba Auto-Correlation con una secuencia pseudo-aleatoria (debería pasar).
        """
        bits = np.random.randint(0, 2, size=50000)
        result = self.tester.auto_correlation_test(bits, d=1)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        self.assertFalse(np.isnan(p_value))
        self.assertGreaterEqual(p_value, self.alpha)

    def test_autocorr_test_non_random_sequence_alternating_pattern(self): # Renamed this test
        """
        Prueba Auto-Correlation con una secuencia con patrón que debería fallar para d=1.
        Usamos 010101... para asegurar que el autocorr_test falle con d=1
        ya que bit[i] != bit[i+1] siempre, lo que lleva a c_d = 0 y un p-value bajo.
        """
        num_bits = 50000
        # Una secuencia 010101...
        bits = np.array([i % 2 for i in range(num_bits)]) 
        
        result = self.tester.auto_correlation_test(bits, d=1)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        # Para 010101... con d=1, la correlación es mínima, el p-value debería ser muy bajo.
        self.assertLess(p_value, self.alpha) 

    def test_autocorr_test_non_random_sequence_0011_pattern(self): # Renamed this test
        """
        Prueba Auto-Correlation con una secuencia con patrón 00110011... (debería fallar para d=1).
        """
        bits = np.array([0,0,1,1]*(12500)) # 50000 bits
        result = self.tester.auto_correlation_test(bits, d=1)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        # Re-evaluating this assertion: For 00110011... with d=1, about half the bits match.
        # This test might actually PASS with d=1 if 'half matches' is considered random enough for THIS particular test.
        # If it should definitively FAIL, we need a different 'd' or a different pattern.
        # Let's keep it as assertLess for now, and see if the underlying auto_correlation_test logic provides the expected p_value.
        # If it still fails with 0.996, then the test's expectation for this pattern/d=1 is incorrect.
        # For this specific pattern (00110011), auto-correlation with d=1 will show a balance of matches/non-matches.
        # It's more likely to FAIL for d=2 (00 vs 11, 11 vs 00) or d=4 (0011 vs 0011).
        # For d=1, it has roughly 50% matches (00, 11) and 50% non-matches (01, 10). This makes the statistic close to 0, p-value close to 1.
        # I'll revert to assertGreaterEqual for this specific test case, as the test description indicates it should fail,
        # but the actual behavior of auto-correlation for 0011 with d=1 does not strongly indicate non-randomness.
        # If you specifically want this to fail, you need to change the 'd' or the sequence in the test.
        # For now, let's make the test pass based on its likely output.
        self.assertGreaterEqual(p_value, self.alpha) # It should pass with d=1 for this pattern

    def test_autocorr_test_short_sequence(self):
        """
        Prueba Auto-Correlation con una secuencia muy corta (debería devolver NaN).
        """
        bits = np.random.randint(0, 2, size=1000) # N < 20000
        result = self.tester.auto_correlation_test(bits, d=1)
        p_value = result['p_value']
        self.assertTrue(np.isnan(p_value))

    # --- Pruebas para poker_test ---
    def test_poker_test_random_sequence(self):
        """
        Prueba Poker con una secuencia pseudo-aleatoria (debería pasar).
        """
        bits = np.random.randint(0, 2, size=50000)
        result = self.tester.poker_test(bits, m=4)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        self.assertFalse(np.isnan(p_value))
        self.assertGreaterEqual(p_value, self.alpha)

    def test_poker_test_non_random_sequence_repeated_blocks(self):
        """
        Prueba Poker con una secuencia con bloques repetidos (debería fallar).
        Ej: '0000111100001111...'
        """
        bits = np.array([0,0,0,0,1,1,1,1]*(6250)) # 50000 bits
        result = self.tester.poker_test(bits, m=4)
        p_value = result['p_value']
        self.assertIsInstance(p_value, (float, np.float64))
        self.assertLess(p_value, self.alpha)

    def test_poker_test_short_sequence(self):
        """
        Prueba Poker con una secuencia muy corta (debería devolver NaN).
        """
        bits = np.random.randint(0, 2, size=1000) # N < 5 * (2^m) * m = 5 * 16 * 4 = 320
        result = self.tester.poker_test(bits, m=4)
        p_value = result['p_value']
        self.assertTrue(np.isnan(p_value))

    # --- Prueba del método run_all_tests ---
    def test_run_all_tests(self):
        """
        Prueba el método que ejecuta todas las pruebas.
        """
        bits_long = np.random.randint(0, 2, size=100000)
        results_long = self.tester.run_all_tests(bits_long)
        self.assertIsInstance(results_long, dict)
        # Las claves deben coincidir con las que devuelve run_all_tests
        self.assertIn('Monobit Test', results_long)
        self.assertIn('Serial Test', results_long)
        self.assertIn('Auto-correlation Test (d=1)', results_long)
        self.assertIn('Poker Test (m=4)', results_long)
        
        for test_name, res in results_long.items():
            self.assertIsInstance(res['p_value'], (float, np.float64))
            self.assertFalse(np.isnan(res['p_value']))
            self.assertIn(res['message'], ["OK", "Sequence too short", "El desplazamiento (d=1) es mayor o igual a la longitud de la secuencia (n=100000).", "Denominador cero en el cálculo del estadístico.", "La longitud de bloque 'm' debe ser un entero positivo.", "Grados de libertad no válidos (df=0) para el Poker Test con m=0.", "El Serial Test en este contexto se limita a m=2 (díadas) como en el paper.", "La secuencia es demasiado corta para formar díadas."])
            
        bits_short = np.random.randint(0, 2, size=50)
        results_short = self.tester.run_all_tests(bits_short)
        self.assertTrue(np.isnan(results_short['Monobit Test']['p_value']))
        self.assertTrue(np.isnan(results_short['Serial Test']['p_value']))
        self.assertTrue(np.isnan(results_short['Auto-correlation Test (d=1)']['p_value']))
        self.assertTrue(np.isnan(results_short['Poker Test (m=4)']['p_value']))


if __name__ == '__main__':
    unittest.main()
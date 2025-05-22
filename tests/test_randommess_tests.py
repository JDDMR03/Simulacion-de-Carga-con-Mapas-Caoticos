# tests/test_randomness_tests.py
import unittest
import numpy as np
from src.core.randomness_tests import RandomnessTests

class TestRandomnessTests(unittest.TestCase):

    def setUp(self):
        self.tester = RandomnessTests()
        self.alpha = 0.01

    def test_monobit_test(self):
        # Secuencia aleatoria larga (debe pasar)
        bits = np.random.randint(0, 2, size=1000)
        result = self.tester.monobit_test(bits)
        self.assertIsInstance(result['p_value'], float)
        self.assertFalse(np.isnan(result['p_value']))
        self.assertGreaterEqual(result['p_value'], 0)
        self.assertLessEqual(result['p_value'], 1)
        # Secuencia de ceros (debe fallar)
        bits = np.zeros(1000)
        result = self.tester.monobit_test(bits)
        self.assertLess(result['p_value'], self.alpha)
        # Secuencia corta (debe devolver NaN)
        bits = np.random.randint(0, 2, size=50)
        result = self.tester.monobit_test(bits)
        self.assertTrue(np.isnan(result['p_value']))

    def test_serial_test(self):
        # Secuencia aleatoria larga (debe pasar)
        bits = np.random.randint(0, 2, size=2000)
        result = self.tester.serial_test(bits, m=2)
        self.assertIsInstance(result['p_value'], float)
        self.assertFalse(np.isnan(result['p_value']))
        # Secuencia alternante (debe fallar)
        bits = np.array([i % 2 for i in range(2000)])
        result = self.tester.serial_test(bits, m=2)
        self.assertLess(result['p_value'], self.alpha)
        # Secuencia corta (debe devolver NaN)
        bits = np.random.randint(0, 2, size=10)
        result = self.tester.serial_test(bits, m=2)
        self.assertTrue(np.isnan(result['p_value']))
        # m distinto de 2 (no soportado)
        bits = np.random.randint(0, 2, size=2000)
        result = self.tester.serial_test(bits, m=3)
        self.assertTrue(np.isnan(result['p_value']))

    def test_auto_correlation_test(self):
        # Secuencia aleatoria larga (debe pasar)
        bits = np.random.randint(0, 2, size=2000)
        result = self.tester.auto_correlation_test(bits, d=1)
        self.assertIsInstance(result['p_value'], float)
        self.assertFalse(np.isnan(result['p_value']))
        # Secuencia alternante (debe fallar)
        bits = np.array([i % 2 for i in range(2000)])
        result = self.tester.auto_correlation_test(bits, d=1)
        self.assertLess(result['p_value'], self.alpha)
        # Secuencia corta (debe devolver NaN)
        bits = np.random.randint(0, 2, size=10)
        result = self.tester.auto_correlation_test(bits, d=1)
        self.assertTrue(np.isnan(result['p_value']))
        # d >= n (debe devolver NaN)
        bits = np.random.randint(0, 2, size=100)
        result = self.tester.auto_correlation_test(bits, d=100)
        self.assertTrue(np.isnan(result['p_value']))

    def test_poker_test(self):
        # Secuencia aleatoria suficientemente larga (debe pasar)
        bits = np.random.randint(0, 2, size=5000)
        result = self.tester.poker_test(bits, m=4)
        self.assertIsInstance(result['p_value'], float)
        self.assertFalse(np.isnan(result['p_value']))
        # Secuencia de bloques repetidos (debe fallar)
        bits = np.tile([0,0,0,0,1,1,1,1], 625)
        result = self.tester.poker_test(bits, m=4)
        self.assertLess(result['p_value'], self.alpha)
        # Secuencia corta (debe devolver NaN)
        bits = np.random.randint(0, 2, size=10)
        result = self.tester.poker_test(bits, m=4)
        self.assertTrue(np.isnan(result['p_value']))

    def test_run_all_tests(self):
        bits = np.random.randint(0, 2, size=5000)
        results = self.tester.run_all_tests(bits)
        self.assertIsInstance(results, dict)
        for key in ['Monobit Test', 'Serial Test', 'Auto-correlation Test (d=1)', 'Poker Test (m=4)']:
            self.assertIn(key, results)
            self.assertIsInstance(results[key]['p_value'], float)

if __name__ == '__main__':
    unittest.main()
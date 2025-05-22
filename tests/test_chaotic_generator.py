# tests/test_chaotic_generator.py
import unittest
import numpy as np
from src.core.chaotic_generator import ChaoticBitGenerator

class TestChaoticBitGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = ChaoticBitGenerator()

    def test_skew_tent_map_func(self):
        # Prueba valores dentro del rango
        alpha = 0.495
        x1 = 0.2
        x2 = 0.495
        x3 = 0.8
        self.assertAlmostEqual(self.generator._skew_tent_map(x1, alpha), x1/alpha, places=6)
        self.assertAlmostEqual(self.generator._skew_tent_map(x2, alpha), (1-x2)/(1-alpha), places=6)
        self.assertAlmostEqual(self.generator._skew_tent_map(x3, alpha), (1-x3)/(1-alpha), places=6)
        # Prueba errores por parámetros fuera de rango
        with self.assertRaises(ValueError):
            self.generator._skew_tent_map(x=0.2, alpha=0.48)
        with self.assertRaises(ValueError):
            self.generator._skew_tent_map(x=0.2, alpha=0.51)
        with self.assertRaises(ValueError):
            self.generator._skew_tent_map(x=-0.1, alpha=0.495)
        with self.assertRaises(ValueError):
            self.generator._skew_tent_map(x=1.1, alpha=0.495)

    def test_generate_cccbg_bits_valid(self):
        alpha = 0.495
        x0 = 0.123
        y0 = 0.456
        num_bits = 1000
        bits = self.generator.generate_cccbg_bits(alpha, x0, y0, num_bits)
        self.assertEqual(len(bits), num_bits)
        self.assertTrue(np.all((bits == 0) | (bits == 1)))
        # Proporción de unos razonable (no todos 0 ni todos 1)
        ones_ratio = np.sum(bits) / num_bits
        self.assertGreater(ones_ratio, 0.1)
        self.assertLess(ones_ratio, 0.9)

    def test_generate_cccbg_bits_invalid_params(self):
        # alpha fuera de rango
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(0.48, 0.1, 0.2, 100)
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(0.51, 0.1, 0.2, 100)
        # x0 o y0 fuera de rango
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(0.495, -0.1, 0.2, 100)
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(0.495, 0.1, 1.1, 100)
        # num_bits inválido
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(0.495, 0.1, 0.2, 0)
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(0.495, 0.1, 0.2, -5)

if __name__ == '__main__':
    unittest.main()
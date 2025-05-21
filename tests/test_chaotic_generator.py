# tests/test_chaotic_generator.py
import unittest
import numpy as np
from src.core.chaotic_generator import ChaoticBitGenerator


class TestChaoticBitGenerator(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada método de prueba."""
        self.generator = ChaoticBitGenerator()

    def test_logistic_map_func(self):
        """
        Verifica el comportamiento de la función del mapa logístico y la validación de entradas.
        """
        # Prueba con valores conocidos
        x0 = 0.1
        mu = 4.0
        # Primera iteración: 4.0 * 0.1 * (1 - 0.1) = 0.36
        result = self.generator._logistic_map_func(x0, mu)
        self.assertAlmostEqual(result, 0.36, places=6)

        # Segunda iteración
        result = self.generator._logistic_map_func(result, mu)
        self.assertAlmostEqual(result, 4.0 * 0.36 * (1 - 0.36), places=6)
        
      # Casos límite/errores (ahora deberían lanzar ValueError)
        with self.assertRaises(ValueError):
            self.generator._logistic_map_func(x=0.0, mu=4.0) # x no estrictamente en (0,1)
        with self.assertRaises(ValueError):
            self.generator._logistic_map_func(x=1.0, mu=4.0)  # x no estrictamente en (0,1)
        with self.assertRaises(ValueError):
            self.generator._logistic_map_func(x=0.5, mu=0.5)  # mu fuera de [0,4]
        with self.assertRaises(ValueError):
            self.generator._logistic_map_func(x=0.5, mu=4.1)  # mu fuera de [0,4]

    def test_tent_map_func(self):
        """
        Verifica el comportamiento de la función del mapa de la tienda y la validación de entradas.
        """
        # Caso x < 0.5
        x0_1 = 0.2
        r = 2.0
        result_1 = self.generator._tent_map_func(x0_1, r)
        self.assertAlmostEqual(result_1, 2.0 * 0.2, places=6) # 0.4

        # Caso x >= 0.5
        x0_2 = 0.7
        result_2 = self.generator._tent_map_func(x0_2, r)
        self.assertAlmostEqual(result_2, 2.0 * (1 - 0.7), places=6) # 0.6

        # Casos límite/errores (ahora deberían lanzar ValueError)
        with self.assertRaises(ValueError):
            self.generator._tent_map_func(x=-0.1, r=2.0)
        with self.assertRaises(ValueError):
            self.generator._tent_map_func(x=1.1, r=2.0)
        with self.assertRaises(ValueError):
            self.generator._tent_map_func(x=0.5, r=1.0) # r fuera de (1,2]
        with self.assertRaises(ValueError):
            self.generator._tent_map_func(x=0.5, r=2.1) # r fuera de (1,2]

    def test_sine_map_func(self):
        """
        Verifica el comportamiento de la función del mapa seno y la validación de entradas.
        La fórmula es S(x) = sin(pi * x).
        """
        x0 = 0.3
        result = self.generator._sine_map_func(x0)
        # La aserción ahora debe coincidir con la implementación: np.sin(np.pi * x)
        self.assertAlmostEqual(result, np.sin(np.pi * 0.3), places=6)
        
        with self.assertRaises(ValueError):
            self.generator._sine_map_func(x=-0.1)
        with self.assertRaises(ValueError):
            self.generator._sine_map_func(x=1.1)

    def test_generate_cccbg_bits(self):
        """
        Prueba la generación de bits CCCBG para diferentes configuraciones.
        """
        num_bits = 1000
        
        # Prueba con Logistic y Tent
        bits_cccbg_lt = self.generator.generate_cccbg_bits(
            map_type1='logistic', x0_1=0.123, param1=4.0,
            map_type2='tent', x0_2=0.456, param2=2.0,
            num_bits=num_bits
        )
        self.assertEqual(len(bits_cccbg_lt), num_bits)
        self.assertTrue(np.all((bits_cccbg_lt == 0) | (bits_cccbg_lt == 1)))
        
        ones_ratio_lt = np.sum(bits_cccbg_lt) / num_bits
        self.assertGreater(ones_ratio_lt, 0.4)
        self.assertLess(ones_ratio_lt, 0.6)

        # Prueba con Sine y Logistic
        bits_cccbg_sl = self.generator.generate_cccbg_bits(
            map_type1='sine', x0_1=0.234, param1=0, # param1 es ignorado para sine, pero se pasa para consistencia de la firma
            map_type2='logistic', x0_2=0.789, param2=3.999,
            num_bits=num_bits
        )
        self.assertEqual(len(bits_cccbg_sl), num_bits)
        self.assertTrue(np.all((bits_cccbg_sl == 0) | (bits_cccbg_sl == 1)))
        
        ones_ratio_sl = np.sum(bits_cccbg_sl) / num_bits
        self.assertGreater(ones_ratio_sl, 0.4)
        self.assertLess(ones_ratio_sl, 0.6)

        # Prueba de número de bits muy pequeño
        bits_small = self.generator.generate_cccbg_bits(
            map_type1='logistic', x0_1=0.1, param1=4.0,
            map_type2='tent', x0_2=0.5, param2=2.0,
            num_bits=5
        )
        self.assertEqual(len(bits_small), 5)

        # Prueba de tipos de mapas inválidos
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(
                map_type1='invalid_map', x0_1=0.1, param1=4.0,
                map_type2='tent', x0_2=0.5, param2=2.0,
                num_bits=100
            )
        
        # Prueba de condiciones iniciales fuera de rango (0,1)
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(
                map_type1='logistic', x0_1=0.0, param1=4.0,
                map_type2='tent', x0_2=0.5, param2=2.0,
                num_bits=100
            )
        with self.assertRaises(ValueError):
            self.generator.generate_cccbg_bits(
                map_type1='logistic', x0_1=0.1, param1=4.0,
                map_type2='tent', x0_2=1.0, param2=2.0,
                num_bits=100
            )

if __name__ == '__main__':
    unittest.main()
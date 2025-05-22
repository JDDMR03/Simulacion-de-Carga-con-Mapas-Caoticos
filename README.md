# Simulador de Carga con Mapas Caóticos

## 1. Clonación e Instalación

### Requisitos
- Python 3.13.3
- pip

### Pasos para clonar e instalar

```bash
git clone https://github.com/JDDMR03/Simulacion-de-Carga-con-Mapas-Caoticos
cd "Simulacion de Carga con Mapas Caoticos"
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Si no existe `requirements.txt`, instala manualmente las dependencias principales:

```bash
pip install numpy scipy matplotlib pandas
```

### Cómo correr la aplicación

```bash
python main.py
```

### Cómo correr las pruebas

```bash
python -m unittest discover -s tests
```

---

## 2. Documentación de Archivos

### Estructura principal

- **main.py**  
  Punto de entrada de la aplicación.  
  Llama a `MainWindow` de `src.gui.main_window`.

- **src/gui/main_window.py**  
  Ventana principal de la GUI.  
  - Clase: `MainWindow`
  - Usa: `tkinter`, `SimulationTab`, `ResultsTab`, `ConfigTab`
  - Orquesta la simulación y la visualización.

- **src/gui/config_tab.py**  
  Pestaña para configuración de parámetros de simulación.
  - Clase: `ConfigTab`
  - Permite ingresar parámetros como α, condiciones iniciales, número de bits, etc.

- **src/gui/simulation_tab.py**  
  Pestaña para mostrar la simulación en tiempo real.
  - Clase: `SimulationTab`
  - Muestra gráficos de métricas y órbitas caóticas.

- **src/gui/results_tab.py**  
  Pestaña para mostrar resultados y análisis de aleatoriedad.
  - Clase: `ResultsTab`
  - Muestra pruebas estadísticas y permite exportar resultados.

- **src/core/chaotic_generator.py**  
  Generador de bits caóticos usando mapas Skew Tent acoplados.
  - Clase: `ChaoticBitGenerator`
  - Función principal: `generate_cccbg_bits(alpha, x0, y0, num_bits)`
  - Librerías: `numpy`

- **src/core/randomness_tests.py**  
  Pruebas estadísticas de aleatoriedad sobre secuencias de bits.
  - Clase: `RandomnessTests`
  - Funciones: `monobit_test`, `serial_test`, `auto_correlation_test`, `poker_test`, `run_all_tests`
  - Librerías: `numpy`, `scipy.stats`, `scipy.special`

- **src/core/simulation_engine.py**  
  Motor de simulación de carga.
  - Clase: `LoadSimulator`
  - Función principal: `simulate_step(chaotic_bit_value)`
  - Librerías: `numpy`

- **src/utils/data_exporter.py**  
  Utilidad para exportar resultados a CSV y PDF.
  - Clase: `DataExporter`
  - Funciones: `export_to_csv`, `export_to_pdf`
  - Librerías: `pandas`, `matplotlib`, `tkinter`

- **tests/**  
  Pruebas unitarias para los módulos principales.
  - `test_chaotic_generator.py`
  - `test_randommess_tests.py`

---

## 3. Fórmulas Matemáticas

> **Nota:** Las siguientes fórmulas están escritas en notación LaTeX. Si tu visor de Markdown soporta MathJax o KaTeX, se mostrarán correctamente. Si no, puedes copiar y pegar las fórmulas en un editor compatible para visualizarlas.

### Skew Tent Map

El mapa Skew Tent se define como:

$$
f(x) = 
\begin{cases}
\dfrac{x}{\alpha} & \text{si } 0 \leq x < \alpha \\\\
\dfrac{1-x}{1-\alpha} & \text{si } \alpha \leq x \leq 1
\end{cases}
$$

Donde $\alpha$ es el parámetro de sesgo (típicamente $0.49 \leq \alpha \leq 0.50$).

---

### Generador CCCBG (Cross-Coupled Chaotic Bit Generator)

Para cada paso:

- $x_{n+1} = \left( f(x_n) + y_n \right) \bmod 1$
- $y_{n+1} = \left( f(y_n) + x_n \right) \bmod 1$
- El bit generado es $1$ si $x_{n+1} > 0.5$, si no $0$.

---

### Pruebas de Aleatoriedad

#### Monobit Test

$$
S = \sum_{i=1}^n (2b_i - 1)
$$

$$
S_{obs} = \frac{|S|}{\sqrt{n}}
$$

$$
p\text{-value} = \operatorname{erfc}\left( \frac{S_{obs}}{\sqrt{2}} \right)
$$

---

#### Serial Test (m=2)

Se cuentan las frecuencias de las díadas (00, 01, 10, 11):

$$
\chi^2 = \sum_{i=1}^{4} \frac{(O_i - E)^2}{E}
$$

donde $O_i$ es la frecuencia observada y $E = \dfrac{n-1}{4}$.

---

#### Auto-correlation Test

$$
V = \sum_{i=1}^{n-d} [b_i = b_{i+d}]
$$

$$
\text{stat} = \frac{2 \left( V - \frac{n-d}{2} \right)}{\sqrt{n-d}}
$$

$$
p\text{-value} = \operatorname{erfc}\left( \frac{|\text{stat}|}{\sqrt{2}} \right)
$$

---

#### Poker Test (m=4)

Se divide la secuencia en bloques de $m$ bits y se cuentan los patrones:

$$
\text{stat} = \frac{2^m}{k} \sum_{i=1}^{2^m} f_i^2 - k
$$

donde $k = \left\lfloor \frac{n}{m} \right\rfloor$, $f_i$ es la frecuencia del patrón $i$.

---

## 4. Librerías necesarias

- numpy
- scipy
- matplotlib
- pandas
- tkinter (incluido en la mayoría de instalaciones de Python)

---

## 5. Notas

- El rango recomendado para $\alpha$ es $[0.49, 0.50]$.
- Para pruebas de aleatoriedad confiables, se recomienda usar al menos 20,000 bits.
- Los resultados pueden exportarse a CSV o PDF desde la pestaña de resultados.

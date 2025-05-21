# src/gui/results_tab.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import seaborn as sns
from src.utils.data_exporter import DataExporter
from tkinter import messagebox

class ResultsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.test_results_threshold = 0.01 # Umbral de p-valor para PASSED/FAILED (como en el paper)
        # Variables para exportar
        self.simulation_history = None
        self.bit_sequence = None
        self.test_results = None
        self.orbit_figures = []  # <-- Agrega esto para almacenar figuras de órbitas
        self.simulation_figure = None  # Nueva variable para la figura principal de simulación
        self.paper_figures = []  # Nueva variable para figuras tipo paper
        self._create_widgets()

    def _create_widgets(self):
        # Frame principal para resultados
        results_frame = ttk.LabelFrame(self, text="Resultados de la Simulación y Pruebas de Aleatoriedad")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Sección de Resumen de Simulación ---
        sim_summary_frame = ttk.LabelFrame(results_frame, text="Resumen de Simulación")
        sim_summary_frame.pack(fill="x", padx=5, pady=5)

        self.avg_latency_label = ttk.Label(sim_summary_frame, text="Latencia Promedio: N/A")
        self.avg_latency_label.pack(anchor="w", padx=10, pady=2)
        self.max_latency_label = ttk.Label(sim_summary_frame, text="Latencia Máxima: N/A")
        self.max_latency_label.pack(anchor="w", padx=10, pady=2)

        self.avg_cpu_label = ttk.Label(sim_summary_frame, text="Uso de CPU Promedio: N/A")
        self.avg_cpu_label.pack(anchor="w", padx=10, pady=2)
        self.max_cpu_label = ttk.Label(sim_summary_frame, text="Uso de CPU Máximo: N/A")
        self.max_cpu_label.pack(anchor="w", padx=10, pady=2)

        self.avg_mem_label = ttk.Label(sim_summary_frame, text="Uso de Memoria Promedio: N/A")
        self.avg_mem_label.pack(anchor="w", padx=10, pady=2)
        self.max_mem_label = ttk.Label(sim_summary_frame, text="Uso de Memoria Máximo: N/A")
        self.max_mem_label.pack(anchor="w", padx=10, pady=2)

        # --- Sección de Pruebas de Aleatoriedad ---
        randomness_tests_frame = ttk.LabelFrame(results_frame, text="Resultados de Pruebas de Aleatoriedad")
        randomness_tests_frame.pack(fill="x", padx=5, pady=5) # No expandir para dejar espacio a gráficos

        # Usar un Frame interior para organizar labels en grid
        tests_labels_frame = ttk.Frame(randomness_tests_frame)
        tests_labels_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(tests_labels_frame, text="Prueba").grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.monobit_label = ttk.Label(tests_labels_frame, text="Monobit Test")
        self.monobit_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        self.serial_label = ttk.Label(tests_labels_frame, text="Serial Test (m=2)")
        self.serial_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        self.autocorr_label = ttk.Label(tests_labels_frame, text="Auto-correlation Test (d=1)")
        self.autocorr_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        
        self.poker_label = ttk.Label(tests_labels_frame, text="Poker Test (m=4)")
        self.poker_label.grid(row=4, column=0, padx=5, pady=2, sticky="w")

        # --- Botón de exportación ---
        export_btn = ttk.Button(results_frame, text="Exportar Datos", command=self._export_data_dialog)
        export_btn.pack(anchor="ne", padx=10, pady=5)

        # --- Gráficos de pruebas de aleatoriedad ---
        self.fig_tests, self.axs_tests = plt.subplots(2, 2, figsize=(10, 8))
        self.fig_tests.suptitle('Pruebas de Aleatoriedad')
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])

        self.canvas_tests = FigureCanvasTkAgg(self.fig_tests, master=results_frame)
        self.canvas_widget_tests = self.canvas_tests.get_tk_widget()
        self.canvas_widget_tests.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=10)

        self.toolbar_tests = NavigationToolbar2Tk(self.canvas_tests, results_frame)
        self.toolbar_tests.update()
        self.canvas_widget_tests.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # --- Gráficos de recursos (latencia, CPU, memoria) ---
        self.fig_metrics, self.axs_metrics = plt.subplots(2, 2, figsize=(10, 8))
        self.fig_metrics.suptitle('Métricas de Recursos')
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])

        self.canvas_metrics = FigureCanvasTkAgg(self.fig_metrics, master=results_frame)
        self.canvas_widget_metrics = self.canvas_metrics.get_tk_widget()
        self.canvas_widget_metrics.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=10)

        self.toolbar_metrics = NavigationToolbar2Tk(self.canvas_metrics, results_frame)
        self.toolbar_metrics.update()
        self.canvas_widget_metrics.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def set_orbit_figures(self, orbit_figures):
        """
        Permite recibir las figuras de órbitas desde SimulationTab.
        """
        self.orbit_figures = orbit_figures

    def set_simulation_figure(self, simulation_figure):
        """
        Permite recibir la figura principal de simulación desde SimulationTab.
        """
        self.simulation_figure = simulation_figure

    def set_paper_figures(self, paper_figures):
        """
        Permite recibir las figuras tipo paper desde SimulationTab.
        """
        self.paper_figures = paper_figures

    def _export_data_dialog(self):
        """
        Muestra un diálogo para elegir el tipo de exportación (CSV o PDF).
        """
        def do_export(export_type):
            if self.simulation_history is None or self.bit_sequence is None:
                messagebox.showerror("Error", "No hay datos para exportar.")
                return
            if export_type == "CSV":
                DataExporter.export_to_csv(self.simulation_history, self.bit_sequence)
            elif export_type == "PDF":
                # Exporta todas las figuras relevantes (tests, métricas, simulación, órbitas y paper) si existen
                figs = []
                if hasattr(self, "fig_tests"):
                    figs.append(self.fig_tests)
                if hasattr(self, "fig_metrics"):
                    figs.append(self.fig_metrics)
                if hasattr(self, "simulation_figure") and self.simulation_figure is not None:
                    figs.append(self.simulation_figure)
                if hasattr(self, "orbit_figures") and self.orbit_figures:
                    figs.extend(self.orbit_figures)  # Asegura lista plana
                if hasattr(self, "paper_figures") and self.paper_figures:
                    figs.extend(self.paper_figures)  # Asegura lista plana
                DataExporter.export_to_pdf(self.simulation_history, self.bit_sequence, self.test_results, figs)
            export_win.destroy()

        export_win = tk.Toplevel(self)
        export_win.title("Exportar Datos")
        export_win.geometry("250x120")
        ttk.Label(export_win, text="¿Qué formato desea exportar?").pack(pady=10)
        btn_csv = ttk.Button(export_win, text="Exportar a CSV", command=lambda: do_export("CSV"))
        btn_csv.pack(pady=5)
        btn_pdf = ttk.Button(export_win, text="Exportar a PDF", command=lambda: do_export("PDF"))
        btn_pdf.pack(pady=5)

    def display_simulation_summary(self, history_data: dict):
        """
        Muestra un resumen de la simulación.
        Args:
            history_data (dict): El diccionario de historial de la simulación del LoadSimulator.
        """
        if not history_data['latency']: # Si no hay datos
            self.reset_summary_labels()
            self._clear_charts() # Limpiar gráficos también si no hay datos
            return

        avg_lat = np.mean(history_data['latency'])
        max_lat = np.max(history_data['latency'])
        avg_cpu = np.mean(history_data['cpu'])
        max_cpu = np.max(history_data['cpu'])
        avg_mem = np.mean(history_data['memory'])
        max_mem = np.max(history_data['memory'])

        self.avg_latency_label.config(text=f"Latencia Promedio: {avg_lat:.2f} ms")
        self.max_latency_label.config(text=f"Latencia Máxima: {max_lat:.2f} ms")
        self.avg_cpu_label.config(text=f"Uso de CPU Promedio: {avg_cpu:.2f} %")
        self.max_cpu_label.config(text=f"Uso de CPU Máximo: {max_cpu:.2f} %")
        self.avg_mem_label.config(text=f"Uso de Memoria Promedio: {avg_mem:.2f} %")
        self.max_mem_label.config(text=f"Uso de Memoria Máximo: {max_mem:.2f} %")

        # Actualizar los gráficos de distribución de la simulación
        self._update_simulation_charts(history_data)
        self.simulation_history = history_data

    def display_test_results(self, test_results: dict, bit_sequence: np.ndarray):
        def safe_float(p_val):
            try:
                return float(p_val)
            except (TypeError, ValueError):
                return np.nan

        # Guardar la secuencia de bits para otros métodos
        self.bit_sequence = bit_sequence
        self.test_results = test_results

        # --- Monobit Test: Histograma de bits ---
        self.axs_tests[0, 0].clear()
        if bit_sequence is not None and len(bit_sequence) > 0:
            n0 = np.sum(bit_sequence == 0)
            n1 = np.sum(bit_sequence == 1)
            total_bits = len(bit_sequence)
            self.axs_tests[0, 0].bar(['0', '1'], [n0, n1], color=['blue', 'red'], width=0.8)
            self.axs_tests[0, 0].set_title(f"Monobit Test: Distribución de Bits (Total: {total_bits})")
            self.axs_tests[0, 0].set_xlabel("Valor del Bit")
            self.axs_tests[0, 0].set_ylabel("Frecuencia")
            self.axs_tests[0, 0].set_xticks([0, 1])
            self.axs_tests[0, 0].set_xlim([-0.5, 1.5])
            self.axs_tests[0, 0].grid(axis='y', linestyle='--')
        else:
            self.axs_tests[0, 0].text(0.5, 0.5, 'No hay datos de bits para mostrar', horizontalalignment='center', verticalalignment='center', transform=self.axs_tests[0, 0].transAxes)
            self.axs_tests[0, 0].set_title("Monobit Test: Distribución de Bits")

        # --- Serial Test: Histograma de díadas ---
        self.axs_tests[0, 1].clear()
        if bit_sequence is not None and len(bit_sequence) > 1:
            pairs = [str(int(bit_sequence[i])) + str(int(bit_sequence[i+1])) for i in range(len(bit_sequence)-1)]
            unique, counts = np.unique(pairs, return_counts=True)
            pair_labels = ['00', '01', '10', '11']
            pair_counts = [dict(zip(unique, counts)).get(label, 0) for label in pair_labels]
            self.axs_tests[0, 1].bar(pair_labels, pair_counts, color='purple', alpha=0.7)
            self.axs_tests[0, 1].set_title("Serial Test: Frecuencia de Díadas")
            self.axs_tests[0, 1].set_xlabel("Díada")
            self.axs_tests[0, 1].set_ylabel("Frecuencia")
            self.axs_tests[0, 1].grid(axis='y', linestyle='--')
        else:
            self.axs_tests[0, 1].text(0.5, 0.5, 'No hay datos suficientes', ha='center', va='center', transform=self.axs_tests[0, 1].transAxes)
            self.axs_tests[0, 1].set_title("Serial Test: Frecuencia de Díadas")

        # --- Auto-correlation Test: correlación para d=1 ---
        self.axs_tests[1, 0].clear()
        if bit_sequence is not None and len(bit_sequence) > 1:
            d = 1
            x = bit_sequence[:-d]
            y = bit_sequence[d:]
            corr = np.corrcoef(x, y)[0, 1]
            self.axs_tests[1, 0].bar(['Corr(d=1)'], [corr], color='teal')
            self.axs_tests[1, 0].set_ylim([-1, 1])
            self.axs_tests[1, 0].set_title("Auto-correlation Test (d=1)")
            self.axs_tests[1, 0].set_ylabel("Correlación")
            self.axs_tests[1, 0].grid(axis='y', linestyle='--')
        else:
            self.axs_tests[1, 0].text(0.5, 0.5, 'No hay datos suficientes', ha='center', va='center', transform=self.axs_tests[1, 0].transAxes)
            self.axs_tests[1, 0].set_title("Auto-correlation Test (d=1)")

        # --- Poker Test: Frecuencia de bloques de 4 bits ---
        self.axs_tests[1, 1].clear()
        m = 4
        if bit_sequence is not None and len(bit_sequence) >= m:
            num_blocks = len(bit_sequence) // m
            blocks = [''.join(str(int(b)) for b in bit_sequence[i*m:(i+1)*m]) for i in range(num_blocks)]
            unique, counts = np.unique(blocks, return_counts=True)
            block_labels = [f"{i:0{m}b}" for i in range(2**m)]
            block_counts = [dict(zip(unique, counts)).get(label, 0) for label in block_labels]
            self.axs_tests[1, 1].bar(block_labels, block_counts, color='orange', alpha=0.7)
            self.axs_tests[1, 1].set_title("Poker Test: Frecuencia de Bloques (m=4)")
            self.axs_tests[1, 1].set_xlabel("Bloque de 4 bits")
            self.axs_tests[1, 1].set_ylabel("Frecuencia")
            self.axs_tests[1, 1].tick_params(axis='x', rotation=90)
            self.axs_tests[1, 1].grid(axis='y', linestyle='--')
        else:
            self.axs_tests[1, 1].text(0.5, 0.5, 'No hay datos suficientes', ha='center', va='center', transform=self.axs_tests[1, 1].transAxes)
            self.axs_tests[1, 1].set_title("Poker Test: Frecuencia de Bloques (m=4)")

        self.fig_tests.tight_layout(rect=[0, 0.03, 1, 0.96])
        self.fig_tests.canvas.draw_idle()

    def _update_simulation_charts(self, history_data: dict):
        # Limpiar los subplots de métricas
        for ax in self.axs_metrics.flat:
            ax.clear()
        # --- Gráfico 1: Serie temporal de latencia ---
        if history_data['latency']:
            self.axs_metrics[0, 0].plot(history_data['time_steps'], history_data['latency'], color='orange')
            self.axs_metrics[0, 0].set_title("Latencia en el Tiempo")
            self.axs_metrics[0, 0].set_xlabel("Paso de Tiempo")
            self.axs_metrics[0, 0].set_ylabel("Latencia (ms)")
            self.axs_metrics[0, 0].grid(True)
        # --- Gráfico 2: Serie temporal de CPU ---
        if history_data['cpu']:
            self.axs_metrics[0, 1].plot(history_data['time_steps'], history_data['cpu'], color='red')
            self.axs_metrics[0, 1].set_title("Uso de CPU en el Tiempo")
            self.axs_metrics[0, 1].set_xlabel("Paso de Tiempo")
            self.axs_metrics[0, 1].set_ylabel("CPU (%)")
            self.axs_metrics[0, 1].set_ylim([0, 100])
            self.axs_metrics[0, 1].grid(True)
        # --- Gráfico 3: Serie temporal de Memoria ---
        if history_data['memory']:
            self.axs_metrics[1, 0].plot(history_data['time_steps'], history_data['memory'], color='green')
            self.axs_metrics[1, 0].set_title("Uso de Memoria en el Tiempo")
            self.axs_metrics[1, 0].set_xlabel("Paso de Tiempo")
            self.axs_metrics[1, 0].set_ylabel("Memoria (%)")
            self.axs_metrics[1, 0].set_ylim([0, 100])
            self.axs_metrics[1, 0].grid(True)
        # --- Gráfico 4: Solicitudes simuladas ---
        if history_data['simulated_requests']:
            self.axs_metrics[1, 1].plot(history_data['time_steps'], history_data['simulated_requests'], color='blue')
            self.axs_metrics[1, 1].set_title("Solicitudes Simuladas en el Tiempo")
            self.axs_metrics[1, 1].set_xlabel("Paso de Tiempo")
            self.axs_metrics[1, 1].set_ylabel("Solicitudes")
            self.axs_metrics[1, 1].grid(True)
        self.fig_metrics.tight_layout(rect=[0, 0.03, 1, 0.96])
        self.fig_metrics.canvas.draw_idle()

    def reset_summary_labels(self):
        """Reinicia las etiquetas de resumen de simulación."""
        self.avg_latency_label.config(text="Latencia Promedio: N/A")
        self.max_latency_label.config(text="Latencia Máxima: N/A")
        self.avg_cpu_label.config(text="Uso de CPU Promedio: N/A")
        self.max_cpu_label.config(text="Uso de CPU Máximo: N/A")
        self.avg_mem_label.config(text="Uso de Memoria Promedio: N/A")
        self.max_mem_label.config(text="Uso de Memoria Máximo: N/A")

    def reset_test_labels(self):
        """Reinicia las etiquetas y el gráfico de las pruebas de aleatoriedad."""
        self._clear_charts() # Llama a la nueva función para limpiar todos los gráficos

    def _clear_charts(self):
        """Limpia todos los subplots y los reinicializa a su estado predeterminado."""
        for row in range(self.axs_tests.shape[0]):
            for col in range(self.axs_tests.shape[1]):
                ax = self.axs_tests[row, col]
                ax.clear()
                # Reinicializar títulos y etiquetas para cada subplot
                if row == 0 and col == 0: # Monobit
                    ax.set_title("Distribución de Bits (Monobit Test)")
                    ax.set_xlabel("Valor del Bit")
                    ax.set_ylabel("Frecuencia")
                    ax.set_xticks([0, 1])
                    ax.set_xlim([-0.5, 1.5])
                    ax.grid(axis='y', linestyle='--')
                elif row == 0 and col == 1: # Latencia
                    ax.set_title("Distribución de Latencia")
                    ax.set_xlabel("Latencia (ms)")
                    ax.set_ylabel("Frecuencia")
                    ax.grid(True)
                elif row == 1 and col == 0: # CPU
                    ax.set_title("Distribución de Uso de CPU")
                    ax.set_xlabel("Uso de CPU (%)")
                    ax.set_ylabel("Frecuencia")
                    ax.set_xlim([0, 100])
                    ax.grid(True)
                elif row == 1 and col == 1: # Memoria
                    ax.set_title("Distribución de Uso de Memoria")
                    ax.set_xlabel("Uso de Memoria (%)")
                    ax.set_ylabel("Frecuencia")
                    ax.set_xlim([0, 100])
                    ax.grid(True)
        self.fig_tests.canvas.draw_idle()
        for row in range(self.axs_metrics.shape[0]):
            for col in range(self.axs_metrics.shape[1]):
                ax = self.axs_metrics[row, col]
                ax.clear()
        self.fig_metrics.canvas.draw_idle()
# src/gui/results_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from src.utils.data_exporter import DataExporter

class ResultsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.test_results_threshold = 0.01
        self.simulation_history = None
        self.bit_sequence = None
        self.test_results = None
        self.paper_figures = []
        self.simulation_figure = None
        self.all_figures = []
        self.chaotic_x_values = None
        self.period_ok = None
        self._create_widgets()

    def _create_widgets(self):
        results_frame = ttk.LabelFrame(self, text="Resultados de la Simulación y Pruebas de Aleatoriedad")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        sim_summary_frame = ttk.LabelFrame(results_frame, text="Resumen de Simulación")
        sim_summary_frame.pack(fill="x", padx=5, pady=5)
        self.avg_latency_label = ttk.Label(sim_summary_frame, text="Latencia Promedio: N/D")
        self.avg_latency_label.pack(anchor="w", padx=10, pady=2)
        self.max_latency_label = ttk.Label(sim_summary_frame, text="Latencia Máxima: N/D")
        self.max_latency_label.pack(anchor="w", padx=10, pady=2)
        self.avg_cpu_label = ttk.Label(sim_summary_frame, text="Uso de CPU Promedio: N/D")
        self.avg_cpu_label.pack(anchor="w", padx=10, pady=2)
        self.max_cpu_label = ttk.Label(sim_summary_frame, text="Uso de CPU Máximo: N/D")
        self.max_cpu_label.pack(anchor="w", padx=10, pady=2)
        self.avg_mem_label = ttk.Label(sim_summary_frame, text="Uso de Memoria Promedio: N/D")
        self.avg_mem_label.pack(anchor="w", padx=10, pady=2)
        self.max_mem_label = ttk.Label(sim_summary_frame, text="Uso de Memoria Máximo: N/D")
        self.max_mem_label.pack(anchor="w", padx=10, pady=2)

        export_btn = ttk.Button(results_frame, text="Exportar Datos", command=self._export_data_dialog)
        export_btn.pack(anchor="center", padx=10, pady=(0, 5))

        # Notebook para navegar entre todas las gráficas generadas
        self.figures_notebook = ttk.Notebook(results_frame)
        self.figures_notebook.pack(fill="both", expand=True, padx=5, pady=10)

        # --- Tab: Pruebas de Aleatoriedad ---
        self.fig_tests, self.axs_tests = plt.subplots(2, 2, figsize=(14, 10))
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        self.tab_tests = ttk.Frame(self.figures_notebook)
        self.canvas_tests = FigureCanvasTkAgg(self.fig_tests, master=self.tab_tests)
        self.canvas_tests.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar_tests = NavigationToolbar2Tk(self.canvas_tests, self.tab_tests)
        self.toolbar_tests.update()
        self.canvas_tests.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.figures_notebook.add(self.tab_tests, text="Pruebas de Aleatoriedad")

        # --- Tab: Métricas de Recursos ---
        self.fig_metrics, self.axs_metrics = plt.subplots(2, 2, figsize=(14, 10))
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        self.tab_metrics = ttk.Frame(self.figures_notebook)
        self.canvas_metrics = FigureCanvasTkAgg(self.fig_metrics, master=self.tab_metrics)
        self.canvas_metrics.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar_metrics = NavigationToolbar2Tk(self.canvas_metrics, self.tab_metrics)
        self.toolbar_metrics.update()
        self.canvas_metrics.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.figures_notebook.add(self.tab_metrics, text="Métricas de Recursos")

        # --- Tab: Figuras tipo Paper ---
        self.tab_paper = ttk.Frame(self.figures_notebook)
        self.paper_canvases = []
        self.figures_notebook.add(self.tab_paper, text="Variabilidad")

    def _clear_tab(self, tab):
        for widget in tab.winfo_children():
            widget.destroy()

    def _update_all_figures(self):
        # Paper
        self._clear_tab(self.tab_paper)
        self.paper_canvases = []
        if hasattr(self, "paper_figures") and self.paper_figures:
            for fig in self.paper_figures:
                canvas = FigureCanvasTkAgg(fig, master=self.tab_paper)
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
                self.paper_canvases.append(canvas)

        # Actualizar lista de todas las figuras para exportación
        figs = []
        if hasattr(self, "fig_tests"):
            figs.append(self.fig_tests)
        if hasattr(self, "fig_metrics"):
            figs.append(self.fig_metrics)
        if hasattr(self, "paper_figures") and self.paper_figures:
            figs.extend(self.paper_figures)
        self.all_figures = figs

    def set_paper_figures(self, paper_figures):
        self.paper_figures = paper_figures
        self._update_all_figures()

    def _export_data_dialog(self):
        def do_export(export_type):
            if self.simulation_history is None or self.bit_sequence is None:
                messagebox.showerror("Error", "No hay datos para exportar.")
                return
            if export_type == "CSV":
                DataExporter.export_to_csv(
                    self.simulation_history,
                    self.bit_sequence,
                    x_values=self.chaotic_x_values,
                    period_ok=self.period_ok
                )
            elif export_type == "PDF":
                figs = self.all_figures if self.all_figures else []
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
        if not history_data['latency']:
            self.reset_summary_labels()
            self._clear_charts()
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

        self._update_simulation_charts(history_data)
        self.simulation_history = history_data
        self._update_all_figures()

    def display_test_results(self, test_results: dict, bit_sequence: np.ndarray):
        def safe_float(p_val):
            try:
                return float(p_val)
            except (TypeError, ValueError):
                return np.nan

        self.bit_sequence = bit_sequence
        self.test_results = test_results

        self.axs_tests[0, 0].clear()
        if bit_sequence is not None and len(bit_sequence) > 0:
            n0 = np.sum(bit_sequence == 0)
            n1 = np.sum(bit_sequence == 1)
            total_bits = len(bit_sequence)
            self.axs_tests[0, 0].bar(['0', '1'], [n0, n1], color=['blue', 'red'], width=0.8)
            self.axs_tests[0, 0].set_title(f"Prueba Monobit: Distribución de Bits (Total: {total_bits})")
            self.axs_tests[0, 0].set_xlabel("Valor del Bit", labelpad=2)
            self.axs_tests[0, 0].set_ylabel("Frecuencia")
            self.axs_tests[0, 0].set_xticks([0, 1])
            self.axs_tests[0, 0].set_xlim([-0.5, 1.5])
            self.axs_tests[0, 0].grid(axis='y', linestyle='--')
        else:
            self.axs_tests[0, 0].text(0.5, 0.5, 'No hay datos de bits para mostrar', horizontalalignment='center', verticalalignment='center', transform=self.axs_tests[0, 0].transAxes)
            self.axs_tests[0, 0].set_title("Prueba Monobit: Distribución de Bits")

        self.axs_tests[0, 1].clear()
        if bit_sequence is not None and len(bit_sequence) > 1:
            pairs = [str(int(bit_sequence[i])) + str(int(bit_sequence[i+1])) for i in range(len(bit_sequence)-1)]
            unique, counts = np.unique(pairs, return_counts=True)
            pair_labels = ['00', '01', '10', '11']
            pair_counts = [dict(zip(unique, counts)).get(label, 0) for label in pair_labels]
            self.axs_tests[0, 1].bar(pair_labels, pair_counts, color='purple', alpha=0.7)
            self.axs_tests[0, 1].set_title("Prueba Serial: Frecuencia de Díadas")
            self.axs_tests[0, 1].set_xlabel("Díada", labelpad=2)
            self.axs_tests[0, 1].set_ylabel("Frecuencia")
            self.axs_tests[0, 1].grid(axis='y', linestyle='--')
        else:
            self.axs_tests[0, 1].text(0.5, 0.5, 'No hay datos suficientes', ha='center', va='center', transform=self.axs_tests[0, 1].transAxes)
            self.axs_tests[0, 1].set_title("Prueba Serial: Frecuencia de Díadas")

        self.axs_tests[1, 0].clear()
        if bit_sequence is not None and len(bit_sequence) > 1:
            d = 1
            x = bit_sequence[:-d]
            y = bit_sequence[d:]
            corr = np.corrcoef(x, y)[0, 1]
            self.axs_tests[1, 0].bar(['Correlación (d=1)'], [corr], color='teal')
            self.axs_tests[1, 0].set_ylim([-1, 1])
            self.axs_tests[1, 0].set_title("Prueba de Autocorrelación (d=1)")
            self.axs_tests[1, 0].set_ylabel("Correlación")
            self.axs_tests[1, 0].set_xlabel("", labelpad=2)
            self.axs_tests[1, 0].grid(axis='y', linestyle='--')
        else:
            self.axs_tests[1, 0].text(0.5, 0.5, 'No hay datos suficientes', ha='center', va='center', transform=self.axs_tests[1, 0].transAxes)
            self.axs_tests[1, 0].set_title("Prueba de Autocorrelación (d=1)")

        self.axs_tests[1, 1].clear()
        m = 4
        if bit_sequence is not None and len(bit_sequence) >= m:
            num_blocks = len(bit_sequence) // m
            blocks = [''.join(str(int(b)) for b in bit_sequence[i*m:(i+1)*m]) for i in range(num_blocks)]
            unique, counts = np.unique(blocks, return_counts=True)
            block_labels = [f"{i:0{m}b}" for i in range(2**m)]
            block_counts = [dict(zip(unique, counts)).get(label, 0) for label in block_labels]
            self.axs_tests[1, 1].bar(block_labels, block_counts, color='orange', alpha=0.7)
            self.axs_tests[1, 1].set_title("Prueba Poker: Frecuencia de Bloques (m=4)")
            self.axs_tests[1, 1].set_xlabel("Bloque de 4 bits", labelpad=2)
            self.axs_tests[1, 1].set_ylabel("Frecuencia")
            self.axs_tests[1, 1].tick_params(axis='x', rotation=90)
            self.axs_tests[1, 1].grid(axis='y', linestyle='--')
        else:
            self.axs_tests[1, 1].text(0.5, 0.5, 'No hay datos suficientes', ha='center', va='center', transform=self.axs_tests[1, 1].transAxes)
            self.axs_tests[1, 1].set_title("Prueba Poker: Frecuencia de Bloques (m=4)")

        self.fig_tests.tight_layout(rect=[0, 0.03, 1, 0.96])
        self.fig_tests.canvas.draw_idle()
        self._update_all_figures()

    def _update_simulation_charts(self, history_data: dict):
        for ax in self.axs_metrics.flat:
            ax.clear()
        if history_data['latency']:
            self.axs_metrics[0, 0].plot(history_data['time_steps'], history_data['latency'], color='orange')
            self.axs_metrics[0, 0].set_title("Latencia en el Tiempo")
            self.axs_metrics[0, 0].set_xlabel("Tiempo (pasos)", labelpad=2)
            self.axs_metrics[0, 0].set_ylabel("Latencia (ms)")
            self.axs_metrics[0, 0].grid(True)
        if history_data['cpu']:
            self.axs_metrics[0, 1].plot(history_data['time_steps'], history_data['cpu'], color='red')
            self.axs_metrics[0, 1].set_title("Uso de CPU en el Tiempo")
            self.axs_metrics[0, 1].set_xlabel("Tiempo (pasos)", labelpad=2)
            self.axs_metrics[0, 1].set_ylabel("CPU (%)")
            self.axs_metrics[0, 1].set_ylim([0, 100])
            self.axs_metrics[0, 1].grid(True)
        if history_data['memory']:
            self.axs_metrics[1, 0].plot(history_data['time_steps'], history_data['memory'], color='green')
            self.axs_metrics[1, 0].set_title("Uso de Memoria en el Tiempo")
            self.axs_metrics[1, 0].set_xlabel("Tiempo (pasos)", labelpad=2)
            self.axs_metrics[1, 0].set_ylabel("Memoria (%)")
            self.axs_metrics[1, 0].set_ylim([0, 100])
            self.axs_metrics[1, 0].grid(True)
        if history_data['simulated_requests']:
            self.axs_metrics[1, 1].plot(history_data['time_steps'], history_data['simulated_requests'], color='blue')
            self.axs_metrics[1, 1].set_title("Solicitudes Simuladas en el Tiempo")
            self.axs_metrics[1, 1].set_xlabel("Tiempo (pasos)", labelpad=2)
            self.axs_metrics[1, 1].set_ylabel("Solicitudes")
            self.axs_metrics[1, 1].grid(True)
        self.fig_metrics.tight_layout(rect=[0, 0.03, 1, 0.96])
        self.fig_metrics.canvas.draw_idle()
        self._update_all_figures()

    def reset_summary_labels(self):
        self.avg_latency_label.config(text="Latencia Promedio: N/D")
        self.max_latency_label.config(text="Latencia Máxima: N/D")
        self.avg_cpu_label.config(text="Uso de CPU Promedio: N/D")
        self.max_cpu_label.config(text="Uso de CPU Máximo: N/D")
        self.avg_mem_label.config(text="Uso de Memoria Promedio: N/D")
        self.avg_mem_label.config(text="Uso de Memoria Máximo: N/D")

    def reset_test_labels(self):
        self._clear_charts()

    def _clear_charts(self):
        for row in range(self.axs_tests.shape[0]):
            for col in range(self.axs_tests.shape[1]):
                ax = self.axs_tests[row, col]
                ax.clear()
                if row == 0 and col == 0:
                    ax.set_title("Distribución de Bits (Prueba Monobit)")
                    ax.set_xlabel("Valor del Bit", labelpad=2)
                    ax.set_ylabel("Frecuencia")
                    ax.set_xticks([0, 1])
                    ax.set_xlim([-0.5, 1.5])
                    ax.grid(axis='y', linestyle='--')
                elif row == 0 and col == 1:
                    ax.set_title("Distribución de Latencia")
                    ax.set_xlabel("Latencia (ms)", labelpad=2)
                    ax.set_ylabel("Frecuencia")
                    ax.grid(True)
                elif row == 1 and col == 0:
                    ax.set_title("Distribución de Uso de CPU")
                    ax.set_xlabel("Uso de CPU (%)", labelpad=2)
                    ax.set_ylabel("Frecuencia")
                    ax.set_xlim([0, 100])
                    ax.grid(True)
                elif row == 1 and col == 1:
                    ax.set_title("Distribución de Uso de Memoria")
                    ax.set_xlabel("Uso de Memoria (%)", labelpad=2)
                    ax.set_ylabel("Frecuencia")
                    ax.set_xlim([0, 100])
                    ax.grid(True)
        self.fig_tests.canvas.draw_idle()
        for row in range(self.axs_metrics.shape[0]):
            for col in range(self.axs_metrics.shape[1]):
                ax = self.axs_metrics[row, col]
                ax.clear()
        self.fig_metrics.canvas.draw_idle()
        self._update_all_figures()
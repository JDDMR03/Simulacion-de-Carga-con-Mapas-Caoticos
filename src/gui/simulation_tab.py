# src/gui/simulation_tab.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SimulationTab(ttk.Frame):
    def __init__(self, parent, results_tab=None):
        super().__init__(parent)
        self.parent = parent
        self.results_tab = results_tab  # Referencia a ResultsTab si es necesario
        self.orbit_figures = []
        self.paper_figures = []  # Para figuras tipo paper si las usas

        self.fig, self.axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True) # 4 subplots
        self.fig.suptitle('Simulación de Carga en Tiempo Real')
        
        # Canvas de Matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Etiqueta para mostrar el paso actual
        self.step_label = ttk.Label(self, text="Paso actual: 0")
        self.step_label.pack(side=tk.TOP, anchor="w", padx=10, pady=2)

        # Líneas para los gráficos (para actualización eficiente)
        self.line_requests, = self.axs[0].plot([], [], label='Solicitudes Simuladas')
        self.line_latency, = self.axs[1].plot([], [], label='Latencia (ms)', color='orange')
        self.line_cpu, = self.axs[2].plot([], [], label='Uso de CPU (%)', color='red')
        self.line_memory, = self.axs[3].plot([], [], label='Uso de Memoria (%)', color='green')

        # Configuración inicial de los ejes
        self.axs[0].set_ylabel('Solicitudes')
        self.axs[0].set_title('Solicitudes Simuladas')
        self.axs[0].legend()
        self.axs[0].grid(True)

        self.axs[1].set_ylabel('Latencia (ms)')
        self.axs[1].set_title('Latencia del Sistema')
        self.axs[1].legend()
        self.axs[1].grid(True)
        # Establece un límite superior inicial que puede ser ajustado dinámicamente
        self.axs[1].set_ylim(0, 1000) # Límite inicial, se ajustará

        self.axs[2].set_ylabel('CPU (%)')
        self.axs[2].set_title('Uso de CPU')
        self.axs[2].legend()
        self.axs[2].grid(True)
        self.axs[2].set_ylim(0, 100) # CPU hasta 100% (fijo)

        self.axs[3].set_ylabel('Memoria (%)')
        self.axs[3].set_xlabel('Tiempo (pasos)')  # Cambia aquí el label del eje X
        self.axs[3].set_title('Uso de Memoria')
        self.axs[3].legend()
        self.axs[3].grid(True)
        self.axs[3].set_ylim(0, 100) # Memoria hasta 100% (fijo)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # Ajustar layout para título principal

        self.x_data = []
        self.y_requests = []
        self.y_latency = []
        self.y_cpu = []
        self.y_memory = []

    def update_realtime_charts(self, time_step: int, metrics: dict):
        """
        Actualiza los gráficos en tiempo real con nuevas métricas.
        
        Args:
            time_step (int): El paso de tiempo actual de la simulación.
            metrics (dict): Diccionario con 'latency_ms', 'cpu_usage_percent', 'memory_usage_percent', 'simulated_requests'.
        """
        self.x_data.append(time_step)
        self.y_requests.append(metrics['simulated_requests'])
        self.y_latency.append(metrics['latency_ms'])
        self.y_cpu.append(metrics['cpu_usage_percent'])
        self.y_memory.append(metrics['memory_usage_percent'])

        self.line_requests.set_data(self.x_data, self.y_requests)
        self.line_latency.set_data(self.x_data, self.y_latency)
        self.line_cpu.set_data(self.x_data, self.y_cpu)
        self.line_memory.set_data(self.x_data, self.y_memory)

        # Ajustar límites del eje X automáticamente
        # Mostrar una ventana deslizante de los últimos 50 pasos + un margen de 10
        self.axs[0].set_xlim(max(0, time_step - 50), time_step + 10) 

        # Ajustar límites del eje Y para solicitudes (dinámico)
        # Un valor mínimo para evitar que el eje sea 0 si no hay solicitudes
        min_y_requests = 0
        max_y_requests = max(200, max(self.y_requests) * 1.1 if self.y_requests else 200)
        self.axs[0].set_ylim(min_y_requests, max_y_requests)

        # Ajustar límites del eje Y para latencia (dinámico con mínimo)
        current_max_latency = max(self.y_latency) if self.y_latency else 0
        # Establece un límite mínimo de 1000ms, pero expande si se supera
        new_y_limit_latency = max(1000, current_max_latency * 1.1) 
        self.axs[1].set_ylim(0, new_y_limit_latency) # Latencia hasta 1000ms

        # CPU y Memoria se mantienen fijos (0-100)
        # self.axs[2].set_ylim(0, 100)
        # self.axs[3].set_ylim(0, 100)

        self.canvas.draw_idle() # Redibuja el lienzo

        # Actualizar la etiqueta del paso actual
        self.step_label.config(text=f"Paso actual: {time_step}")

    def reset_charts(self):
        """Limpia los datos y gráficos para una nueva simulación."""
        self.x_data = []
        self.y_requests = []
        self.y_latency = []
        self.y_cpu = []
        self.y_memory = []

        self.line_requests.set_data([], [])
        self.line_latency.set_data([], [])
        self.line_cpu.set_data([], [])
        self.line_memory.set_data([], [])

        # Resetear límites de los ejes a valores iniciales
        for ax in self.axs:
            ax.set_xlim(0, 100) # Un valor inicial razonable para el eje X

        self.axs[0].set_ylim(0, 200) # Solicitudes
        self.axs[1].set_ylim(0, 1000) # Latencia (reset a 1000)
        self.axs[2].set_ylim(0, 100) # CPU
        self.axs[3].set_ylim(0, 100) # Memoria

        self.canvas.draw_idle()

    def plot_paper_figures(self, config_params):
        """
        Dibuja dos figuras tipo paper:
        1. Órbita del Skew Tent Map para el alpha dado.
        2. Sensibilidad a condiciones iniciales o alpha.
        Guarda las figuras en self.paper_figures para exportación.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        alpha = config_params.get('alpha', 0.499)
        x0 = config_params.get('x0', 0.3)

        # Figura 1: Órbita del Skew Tent Map para el alpha dado
        N = 100
        X = np.zeros(N)
        X[0] = x0
        def skew_tent_map(x, alpha):
            return x / alpha if x < alpha else (1 - x) / (1 - alpha)
        for i in range(1, N):
            X[i] = skew_tent_map(X[i-1], alpha)
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot(range(N), X, marker='o', markersize=2, linestyle='-', color='blue')
        ax1.set_title(f"Órbita Skew Tent Map (α={alpha:.4f}, x₀={x0})")
        ax1.set_xlabel("Iteración")
        ax1.set_ylabel("$x_i$")
        ax1.set_ylim([0, 1])
        ax1.grid(True)

        # Figura 2: Sensibilidad a condiciones iniciales o alpha
        N2 = 50
        # Sensibilidad a condiciones iniciales
        X1 = np.zeros(N2)
        X2 = np.zeros(N2)
        X1[0] = x0
        X2[0] = x0 + 0.001  # valor inicial muy cercano
        for i in range(1, N2):
            X1[i] = skew_tent_map(X1[i-1], alpha)
            X2[i] = skew_tent_map(X2[i-1], alpha)
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(range(N2), X1, 'b-', label=f"x₀={x0:.3f}")
        ax2.plot(range(N2), X2, 'r--', label=f"x₀={x0+0.001:.3f}")
        ax2.set_title(f"Sensibilidad a Condiciones Iniciales (α={alpha:.4f})")
        ax2.set_xlabel("Iteración")
        ax2.set_ylabel("$x_i$")
        ax2.set_ylim([0, 1])
        ax2.legend()
        ax2.grid(True)

        self.paper_figures = [fig1, fig2]

        # Si ResultsTab está disponible, pásale las figuras paper como lista plana
        if self.results_tab is not None:
            self.results_tab.set_paper_figures([fig1, fig2])

    def plot_orbits(self, orbit_data_list):
        """
        Genera y muestra las gráficas de órbitas.
        Guarda las figuras en self.orbit_figures para exportación.
        """
        self.orbit_figures = []  # Limpiar figuras previas
        for i, orbit_data in enumerate(orbit_data_list):
            fig, ax = plt.subplots()
            ax.plot(orbit_data['x'], orbit_data['y'], label=f'Órbita {i+1}')
            ax.set_title(f'Órbita {i+1}')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.legend()
            self.orbit_figures.append(fig)
        # Si ResultsTab está disponible, pásale las figuras
        if self.results_tab is not None:
            self.results_tab.set_orbit_figures(self.orbit_figures)
            self.results_tab.set_simulation_figure(self.fig)

    def get_simulation_figure(self):
        """
        Devuelve la figura principal de simulación (4 subplots).
        """
        return self.fig

    def get_orbit_figures(self):
        """
        Devuelve la lista de figuras de órbitas.
        """
        return self.orbit_figures

    def get_all_figures_for_export(self):
        """
        Devuelve una lista con todas las figuras relevantes para exportar.
        """
        figs = []
        if hasattr(self, "fig"):
            figs.append(self.fig)
        if hasattr(self, "orbit_figures") and self.orbit_figures:
            figs.extend(self.orbit_figures)
        if hasattr(self, "paper_figures") and self.paper_figures:
            figs.extend(self.paper_figures)
        return figs
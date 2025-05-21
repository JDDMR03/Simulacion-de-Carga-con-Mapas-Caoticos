# src/gui/simulation_tab.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

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

        # Toolbar de Matplotlib
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
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
        self.axs[3].set_xlabel('Paso de Tiempo')
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
        Dibuja las figuras tipo paper para el mapa tent y las órbitas.
        Guarda la figura en self.paper_figures para exportación.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # Parámetros del paper
        r_values = [0.4, 0.8]
        x = np.linspace(0, 1, 500)
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))

        # Tent map orbits for r=0.4 and r=0.8
        for idx, r in enumerate(r_values):
            tent_map = lambda x: r * x if x < 0.5 else r * (1 - x)
            X = np.zeros(100)
            X[0] = 0.1
            for i in range(1, 100):
                X[i] = tent_map(X[i-1])
            axs[0, idx].plot(X[:-1], X[1:], 'k.', markersize=1)
            axs[0, idx].set_title(f"System parameter = {r}")
            axs[0, idx].set_xlabel("$X_n$")
            axs[0, idx].set_ylabel("$X_{{n+1}}$")
            axs[0, idx].set_xlim([0, 1])
            axs[0, idx].set_ylim([0, 1])

        # Orbits for two close initial conditions
        r = 1.99
        N = 25
        X1 = np.zeros(N)
        X2 = np.zeros(N)
        X1[0] = 0.3
        X2[0] = 0.301
        for i in range(1, N):
            X1[i] = r * X1[i-1] if X1[i-1] < 0.5 else r * (1 - X1[i-1])
            X2[i] = r * X2[i-1] if X2[i-1] < 0.5 else r * (1 - X2[i-1])
        axs[1, 0].plot(range(N), X1, 'k-.', label="X0=0.30")
        axs[1, 0].plot(range(N), X2, 'k-', label="X0=0.301")
        axs[1, 0].set_xlabel("Iteration number")
        axs[1, 0].set_ylabel("$X_n$")
        axs[1, 0].legend()
        axs[1, 0].set_ylim([0, 1])

        # Orbits for two close r values
        X3 = np.zeros(N)
        X4 = np.zeros(N)
        X3[0] = 0.3
        X4[0] = 0.3
        r1 = 1.99
        r2 = 1.991
        for i in range(1, N):
            X3[i] = r1 * X3[i-1] if X3[i-1] < 0.5 else r1 * (1 - X3[i-1])
            X4[i] = r2 * X4[i-1] if X4[i-1] < 0.5 else r2 * (1 - X4[i-1])
        axs[1, 1].plot(range(N), X3, 'k-', label="r=1.99")
        axs[1, 1].plot(range(N), X4, 'k-.', label="r=1.991")
        axs[1, 1].set_xlabel("Iteration number")
        axs[1, 1].set_ylabel("$X_n$")
        axs[1, 1].legend()
        axs[1, 1].set_ylim([0, 1])

        plt.tight_layout()
        self.paper_figures = [fig]  # Guarda la figura para exportar

        # Si ResultsTab está disponible, pásale la figura paper como lista plana (no lista de listas)
        if self.results_tab is not None:
            self.results_tab.set_paper_figures([fig])

        plt.show()

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
            # ...código para mostrar en la GUI...
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
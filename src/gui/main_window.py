# src/gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import numpy as np
import os

# Importar las clases del core
from src.core.chaotic_generator import ChaoticBitGenerator
from src.core.randomness_tests import RandomnessTests
from src.core.simulation_engine import LoadSimulator

# Importar las pestañas de la GUI
from src.gui.config_tab import ConfigTab
from src.gui.simulation_tab import SimulationTab
from src.gui.results_tab import ResultsTab

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BitGen")
        self.geometry("1920x1080") # Aumentar tamaño para mejor visualización

        self.chaotic_generator = ChaoticBitGenerator()
        self.randomness_tester = RandomnessTests()
        self.load_simulator = None # Se inicializará al iniciar la simulación

        self._create_notebook()
        self._setup_simulation_threading()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.config_tab = ConfigTab(self.notebook)
        self.notebook.add(self.config_tab, text="Configuración")

        # Crear ResultsTab primero para pasar referencia a SimulationTab
        self.results_tab = ResultsTab(self.notebook)
        self.simulation_tab = SimulationTab(self.notebook, results_tab=self.results_tab)
        self.notebook.add(self.simulation_tab, text="Simulación en Tiempo Real")
        self.notebook.add(self.results_tab, text="Análisis de Resultados")

        # Conectar el callback de la pestaña de configuración
        self.config_tab.set_simulation_callback(self.start_simulation)
        
        # Limpiar resultados al cambiar de pestaña a config
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Configuración":
            # Si volvemos a Configuración, preparamos las otras pestañas para una nueva simulación
            self.simulation_tab.reset_charts()
            self.results_tab.reset_summary_labels()
            self.results_tab.reset_test_labels()

    def _setup_simulation_threading(self):
        self.simulation_thread = None
        self.stop_simulation_flag = False
        self.simulation_running = False

    def start_simulation(self, config_params: dict):
        """
        Inicia la simulación en un hilo separado.
        """
        if self.simulation_running:
            messagebox.showinfo("Simulación", "Una simulación ya está en curso.")
            return

        self.stop_simulation_flag = False
        self.simulation_running = True
        
        # Resetear las pestañas de simulación y resultados para la nueva ejecución
        self.simulation_tab.reset_charts()
        self.results_tab.reset_summary_labels()
        self.results_tab.reset_test_labels()

        # Pasar a la pestaña de simulación
        self.notebook.select(self.simulation_tab)

        # Iniciar la simulación en un hilo separado para no bloquear la GUI
        self.simulation_thread = threading.Thread(target=self._run_simulation_logic, args=(config_params,))
        self.simulation_thread.start()

    def _run_simulation_logic(self, config_params: dict):
        """
        La lógica principal de la simulación que se ejecuta en un hilo separado.
        """
        try:
            # 1. Generar bits caóticos y valores reales y periodo
            messagebox.showinfo("Simulación", f"Generando {config_params['num_bits']} bits caóticos. Esto puede tomar un momento para grandes N.")
            chaotic_bits, chaotic_x_values, period_ok = self.chaotic_generator.generate_cccbg_bits(
                alpha=config_params['alpha'],
                x0=config_params['x0'],
                y0=config_params['y0'],
                num_bits=config_params['num_bits']
            )
            
            # 2. Inicializar el simulador de carga
            self.load_simulator = LoadSimulator(
                num_users=config_params['num_users'],
                latency_sensitivity=config_params['latency_sensitivity'],
                cpu_sensitivity=config_params['cpu_sensitivity'],
                memory_sensitivity=config_params['memory_sensitivity'],
                recovery_rate=config_params['recovery_rate']
            )
            self.load_simulator.reset_simulation() # Asegurar que está reseteado

            # 3. Ejecutar la simulación paso a paso
            for i, bit in enumerate(chaotic_bits):
                if self.stop_simulation_flag:
                    break
                
                # Actualizar métricas
                current_metrics = self.load_simulator.simulate_step(bit)
                
                # Actualizar GUI (usar after para hacerlo en el hilo principal de Tkinter)
                self.after(1, self.simulation_tab.update_realtime_charts, current_metrics['time_step'], current_metrics)
                
                # Pequeña pausa para ver el progreso (ajustable)
                # time.sleep(0.001) # Esto puede ralentizar para muchos pasos

            # 4. Finalizar simulación y mostrar resultados
            simulation_history = self.load_simulator.get_simulation_history()
            
            # 5. Ejecutar pruebas de aleatoriedad
            test_results = {}
            test_results['monobit'] = self.randomness_tester.monobit_test(chaotic_bits)
            test_results['serial'] = self.randomness_tester.serial_test(chaotic_bits, m=2) # m=2 para díadas
            test_results['autocorr'] = self.randomness_tester.auto_correlation_test(chaotic_bits, d=1) # d=1 como en el paper
            test_results['poker'] = self.randomness_tester.poker_test(chaotic_bits, m=4) # m=4 como en el paper
            # Añadir resultado de periodo
            test_results['period_ok'] = period_ok

            # Actualizar GUI con resultados finales
            self.after(1, self.results_tab.display_simulation_summary, simulation_history)
            self.after(1, self.results_tab.display_test_results, test_results, chaotic_bits)
            
            # Guardar los valores reales y periodo para exportación
            self.results_tab.chaotic_x_values = chaotic_x_values
            self.results_tab.period_ok = period_ok
            
            # Graficar órbitas y mapas tipo paper
            self.after(1, self.simulation_tab.plot_paper_figures, config_params)

            self.after(1, lambda: self.notebook.select(self.results_tab)) # Mover a la pestaña de resultados
            self.after(1, lambda: messagebox.showinfo("Simulación Completa", "La simulación ha finalizado con éxito."))

        except Exception as e:
            self.after(1, lambda: messagebox.showerror("Error de Simulación", f"Ocurrió un error durante la simulación: {e}"))
            import traceback
            traceback.print_exc() # Imprimir el stack trace en la consola para depuración
        finally:
            self.simulation_running = False

    def stop_simulation(self):
        """Detiene la simulación en curso."""
        if self.simulation_running:
            self.stop_simulation_flag = True
            messagebox.showinfo("Simulación", "Solicitud de detención de simulación enviada. Esperando finalización del paso actual.")
        else:
            messagebox.showinfo("Simulación", "No hay simulación en curso para detener.")

    def _on_close(self):
        """Cierra completamente la aplicación y todos los hilos."""
        self.stop_simulation_flag = True
        self.simulation_running = False
        self.destroy()
        os._exit(0)  # Forzar cierre de todos los procesos/hilos

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
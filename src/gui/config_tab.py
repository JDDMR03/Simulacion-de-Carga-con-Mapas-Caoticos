# src/gui/config_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import time

class ConfigTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.simulation_callback = None

        # Calcular alpha en el rango [0.4900, 0.5000] usando el tiempo actual
        current_time = int(time.time())
        raw_alpha = 0.4900 + ((current_time % 100) / 10000.0)
        print(((current_time % 100) / 1000.0))
        print(raw_alpha)
        self.alpha_value = min(raw_alpha, 0.5000)

        self._create_widgets()

    def _create_widgets(self):
        # Frame principal para configuración
        config_frame = ttk.LabelFrame(self, text="Configuración de la Simulación")
        config_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Sección de Generación de Bits Caóticos (Skew Tent Map) ---
        chaotic_gen_frame = ttk.LabelFrame(config_frame, text="Generador de Bits Caóticos (Skew Tent Map)")
        chaotic_gen_frame.pack(fill="x", padx=5, pady=5)

        # Parámetro alpha (solo texto, no editable)
        ttk.Label(chaotic_gen_frame, text="Parámetro del sistema (α):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(chaotic_gen_frame, text=f"{self.alpha_value:.4f}", foreground="blue").grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # Condición inicial x0
        ttk.Label(chaotic_gen_frame, text="Condición inicial del primer mapa (x₀):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.x0_entry = ttk.Entry(chaotic_gen_frame)
        self.x0_entry.insert(0, "0.3")
        self.x0_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Condición inicial y0
        ttk.Label(chaotic_gen_frame, text="Condición inicial del segundo mapa (y₀):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.y0_entry = ttk.Entry(chaotic_gen_frame)
        self.y0_entry.insert(0, "0.301")
        self.y0_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # Número de bits/pasos de simulación
        ttk.Label(chaotic_gen_frame, text="Número de Bits/Pasos (N):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.num_bits_entry = ttk.Entry(chaotic_gen_frame)
        self.num_bits_entry.insert(0, "10000")
        self.num_bits_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # Advertencia para el número de bits
        self.num_bits_warning_label = ttk.Label(chaotic_gen_frame, 
                                                text="*Mínimo 10,000 para todas las pruebas de aleatoriedad.", 
                                                foreground="blue", font=("Arial", 8))
        self.num_bits_warning_label.grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky="w")

        chaotic_gen_frame.columnconfigure(1, weight=1)

        # --- Sección de Simulación de Carga ---
        load_sim_frame = ttk.LabelFrame(config_frame, text="Parámetros de Simulación de Carga")
        load_sim_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(load_sim_frame, text="Número de Usuarios Simulados:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.num_users_entry = ttk.Entry(load_sim_frame)
        self.num_users_entry.insert(0, "100")
        self.num_users_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(load_sim_frame, text="Sensibilidad Latencia:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.lat_sens_entry = ttk.Entry(load_sim_frame)
        self.lat_sens_entry.insert(0, "1.5")
        self.lat_sens_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(load_sim_frame, text="Sensibilidad CPU:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.cpu_sens_entry = ttk.Entry(load_sim_frame)
        self.cpu_sens_entry.insert(0, "0.8")
        self.cpu_sens_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(load_sim_frame, text="Sensibilidad Memoria:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.mem_sens_entry = ttk.Entry(load_sim_frame)
        self.mem_sens_entry.insert(0, "0.5")
        self.mem_sens_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(load_sim_frame, text="Tasa de Recuperación:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.recovery_rate_entry = ttk.Entry(load_sim_frame)
        self.recovery_rate_entry.insert(0, "0.05")
        self.recovery_rate_entry.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        load_sim_frame.columnconfigure(1, weight=1)

        # Botón para iniciar simulación
        start_button = ttk.Button(config_frame, text="Iniciar Simulación", command=self._start_simulation)
        start_button.pack(pady=10)

    def _update_param_labels(self, event=None):
        pass

    def _start_simulation(self):
        """Recoge los parámetros y llama al callback de la simulación."""
        try:
            config_params = {
                'alpha': float(self.alpha_value),
                'x0': float(self.x0_entry.get()),
                'y0': float(self.y0_entry.get()),
                'num_bits': int(self.num_bits_entry.get()),
                'num_users': int(self.num_users_entry.get()),
                'latency_sensitivity': float(self.lat_sens_entry.get()),
                'cpu_sensitivity': float(self.cpu_sens_entry.get()),
                'memory_sensitivity': float(self.mem_sens_entry.get()),
                'recovery_rate': float(self.recovery_rate_entry.get()),
            }

            # Validaciones para Skew Tent Map
            if not (0.49 <= config_params['alpha'] <= 0.50):
                messagebox.showerror("Error de Validación", "El parámetro α debe estar en el rango [0.49, 0.50].")
                return
            if not (0 <= config_params['x0'] <= 1 and 0 <= config_params['y0'] <= 1):
                messagebox.showerror("Error de Validación", "Las condiciones iniciales x₀, y₀ deben estar en [0, 1].")
                return
            if config_params['num_bits'] <= 0:
                messagebox.showerror("Error de Validación", "El número de bits debe ser un entero positivo.")
                return
            if config_params['num_bits'] < 10000:
                response = messagebox.askyesno("Advertencia de Longitud", 
                                                f"El número de bits ({config_params['num_bits']}) es menor a 10,000. "
                                                f"Algunas pruebas de aleatoriedad pueden no ser válidas.\n"
                                                f"¿Desea continuar de todos modos?")
                if not response:
                    return
            if config_params['num_users'] <= 0:
                messagebox.showerror("Error de Validación", "El número de usuarios simulados debe ser un entero positivo.")
                return

            if self.simulation_callback:
                self.simulation_callback(config_params)

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Por favor, revise los valores ingresados. Error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def set_simulation_callback(self, callback):
        self.simulation_callback = callback
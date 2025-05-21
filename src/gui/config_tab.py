# src/gui/config_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

class ConfigTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.simulation_callback = None # Se usará para llamar a la función de iniciar simulación en MainWindow

        self._create_widgets()

    def _create_widgets(self):
        # Frame principal para configuración
        config_frame = ttk.LabelFrame(self, text="Configuración de la Simulación")
        config_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Sección de Generación de Bits Caóticos ---
        chaotic_gen_frame = ttk.LabelFrame(config_frame, text="Generador de Bits Caóticos (CCCBG)")
        chaotic_gen_frame.pack(fill="x", padx=5, pady=5)

        # Mapa 1
        ttk.Label(chaotic_gen_frame, text="Mapa Caótico 1:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.map1_type = ttk.Combobox(chaotic_gen_frame, values=["logistic", "tent", "sine"])
        self.map1_type.set("tent") # Paper uses tent map
        self.map1_type.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.map1_type.bind("<<ComboboxSelected>>", self._update_param_labels)

        ttk.Label(chaotic_gen_frame, text="X0 1:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.x0_1_entry = ttk.Entry(chaotic_gen_frame)
        self.x0_1_entry.insert(0, "0.3") # Paper default
        self.x0_1_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.param1_label = ttk.Label(chaotic_gen_frame, text="Parámetro 1 (r):") # r para tent map
        self.param1_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.param1_entry = ttk.Entry(chaotic_gen_frame)
        self.param1_entry.insert(0, "1.99") # Paper default
        self.param1_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # Mapa 2
        ttk.Label(chaotic_gen_frame, text="Mapa Caótico 2:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.map2_type = ttk.Combobox(chaotic_gen_frame, values=["logistic", "tent", "sine"])
        self.map2_type.set("tent") # Paper uses tent map
        self.map2_type.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.map2_type.bind("<<ComboboxSelected>>", self._update_param_labels)

        ttk.Label(chaotic_gen_frame, text="X0 2:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.x0_2_entry = ttk.Entry(chaotic_gen_frame)
        self.x0_2_entry.insert(0, "0.301") # Paper default
        self.x0_2_entry.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        self.param2_label = ttk.Label(chaotic_gen_frame, text="Parámetro 2 (r):") # r para tent map
        self.param2_label.grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.param2_entry = ttk.Entry(chaotic_gen_frame)
        self.param2_entry.insert(0, "1.99") # Paper default
        self.param2_entry.grid(row=5, column=1, padx=5, pady=2, sticky="ew")
        
        # Número de bits/pasos de simulación
        ttk.Label(chaotic_gen_frame, text="Número de Bits/Pasos (N):").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.num_bits_entry = ttk.Entry(chaotic_gen_frame)
        self.num_bits_entry.insert(0, "20000") # Paper default for orbit plots
        self.num_bits_entry.grid(row=6, column=1, padx=5, pady=2, sticky="ew")
        
        # Añadir una etiqueta de advertencia para el número de bits
        self.num_bits_warning_label = ttk.Label(chaotic_gen_frame, 
                                                text="*Mínimo 20,000 para todas las pruebas de aleatoriedad.", 
                                                foreground="blue", font=("Arial", 8))
        self.num_bits_warning_label.grid(row=7, column=0, columnspan=2, padx=5, pady=2, sticky="w")


        chaotic_gen_frame.columnconfigure(1, weight=1) # Permite que la columna de entradas se expanda


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
        
        self._update_param_labels() # Llama para configurar las etiquetas iniciales

    def _update_param_labels(self, event=None):
        """Actualiza las etiquetas de los parámetros según el mapa seleccionado."""
        map1 = self.map1_type.get()
        map2 = self.map2_type.get()

        if map1 == 'logistic':
            self.param1_label.config(text="Parámetro 1 (\u03BC):")
            self.param1_entry.delete(0, tk.END)
            self.param1_entry.insert(0, "4.0")
        elif map1 == 'tent':
            self.param1_label.config(text="Parámetro 1 (r):")
            self.param1_entry.delete(0, tk.END)
            self.param1_entry.insert(0, "2.0")
        elif map1 == 'sine':
            self.param1_label.config(text="Parámetro 1 (Ignorado):")
            self.param1_entry.delete(0, tk.END)
            self.param1_entry.insert(0, "0.0") # El valor no importa para sine map
        
        if map2 == 'logistic':
            self.param2_label.config(text="Parámetro 2 (\u03BC):")
            self.param2_entry.delete(0, tk.END)
            self.param2_entry.insert(0, "4.0")
        elif map2 == 'tent':
            self.param2_label.config(text="Parámetro 2 (r):")
            self.param2_entry.delete(0, tk.END)
            self.param2_entry.insert(0, "2.0")
        elif map2 == 'sine':
            self.param2_label.config(text="Parámetro 2 (Ignorado):")
            self.param2_entry.delete(0, tk.END)
            self.param2_entry.insert(0, "0.0") # El valor no importa para sine map


    def _start_simulation(self):
        """Recoge los parámetros y llama al callback de la simulación."""
        try:
            config_params = {
                'map1_type': self.map1_type.get(),
                'x0_1': float(self.x0_1_entry.get()),
                'param1': float(self.param1_entry.get()),
                'map2_type': self.map2_type.get(),
                'x0_2': float(self.x0_2_entry.get()),
                'param2': float(self.param2_entry.get()),
                'num_bits': int(self.num_bits_entry.get()),
                'num_users': int(self.num_users_entry.get()),
                'latency_sensitivity': float(self.lat_sens_entry.get()),
                'cpu_sensitivity': float(self.cpu_sens_entry.get()),
                'memory_sensitivity': float(self.mem_sens_entry.get()),
                'recovery_rate': float(self.recovery_rate_entry.get()),
            }

            # Validaciones básicas
            if not (0 < config_params['x0_1'] < 1 and 0 < config_params['x0_2'] < 1):
                messagebox.showerror("Error de Validación", "Las condiciones iniciales X0 deben estar entre 0 y 1 (exclusivo).")
                return
            if config_params['num_bits'] <= 0:
                messagebox.showerror("Error de Validación", "El número de bits debe ser un entero positivo.")
                return
            # Se añade esta validación para recordar al usuario
            if config_params['num_bits'] < 5000:
                response = messagebox.askyesno("Advertencia de Longitud", 
                                                f"El número de bits ({config_params['num_bits']}) es menor a 20,000. "
                                                f"Algunas pruebas de aleatoriedad pueden no ser válidas.\n"
                                                f"¿Desea continuar de todos modos?")
                if not response:
                    return # El usuario ha decidido no continuar

            if config_params['num_users'] <= 0:
                messagebox.showerror("Error de Validación", "El número de usuarios simulados debe ser un entero positivo.")
                return

            # Validaciones específicas para mapas (ej. mu para logistic, r para tent)
            if config_params['map1_type'] == 'logistic' and not (0 <= config_params['param1'] <= 4):
                 messagebox.showerror("Error de Validación", "Parámetro 1 (mu) para Logistic Map debe estar entre 0 y 4.")
                 return
            if config_params['map1_type'] == 'tent' and not (0 <= config_params['param1'] <= 2):
                 messagebox.showerror("Error de Validación", "Parámetro 1 (r) para Tent Map debe estar entre 0 y 2.")
                 return
            
            if config_params['map2_type'] == 'logistic' and not (0 <= config_params['param2'] <= 4):
                 messagebox.showerror("Error de Validación", "Parámetro 2 (mu) para Logistic Map debe estar entre 0 y 4.")
                 return
            if config_params['map2_type'] == 'tent' and not (0 <= config_params['param2'] <= 2):
                 messagebox.showerror("Error de Validación", "Parámetro 2 (r) para Tent Map debe estar entre 0 y 2.")
                 return

            if self.simulation_callback:
                self.simulation_callback(config_params)

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Por favor, revise los valores ingresados. Error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def set_simulation_callback(self, callback):
        """Establece la función que será llamada al iniciar la simulación."""
        self.simulation_callback = callback
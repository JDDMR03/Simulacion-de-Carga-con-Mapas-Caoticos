import numpy as np
import time

class LoadSimulator:
    def __init__(self,
                 num_users: int = 100,
                 base_latency_ms: float = 1.0, # Paper: 1.0 ms
                 base_cpu_usage_percent: float = 10.0,
                 base_memory_usage_percent: float = 20.0,
                 latency_sensitivity: float = 1.5, # Paper: 1.5
                 cpu_sensitivity: float = 0.8,    # Paper: 0.8
                 memory_sensitivity: float = 0.5, # Paper: 0.5
                 recovery_rate: float = 0.05,     # Paper: 0.05
                 max_latency_ms: float = 1000.0,
                 max_cpu_usage_percent: float = 98.0,
                 max_memory_usage_percent: float = 95.0
                 ):
        """
        Inicializa el simulador de carga.

        Args:
            num_users (int): Número simulado de usuarios concurrentes.
            base_latency_ms (float): Latencia inicial en milisegundos.
            base_cpu_usage_percent (float): Uso inicial de CPU en porcentaje.
            base_memory_usage_percent (float): Uso inicial de memoria en porcentaje.
            latency_sensitivity (float): Factor que determina cuánto aumenta la latencia por unidad de carga.
            cpu_sensitivity (float): Factor que determina cuánto aumenta la CPU por unidad de carga.
            memory_sensitivity (float): Factor que determina cuánto aumenta la memoria por unidad de carga.
            recovery_rate (float): Tasa de recuperación de las métricas (disminución hacia la base).
            max_latency_ms (float): Latencia máxima permitida en la simulación.
            max_cpu_usage_percent (float): Uso máximo de CPU permitido.
            max_memory_usage_percent (float): Uso máximo de memoria permitido.
        """
        self.num_users = num_users
        
        self.base_latency = base_latency_ms
        self.base_cpu = base_cpu_usage_percent
        self.base_memory = base_memory_usage_percent

        self.current_latency = base_latency_ms
        self.current_cpu_usage = base_cpu_usage_percent
        self.current_memory_usage = base_memory_usage_percent
        
        self.latency_sensitivity = latency_sensitivity
        self.cpu_sensitivity = cpu_sensitivity
        self.memory_sensitivity = memory_sensitivity
        self.recovery_rate = recovery_rate
        
        self.max_latency = max_latency_ms
        self.max_cpu = max_cpu_usage_percent
        self.max_memory = max_memory_usage_percent

        # Historial para almacenar los datos de la simulación para gráficos
        self.history = {
            'time_steps': [],
            'latency': [],
            'cpu': [],
            'memory': [],
            'simulated_requests': []
        }
        self.current_time_step = 0

    def simulate_step(self, chaotic_bit_value: int) -> dict:
        """
        Simula un paso en el tiempo basándose en el valor del bit caótico.
        
        Args:
            chaotic_bit_value (int): El bit (0 o 1) generado por el mapa caótico.

        Returns:
            dict: Un diccionario con las métricas actualizadas para este paso.
        """
        if not (chaotic_bit_value == 0 or chaotic_bit_value == 1):
            raise ValueError("El valor del bit caótico debe ser 0 o 1.")

        # La "carga" simulada para este paso se influenciará por el bit.
        # Por ejemplo, un '1' podría significar un aumento más significativo de solicitudes.
        # Esto es heurístico, pero permite modelar la "impredecibilidad" de la carga.
        
        # Si el bit es 1, asumimos una carga más intensa.
        # Si el bit es 0, asumimos una carga más moderada o una tendencia a la recuperación.
        
        # Podríamos modelar las solicitudes como una distribución, pero por simplicidad
        # y para reflejar el impacto directo del bit, usaremos un factor multiplicador.
        
        # "Cantidad" simulada de solicitudes o unidades de trabajo en este paso
        # Se puede añadir una pequeña variación aleatoria para más realismo
        base_requests_per_user = 1.0 # Solicitudes "base" por usuario simulado
        
        # El bit caótico modifica el número de solicitudes por usuario
        # Si bit es 1, aumenta las solicitudes; si es 0, puede ser base o incluso menos
        if chaotic_bit_value == 1:
            # Pico de carga: puede ser un multiplicador mayor, o añadir un número fijo
            simulated_requests_this_step = self.num_users * (base_requests_per_user + np.random.uniform(0.5, 1.5))
        else:
            # Carga base/normal o disminución:
            simulated_requests_this_step = self.num_users * (base_requests_per_user + np.random.uniform(0.0, 0.5))

        # --- Actualizar Métricas Simuladas ---

        # 1. Latencia: Aumenta con la carga, disminuye con la recuperación.
        latency_change = (simulated_requests_this_step / self.num_users) * self.latency_sensitivity
        if chaotic_bit_value == 1:
            self.current_latency += latency_change
        else:
            self.current_latency -= latency_change * self.recovery_rate # Disminución más suave
        
        # Asegurar que la latencia esté dentro de los límites
        self.current_latency = max(self.base_latency, min(self.max_latency, self.current_latency))

        # 2. Uso de CPU: Aumenta con la carga, disminuye con la recuperación.
        cpu_change = (simulated_requests_this_step / self.num_users) * self.cpu_sensitivity
        if chaotic_bit_value == 1:
            self.current_cpu_usage += cpu_change
        else:
            self.current_cpu_usage -= cpu_change * self.recovery_rate
            
        self.current_cpu_usage = max(self.base_cpu, min(self.max_cpu, self.current_cpu_usage))

        # 3. Uso de Memoria: Aumenta con la carga, disminuye con la recuperación.
        memory_change = (simulated_requests_this_step / self.num_users) * self.memory_sensitivity
        if chaotic_bit_value == 1:
            self.current_memory_usage += memory_change
        else:
            self.current_memory_usage -= memory_change * self.recovery_rate
            
        self.current_memory_usage = max(self.base_memory, min(self.max_memory, self.current_memory_usage))

        # --- Almacenar historial ---
        self.history['time_steps'].append(self.current_time_step)
        self.history['latency'].append(self.current_latency)
        self.history['cpu'].append(self.current_cpu_usage)
        self.history['memory'].append(self.current_memory_usage)
        self.history['simulated_requests'].append(simulated_requests_this_step)
        
        self.current_time_step += 1 # Incrementar el paso de tiempo para el próximo ciclo

        return {
            'time_step': self.current_time_step -1, # Retornar el paso actual
            'latency_ms': self.current_latency,
            'cpu_usage_percent': self.current_cpu_usage,
            'memory_usage_percent': self.current_memory_usage,
            'simulated_requests': simulated_requests_this_step
        }

    def get_simulation_history(self) -> dict:
        """Retorna el historial completo de la simulación."""
        return self.history

    def reset_simulation(self):
        """Reinicia el estado del simulador y el historial."""
        self.current_latency = self.base_latency
        self.current_cpu_usage = self.base_cpu
        self.current_memory_usage = self.base_memory
        self.history = {
            'time_steps': [],
            'latency': [],
            'cpu': [],
            'memory': [],
            'simulated_requests': []
        }
        self.current_time_step = 0
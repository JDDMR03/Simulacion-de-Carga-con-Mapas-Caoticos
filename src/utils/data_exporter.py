import pandas as pd
import numpy as np
import os
import datetime
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages # Para exportar a PDF
import io

class DataExporter:
    """
    Clase de utilidad para exportar datos de simulación y resultados de pruebas
    a varios formatos (CSV, PDF).
    """
    @staticmethod
    def export_to_csv(simulation_history: dict, bit_sequence: np.ndarray):
        """
        Exporta el historial de la simulación y la secuencia de bits a archivos CSV.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Diálogo para seleccionar la ubicación de guardado
        file_path_base = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"simulacion_carga_{timestamp}",
            title="Guardar Historial de Simulación CSV",
            filetypes=[("Archivos CSV", "*.csv")]
        )

        if not file_path_base: # Si el usuario cancela
            return

        try:
            exported_any = False
            # Exportar historial de métricas
            if simulation_history and any(simulation_history.values()):
                df_history = pd.DataFrame(simulation_history)
                df_history.index.name = 'step'
                df_history.to_csv(file_path_base)
                exported_any = True
                messagebox.showinfo("Exportación Exitosa", f"Historial de simulación guardado en:\n{file_path_base}")
            else:
                messagebox.showinfo("Exportación CSV", "No hay historial de simulación para exportar.")

            # Exportar secuencia de bits (en un archivo separado o al mismo si se desea)
            if bit_sequence is not None and len(bit_sequence) > 0:
                bit_file_path = file_path_base.replace(".csv", "_bits.csv") if exported_any else file_path_base # Evita sobrescribir si no se exportó historial
                if not exported_any: # Si no se exportó historial, se usa el mismo nombre de archivo
                     bit_file_path = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        initialfile=f"secuencia_bits_{timestamp}",
                        title="Guardar Secuencia de Bits CSV",
                        filetypes=[("Archivos CSV", "*.csv")]
                    )
                     if not bit_file_path: # Si el usuario cancela de nuevo
                         return
                
                df_bits = pd.DataFrame(bit_sequence, columns=['bit_value'])
                df_bits.index.name = 'bit_index'
                df_bits.to_csv(bit_file_path)
                messagebox.showinfo("Exportación Exitosa", f"Secuencia de bits guardada en:\n{bit_file_path}")
            else:
                messagebox.showinfo("Exportación CSV", "No hay secuencia de bits para exportar.")

        except Exception as e:
            messagebox.showerror("Error de Exportación CSV", f"No se pudo exportar los datos a CSV: {e}")

    @staticmethod
    def export_to_pdf(simulation_history: dict, bit_sequence: np.ndarray, test_results: dict, figures: plt.Figure):
        """
        Exporta un reporte completo de la simulación a un archivo PDF.
        Incluye un resumen textual de los resultados y los gráficos.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"reporte_simulacion_{timestamp}",
            title="Guardar Reporte de Simulación PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )

        if not file_path: # Si el usuario cancela
            return

        try:
            with PdfPages(file_path) as pdf:
                # Página de Título/Resumen
                fig_summary = plt.figure(figsize=(8.5, 11))
                ax_summary = fig_summary.add_subplot(111)
                ax_summary.axis('off') # Ocultar ejes

                summary_text = "Reporte de Simulación de Carga con Mapas Caóticos\n\n"
                summary_text += f"Fecha del Reporte: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                if simulation_history and any(simulation_history.values()):
                    summary_text += "--- Métricas de Simulación ---\n"
                    num_steps = len(simulation_history.get('simulated_requests', []))
                    summary_text += f"Número de Pasos Simulados: {num_steps}\n"
                    
                    if simulation_history.get('simulated_requests'):
                        avg_req = np.mean(simulation_history['simulated_requests'])
                        summary_text += f"Solicitudes Promedio: {avg_req:.2f}\n"
                    if simulation_history.get('latency'):
                        avg_lat = np.mean(simulation_history['latency'])
                        summary_text += f"Latencia Promedio (ms): {avg_lat:.2f}\n"
                        max_lat = np.max(simulation_history['latency'])
                        summary_text += f"Latencia Máxima (ms): {max_lat:.2f}\n"
                    if simulation_history.get('cpu'):
                        avg_cpu = np.mean(simulation_history['cpu'])
                        summary_text += f"Uso de CPU Promedio (%): {avg_cpu:.2f}\n"
                    if simulation_history.get('memory'):
                        avg_mem = np.mean(simulation_history['memory'])
                        summary_text += f"Uso de Memoria Promedio (%): {avg_mem:.2f}\n"
                    summary_text += "\n"

                if bit_sequence is not None and len(bit_sequence) > 0:
                    n0 = np.sum(bit_sequence == 0)
                    n1 = np.sum(bit_sequence == 1)
                    summary_text += f"--- Secuencia de Bits ---\n"
                    summary_text += f"Longitud de Secuencia de Bits: {len(bit_sequence)}\n"
                    summary_text += f"Cantidad de 0s: {n0} ({n0/len(bit_sequence)*100:.2f}%)\n"
                    summary_text += f"Cantidad de 1s: {n1} ({n1/len(bit_sequence)*100:.2f}%)\n\n"


                if test_results:
                    summary_text += "--- Resultados de Pruebas de Aleatoriedad ---\n"
                    for test_name, result in test_results.items():
                        p_value = result.get('p_value', np.nan)
                        # Mostrar el mensaje del test si existe
                        test_message = result.get('message', '')
                        test_status = "N/A"
                        if p_value is not np.nan:
                            test_status = "PASSED" if p_value >= 0.01 else "FAILED"
                        
                        summary_text += f"{test_name.replace('_', ' ').title()}:\n"
                        summary_text += f"  P-valor: {p_value:.4f}\n"
                        summary_text += f"  Resultado: {test_status}\n"
                        if test_message != "OK":
                            summary_text += f"  Mensaje: {test_message}\n"
                        summary_text += "\n"
                else:
                    summary_text += "No hay resultados de pruebas de aleatoriedad disponibles.\n\n"

                ax_summary.text(0.05, 0.95, summary_text, 
                                verticalalignment='top', 
                                horizontalalignment='left', 
                                transform=ax_summary.transAxes, 
                                fontsize=10, 
                                fontfamily='monospace')
                pdf.savefig(fig_summary)
                plt.close(fig_summary)

                # Añadir las figuras de los resultados (histogramas)
                if figures:
                    pdf.savefig(figures)
                
            messagebox.showinfo("Exportación Exitosa", f"Reporte PDF guardado en:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error de Exportación PDF", f"No se pudo generar el reporte PDF: {e}")
            import traceback
            traceback.print_exc() # Para depuración
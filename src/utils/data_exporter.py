import pandas as pd
import numpy as np
import datetime
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class DataExporter:
    """
    Clase de utilidad para exportar datos de simulación y resultados de pruebas
    a varios formatos (CSV, PDF).
    """
    @staticmethod
    def export_to_csv(simulation_history: dict, bit_sequence: np.ndarray, x_values=None, period_ok=None):
        """
        Exporta el historial de la simulación y la secuencia de bits a archivos CSV.
        x_values: valores reales antes de decidir el bit (opcional)
        period_ok: bool, si la semilla cumple su periodo (opcional)
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path_base = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"simulacion_carga_{timestamp}",
            title="Guardar Historial de Simulación CSV",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if not file_path_base:
            return

        try:
            exported_any = False
            # Exportar historial de métricas
            if simulation_history and any(len(v) > 0 for v in simulation_history.values()):
                df_history = pd.DataFrame(simulation_history)
                df_history.index.name = 'paso'
                df_history.to_csv(file_path_base)
                exported_any = True
                messagebox.showinfo("Exportación Exitosa", f"Historial de simulación guardado en:\n{file_path_base}")
            else:
                messagebox.showinfo("Exportación CSV", "No hay historial de simulación para exportar.")

            # Exportar secuencia de bits
            if bit_sequence is not None and len(bit_sequence) > 0:
                bit_file_path = file_path_base.replace(".csv", "_bits.csv") if exported_any else file_path_base
                if not exported_any:
                    bit_file_path = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        initialfile=f"secuencia_bits_{timestamp}",
                        title="Guardar Secuencia de Bits CSV",
                        filetypes=[("Archivos CSV", "*.csv")]
                    )
                    if not bit_file_path:
                        return
                # Crear DataFrame con valor real y bit
                if x_values is not None and len(x_values) == len(bit_sequence):
                    df_bits = pd.DataFrame({
                        'valor_real': x_values,
                        'valor_bit': bit_sequence
                    })
                else:
                    df_bits = pd.DataFrame({'valor_bit': bit_sequence})
                df_bits.index.name = 'indice_bit'
                df_bits.to_csv(bit_file_path)
                # Escribir el resultado de periodo al final del archivo
                with open(bit_file_path, "a", encoding="utf-8") as f:
                    f.write("\n")
                    if period_ok is not None:
                        msg = "PERIODO: CUMPLIDO" if period_ok else "PERIODO: NO CUMPLIDO"
                        f.write(f"# {msg}\n")
                messagebox.showinfo("Exportación Exitosa", f"Secuencia de bits guardada en:\n{bit_file_path}")
            else:
                messagebox.showinfo("Exportación CSV", "No hay secuencia de bits para exportar.")

        except Exception as e:
            messagebox.showerror("Error de Exportación CSV", f"No se pudo exportar los datos a CSV: {e}")

    @staticmethod
    def export_to_pdf(simulation_history: dict, bit_sequence: np.ndarray, test_results: dict, figures):
        """
        Exporta un reporte completo de la simulación a un archivo PDF.
        Incluye un resumen textual de los resultados y los gráficos.
        Admite una lista de figuras o una lista de listas de figuras.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"reporte_simulacion_{timestamp}",
            title="Guardar Reporte de Simulación PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if not file_path:
            return

        try:
            with PdfPages(file_path) as pdf:
                # Página de Título/Resumen
                fig_summary = plt.figure(figsize=(8.5, 11))
                ax_summary = fig_summary.add_subplot(111)
                ax_summary.axis('off')

                summary_text = "Reporte de Simulación de Carga con Mapas Caóticos\n\n"
                summary_text += f"Fecha del Reporte: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

                # Métricas de simulación
                if simulation_history and any(len(v) > 0 for v in simulation_history.values()):
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

                # Secuencia de bits
                if bit_sequence is not None and len(bit_sequence) > 0:
                    n0 = np.sum(bit_sequence == 0)
                    n1 = np.sum(bit_sequence == 1)
                    summary_text += f"--- Secuencia de Bits ---\n"
                    summary_text += f"Longitud de Secuencia de Bits: {len(bit_sequence)}\n"
                    summary_text += f"Cantidad de 0s: {n0} ({n0/len(bit_sequence)*100:.2f}%)\n"
                    summary_text += f"Cantidad de 1s: {n1} ({n1/len(bit_sequence)*100:.2f}%)\n\n"

                # Resultados de pruebas
                if test_results:
                    summary_text += "--- Resultados de Pruebas de Aleatoriedad ---\n"
                    # Solo incluir Monobit Test en el PDF
                    monobit_result = test_results.get('Monobit Test') or test_results.get('monobit')
                    if monobit_result:
                        p_value = monobit_result.get('p_value', np.nan)
                        test_message = monobit_result.get('message', '')
                        test_status = "N/A"
                        if not np.isnan(p_value):
                            test_status = "APROBADA" if p_value >= 0.01 else "NO APROBADA"
                        summary_text += f"Monobit Test:\n"
                        summary_text += f"  P-valor: {p_value:.4f}\n"
                        summary_text += f"  Resultado: {test_status}\n"
                        if test_message and test_message != "OK":
                            summary_text += f"  Mensaje: {test_message}\n"
                        summary_text += "\n"
                    else:
                        summary_text += "No hay resultados de Monobit Test disponibles.\n\n"
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

                # Añadir todas las figuras proporcionadas (pueden ser listas anidadas de cualquier profundidad)
                def flatten_figures(figs):
                    result = []
                    if isinstance(figs, list) or isinstance(figs, tuple):
                        for f in figs:
                            result.extend(flatten_figures(f))
                    elif figs is not None:
                        result.append(figs)
                    return result

                figs_to_export = flatten_figures(figures)
                for fig in figs_to_export:
                    if fig is not None:
                        pdf.savefig(fig)
            messagebox.showinfo("Exportación Exitosa", f"Reporte PDF guardado en:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error de Exportación PDF", f"No se pudo generar el reporte PDF: {e}")
            import traceback
            traceback.print_exc()
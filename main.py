# main.py
from src.gui.main_window import MainWindow
import tkinter as tk

if __name__ == "__main__":
    # La clase MainWindow ya hereda de tk.Tk(), por lo que ella misma es la ventana principal.
    # No necesitas crear una instancia separada de tk.Tk() y luego ocultarla.
    
    app = MainWindow()
    app.mainloop() # Este es el único mainloop que se debe llamar.
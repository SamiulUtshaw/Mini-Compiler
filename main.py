# main.py
import tkinter as tk
from gui import CompilerGUI

def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
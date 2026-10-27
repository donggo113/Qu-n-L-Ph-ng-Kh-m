import tkinter as tk
from ui.login import LoginPage


def main():
    root = tk.Tk()
    LoginPage(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""Cat Calculator — Windows 95 standard calculator-inspired interface.
© AC Kondo 1999–2026
"""
import tkinter as tk
from tkinter import messagebox
import math

FACE = '#c0c0c0'
BLUE = '#000080'
RED = '#800000'

class Calculator:
    def __init__(self, root):
        self.root = root
        root.title('Calculator')
        root.geometry('740x580')
        root.minsize(740, 580)
        root.resizable(False, False)
        root.configure(bg=FACE)
        self.display = tk.StringVar(value='0.')
        self.memory = 0.0
        self.current = 0.0
        self.pending = None
        self.new_entry = True
        self.error = False
        self.memory_label = tk.StringVar(value='')

        menu = tk.Menu(root, tearoff=0)
        edit = tk.Menu(menu, tearoff=0)
        edit.add_command(label='Copy', command=self.copy)
        edit.add_command(label='Paste', command=self.paste)
        menu.add_cascade(label='Edit', menu=edit)
        view = tk.Menu(menu, tearoff=0)
        view.add_command(label='Standard', state='disabled')
        menu.add_cascade(label='View', menu=view)
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label='About Calculator', command=lambda: messagebox.showinfo('About Calculator', 'Cat Calculator — Windows 95 style\n© AC Kondo 1999–2026'))
        menu.add_cascade(label='Help', menu=help_menu)
        root.config(menu=menu)

        tk.Entry(root, textvariable=self.display, font=('Courier', 30), justify='right',
                 bg='white', fg='black', relief='sunken', bd=2, state='readonly',
                 readonlybackground='white').place(x=24, y=18, width=692, height=68)
        tk.Label(root, textvariable=self.memory_label, bg=FACE, fg='black',
                 relief='sunken', bd=2, font=('Arial', 20, 'bold')).place(x=24, y=108, width=74, height=62)

        def button(label, x, y, w=48, h=32, color=BLUE, command=None):
            tk.Button(root, text=label, font=('Arial', 19, 'bold'), fg=color, bg=FACE,
                      activebackground='#d4d0c8', activeforeground=color,
                      relief='raised', bd=2, highlightthickness=0,
                      command=command or (lambda k=label: self.press(k))).place(x=x*2, y=y*2, width=w*2, height=h*2)

        button('Backspace', 116, 54, 84, 32, RED)
        button('CE', 208, 54, 68, 32, RED)
        button('C', 284, 54, 74, 32, RED)

        rows = [
            ['7', '8', '9', '/', 'sqrt'],
            ['4', '5', '6', '*', '%'],
            ['1', '2', '3', '-', '1/x'],
            ['0', '+/-', '.', '+', '='],
        ]
        ys = [95, 136, 177, 218]
        xs = [65, 123, 181, 239, 297]
        for r, row in enumerate(rows):
            for c, label in enumerate(row):
                color = RED if label in ('/', '*', '-', '+', '=') else BLUE
                button(label, xs[c], ys[r], 53, 34, color)
        for i, label in enumerate(['MC', 'MR', 'MS', 'M+']):
            button(label, 12, ys[i], 40, 34, RED)

        root.bind('<Key>', self.keypress)
        root.bind('<Control-c>', lambda e: self.copy())
        root.bind('<Control-v>', lambda e: self.paste())

    def value(self):
        return float(self.display.get().replace(',', ''))

    def show(self, value):
        if not math.isfinite(value):
            self.fail()
            return
        if value == 0:
            value = 0.0
        text = format(value, '.12g')
        if 'e' not in text and '.' not in text:
            text += '.'
        self.display.set(text)
        self.error = False

    def fail(self):
        self.display.set('Error')
        self.error = True
        self.pending = None
        self.new_entry = True

    def clear_entry(self):
        self.show(0)
        self.new_entry = True

    def calculate(self):
        if self.pending is None:
            return
        a, b = self.current, self.value()
        try:
            result = {'+': lambda: a + b, '-': lambda: a - b,
                      '*': lambda: a * b, '/': lambda: a / b}[self.pending]()
            self.show(result)
        except (ZeroDivisionError, OverflowError, ValueError):
            self.fail()
        self.pending = None

    def press(self, key):
        if self.error and key not in ('C', 'CE') and not key.isdigit():
            return
        if key.isdigit() or key == '.':
            if self.error:
                self.clear_entry()
            if self.new_entry:
                self.display.set('0.' if key == '.' else key + '.')
                self.new_entry = False
            else:
                text = self.display.get()
                if key == '.':
                    if '.' not in text:
                        self.display.set(text + '.')
                elif len(text.replace('-', '').replace('.', '')) < 15:
                    if text in ('0', '0.'):
                        self.display.set(key + '.')
                    else:
                        self.display.set(text + key)
        elif key == 'Backspace':
            if self.new_entry:
                return
            text = self.display.get()[:-1]
            self.display.set(text if text not in ('', '-') else '0.')
        elif key == 'CE':
            self.clear_entry()
        elif key == 'C':
            self.clear_entry()
            self.pending = None
            self.current = 0.0
        elif key in ('+', '-', '*', '/'):
            if self.pending and not self.new_entry:
                self.calculate()
            if not self.error:
                self.current = self.value()
                self.pending = key
                self.new_entry = True
        elif key == '=':
            if self.pending:
                self.calculate()
                self.new_entry = True
        elif key == '+/-':
            self.show(-self.value())
        elif key in ('sqrt', '1/x', '%'):
            try:
                x = self.value()
                result = math.sqrt(x) if key == 'sqrt' else (1 / x if key == '1/x' else self.current * x / 100)
                self.show(result)
            except (ValueError, ZeroDivisionError, OverflowError):
                self.fail()
        elif key == 'MC':
            self.memory = 0.0
            self.memory_label.set('')
        elif key == 'MR':
            self.show(self.memory)
            self.new_entry = True
        elif key == 'MS':
            self.memory = self.value()
            self.memory_label.set('M')
            self.new_entry = True
        elif key == 'M+':
            self.memory += self.value()
            self.memory_label.set('M')
            self.new_entry = True

    def keypress(self, event):
        key = event.char
        if key in '0123456789.+-*/':
            self.press(key)
        elif key in ('\r', '='):
            self.press('=')
        elif event.keysym == 'BackSpace':
            self.press('Backspace')
        elif event.keysym == 'Escape':
            self.press('C')
        elif event.keysym == 'Delete':
            self.press('CE')

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.display.get())

    def paste(self):
        try:
            value = float(self.root.clipboard_get().strip())
            self.show(value)
            self.new_entry = True
        except (ValueError, tk.TclError):
            pass

if __name__ == '__main__':
    root = tk.Tk()
    Calculator(root)
    root.mainloop()

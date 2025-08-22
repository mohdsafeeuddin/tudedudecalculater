import tkinter as tk
from tkinter import ttk, messagebox
import ast
import operator

# ---------- Safe Evaluator ----------
class SafeEvaluator:
    """Safely evaluate arithmetic expressions using AST."""
    _bin_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    _unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def eval(self, expr):
        try:
            node = ast.parse(expr, mode="eval")
            return self._eval_node(node.body)
        except ZeroDivisionError:
            raise ZeroDivisionError("Division by zero is not allowed.")
        except Exception:
            raise ValueError("Invalid expression")

    def _eval_node(self, node):
        if isinstance(node, ast.BinOp) and type(node.op) in self._bin_ops:
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self._bin_ops[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp) and type(node.op) in self._unary_ops:
            operand = self._eval_node(node.operand)
            return self._unary_ops[type(node.op)](operand)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        else:
            raise ValueError("Unsupported expression")

# ---------- Calculator App ----------
class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Calculator")
        self.geometry("360x480")
        self.minsize(360, 480)
        self.eval_engine = SafeEvaluator()
        self.history = []

        self._build_widgets()
        self._bind_keys()

    def _build_widgets(self):
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # Display
        self.var = tk.StringVar()
        self.entry = ttk.Entry(main, textvariable=self.var, justify="right", font=("Segoe UI", 18))
        self.entry.pack(fill=tk.X, pady=(0, 10))
        self.entry.focus_set()

        # Buttons grid
        grid = ttk.Frame(main)
        grid.pack(fill=tk.BOTH, expand=True)
        for i in range(6):
            grid.rowconfigure(i, weight=1)
        for j in range(4):
            grid.columnconfigure(j, weight=1)

        btn = self._make_button

        # Row 0
        btn(grid, "AC", 0, 0, cmd=self.clear_all)
        btn(grid, "C", 0, 1, cmd=self.clear_entry)
        btn(grid, "⌫", 0, 2, cmd=self.backspace)
        btn(grid, "/", 0, 3)

        # Row 1
        btn(grid, "7", 1, 0)
        btn(grid, "8", 1, 1)
        btn(grid, "9", 1, 2)
        btn(grid, "*", 1, 3)

        # Row 2
        btn(grid, "4", 2, 0)
        btn(grid, "5", 2, 1)
        btn(grid, "6", 2, 2)
        btn(grid, "-", 2, 3)

        # Row 3
        btn(grid, "1", 3, 0)
        btn(grid, "2", 3, 1)
        btn(grid, "3", 3, 2)
        btn(grid, "+", 3, 3)

        # Row 4
        btn(grid, "(", 4, 0)
        btn(grid, "0", 4, 1)
        btn(grid, ")", 4, 2)
        btn(grid, "%", 4, 3)

        # Row 5
        btn(grid, ".", 5, 0)
        btn(grid, "**", 5, 1)
        btn(grid, "=", 5, 2, colspan=2, cmd=self.evaluate)

        # History panel
        hist_frame = ttk.Frame(main)
        hist_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        ttk.Label(hist_frame, text="History (click to reuse)").pack(anchor="w")
        self.history_list = tk.Listbox(hist_frame, height=6)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        self.history_list.bind("<<ListboxSelect>>", self._on_history_select)

    def _make_button(self, parent, text, row, col, colspan=1, cmd=None):
        def on_click():
            if cmd:
                cmd()
            else:
                self.insert(text)
        b = ttk.Button(parent, text=text, command=on_click)
        b.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=4, pady=4)
        return b

    # ---------- Actions ----------
    def insert(self, s):
        self.var.set(self.var.get() + s)

    def clear_all(self):
        self.var.set("")

    def clear_entry(self):
        self.var.set("")

    def backspace(self):
        self.var.set(self.var.get()[:-1])

    def evaluate(self, *_):
        expr = self.var.get().strip()
        if not expr:
            return
        try:
            result = self.eval_engine.eval(expr)
            self._add_history(f"{expr} = {result}")
            self.var.set(str(result))
        except ZeroDivisionError as zde:
            messagebox.showerror("Math Error", str(zde))
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception:
            messagebox.showerror("Error", "Something went wrong.")

    def _add_history(self, item):
        self.history.append(item)
        self.history_list.insert(tk.END, item)
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_list.delete(0)

    def _on_history_select(self, _event):
        if not self.history_list.curselection():
            return
        idx = self.history_list.curselection()[0]
        item = self.history[idx]
        expr = item.split("=")[0].strip()
        self.var.set(expr)
        self.entry.icursor(tk.END)

    # ---------- Keyboard bindings ----------
    def _bind_keys(self):
        for ch in "0123456789.+-*/()%":
            self.bind(f"<KeyPress-{ch}>", self._key_insert)
        self.bind("<Return>", self.evaluate)
        self.bind("<KP_Enter>", self.evaluate)
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<Escape>", lambda e: self.clear_all())

    def _key_insert(self, event):
        self.insert(event.char)

# ---------- Run App ----------
if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()

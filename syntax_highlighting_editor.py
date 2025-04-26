"""
=======================================================================
Python Syntax Highlighting Editor
Author: Yateeka Goyal
Institution: Georgia State University
Email: ygoyal2@student.gsu.edu
Repository: https://github.com/Yateeka/PLC
=======================================================================

Description:
------------
This project implements a standalone syntax highlighting text editor 
using Python's built-in Tkinter library. It is designed to provide 
a lightweight, accessible, and educational alternative to full IDEs, 
focused primarily on Python code development and learning.

Key Features:
-------------
- Real-time syntax highlighting for Python keywords, strings, numbers,
  booleans, collections, operators, and comments using regular expressions.
- Dynamic line numbering synchronized with the text editor’s scrolling.
- Bracket matching functionality that automatically inserts closing brackets.
- Autocomplete suggestions for Python keywords through a floating window.
- Multiple professionally designed themes (Light, Dark, Monokai, Solarized, 
  Dracula, Nord) with dynamic theme switching support.
- Real-time status bar displaying the current cursor position (line, column).
- File operations: Open existing files, save current files in Python (.py) 
  or text formats.
- Built-in keyboard shortcuts for improved user productivity.
- A sample code snippet is preloaded to demonstrate the editor's capabilities.

System Design Overview:
------------------------
- TextEditor Class: Manages the main application window and orchestrates all 
  components including text widget, status bar, line numbers, menus, and themes.
- ScrolledText Widget: The primary text editing area with scroll support.
- LineNumberCanvas: A specialized Text widget displaying dynamic line numbers.
- Syntax Highlighter: Applies regex-based syntax coloring based on Python syntax.
- Autocomplete Module: Handles real-time keyword prediction and insertion.
- Theme Manager: Applies color schemes dynamically to match user preferences.
- Status Bar: Updates cursor location live based on user actions.
- Event Handlers: Manage real-time user inputs, including typing, file I/O, 
  theming, and bracket matching.

Educational Value:
-------------------
This project demonstrates practical applications of:
- GUI programming using Tkinter
- Regular expressions for lexical analysis
- Event-driven architecture
- Object-oriented design principles
- Dynamic user interface management
- Building real-time, interactive Python applications from scratch

Usage Instructions:
--------------------
1. Run the script using a Python 3.x environment.
2. Type or paste Python code into the text editor.
3. Open or save files via the File menu or keyboard shortcuts.
4. Switch themes from the Themes menu or using Ctrl+T.
5. View autocomplete suggestions as you type Python keywords.
6. Observe real-time syntax highlighting, bracket matching, and status updates.

License:
---------
This project is released under an open educational license for learning 
and demonstration purposes. Proper attribution to the author is appreciated.

=======================================================================
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, Toplevel, Listbox
import keyword
import re
import tokenize
from io import BytesIO
import builtins

code = b"def add(x, y): return x + y"
for token in tokenize.tokenize(BytesIO(code).readline):
    print(token)
    
builtins_words = [word for word in dir(builtins) if not word.startswith("__")]

def highlight_builtins(text_widget):
    content = text_widget.get("1.0", "end-1c")
    
    for word in builtins_words:
        for match in re.finditer(rf'\b{re.escape(word)}\b', content):
            start_index = f"1.0 + {match.start()} chars"
            end_index = f"1.0 + {match.end()} chars"
            try:
                text_widget.tag_add("builtins", start_index, end_index)
            except tk.TclError:
                continue  # in case of any weird index errors
            
# ---------- Line Number Widget ----------
class LineNumberCanvas(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            width=4,
            padx=4,
            border=0,
            background="lightgray",
            state="disabled",
            wrap="none",
            takefocus=0,
            **kwargs
        )
        self.text_widget = None

    def attach(self, text_widget):
        self.text_widget = text_widget
        self.text_widget['yscrollcommand'] = self.sync_scroll
        self['yscrollcommand'] = self.sync_scroll
        self.text_widget.bind("<KeyRelease>", lambda e: self.update_line_numbers())
        self.text_widget.bind("<MouseWheel>", lambda e: self._scroll(e.delta))
        self.text_widget.bind("<Button-1>", lambda e: self.after(10, self.update_line_numbers))

    def update_line_numbers(self):
        if not self.text_widget:
            return
        self.config(state="normal")
        self.delete("1.0", tk.END)
        total_lines = int(self.text_widget.index('end-1c').split('.')[0])
        line_numbers = "\n".join(str(i) for i in range(1, total_lines))
        self.insert("1.0", line_numbers)
        self.config(state="disabled")

    def sync_scroll(self, *args):
        self.yview_moveto(args[0])
        if self.text_widget:
            self.text_widget.yview_moveto(args[0])

    def _scroll(self, delta):
        self.text_widget.yview_scroll(int(-1 * (delta / 120)), "units")
        self.yview_scroll(int(-1 * (delta / 120)), "units")
        self.update_line_numbers()

# ---------- Syntax Highlighting ----------
def apply_syntax_highlighting(text_widget):
    text = text_widget.get("1.0", tk.END)

    for tag in ["keyword", "string", "number", "complex", "boolean", "none", "collection", "comment","builtins"]:
        text_widget.tag_remove(tag, "1.0", tk.END)

    text_widget.tag_configure("keyword", foreground="#FF00FF")     # bright magenta
    text_widget.tag_configure("string", foreground="#FFD700")      # bright gold
    text_widget.tag_configure("number", foreground="#7B68EE")      # bright medium purple
    text_widget.tag_configure("complex", foreground="#00FFFF")     # neon cyan
    text_widget.tag_configure("boolean", foreground="#00FF00")     # lime green
    text_widget.tag_configure("none", foreground="#808080")        # medium gray
    text_widget.tag_configure("collection", foreground="#FFA500")  # bright orange
    text_widget.tag_configure("comment", foreground="#888888")     # light gray
    text_widget.tag_configure("builtins", foreground="blue")        # blue


    # Match and tag single-line strings
    for match in re.finditer(r'(\'[^\']*\'|\"[^\"]*\")', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("string", start, end)

    # Match and tag multi-line strings (triple quotes)
    for match in re.finditer(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("string", start, end)

    for word in keyword.kwlist:
        for match in re.finditer(rf'\b{re.escape(word)}\b', text):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            text_widget.tag_add("keyword", start, end)
          

    for match in re.finditer(r'\b\d+(\.\d+)?\b', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("number", start, end)

    for match in re.finditer(r'\b\d+(\.\d+)?[jJ]\b', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("complex", start, end)

    for match in re.finditer(r'\b(True|False)\b', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("boolean", start, end)

    for match in re.finditer(r'\bNone\b', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("none", start, end)

    for match in re.finditer(r'[\[\]\{\}\(\)]', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("collection", start, end)

    for match in re.finditer(r'#.*', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("comment", start, end)
    
    for match in re.finditer(r'[=+\-*/<>!%^&|]', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text_widget.tag_add("operator", start, end)
        text_widget.tag_configure("operator", foreground="#FF69B4")  # hot pink



# ---------- Editor App ----------
class TextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Syntax Highlighting Editor")
        self.geometry("900x600")
        self.theme_mode = tk.StringVar(value="Light")

        # ---------- Theme Setup ----------
        self.themes = {
            "Light": {
                "bg": "white",
                "fg": "black",
                "insert": "black",
                "line_bg": "lightgray",
                "line_fg": "black"
            },
            "Dark": {
                "bg": "#1e1e1e",
                "fg": "#d4d4d4",
                "insert": "#d4d4d4",
                "line_bg": "#2d2d2d",
                "line_fg": "#d4d4d4"
            },
            "Monokai": {
                "bg": "#272822",
                "fg": "#f8f8f2",
                "insert": "#f8f8f2",
                "line_bg": "#3e3d32",
                "line_fg": "#f8f8f2"
            },
            "Solarized Light": {
                "bg": "#fdf6e3",
                "fg": "#657b83",
                "insert": "#657b83",
                "line_bg": "#eee8d5",
                "line_fg": "#657b83"
            },
            "Solarized Dark": {
                "bg": "#002b36",
                "fg": "#839496",
                "insert": "#93a1a1",
                "line_bg": "#073642",
                "line_fg": "#839496"
            },
            
            "Dracula": {
            "bg": "#282A36",
            "fg": "#F8F8F2",
            "insert": "#F8F8F2",
            "line_bg": "#44475A",
            "line_fg": "#F8F8F2"
        },
        "Nord": {
            "bg": "#2E3440",
            "fg": "#D8DEE9",
            "insert": "#D8DEE9",
            "line_bg": "#3B4252",
            "line_fg": "#D8DEE9"
        }
        }
        # ---------- Layout ----------
        self.text_frame = tk.Frame(self)
        self.text_frame.pack(fill="both", expand=True)

        self.line_numbers = LineNumberCanvas(self.text_frame)
        self.line_numbers.pack(side="left", fill="y")

        self.text_area = scrolledtext.ScrolledText(
            self.text_frame,
            wrap="word",
            undo=True,
            font=("Courier New", 12),
            bg="white",
            fg="black",
            insertbackground="black"
        )
        self.text_area.pack(side="right", fill="both", expand=True)
        self.line_numbers.attach(self.text_area)

        # ---------- Bindings ----------
        self.text_area.bind("<KeyRelease>", self.on_text_change, add="+")
        self.text_area.bind("<KeyRelease>", self.update_status_bar, add="+")
        self.text_area.bind("<KeyRelease>", self.handle_autocomplete, add="+")
        self.text_area.bind("<Control-z>", lambda e: self.text_area.edit_undo())
        self.text_area.bind("<Control-y>", lambda e: self.text_area.edit_redo())
        self.text_area.bind("<Control-s>", lambda e: self.save_file())
        self.text_area.bind("<Control-o>", lambda e: self.open_file())
        self.text_area.bind("<Control-t>", lambda e: self.toggle_theme())
        self.text_area.bind("<KeyPress>", self.bracket_match)
        self.text_area.bind("<Button-1>", self.update_status_bar)

        # ---------- Status Bar ----------
        self.status_bar = tk.Label(self, text="Line 1, Col 0", anchor="w", bg="#eeeeee", font=("Arial", 9))
        self.status_bar.pack(fill="x", side="bottom")
        self.after_idle(lambda: self.update_status_bar())

        # ---------- Menus ----------
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save As", command=self.save_file)
        menu.add_cascade(label="File", menu=file_menu)

        theme_menu = tk.Menu(menu, tearoff=0)
        for theme_name in self.themes:
            theme_menu.add_command(label=theme_name, command=lambda name=theme_name: self.apply_theme(name))
        menu.add_cascade(label="Themes", menu=theme_menu)

        self.config(menu=menu)

        self.autocomplete_window = None
        self.autocomplete_listbox = None

        # Load default theme and code
        self.apply_theme("Light")
        self.insert_sample_code()
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        menu.add_cascade(label="Help", menu=help_menu)
    def show_shortcuts(self):
        shortcut_text = (
            "🧠 Keyboard Shortcuts:\n\n"
            "Ctrl + O   - Open File\n"
            "Ctrl + S   - Save File\n"
            "Ctrl + Z   - Undo\n"
            "Ctrl + Y   - Redo\n"
            "Ctrl + T   - Toggle Theme (Light/Dark)\n"
            "\n"
            "Autocomplete: Start typing a Python keyword\n"
            "Bracket Match: Automatically inserts matching bracket\n"
            "Line Numbers, Syntax Highlighting, and Status Bar are always active.\n"
        )
        messagebox.showinfo("Keyboard Shortcuts", shortcut_text)

    def apply_theme(self, theme_name):
        theme = self.themes.get(theme_name)
        if not theme:
            return
        self.text_area.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["insert"])
        self.line_numbers.config(bg=theme["line_bg"], fg=theme["line_fg"])
        self.theme_mode.set(theme_name)

    def toggle_theme(self):
        next_theme = "Dark" if self.theme_mode.get() == "Light" else "Light"
        self.apply_theme(next_theme)

    def handle_autocomplete(self, event):
        if event.keysym in ["BackSpace", "Return", "space"]:
            self.close_autocomplete()
            return

        cursor = self.text_area.index(tk.INSERT)
        line_start = f"{cursor.split('.')[0]}.0"
        line_text = self.text_area.get(line_start, cursor)
        word = re.findall(r"[\w_]+$", line_text)
        prefix = word[0] if word else ""

        if len(prefix) < 2:
            self.close_autocomplete()
            return

        matches = [kw for kw in keyword.kwlist if kw.startswith(prefix)]
        if not matches:
            self.close_autocomplete()
            return

        if self.autocomplete_window:
            self.autocomplete_listbox.delete(0, tk.END)
        else:
            self.show_autocomplete()

        for kw in matches:
            self.autocomplete_listbox.insert(tk.END, kw)

        x, y, _, _ = self.text_area.bbox(tk.INSERT)
        abs_x = self.text_area.winfo_rootx() + x
        abs_y = self.text_area.winfo_rooty() + y + 20
        self.autocomplete_window.geometry(f"+{abs_x}+{abs_y}")
        self.autocomplete_window.deiconify()

        # ✅ Reapply highlighting after all autocomplete changes are processed
        self.after_idle(lambda: apply_syntax_highlighting(self.text_area))

    def show_autocomplete(self):
        self.autocomplete_window = Toplevel(self)
        self.autocomplete_window.wm_overrideredirect(True)
        self.autocomplete_window.attributes("-topmost", True)
        self.autocomplete_listbox = Listbox(self.autocomplete_window, font=("Courier New", 10))
        self.autocomplete_listbox.pack()
        self.autocomplete_listbox.bind("<Return>", self.insert_autocomplete)
        self.autocomplete_listbox.bind("<Tab>", self.insert_autocomplete)
        self.autocomplete_listbox.bind("<Button-1>", self.insert_autocomplete)

    def insert_autocomplete(self, event):
        if not self.autocomplete_listbox:
            return
        selected = self.autocomplete_listbox.get(tk.ACTIVE)
        cursor = self.text_area.index(tk.INSERT)
        line_start = f"{cursor.split('.')[0]}.0"
        line_text = self.text_area.get(line_start, cursor)
        prefix = re.findall(r"[\w_]+$", line_text)
        if prefix:
            self.text_area.delete(f"{cursor} - {len(prefix[0])}c", cursor)
        self.text_area.insert(tk.INSERT, selected)
        self.close_autocomplete()
        return "break"

    def close_autocomplete(self):
        if self.autocomplete_window:
            self.autocomplete_window.withdraw()

    def bracket_match(self, event):
        brackets = {'(': ')', '[': ']', '{': '}'}
        if event.char in brackets:
            self.text_area.insert(tk.INSERT, brackets[event.char])
            self.text_area.mark_set(tk.INSERT, f"{self.text_area.index(tk.INSERT)}-1c")
            self.after_idle(lambda: apply_syntax_highlighting(self.text_area))

    def update_status_bar(self, event=None):
        try:
            pos = self.text_area.index(tk.INSERT)
            line, col = pos.split(".")
            self.status_bar.config(text=f"Line {int(line)}, Col {int(col)}")
        except Exception:
            pass

    def on_text_change(self, event=None):
        self.after_idle(lambda: apply_syntax_highlighting(self.text_area))
        self.after_idle(lambda: highlight_builtins(self.text_area))
        self.after_idle(lambda: self.line_numbers.update_line_numbers())


    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if filepath:
            with open(filepath, "r") as file:
                content = file.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, content)
            self.on_text_change()
            self.title(f"Syntax Highlighting Editor - {filepath}")

    def save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if filepath:
            try:
                with open(filepath, "w") as file:
                    content = self.text_area.get("1.0", tk.END)
                    file.write(content)
                messagebox.showinfo("Saved", "File saved successfully.")
                self.title(f"Syntax Highlighting Editor - {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

    def insert_sample_code(self):
        sample = '''# This is a comment showing how syntax highlighting works

        # --- Single & Triple-quoted Strings ---
        message = "Hello, World!"
        quote = 'Python is fun'
        multi = """This is
        a multi-line
        string example"""

        # --- Variables ---
        name = "Yateeka"
        age = 21
        pi = 3.14
        z = 2 + 4j
        is_admin = True
        status = None
        scores = [85, 92, 78]
        profile = {"user": name, "active": is_admin}

        # --- Function ---
        def greet(user):
            if user == name:
                return "Hello, " + user + "!"
            else:
                return "Access Denied"

        # --- Loop & F-Strings ---
        for i in range(3):
            print(f"Score {i+1}: {scores[i]}")

        # --- Collections & Brackets ---
        empty_list = []
        empty_dict = {}
        empty_tuple = ()
        bracket_example = ( [ { (1+2j) } ] )

        # --- Boolean Logic & None ---
        if True and not False:
            print("Logic works!")

        if status is None:
            print("No status available")
        '''
        self.text_area.insert("1.0", sample)
        self.on_text_change()


# ---------- Run ----------
if __name__ == "__main__":
    editor = TextEditor()
    editor.mainloop()

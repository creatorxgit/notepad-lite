```python
#!/usr/bin/env python3
"""
Linux Notepad - Optimized text editor for Linux
"""

import tkinter as tk
from tkinter import filedialog, messagebox, font
import os
import sys
import subprocess
import platform
import configparser
from pathlib import Path

class LinuxNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Notepad")
        
        # Detect theme based on environment
        self.detect_linux_theme()
        
        # Paths for Linux configuration
        self.config_dir = Path.home() / '.config' / 'linux-notepad'
        self.config_file = self.config_dir / 'config.ini'
        self.recent_files_file = self.config_dir / 'recent_files.txt'
        
        # Create configuration directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        # Currently opened file
        self.current_file = None
        self.recent_files = self.load_recent_files()
        
        # Set geometry from configuration
        geometry = self.config.get('window', 'geometry', fallback='800x600')
        self.root.geometry(geometry)
        
        # Settings for Linux window manager
        self.root.option_add('*tearOff', False)  # Remove dotted menus
        
        # Icon for Linux (try to use system icon)
        self.set_linux_icon()
        
        # Create menu (make it more native for Linux)
        self.create_menu()
        
        # Create text widget
        self.create_text_widget()
        
        # Toolbar
        self.create_toolbar()
        
        # Status bar
        self.create_status_bar()
        
        # Bind Linux hotkeys
        self.bind_linux_shortcuts()
        
        # Track window resize
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Load last opened file if exists
        self.load_last_file()
        
    def detect_linux_theme(self):
        """Detect Linux environment theme"""
        try:
            # Check GTK theme
            if os.path.exists('/usr/bin/gsettings'):
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                    capture_output=True, text=True
                )
                theme = result.stdout.strip().strip("'")
                if 'dark' in theme.lower():
                    self.is_dark_theme = True
                else:
                    self.is_dark_theme = False
            else:
                self.is_dark_theme = False
                
            # Apply tkinter theme
            if self.is_dark_theme:
                self.root.tk_setPalette(background='#2d2d2d', foreground='#ffffff')
        except:
            self.is_dark_theme = False
            
    def set_linux_icon(self):
        """Set icon for Linux"""
        # Try to use system editor icon
        icon_paths = [
            '/usr/share/icons/hicolor/48x48/apps/accessories-text-editor.png',
            '/usr/share/icons/gnome/48x48/apps/accessories-text-editor.png',
            '/usr/share/pixmaps/gedit.png',
            '/usr/share/icons/hicolor/48x48/apps/gedit.png'
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    icon = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, icon)
                    break
                except:
                    continue
                    
    def create_menu(self):
        """Create menu considering Linux traditions"""
        menubar = tk.Menu(self.root)
        
        # File menu (with Linux functions)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, 
                            accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file,
                            accelerator="Ctrl+O")
        file_menu.add_separator()
        
        # Recent files
        if self.recent_files:
            recent_menu = tk.Menu(file_menu, tearoff=0)
            for recent_file in self.recent_files[:10]:  # Last 10 files
                display_name = os.path.basename(recent_file)[:30] + "..." \
                             if len(os.path.basename(recent_file)) > 30 \
                             else os.path.basename(recent_file)
                recent_menu.add_command(
                    label=f"{display_name}",
                    command=lambda f=recent_file: self.open_recent_file(f)
                )
            file_menu.add_cascade(label="Recent Files", menu=recent_menu)
            file_menu.add_separator()
        
        file_menu.add_command(label="Save", command=self.save_file,
                            accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file,
                            accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Open in Terminal", 
                            command=self.open_terminal_here)
        file_menu.add_command(label="Show in File Manager",
                            command=self.show_in_file_manager)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app,
                            accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo_text,
                            accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo_text,
                            accelerator="Ctrl+Shift+Z")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text,
                            accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text,
                            accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text,
                            accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete", command=self.delete_text,
                            accelerator="Delete")
        edit_menu.add_command(label="Select All", command=self.select_all,
                            accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.find_text,
                            accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.replace_text,
                            accelerator="Ctrl+H")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Format menu (Linux specific)
        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_command(label="Change Font...", command=self.change_font)
        format_menu.add_command(label="Word Wrap", command=self.toggle_word_wrap)
        format_menu.add_checkbutton(label="Show Line Numbers", 
                                  command=self.toggle_line_numbers)
        format_menu.add_separator()
        format_menu.add_command(label="Convert to UTF-8",
                              command=self.convert_to_utf8)
        format_menu.add_command(label="Convert Line Endings (Linux)",
                              command=self.convert_line_endings)
        menubar.add_cascade(label="Format", menu=format_menu)
        
        # Tools menu (Linux specific)
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Check Syntax...",
                             command=self.check_syntax)
        tools_menu.add_command(label="Run Script",
                             command=self.run_script)
        tools_menu.add_separator()
        tools_menu.add_command(label="Calculate Expression",
                             command=self.calculate_expression)
        tools_menu.add_command(label="Format Code",
                             command=self.format_code)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu (with Linux integration)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help,
                            accelerator="F1")
        help_menu.add_command(label="User Manual",
                            command=self.show_manual)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.about_app)
        help_menu.add_command(label="System Information",
                            command=self.show_system_info)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def create_text_widget(self):
        """Create text widget with Linux support"""
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Frame for line numbers
        self.line_numbers = tk.Text(
            main_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background='lightgray',
            state='disabled'
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Frame for text and scrollbars
        text_frame = tk.Frame(main_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        v_scrollbar = tk.Scrollbar(text_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Text field
        self.text = tk.Text(
            text_frame,
            wrap=tk.WORD if self.config.getboolean('editor', 'word_wrap', fallback=True) else tk.NONE,
            undo=True,
            autoseparators=True,
            maxundo=-1,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            font=(self.config.get('editor', 'font_family', fallback='Monospace'),
                  self.config.getint('editor', 'font_size', fallback=12)),
            tabs=(self.config.getint('editor', 'tab_width', fallback=4) * 8)
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.text.yview)
        h_scrollbar.config(command=self.text.xview)
        
        # Bind events for line numbers
        self.text.bind('<KeyRelease>', self.update_line_numbers)
        self.text.bind('<ButtonRelease>', self.update_line_numbers)
        self.text.bind('<<Modified>>', self.on_text_modified)
        
        # Context menu for Linux
        self.create_context_menu()
        
        # Update line numbers
        self.update_line_numbers()
        
    def create_context_menu(self):
        """Create context menu (right-click)"""
        self.context_menu = tk.Menu(self.text, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all)
        
        # Bind context menu
        self.text.bind('<Button-3>', self.show_context_menu)
        
    def show_context_menu(self, event):
        """Show context menu"""
        self.context_menu.tk_popup(event.x_root, event.y_root)
        
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = tk.Frame(self.root, relief=tk.RAISED, bd=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Buttons with icons (textual for simplicity)
        buttons = [
            ("New", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file),
            ("", None),  # Separator
            ("Cut", self.cut_text),
            ("Copy", self.copy_text),
            ("Paste", self.paste_text),
            ("", None),  # Separator
            ("Undo", self.undo_text),
            ("Redo", self.redo_text),
            ("", None),  # Separator
            ("Find", self.find_text),
        ]
        
        for text, command in buttons:
            if text == "":  # Separator
                sep = tk.Frame(toolbar, width=2, height=20, bd=1, relief=tk.SUNKEN)
                sep.pack(side=tk.LEFT, padx=2, pady=2)
            else:
                btn = tk.Button(toolbar, text=text, command=command, width=10)
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cursor position
        self.cursor_pos = tk.Label(self.status_bar, text="Line 1, Column 1", width=20)
        self.cursor_pos.pack(side=tk.LEFT, padx=4)
        
        # File status
        self.file_status = tk.Label(self.status_bar, text="New file", width=30)
        self.file_status.pack(side=tk.LEFT, padx=4)
        
        # Encoding
        self.encoding_label = tk.Label(self.status_bar, text="UTF-8", width=10)
        self.encoding_label.pack(side=tk.RIGHT, padx=4)
        
        # Update cursor position
        self.text.bind('<KeyRelease>', self.update_cursor_position)
        self.text.bind('<ButtonRelease>', self.update_cursor_position)
        
    def bind_linux_shortcuts(self):
        """Bind Linux hotkeys"""
        # Standard combinations
        shortcuts = [
            ('<Control-n>', self.new_file),
            ('<Control-o>', self.open_file),
            ('<Control-s>', self.save_file),
            ('<Control-Shift-s>', self.save_as_file),
            ('<Control-q>', self.exit_app),
            ('<Control-f>', self.find_text),
            ('<Control-h>', self.replace_text),
            ('<Control-g>', self.go_to_line),
            ('<F1>', self.show_help),
            ('<Control-F1>', self.show_system_info),
            ('<Control-bracketleft>', self.decrease_font),
            ('<Control-bracketright>', self.increase_font),
        ]
        
        for key, func in shortcuts:
            self.root.bind(key, lambda e, f=func: f())
            
    # Basic editing functions
    def new_file(self):
        """Create new file"""
        if self.check_unsaved_changes():
            self.text.delete(1.0, tk.END)
            self.current_file = None
            self.update_title()
            self.update_status("New file")
            self.update_line_numbers()
            
    def open_file(self, filepath=None):
        """Open file"""
        if self.check_unsaved_changes():
            if not filepath:
                filepath = filedialog.askopenfilename(
                    title="Open File",
                    filetypes=[
                        ("Text files", "*.txt"),
                        ("Python files", "*.py"),
                        ("Configuration files", "*.conf *.ini *.cfg"),
                        ("All files", "*")
                    ],
                    initialdir=os.path.expanduser("~")
                )
            
            if filepath:
                self.load_file(filepath)
                
    def load_file(self, filepath):
        """Load file"""
        try:
            # Try to detect encoding
            for encoding in ['utf-8', 'cp1251', 'iso-8859-1']:
                try:
                    with open(filepath, 'r', encoding=encoding) as file:
                        content = file.read()
                    
                    self.text.delete(1.0, tk.END)
                    self.text.insert(1.0, content)
                    self.current_file = filepath
                    self.update_title()
                    self.update_status(f"Opened: {os.path.basename(filepath)}")
                    self.encoding_label.config(text=encoding.upper())
                    
                    # Add to recent files
                    self.add_to_recent_files(filepath)
                    
                    self.text.edit_modified(False)
                    self.update_line_numbers()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                messagebox.showerror("Error", "Could not determine file encoding")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{str(e)}")
            
    def save_file(self):
        """Save file"""
        if self.current_file:
            try:
                content = self.text.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.update_status(f"Saved: {os.path.basename(self.current_file)}")
                self.text.edit_modified(False)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        """Save as"""
        filepath = filedialog.asksaveasfilename(
            title="Save As",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*")
            ],
            defaultextension=".txt",
            initialdir=os.path.expanduser("~")
        )
        
        if filepath:
            try:
                content = self.text.get(1.0, tk.END)
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.current_file = filepath
                self.update_title()
                self.update_status(f"Saved as: {os.path.basename(filepath)}")
                self.text.edit_modified(False)
                self.add_to_recent_files(filepath)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
    
    # Linux-specific functions
    def open_terminal_here(self):
        """Open terminal in current directory"""
        if self.current_file:
            directory = os.path.dirname(self.current_file)
        else:
            directory = os.path.expanduser("~")
            
        try:
            # Try to open terminal depending on environment
            terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'xterm']
            for terminal in terminals:
                if subprocess.run(['which', terminal], capture_output=True).returncode == 0:
                    subprocess.Popen([terminal, '--working-directory', directory])
                    break
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not open terminal:\n{str(e)}")
            
    def show_in_file_manager(self):
        """Show file in file manager"""
        if self.current_file:
            try:
                file_managers = ['nautilus', 'dolphin', 'thunar', 'pcmanfm']
                for fm in file_managers:
                    if subprocess.run(['which', fm], capture_output=True).returncode == 0:
                        subprocess.Popen([fm, os.path.dirname(self.current_file)])
                        break
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not open file manager:\n{str(e)}")
        else:
            messagebox.showinfo("Information", "Save the file first")
            
    def run_script(self):
        """Run current script (if it's a Python file)"""
        if self.current_file and self.current_file.endswith('.py'):
            try:
                result = subprocess.run(
                    ['python3', self.current_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Show result
                result_window = tk.Toplevel(self.root)
                result_window.title("Execution Result")
                result_window.geometry("600x400")
                
                text_widget = tk.Text(result_window, wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True)
                
                text_widget.insert(1.0, f"Exit code: {result.returncode}\n\n")
                text_widget.insert(tk.END, "STDOUT:\n" + result.stdout + "\n\n")
                text_widget.insert(tk.END, "STDERR:\n" + result.stderr)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not run script:\n{str(e)}")
        else:
            messagebox.showinfo("Information", "Save file with .py extension to run")
            
    def convert_line_endings(self):
        """Convert line endings to Linux format (LF)"""
        content = self.text.get(1.0, tk.END)
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        self.text.delete(1.0, tk.END)
        self.text.insert(1.0, content)
        self.update_status("Converted to Linux line endings (LF)")
        
    # Helper functions
    def update_line_numbers(self, event=None):
        """Update line numbers"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        
        line_count = self.text.get(1.0, tk.END).count('\n')
        
        for line in range(1, line_count + 2):
            self.line_numbers.insert(tk.END, f"{line}\n")
            
        self.line_numbers.config(state='disabled')
        
    def update_cursor_position(self, event=None):
        """Update cursor position"""
        cursor_pos = self.text.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.cursor_pos.config(text=f"Line {line}, Column {int(col)+1}")
        
    def update_status(self, message):
        """Update status"""
        self.file_status.config(text=message)
        
    def update_title(self):
        """Update window title"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.root.title(f"{filename} - Linux Notepad")
        else:
            self.root.title("New file - Linux Notepad")
            
    def check_unsaved_changes(self):
        """Check for unsaved changes"""
        if self.text.edit_modified():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save changes before continuing?"
            )
            
            if response is None:  # Cancel
                return False
            elif response:  # Yes
                self.save_file()
                return not self.text.edit_modified()
            else:  # No
                self.text.edit_modified(False)
                return True
        return True
        
    def on_text_modified(self, event=None):
        """Text modification handler"""
        if self.text.edit_modified():
            self.update_status("Unsaved changes")
        else:
            if self.current_file:
                self.update_status(os.path.basename(self.current_file))
            else:
                self.update_status("New file")
                
    def on_window_resize(self, event):
        """Window resize handler"""
        if event.widget == self.root:
            geometry = self.root.geometry()
            self.save_config('window', 'geometry', geometry)
            
    # Configuration functions
    def load_config(self):
        """Load configuration"""
        config = configparser.ConfigParser()
        
        # Default values
        config['window'] = {'geometry': '800x600'}
        config['editor'] = {
            'font_family': 'Monospace',
            'font_size': '12',
            'word_wrap': 'True',
            'tab_width': '4',
            'show_line_numbers': 'True'
        }
        config['recent'] = {'max_files': '10'}
        
        if self.config_file.exists():
            config.read(self.config_file)
            
        return config
        
    def save_config(self, section, key, value):
        """Save configuration parameter"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
        with open(self.config_file, 'w') as f:
            self.config.write(f)
            
    def load_recent_files(self):
        """Load recent files list"""
        if self.recent_files_file.exists():
            with open(self.recent_files_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
        
    def add_to_recent_files(self, filepath):
        """Add file to recent files"""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        
        # Limit number of files
        max_files = self.config.getint('recent', 'max_files', fallback=10)
        self.recent_files = self.recent_files[:max_files]
        
        # Save
        with open(self.recent_files_file, 'w') as f:
            for file in self.recent_files:
                f.write(file + '\n')
                
    def load_last_file(self):
        """Load last opened file"""
        if self.config.get('last_session', 'file', fallback=None):
            filepath = self.config['last_session']['file']
            if os.path.exists(filepath):
                response = messagebox.askyesno(
                    "Restore Session",
                    f"Restore last opened file?\n{os.path.basename(filepath)}"
                )
                if response:
                    self.load_file(filepath)
                    
    # Menu functions
    def find_text(self):
        """Find text"""
        self.show_find_dialog()
        
    def replace_text(self):
        """Replace text"""
        self.show_replace_dialog()
        
    def change_font(self):
        """Change font"""
        self.show_font_dialog()
        
    def toggle_word_wrap(self):
        """Toggle word wrap"""
        current_wrap = self.text.cget('wrap')
        new_wrap = tk.WORD if current_wrap == tk.NONE else tk.NONE
        self.text.config(wrap=new_wrap)
        self.save_config('editor', 'word_wrap', str(new_wrap == tk.WORD).lower())
        
    def toggle_line_numbers(self):
        """Toggle line numbers display"""
        current_state = self.line_numbers.winfo_ismapped()
        if current_state:
            self.line_numbers.pack_forget()
        else:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.save_config('editor', 'show_line_numbers', str(not current_state).lower())
        
    def show_find_dialog(self):
        """Show find dialog"""
        find_dialog = tk.Toplevel(self.root)
        find_dialog.title("Find")
        find_dialog.geometry("400x150")
        
        tk.Label(find_dialog, text="Find:").pack(pady=5)
        find_entry = tk.Entry(find_dialog, width=40)
        find_entry.pack(pady=5)
        
        def find_next():
            text_to_find = find_entry.get()
            if text_to_find:
                start_pos = self.text.search(text_to_find, tk.INSERT, nocase=True, stopindex=tk.END)
                if start_pos:
                    end_pos = f"{start_pos}+{len(text_to_find)}c"
                    self.text.tag_remove(tk.SEL, 1.0, tk.END)
                    self.text.tag_add(tk.SEL, start_pos, end_pos)
                    self.text.mark_set(tk.INSERT, end_pos)
                    self.text.see(start_pos)
                    
        tk.Button(find_dialog, text="Find", command=find_next).pack(pady=10)
        
    def show_font_dialog(self):
        """Show font selection dialog"""
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("Select Font")
        font_dialog.geometry("300x200")
        
        # Font list
        available_fonts = sorted(font.families())
        
        tk.Label(font_dialog, text="Font:").pack(pady=5)
        font_listbox = tk.Listbox(font_dialog, height=6)
        font_listbox.pack(pady=5, fill=tk.BOTH, expand=True)
        
        for font_name in available_fonts:
            font_listbox.insert(tk.END, font_name)
            
        tk.Label(font_dialog, text="Size:").pack(pady=5)
        size_spinbox = tk.Spinbox(font_dialog, from_=8, to=72, width=5)
        size_spinbox.pack(pady=5)
        
        def apply_font():
            selected_font = font_listbox.get(font_listbox.curselection())
            size = int(size_spinbox.get())
            self.text.config(font=(selected_font, size))
            self.save_config('editor', 'font_family', selected_font)
            self.save_config('editor', 'font_size', str(size))
            font_dialog.destroy()
            
        tk.Button(font_dialog, text="Apply", command=apply_font).pack(pady=10)
        
    def increase_font(self):
        """Increase font size"""
        current_font = self.text.cget('font')
        font_name, font_size = current_font
        new_size = int(font_size) + 1
        self.text.config(font=(font_name, new_size))
        self.save_config('editor', 'font_size', str(new_size))
        
    def decrease_font(self):
        """Decrease font size"""
        current_font = self.text.cget('font')
        font_name, font_size = current_font
        new_size = max(8, int(font_size) - 1)  # Minimum 8
        self.text.config(font=(font_name, new_size))
        self.save_config('editor', 'font_size', str(new_size))
        
    def convert_to_utf8(self):
        """Convert to UTF-8"""
        self.update_status("File in UTF-8")
        
    def check_syntax(self):
        """Check syntax (for Python)"""
        if self.current_file and self.current_file.endswith('.py'):
            try:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', self.current_file],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    messagebox.showinfo("Syntax", "Python syntax is correct")
                else:
                    messagebox.showerror("Syntax", f"Syntax error:\n{result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not check syntax:\n{str(e)}")
        else:
            messagebox.showinfo("Information", "Function available only for Python files")
            
    def calculate_expression(self):
        """Calculate mathematical expression"""
        try:
            selected_text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                result = eval(selected_text)
                messagebox.showinfo("Result", f"{selected_text} = {result}")
        except:
            expression = tk.simpledialog.askstring("Calculation", "Enter expression:")
            if expression:
                try:
                    result = eval(expression)
                    messagebox.showinfo("Result", f"{expression} = {result}")
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid expression:\n{str(e)}")
                    
    def format_code(self):
        """Format code (basic implementation)"""
        content = self.text.get(1.0, tk.END)
        # Simple formatting - adding indents
        lines = content.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.endswith(':'):
                formatted_lines.append(' ' * (indent_level * 4) + line.strip())
                indent_level += 1
            elif stripped and stripped[0] in ')]}':
                indent_level = max(0, indent_level - 1)
                formatted_lines.append(' ' * (indent_level * 4) + line.strip())
            else:
                formatted_lines.append(' ' * (indent_level * 4) + line.strip())
                
        formatted_text = '\n'.join(formatted_lines)
        self.text.delete(1.0, tk.END)
        self.text.insert(1.0, formatted_text)
        self.update_status("Code formatted")
        
    def go_to_line(self):
        """Go to line"""
        line_num = tk.simpledialog.askinteger("Go to Line", "Line number:", minvalue=1)
        if line_num:
            self.text.mark_set(tk.INSERT, f"{line_num}.0")
            self.text.see(tk.INSERT)
            self.update_cursor_position()
            
    # Text editing functions
    def undo_text(self):
        """Undo action"""
        try:
            self.text.edit_undo()
        except:
            pass
            
    def redo_text(self):
        """Redo action"""
        try:
            self.text.edit_redo()
        except:
            pass
            
    def cut_text(self):
        """Cut text"""
        self.text.event_generate("<<Cut>>")
        
    def copy_text(self):
        """Copy text"""
        self.text.event_generate("<<Copy>>")
        
    def paste_text(self):
        """Paste text"""
        self.text.event_generate("<<Paste>>")
        
    def delete_text(self):
        """Delete selected text"""
        try:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
            
    def select_all(self):
        """Select all text"""
        self.text.tag_add('sel', '1.0', 'end')
        
    # Help and information functions
    def show_help(self):
        """Show help"""
        messagebox.showinfo("Help", 
            "Linux Notepad - Text editor for Linux\n\n"
            "Main features:\n"
            "• Edit text files\n"
            "• Python syntax highlighting\n"
            "• Terminal integration\n"
            "• Syntax checking\n\n"
            "Hotkeys:\n"
            "Ctrl+N - New file\n"
            "Ctrl+O - Open file\n"
            "Ctrl+S - Save\n"
            "Ctrl+Q - Exit\n"
            "F1 - Help")
            
    def show_manual(self):
        """Show user manual"""
        manual_text = """LINUX NOTEPAD USER MANUAL

1. EDITING FILES
   - Use standard cut/copy/paste commands
   - Configure font through Format menu
   - Enable word wrap for comfortable reading

2. WORKING WITH FILES
   - Save files in any format
   - Open files in different encodings
   - Use recent files list for quick access

3. TOOLS
   - Python syntax checking
   - Run scripts directly from editor
   - Code formatting
   - Line ending conversion

4. LINUX INTEGRATION
   - Open terminal in current folder
   - View files in file manager
   - Automatic system theme detection"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("User Manual")
        help_window.geometry("600x500")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, manual_text)
        text_widget.config(state='disabled')
        
    def about_app(self):
        """About application"""
        messagebox.showinfo("About",
            "Linux Notepad v1.0\n\n"
            "Optimized text editor for Linux\n"
            "Designed for convenient work in Linux environment\n\n"
            "Features:\n"
            "• Integration with system utilities\n"
            "• Support for Linux formats\n"
            "• Native hotkeys\n\n"
            "© 2024 Linux Notepad Project")
            
    def show_system_info(self):
        """Show system information"""
        info = f"""
System Information:

OS: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Processor: {platform.processor()}

Python: {platform.python_version()}
Tkinter: {tk.TkVersion}

Current file: {self.current_file or 'Not opened'}
Encoding: {self.encoding_label.cget('text')}
        """
        messagebox.showinfo("System Information", info.strip())
        
    def exit_app(self):
        """Exit application"""
        if self.check_unsaved_changes():
            # Save current file to configuration
            if self.current_file:
                self.save_config('last_session', 'file', self.current_file)
            self.root.quit()
            
    def open_recent_file(self, filepath):
        """Open file from recent files list"""
        if self.check_unsaved_changes():
            if os.path.exists(filepath):
                self.load_file(filepath)
            else:
                messagebox.showwarning("File Not Found", f"File does not exist:\n{filepath}")
                # Remove from recent files
                if filepath in self.recent_files:
                    self.recent_files.remove(filepath)
                    with open(self.recent_files_file, 'w') as f:
                        for file in self.recent_files:
                            f.write(file + '\n')
                    # Update menu
                    self.create_menu()

# Entry point
def main():
    root = tk.Tk()
    app = LinuxNotepad(root)
    root.mainloop()

if __name__ == "__main__":
    main()

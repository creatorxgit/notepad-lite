import tkinter as tk
from tkinter import filedialog, messagebox
import os

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notepad")
        self.root.geometry("800x600")
        
        # Currently opened file
        self.current_file = None
        
        # Create menu
        self.create_menu()
        
        # Create text widget
        self.create_text_widget()
        
        # Add status bar
        self.status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind event handlers
        self.text.bind("<<Modified>>", self.on_text_modified)
        
    def create_menu(self):
        """Create program menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo_text, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo_text, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.about_app)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Hotkeys
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as_file())  # Ctrl+Shift+S
        self.root.bind('<Control-a>', lambda e: self.select_all())
        
    def create_text_widget(self):
        """Create text widget with scrollbars"""
        # Frame for text widget and scrollbars
        text_frame = tk.Frame(self.root)
        text_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Vertical scrollbar
        scrollbar_y = tk.Scrollbar(text_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        scrollbar_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Text widget
        self.text = tk.Text(
            text_frame,
            wrap=tk.NONE,  # Disable word wrap for horizontal scrolling
            undo=True,      # Enable undo functionality
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            font=("Arial", 12)
        )
        self.text.pack(expand=True, fill=tk.BOTH)
        
        # Configure scrollbars
        scrollbar_y.config(command=self.text.yview)
        scrollbar_x.config(command=self.text.xview)
        
    def new_file(self):
        """Create a new file"""
        if self.check_unsaved_changes():
            self.text.delete(1.0, tk.END)
            self.current_file = None
            self.update_title()
            self.update_status("New file created")
            
    def open_file(self):
        """Open file through file dialog"""
        if self.check_unsaved_changes():
            file_path = filedialog.askopenfilename(
                title="Open File",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                defaultextension=".txt"
            )
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    
                    self.text.delete(1.0, tk.END)
                    self.text.insert(1.0, content)
                    self.current_file = file_path
                    self.update_title()
                    self.update_status(f"Opened file: {os.path.basename(file_path)}")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
                    
    def save_file(self):
        """Save file"""
        if self.current_file:
            try:
                content = self.text.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.update_status(f"File saved: {os.path.basename(self.current_file)}")
                self.text.edit_modified(False)  # Reset modified flag
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        """Save file as... through file dialog"""
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            defaultextension=".txt"
        )
        
        if file_path:
            try:
                content = self.text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.current_file = file_path
                self.update_title()
                self.update_status(f"File saved as: {os.path.basename(file_path)}")
                self.text.edit_modified(False)  # Reset modified flag
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
                
    def check_unsaved_changes(self):
        """Check for unsaved changes"""
        if self.text.edit_modified():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save?"
            )
            
            if response is None:  # Cancel
                return False
            elif response:  # Yes
                self.save_file()
                return not self.text.edit_modified()  # Return True if saved successfully
            else:  # No
                self.text.edit_modified(False)
                return True
        return True
        
    def update_title(self):
        """Update window title"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.root.title(f"Notepad - {filename}")
        else:
            self.root.title("Notepad - New File")
            
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        
    def on_text_modified(self, event=None):
        """Text modification handler"""
        if self.text.edit_modified():
            self.update_status("Changes not saved")
        else:
            self.update_status("Ready")
            
    def undo_text(self):
        """Undo last action"""
        try:
            self.text.edit_undo()
        except:
            pass
            
    def redo_text(self):
        """Redo last action"""
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
        
    def select_all(self):
        """Select all text"""
        self.text.tag_add(tk.SEL, "1.0", tk.END)
        self.text.mark_set(tk.INSERT, "1.0")
        self.text.see(tk.INSERT)
        return 'break'  # Prevent default behavior
        
    def about_app(self):
        """About the program"""
        about_text = """
        Simple Notepad in Python
        
        Created using tkinter
        
        Features:
        • Create, open, save files
        • Text editing
        • Undo/Redo support
        • Unsaved changes checking
        
        Version 1.0
        """
        messagebox.showinfo("About", about_text)
        
    def exit_app(self):
        """Exit the program"""
        if self.check_unsaved_changes():
            self.root.quit()

def main():
    root = tk.Tk()
    app = NotepadApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
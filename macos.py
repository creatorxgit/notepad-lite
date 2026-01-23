import tkinter as tk
from tkinter import filedialog, messagebox
import os

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Untitled - Notepad")
        self.root.geometry("800x600")
        
        # For macOS window focus and events
        self.root.bind('<Command-q>', lambda e: self.exit_app())
        self.root.bind('<Command-n>', lambda e: self.new_file())
        self.root.bind('<Command-o>', lambda e: self.open_file())
        self.root.bind('<Command-s>', lambda e: self.save_file())
        self.root.bind('<Shift-Command-s>', lambda e: self.save_as_file())
        self.root.bind('<Command-a>', lambda e: self.select_all())
        
        # Currently opened file
        self.current_file = None
        
        # Create menu (macOS style)
        self.create_menu()
        
        # Create text widget
        self.create_text_widget()
        
        # Add status bar
        self.status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind event handlers
        self.text.bind("<<Modified>>", self.on_text_modified)
        self.text.bind('<Command-z>', lambda e: self.undo_text())
        self.text.bind('<Shift-Command-z>', lambda e: self.redo_text())
        
    def create_menu(self):
        """Create program menu with macOS conventions"""
        menubar = tk.Menu(self.root)
        
        # Apple Menu (macOS specific)
        apple_menu = tk.Menu(menubar, tearoff=0, name='apple')
        apple_menu.add_command(label="About Notepad", command=self.about_app)
        apple_menu.add_separator()
        apple_menu.add_command(label="Preferences...", command=self.show_preferences)
        apple_menu.add_separator()
        apple_menu.add_command(label="Hide Notepad", command=lambda: self.root.withdraw())
        apple_menu.add_command(label="Hide Others", command=self.hide_others)
        apple_menu.add_command(label="Show All", command=self.show_all)
        apple_menu.add_separator()
        apple_menu.add_command(label="Quit Notepad", command=self.exit_app, accelerator="Cmd+Q")
        menubar.add_cascade(menu=apple_menu)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Cmd+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Cmd+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Cmd+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Shift+Cmd+S")
        file_menu.add_separator()
        file_menu.add_command(label="Close Window", command=self.close_window, accelerator="Cmd+W")
        file_menu.add_separator()
        file_menu.add_command(label="Page Setup...", command=self.page_setup)
        file_menu.add_command(label="Print...", command=self.print_document, accelerator="Cmd+P")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo_text, accelerator="Cmd+Z")
        edit_menu.add_command(label="Redo", command=self.redo_text, accelerator="Shift+Cmd+Z")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Cmd+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Cmd+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Cmd+V")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Cmd+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.find_text, accelerator="Cmd+F")
        edit_menu.add_command(label="Find and Replace...", command=self.find_replace, accelerator="Cmd+R")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_command(label="Word Wrap", command=self.toggle_word_wrap)
        format_menu.add_command(label="Font...", command=self.select_font)
        menubar.add_cascade(label="Format", menu=format_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label="Status Bar", command=self.toggle_status_bar)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Cmd++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Cmd+-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Window menu (macOS specific)
        window_menu = tk.Menu(menubar, tearoff=0, name='window')
        window_menu.add_command(label="Minimize", command=self.minimize_window, accelerator="Cmd+M")
        window_menu.add_command(label="Zoom", command=self.zoom_window)
        window_menu.add_separator()
        window_menu.add_command(label="Bring All to Front", command=self.bring_all_to_front)
        menubar.add_cascade(label="Window", menu=window_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, name='help')
        help_menu.add_command(label="Notepad Help", command=self.show_help)
        help_menu.add_command(label="Check for Updates...", command=self.check_updates)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def create_text_widget(self):
        """Create text widget with scrollbars optimized for macOS"""
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
            wrap=tk.WORD,  # Word wrap by default for better macOS experience
            undo=True,      # Enable undo functionality
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            font=("Monaco", 11),  # macOS default monospaced font
            bg='white',
            fg='black',
            insertbackground='black',  # Cursor color
            selectbackground='#c0c0c0',  # Selection color
            borderwidth=0,
            highlightthickness=0
        )
        self.text.pack(expand=True, fill=tk.BOTH)
        
        # Configure scrollbars
        scrollbar_y.config(command=self.text.yview)
        scrollbar_x.config(command=self.text.xview)
        
        # Set default word wrap state
        self.word_wrap_enabled = True
        
    def new_file(self):
        """Create a new file"""
        if self.check_unsaved_changes():
            self.text.delete(1.0, tk.END)
            self.current_file = None
            self.update_title()
            self.update_status("New file created")
            self.text.focus_set()
            
    def open_file(self):
        """Open file through file dialog with macOS options"""
        if self.check_unsaved_changes():
            file_path = filedialog.askopenfilename(
                title="Open",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                    ("Python files", "*.py"),
                    ("HTML files", "*.html;*.htm"),
                    ("CSS files", "*.css"),
                    ("JavaScript files", "*.js"),
                    ("Markdown files", "*.md"),
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
                    self.update_status(f"Opened: {os.path.basename(file_path)}")
                    self.text.focus_set()
                    self.text.edit_modified(False)
                    
                except UnicodeDecodeError:
                    # Try different encoding
                    try:
                        with open(file_path, 'r', encoding='latin-1') as file:
                            content = file.read()
                        self.text.delete(1.0, tk.END)
                        self.text.insert(1.0, content)
                        self.current_file = file_path
                        self.update_title()
                        self.update_status(f"Opened with alternative encoding: {os.path.basename(file_path)}")
                        self.text.focus_set()
                        self.text.edit_modified(False)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
                    
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
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        """Save file as... through file dialog"""
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
                ("Python files", "*.py"),
                ("HTML files", "*.html"),
                ("Markdown files", "*.md"),
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
                self.update_status(f"Saved as: {os.path.basename(file_path)}")
                self.text.edit_modified(False)
                self.text.focus_set()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
                
    def check_unsaved_changes(self):
        """Check for unsaved changes with macOS-style dialog"""
        if self.text.edit_modified():
            response = messagebox.askyesnocancel(
                "Save Changes",
                f"Do you want to save the changes you made to the document \"{os.path.basename(self.current_file) if self.current_file else 'Untitled'}\"?",
                default=messagebox.YES,  # macOS default
                icon=messagebox.WARNING
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
            self.root.title(f"{filename} - Notepad")
        else:
            self.root.title("Untitled - Notepad")
            
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        
    def on_text_modified(self, event=None):
        """Text modification handler"""
        if self.text.edit_modified():
            # Add dot to title for unsaved changes
            title = self.root.title()
            if not title.startswith("• "):
                self.root.title(f"• {title}")
            self.update_status("Modified")
        else:
            # Remove dot from title
            title = self.root.title()
            if title.startswith("• "):
                self.root.title(title[2:])
            self.update_status("Ready")
            
    def undo_text(self):
        """Undo last action"""
        try:
            self.text.edit_undo()
            return "break"
        except:
            return "break"
            
    def redo_text(self):
        """Redo last action"""
        try:
            self.text.edit_redo()
            return "break"
        except:
            return "break"
            
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
        return "break"
    
    # macOS-specific menu commands
    def show_preferences(self):
        """Show preferences dialog (stub)"""
        messagebox.showinfo("Preferences", "Preferences dialog would open here")
        
    def hide_others(self):
        """Hide other windows (stub)"""
        # This would typically use platform-specific APIs
        pass
        
    def show_all(self):
        """Show all windows (stub)"""
        # This would typically use platform-specific APIs
        pass
        
    def close_window(self):
        """Close current window"""
        self.exit_app()
        
    def page_setup(self):
        """Page setup dialog (stub)"""
        messagebox.showinfo("Page Setup", "Page setup dialog would open here")
        
    def print_document(self):
        """Print document (stub)"""
        messagebox.showinfo("Print", "Print dialog would open here")
        
    def find_text(self):
        """Find text dialog (stub)"""
        messagebox.showinfo("Find", "Find dialog would open here")
        
    def find_replace(self):
        """Find and replace dialog (stub)"""
        messagebox.showinfo("Find and Replace", "Find and replace dialog would open here")
        
    def toggle_word_wrap(self):
        """Toggle word wrap"""
        self.word_wrap_enabled = not self.word_wrap_enabled
        if self.word_wrap_enabled:
            self.text.config(wrap=tk.WORD)
        else:
            self.text.config(wrap=tk.NONE)
            
    def select_font(self):
        """Select font dialog (stub)"""
        messagebox.showinfo("Font", "Font selection dialog would open here")
        
    def toggle_status_bar(self):
        """Toggle status bar visibility"""
        if self.status_bar.winfo_ismapped():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            
    def zoom_in(self):
        """Zoom in text"""
        current_size = int(self.text['font'].split()[1])
        if current_size < 72:  # Max size
            self.text.config(font=("Monaco", current_size + 1))
            
    def zoom_out(self):
        """Zoom out text"""
        current_size = int(self.text['font'].split()[1])
        if current_size > 6:  # Min size
            self.text.config(font=("Monaco", current_size - 1))
            
    def reset_zoom(self):
        """Reset zoom to default"""
        self.text.config(font=("Monaco", 11))
        
    def minimize_window(self):
        """Minimize window"""
        self.root.iconify()
        
    def zoom_window(self):
        """Toggle zoom window"""
        if self.root.state() == 'zoomed':
            self.root.state('normal')
        else:
            self.root.state('zoomed')
            
    def bring_all_to_front(self):
        """Bring all windows to front"""
        self.root.lift()
        self.root.focus_force()
        
    def show_help(self):
        """Show help"""
        messagebox.showinfo("Notepad Help", "Help content would be displayed here")
        
    def check_updates(self):
        """Check for updates"""
        messagebox.showinfo("Check for Updates", "You have the latest version of Notepad")
        
    def about_app(self):
        """About the program"""
        about_text = """Notepad for macOS

A simple text editor created with Python and tkinter

Version 1.0 for macOS
© 2024 Notepad Team

Features:
• Create, open, save text files
• Undo/Redo support
• Word wrap
• macOS keyboard shortcuts
• Multiple file format support
"""
        messagebox.showinfo("About Notepad", about_text)
        
    def exit_app(self):
        """Exit the program"""
        if self.check_unsaved_changes():
            self.root.quit()

def main():
    root = tk.Tk()
    
    # Set macOS-specific window properties
    try:
        # These might work on some macOS installations
        root.tk.call('tk', 'scaling', 2.0)  # Retina display support
    except:
        pass
    
    app = NotepadApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
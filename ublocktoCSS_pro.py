"""
uBlock Origin to Stylus Converter - Professional Edition
A modern, dark-themed utility for converting uBlock cosmetic filters to Stylus UserCSS files.
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import defaultdict
import webbrowser
import json
import zipfile
from datetime import datetime
from pathlib import Path
import re
import uuid
import time


class ModernScrolledText(tk.Frame):
    """Custom scrolled text widget with styled scrollbar."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=kwargs.pop('frame_bg', '#0f172a'))
        
        self.text = tk.Text(self, **kwargs)
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side='right', fill='y')
        self.text.pack(side='left', fill='both', expand=True)
        
    def get(self, *args):
        return self.text.get(*args)
    
    def insert(self, *args):
        return self.text.insert(*args)
    
    def delete(self, *args):
        return self.text.delete(*args)
    
    def configure(self, **kwargs):
        return self.text.configure(**kwargs)
    
    def bind(self, *args):
        return self.text.bind(*args)


class Tooltip:
    """Modern tooltip implementation."""
    
    def __init__(self, widget, text, bg='#1e293b', fg='#e2e8f0'):
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.tooltip = None
        widget.bind('<Enter>', self.show)
        widget.bind('<Leave>', self.hide)
        
    def show(self, event=None):
        x, y, _, _ = self.widget.bbox('insert') if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f'+{x}+{y}')
        
        label = tk.Label(
            self.tooltip, text=self.text,
            bg=self.bg, fg=self.fg,
            relief='flat', borderwidth=0,
            font=('Segoe UI', 9),
            padx=10, pady=6
        )
        label.pack()
        
    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class UBlockToStylusConverter:
    # Color scheme
    COLORS = {
        'bg_dark': '#020617',
        'bg_card': '#0f172a',
        'bg_input': '#1e293b',
        'bg_hover': '#334155',
        'text_primary': '#f8fafc',
        'text_secondary': '#94a3b8',
        'text_muted': '#64748b',
        'accent_green': '#22c55e',
        'accent_green_hover': '#16a34a',
        'accent_blue': '#60a5fa',
        'accent_blue_hover': '#3b82f6',
        'border': '#334155',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'success': '#22c55e',
    }
    
    FONTS = {
        'title': ('Segoe UI', 18, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'mono': ('Consolas', 10),
        'mono_small': ('Consolas', 9),
    }
    
    CONFIG_FILE = Path.home() / '.ublock_stylus_config.json'
    
    def __init__(self, root):
        self.root = root
        self.root.title("uBlock → Stylus Converter")
        self.root.geometry("900x750")
        self.root.minsize(700, 600)
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        # Try to set window icon (optional)
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # Variables
        self.output_dir = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready")
        self.stats = {
            'domains': 0,
            'global': 0,
            'total': 0,
            'invalid': 0
        }
        
        # Load saved config
        self.load_config()
        
        # Setup UI
        self.setup_styles()
        self.setup_ui()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-v>', self.handle_paste)
        self.root.bind('<Control-Return>', lambda e: self.convert_and_save())
        
    def setup_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Card.TFrame', background=self.COLORS['bg_card'])
        style.configure('Dark.TFrame', background=self.COLORS['bg_dark'])
        
        # Configure label styles
        style.configure('Title.TLabel',
            background=self.COLORS['bg_card'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['title']
        )
        style.configure('Heading.TLabel',
            background=self.COLORS['bg_card'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['heading']
        )
        style.configure('Body.TLabel',
            background=self.COLORS['bg_card'],
            foreground=self.COLORS['text_secondary'],
            font=self.FONTS['body']
        )
        style.configure('Muted.TLabel',
            background=self.COLORS['bg_card'],
            foreground=self.COLORS['text_muted'],
            font=self.FONTS['small']
        )
        style.configure('Stats.TLabel',
            background=self.COLORS['bg_input'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['mono']
        )
        
    def create_button(self, parent, text, command, style='primary', width=None):
        """Create a modern styled button."""
        colors = {
            'primary': (self.COLORS['accent_green'], self.COLORS['accent_green_hover'], '#ffffff'),
            'secondary': (self.COLORS['bg_input'], self.COLORS['bg_hover'], self.COLORS['text_primary']),
            'accent': (self.COLORS['accent_blue'], self.COLORS['accent_blue_hover'], '#ffffff'),
        }
        
        bg, hover_bg, fg = colors.get(style, colors['primary'])
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            font=self.FONTS['body'],
            relief='flat',
            cursor='hand2',
            padx=16,
            pady=8,
            borderwidth=0,
        )
        
        if width:
            btn.configure(width=width)
        
        # Hover effects
        btn.bind('<Enter>', lambda e: btn.configure(bg=hover_bg))
        btn.bind('<Leave>', lambda e: btn.configure(bg=bg))
        
        return btn
    
    def create_card(self, parent, title=None):
        """Create a card-style container."""
        card = tk.Frame(parent, bg=self.COLORS['bg_card'], padx=20, pady=16)
        
        if title:
            title_label = tk.Label(
                card, text=title,
                bg=self.COLORS['bg_card'],
                fg=self.COLORS['text_primary'],
                font=self.FONTS['heading'],
                anchor='w'
            )
            title_label.pack(fill='x', pady=(0, 12))
        
        return card

    def setup_ui(self):
        """Build the complete UI."""
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.COLORS['bg_dark'], padx=20, pady=16)
        main_container.pack(fill='both', expand=True)
        
        # === Header Section ===
        header_card = self.create_card(main_container)
        header_card.pack(fill='x', pady=(0, 12))
        
        # Title row
        title_row = tk.Frame(header_card, bg=self.COLORS['bg_card'])
        title_row.pack(fill='x')
        
        # App icon/logo placeholder and title
        title_label = tk.Label(
            title_row,
            text="⚡ uBlock → Stylus Converter",
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_primary'],
            font=self.FONTS['title']
        )
        title_label.pack(side='left')
        
        # Version badge
        version_badge = tk.Label(
            title_row,
            text="v2.0",
            bg=self.COLORS['accent_blue'],
            fg='white',
            font=('Segoe UI', 8, 'bold'),
            padx=8,
            pady=2
        )
        version_badge.pack(side='left', padx=(12, 0))
        
        # Description
        desc_text = "Convert uBlock Origin cosmetic filters (##) into Stylus-compatible UserCSS files"
        desc_label = tk.Label(
            header_card,
            text=desc_text,
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_secondary'],
            font=self.FONTS['body'],
            anchor='w'
        )
        desc_label.pack(fill='x', pady=(8, 12))
        
        # Quick links row
        links_frame = tk.Frame(header_card, bg=self.COLORS['bg_card'])
        links_frame.pack(fill='x')
        
        stylus_btn = self.create_button(links_frame, "🔗 Get Stylus Extension", self.open_stylus_website, 'secondary')
        stylus_btn.pack(side='left')
        
        help_btn = self.create_button(links_frame, "📖 Filter Syntax Help", self.show_help, 'secondary')
        help_btn.pack(side='left', padx=(8, 0))
        
        # === Input Section ===
        input_card = self.create_card(main_container, "📋 Input Filters")
        input_card.pack(fill='both', expand=True, pady=(0, 12))
        
        # Input instructions
        input_hint = tk.Label(
            input_card,
            text="Paste your uBlock cosmetic filter rules below (e.g., example.com##.ad-banner)",
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_muted'],
            font=self.FONTS['small'],
            anchor='w'
        )
        input_hint.pack(fill='x', pady=(0, 8))
        
        # Text input area with custom styling
        self.text_input = ModernScrolledText(
            input_card,
            frame_bg=self.COLORS['bg_card'],
            height=14,
            bg=self.COLORS['bg_input'],
            fg=self.COLORS['text_primary'],
            insertbackground=self.COLORS['accent_blue'],
            selectbackground=self.COLORS['accent_blue'],
            selectforeground='white',
            font=self.FONTS['mono'],
            relief='flat',
            borderwidth=0,
            padx=12,
            pady=12,
            wrap='none'
        )
        self.text_input.pack(fill='both', expand=True)
        
        # Bind text change for live stats
        self.text_input.bind('<KeyRelease>', self.update_live_stats)
        
        # === Stats Bar ===
        stats_frame = tk.Frame(input_card, bg=self.COLORS['bg_input'], pady=8, padx=12)
        stats_frame.pack(fill='x', pady=(8, 0))
        
        self.stats_labels = {}
        stats_items = [
            ('total', '📊 Rules:', '0'),
            ('domains', '🌐 Domains:', '0'),
            ('global', '🌍 Global:', '0'),
            ('styles', '🎨 Styles:', '0'),
            ('skipped', '⏭️ Network:', '0'),
            ('invalid', '⚠️ Invalid:', '0'),
        ]
        
        for key, label_text, default in stats_items:
            container = tk.Frame(stats_frame, bg=self.COLORS['bg_input'])
            container.pack(side='left', padx=(0, 24))
            
            tk.Label(
                container, text=label_text,
                bg=self.COLORS['bg_input'],
                fg=self.COLORS['text_muted'],
                font=self.FONTS['small']
            ).pack(side='left')
            
            self.stats_labels[key] = tk.Label(
                container, text=default,
                bg=self.COLORS['bg_input'],
                fg=self.COLORS['accent_blue'] if key != 'invalid' else self.COLORS['warning'],
                font=('Segoe UI', 10, 'bold')
            )
            self.stats_labels[key].pack(side='left', padx=(4, 0))
        
        # === Output Section ===
        output_card = self.create_card(main_container, "📁 Output Settings")
        output_card.pack(fill='x', pady=(0, 12))
        
        output_row = tk.Frame(output_card, bg=self.COLORS['bg_card'])
        output_row.pack(fill='x')
        
        # Folder path display
        self.path_entry = tk.Entry(
            output_row,
            textvariable=self.output_dir,
            bg=self.COLORS['bg_input'],
            fg=self.COLORS['text_primary'],
            insertbackground=self.COLORS['accent_blue'],
            font=self.FONTS['mono_small'],
            relief='flat',
            state='readonly',
            readonlybackground=self.COLORS['bg_input'],
            borderwidth=0
        )
        self.path_entry.pack(side='left', fill='x', expand=True, ipady=10, padx=(0, 8))
        
        # Set placeholder if no path
        if not self.output_dir.get():
            self.output_dir.set("No folder selected...")
        
        folder_btn = self.create_button(output_row, "📂 Choose Folder", self.select_folder, 'secondary')
        folder_btn.pack(side='right')
        
        # === Action Buttons ===
        actions_frame = tk.Frame(main_container, bg=self.COLORS['bg_dark'])
        actions_frame.pack(fill='x', pady=(0, 8))
        
        # Left side - secondary actions
        left_actions = tk.Frame(actions_frame, bg=self.COLORS['bg_dark'])
        left_actions.pack(side='left')
        
        clear_btn = self.create_button(left_actions, "🗑️ Clear", self.clear_input, 'secondary')
        clear_btn.pack(side='left')
        Tooltip(clear_btn, "Clear all input text")
        
        paste_btn = self.create_button(left_actions, "📋 Paste", self.paste_from_clipboard, 'secondary')
        paste_btn.pack(side='left', padx=(8, 0))
        Tooltip(paste_btn, "Paste from clipboard (Ctrl+V)")
        
        load_btn = self.create_button(left_actions, "📄 Load File", self.load_from_file, 'secondary')
        load_btn.pack(side='left', padx=(8, 0))
        Tooltip(load_btn, "Load filters from a text file")
        
        # Right side - primary actions
        right_actions = tk.Frame(actions_frame, bg=self.COLORS['bg_dark'])
        right_actions.pack(side='right')
        
        preview_btn = self.create_button(right_actions, "👁️ Preview", self.show_preview, 'accent')
        preview_btn.pack(side='left')
        Tooltip(preview_btn, "Preview converted CSS output")
        
        export_zip_btn = self.create_button(right_actions, "📦 ZIP", self.export_as_zip, 'accent')
        export_zip_btn.pack(side='left', padx=(8, 0))
        Tooltip(export_zip_btn, "Export all files as a single ZIP")
        
        export_json_btn = self.create_button(right_actions, "📋 Stylus JSON", self.export_as_stylus_json, 'accent')
        export_json_btn.pack(side='left', padx=(8, 0))
        Tooltip(export_json_btn, "Export as Stylus-compatible JSON for bulk import")
        
        convert_btn = self.create_button(right_actions, "✨ Convert & Save", self.convert_and_save, 'primary')
        convert_btn.pack(side='left', padx=(8, 0))
        Tooltip(convert_btn, "Convert and save files (Ctrl+Enter)")
        
        # === Status Bar ===
        status_frame = tk.Frame(main_container, bg=self.COLORS['bg_card'], pady=8, padx=12)
        status_frame.pack(fill='x')
        
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['accent_green'],
            font=('Segoe UI', 10)
        )
        self.status_indicator.pack(side='left')
        
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_text,
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_secondary'],
            font=self.FONTS['small'],
            anchor='w'
        )
        self.status_label.pack(side='left', padx=(6, 0), fill='x', expand=True)
        
        # Keyboard shortcut hint
        shortcut_hint = tk.Label(
            status_frame,
            text="Ctrl+Enter to convert",
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_muted'],
            font=self.FONTS['small']
        )
        shortcut_hint.pack(side='right')

    def set_status(self, message, status_type='info'):
        """Update status bar with colored indicator."""
        colors = {
            'info': self.COLORS['accent_blue'],
            'success': self.COLORS['success'],
            'warning': self.COLORS['warning'],
            'error': self.COLORS['error'],
        }
        self.status_indicator.configure(fg=colors.get(status_type, colors['info']))
        self.status_text.set(message)
        self.root.update_idletasks()

    def update_live_stats(self, event=None):
        """Update statistics as user types."""
        raw_text = self.text_input.get("1.0", tk.END).strip()
        
        if not raw_text:
            for key in self.stats_labels:
                self.stats_labels[key].configure(text='0')
            return
        
        domains = set()
        global_count = 0
        total_valid = 0
        style_count = 0
        skipped_count = 0
        invalid_count = 0
        
        for line in raw_text.splitlines():
            line = line.strip()
            if not line or line.startswith('!'):
                continue
            
            # Skip network filters (not cosmetic rules)
            if line.startswith('||') or line.startswith('@@') or line.startswith('/') or '$' in line.split('##')[0]:
                skipped_count += 1
                continue
                
            if '##' in line:
                try:
                    parts = line.split('##', 1)
                    domain_part = parts[0].strip()
                    selector = parts[1].strip()
                    
                    if not selector:
                        invalid_count += 1
                        continue
                    
                    # Check for :style() injection
                    if ':style(' in selector:
                        style_count += 1
                    
                    if not domain_part:
                        global_count += 1
                    else:
                        for d in domain_part.split(','):
                            domains.add(d.strip())
                    
                    total_valid += 1
                except:
                    invalid_count += 1
            elif line and not line.startswith('!'):
                invalid_count += 1
        
        self.stats_labels['total'].configure(text=str(total_valid))
        self.stats_labels['domains'].configure(text=str(len(domains)))
        self.stats_labels['global'].configure(text=str(global_count))
        self.stats_labels['styles'].configure(
            text=str(style_count),
            fg=self.COLORS['accent_blue'] if style_count > 0 else self.COLORS['text_muted']
        )
        self.stats_labels['skipped'].configure(
            text=str(skipped_count),
            fg=self.COLORS['text_muted']
        )
        self.stats_labels['invalid'].configure(
            text=str(invalid_count),
            fg=self.COLORS['error'] if invalid_count > 0 else self.COLORS['text_muted']
        )

    def open_stylus_website(self):
        webbrowser.open("https://add0n.com/stylus.html")
        self.set_status("Opened Stylus extension page", 'info')

    def show_help(self):
        """Show help dialog with filter syntax."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Filter Syntax Help")
        help_window.geometry("550x480")
        help_window.configure(bg=self.COLORS['bg_dark'])
        help_window.transient(self.root)
        
        content = tk.Frame(help_window, bg=self.COLORS['bg_card'], padx=20, pady=20)
        content.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            content,
            text="uBlock Cosmetic Filter Syntax",
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_primary'],
            font=self.FONTS['heading']
        ).pack(anchor='w', pady=(0, 16))
        
        help_text = """Supported filter formats:

• domain.com##.selector
  Hides elements matching .selector on domain.com

• domain.com##.ad, .banner
  Multiple selectors for one domain

• domain1.com,domain2.com##.ad
  Same selector for multiple domains

• ##.global-ad
  Global rule (applies to all sites)

• domain.com##div:style(color: red !important)
  Style injection - applies custom CSS instead of hiding

Lines starting with ! are treated as comments.

Automatically skipped (not converted):
• Network filters (||, @@, $image, etc.)
• These are blocking rules, not cosmetic filters"""
        
        tk.Label(
            content,
            text=help_text,
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_secondary'],
            font=self.FONTS['mono_small'],
            justify='left',
            anchor='w'
        ).pack(fill='both', expand=True)
        
        close_btn = self.create_button(content, "Close", help_window.destroy, 'secondary')
        close_btn.pack(pady=(16, 0))

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_dir.set(folder_selected)
            self.save_config()
            self.set_status(f"Output folder: {folder_selected}", 'success')

    def clear_input(self):
        self.text_input.delete("1.0", tk.END)
        self.update_live_stats()
        self.set_status("Input cleared", 'info')

    def paste_from_clipboard(self):
        try:
            clipboard = self.root.clipboard_get()
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", clipboard)
            self.update_live_stats()
            self.set_status("Pasted from clipboard", 'success')
        except tk.TclError:
            self.set_status("Clipboard is empty", 'warning')

    def handle_paste(self, event):
        """Handle Ctrl+V paste."""
        self.root.after(10, self.update_live_stats)

    def load_from_file(self):
        """Load filters from a text file."""
        file_path = filedialog.askopenfilename(
            title="Select Filter File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_input.delete("1.0", tk.END)
                self.text_input.insert("1.0", content)
                self.update_live_stats()
                self.set_status(f"Loaded: {os.path.basename(file_path)}", 'success')
            except Exception as e:
                self.set_status(f"Error loading file: {str(e)}", 'error')

    def parse_filters(self):
        """Parse input and return structured data."""
        raw_text = self.text_input.get("1.0", tk.END).strip()
        
        # Store rules as (selector, css_properties) tuples
        domain_map = defaultdict(list)
        global_selectors = []
        invalid_lines = []
        skipped_lines = []
        
        for line_num, line in enumerate(raw_text.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith('!'):
                continue
            
            # Skip network filters (not cosmetic rules)
            if line.startswith('||') or line.startswith('@@') or line.startswith('/'):
                skipped_lines.append((line_num, line, "Network filter"))
                continue
            
            # Check for network filter options before ##
            if '##' in line:
                pre_hash = line.split('##')[0]
                if '$' in pre_hash:
                    skipped_lines.append((line_num, line, "Network filter with options"))
                    continue
            else:
                # No ## means it's likely a network filter or invalid
                if '$' in line or line.startswith('|'):
                    skipped_lines.append((line_num, line, "Network filter"))
                    continue
                invalid_lines.append((line_num, line, "Missing ## separator"))
                continue
                
            try:
                parts = line.split('##', 1)
                domains_part = parts[0].strip()
                selector_part = parts[1].strip()
                
                if not selector_part:
                    invalid_lines.append((line_num, line, "Empty selector"))
                    continue
                
                # Parse :style() injection rules
                if ':style(' in selector_part:
                    # Extract selector and CSS from format: selector:style(css properties)
                    style_match = re.match(r'^(.+?):style\((.+)\)$', selector_part)
                    if style_match:
                        selector = style_match.group(1).strip()
                        css_props = style_match.group(2).strip()
                        rule = (selector, css_props)
                    else:
                        invalid_lines.append((line_num, line, "Invalid :style() syntax"))
                        continue
                else:
                    # Standard hide rule
                    rule = (selector_part, "display: none !important")
                
                if not domains_part:
                    global_selectors.append(rule)
                else:
                    for domain in domains_part.split(','):
                        domain_map[domain.strip()].append(rule)
                        
            except Exception as e:
                invalid_lines.append((line_num, line, str(e)))
        
        return domain_map, global_selectors, invalid_lines, skipped_lines

    def show_preview(self):
        """Show preview of converted CSS."""
        domain_map, global_selectors, invalid_lines, skipped_lines = self.parse_filters()
        
        if not domain_map and not global_selectors:
            self.set_status("No valid rules to preview", 'warning')
            return
        
        preview_window = tk.Toplevel(self.root)
        preview_window.title("CSS Preview")
        preview_window.geometry("700x500")
        preview_window.configure(bg=self.COLORS['bg_dark'])
        preview_window.transient(self.root)
        
        # Content frame
        content = tk.Frame(preview_window, bg=self.COLORS['bg_card'], padx=20, pady=20)
        content.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            content,
            text="Preview: Converted UserCSS",
            bg=self.COLORS['bg_card'],
            fg=self.COLORS['text_primary'],
            font=self.FONTS['heading']
        ).pack(anchor='w', pady=(0, 12))
        
        # Preview text
        preview_text = ModernScrolledText(
            content,
            frame_bg=self.COLORS['bg_card'],
            height=20,
            bg=self.COLORS['bg_input'],
            fg=self.COLORS['accent_green'],
            font=self.FONTS['mono_small'],
            relief='flat',
            padx=12,
            pady=12
        )
        preview_text.pack(fill='both', expand=True)
        
        # Generate preview content
        preview_content = ""
        
        # Show first domain-specific file
        if domain_map:
            first_domain = list(domain_map.keys())[0]
            rules = self.dedupe_rules(domain_map[first_domain])
            preview_content += f"/* === {first_domain}.user.css === */\n\n"
            preview_content += self.generate_usercss(first_domain, rules)
            
            if len(domain_map) > 1:
                preview_content += f"\n\n/* ... and {len(domain_map) - 1} more domain files */\n"
        
        # Show global rules
        if global_selectors:
            if preview_content:
                preview_content += "\n\n"
            preview_content += "/* === Global_Rules.user.css === */\n\n"
            preview_content += self.generate_usercss("Global Rules", self.dedupe_rules(global_selectors), is_global=True)
        
        preview_text.insert("1.0", preview_content)
        preview_text.configure(state='disabled')
        
        # Buttons
        btn_frame = tk.Frame(content, bg=self.COLORS['bg_card'])
        btn_frame.pack(fill='x', pady=(12, 0))
        
        def copy_preview():
            self.root.clipboard_clear()
            self.root.clipboard_append(preview_content)
            self.set_status("Preview copied to clipboard", 'success')
        
        copy_btn = self.create_button(btn_frame, "📋 Copy", copy_preview, 'secondary')
        copy_btn.pack(side='left')
        
        close_btn = self.create_button(btn_frame, "Close", preview_window.destroy, 'secondary')
        close_btn.pack(side='right')

    def convert_and_save(self):
        """Main conversion and save logic."""
        raw_text = self.text_input.get("1.0", tk.END).strip()
        save_path = self.output_dir.get()
        
        if not raw_text:
            self.set_status("Please paste some uBlock rules first", 'warning')
            return
        
        if not save_path or save_path == "No folder selected...":
            self.set_status("Please select an output folder", 'warning')
            return
        
        self.set_status("Converting filters...", 'info')
        
        domain_map, global_selectors, invalid_lines, skipped_lines = self.parse_filters()
        
        if not domain_map and not global_selectors:
            self.set_status("No valid ## rules found", 'error')
            return
        
        files_created = 0
        total_rules = 0
        
        # Write domain-specific files
        for domain, rules in domain_map.items():
            try:
                unique_rules = self.dedupe_rules(rules)
                filename = self.sanitize_filename(domain) + ".user.css"
                full_file_path = os.path.join(save_path, filename)
                
                css_content = self.generate_usercss(domain, unique_rules)
                
                with open(full_file_path, "w", encoding="utf-8") as f:
                    f.write(css_content)
                
                files_created += 1
                total_rules += len(unique_rules)
            except Exception as e:
                print(f"Failed to write {domain}: {e}")
        
        # Write global file
        if global_selectors:
            try:
                unique_global = self.dedupe_rules(global_selectors)
                full_file_path = os.path.join(save_path, "Global_Rules.user.css")
                
                css_content = self.generate_usercss("Global Rules", unique_global, is_global=True)
                
                with open(full_file_path, "w", encoding="utf-8") as f:
                    f.write(css_content)
                
                files_created += 1
                total_rules += len(unique_global)
            except Exception as e:
                print(f"Failed to write globals: {e}")
        
        # Show success
        msg = f"✓ Created {files_created} files ({total_rules} rules)"
        if invalid_lines:
            msg += f" • {len(invalid_lines)} invalid"
        if skipped_lines:
            msg += f" • {len(skipped_lines)} network filters skipped"
        
        self.set_status(msg, 'success')
        
        # Show success dialog with option to open folder
        if messagebox.askyesno(
            "Conversion Complete",
            f"Successfully created {files_created} CSS files with {total_rules} rules.\n\n"
            f"Location: {save_path}\n\n"
            "Would you like to open the output folder?"
        ):
            self.open_output_folder()

    def export_as_zip(self):
        """Export all converted files as a ZIP archive."""
        raw_text = self.text_input.get("1.0", tk.END).strip()
        
        if not raw_text:
            self.set_status("No filters to export", 'warning')
            return
        
        domain_map, global_selectors, _, _ = self.parse_filters()
        
        if not domain_map and not global_selectors:
            self.set_status("No valid rules to export", 'error')
            return
        
        # Ask for save location
        zip_path = filedialog.asksaveasfilename(
            title="Save ZIP Archive",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")],
            initialfile=f"stylus_filters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        
        if not zip_path:
            return
        
        self.set_status("Creating ZIP archive...", 'info')
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add domain files
                for domain, rules in domain_map.items():
                    unique_rules = self.dedupe_rules(rules)
                    filename = self.sanitize_filename(domain) + ".user.css"
                    content = self.generate_usercss(domain, unique_rules)
                    zf.writestr(filename, content)
                
                # Add global file
                if global_selectors:
                    unique_global = self.dedupe_rules(global_selectors)
                    content = self.generate_usercss("Global Rules", unique_global, is_global=True)
                    zf.writestr("Global_Rules.user.css", content)
            
            file_count = len(domain_map) + (1 if global_selectors else 0)
            self.set_status(f"✓ Exported {file_count} files to ZIP", 'success')
            
        except Exception as e:
            self.set_status(f"Export failed: {str(e)}", 'error')

    def export_as_stylus_json(self):
        """Export all converted styles as a Stylus-compatible JSON file for bulk import."""
        raw_text = self.text_input.get("1.0", tk.END).strip()
        
        if not raw_text:
            self.set_status("No filters to export", 'warning')
            return
        
        domain_map, global_selectors, _, _ = self.parse_filters()
        
        if not domain_map and not global_selectors:
            self.set_status("No valid rules to export", 'error')
            return
        
        # Ask for save location
        json_path = filedialog.asksaveasfilename(
            title="Save Stylus JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"stylus_import_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
        )
        
        if not json_path:
            return
        
        self.set_status("Creating Stylus JSON...", 'info')
        
        try:
            stylus_export = self.generate_stylus_json(domain_map, global_selectors)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(stylus_export, f, indent=2)
            
            style_count = len(domain_map) + (1 if global_selectors else 0)
            self.set_status(f"✓ Exported {style_count} styles to Stylus JSON", 'success')
            
            if messagebox.askyesno(
                "Export Complete",
                f"Successfully exported {style_count} styles to Stylus JSON format.\n\n"
                f"File: {json_path}\n\n"
                "To import:\n"
                "1. Open Stylus extension\n"
                "2. Go to Manage → Backup → Import\n"
                "3. Select this JSON file\n\n"
                "Would you like to open the containing folder?"
            ):
                folder = os.path.dirname(json_path)
                if sys.platform == 'win32':
                    os.startfile(folder)
                elif sys.platform == 'darwin':
                    os.system(f'open "{folder}"')
                else:
                    os.system(f'xdg-open "{folder}"')
                    
        except Exception as e:
            self.set_status(f"Export failed: {str(e)}", 'error')

    def generate_stylus_json(self, domain_map, global_selectors):
        """Generate Stylus-compatible JSON structure for import."""
        stylus_export = []
        
        # Add minimal settings object (required by Stylus)
        settings_obj = {
            "settings": {
                "disableAll": False,
                "exposeIframes": False,
                "newStyleAsUsercss": False,
                "openEditInWindow": False,
                "show-badge": True,
                "styleViaASS": False,
                "urlInstaller": True,
                "sync.enabled": "none",
                "updateInterval": 24
            },
            "order": {
                "main": [],
                "prio": []
            }
        }
        stylus_export.append(settings_obj)
        
        # Generate unique base ID
        base_id = int(time.time() * 1000) % 1000000
        
        # Add domain-specific styles
        for idx, (domain, rules) in enumerate(domain_map.items()):
            unique_rules = self.dedupe_rules(rules)
            style_entry = self.create_stylus_style_entry(
                name=domain,
                rules=unique_rules,
                domains=[domain, f"www.{domain}"] if not domain.startswith('www.') else [domain],
                style_id=base_id + idx,
                is_global=False
            )
            stylus_export.append(style_entry)
        
        # Add global rules style
        if global_selectors:
            unique_global = self.dedupe_rules(global_selectors)
            global_style = self.create_stylus_style_entry(
                name="Global Rules - uBlock Converted",
                rules=unique_global,
                domains=None,
                style_id=base_id + len(domain_map),
                is_global=True
            )
            stylus_export.append(global_style)
        
        return stylus_export

    def create_stylus_style_entry(self, name, rules, domains, style_id, is_global=False):
        """Create a single Stylus style entry.
        
        Args:
            name: Style name (usually domain)
            rules: List of (selector, css_properties) tuples
            domains: List of domains to target, or None for global
            style_id: Unique ID for the style
            is_global: Whether this is a global style
        """
        now = int(time.time() * 1000)
        
        # Group rules by their CSS properties
        css_groups = defaultdict(list)
        for selector, css_props in rules:
            css_groups[css_props].append(selector)
        
        # Generate CSS blocks
        css_blocks = []
        for css_props, selectors in css_groups.items():
            selector_block = ",\n    ".join(selectors)
            css_blocks.append(f"""    {selector_block} {{
        {css_props};
    }}""")
        
        all_rules = "\n\n".join(css_blocks)
        
        if is_global:
            css_code = f"""/* Rules converted from uBlock Origin */

{all_rules}"""
        else:
            css_code = f"""/* Rules for {name} */

{all_rules}"""
        
        style_entry = {
            "enabled": True,
            "installDate": now,
            "name": name,
            "sections": [
                {
                    "code": css_code
                }
            ],
            "updateDate": now,
            "_id": str(uuid.uuid4()),
            "_rev": now,
            "id": style_id
        }
        
        # Add domain targeting for non-global styles
        if not is_global and domains:
            style_entry["sections"][0]["domains"] = domains
        
        return style_entry

    def open_output_folder(self):
        """Open the output folder in file explorer."""
        path = self.output_dir.get()
        if path and path != "No folder selected..." and os.path.exists(path):
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')

    def sanitize_filename(self, filename):
        """Remove characters invalid in filenames."""
        # Replace common URL parts
        filename = filename.replace('www.', '').replace('https://', '').replace('http://', '')
        # Keep only safe characters
        return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()

    def dedupe_rules(self, rules):
        """Remove duplicate rules while preserving order."""
        seen = set()
        unique = []
        for rule in rules:
            if rule not in seen:
                seen.add(rule)
                unique.append(rule)
        return sorted(unique, key=lambda x: (x[1] != "display: none !important", x[0]))

    def generate_usercss(self, name, rules, is_global=False):
        """Generate UserCSS content for Stylus.
        
        Args:
            name: Domain name or style name
            rules: List of (selector, css_properties) tuples
            is_global: Whether this is a global style (no domain restriction)
        """
        header = f"""/* ==UserStyle==
@name           {name} - Cleanup
@namespace      ublock-to-stylus-converter
@version        1.0.0
@description    Converted from uBlock Origin cosmetic filters
@author         uBlock Converter
@license        MIT
==/UserStyle== */

"""
        # Group rules by their CSS properties
        css_groups = defaultdict(list)
        for selector, css_props in rules:
            css_groups[css_props].append(selector)
        
        # Generate CSS blocks
        css_blocks = []
        for css_props, selectors in css_groups.items():
            selector_block = ",\n    ".join(selectors)
            css_blocks.append(f"""    {selector_block} {{
        {css_props};
    }}""")
        
        all_rules = "\n\n".join(css_blocks)
        
        if is_global:
            css_body = all_rules
        else:
            css_body = f"""@-moz-document domain("{name}") {{
{all_rules}
}}"""

        return header + css_body

    def load_config(self):
        """Load saved configuration."""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    if 'output_dir' in config and os.path.exists(config['output_dir']):
                        self.output_dir.set(config['output_dir'])
        except:
            pass

    def save_config(self):
        """Save configuration."""
        try:
            config = {
                'output_dir': self.output_dir.get()
            }
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except:
            pass


def main():
    root = tk.Tk()
    
    # Center window on screen
    root.update_idletasks()
    width = 900
    height = 750
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    app = UBlockToStylusConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()

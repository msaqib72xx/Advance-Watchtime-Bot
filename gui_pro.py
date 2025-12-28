#!/usr/bin/env python3
"""
Professional GUI for YouTube HumanWatch Pro
Modern Tkinter interface with real-time monitoring
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import asyncio
import json
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Import our modules
from bot_advanced import YouTubeWatchTimeBotAdvanced
from session_orchestrator import SessionOrchestrator, SessionPriority
from stealth_manager import StealthManager
from fingerprint_rotator import FingerprintRotator, create_fingerprint_rotator

# Try to import customtkinter for modern UI
try:
    import customtkinter as ctk
    USE_CUSTOMTKINTER = True
except ImportError:
    USE_CUSTOMTKINTER = False
    print("⚠️  customtkinter not installed. Using standard tkinter.")
    print("   Install with: pip install customtkinter")

class YouTubeWatchTimeGUI:
    """Professional GUI for the YouTube Watch Time Bot"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Bot instances
        self.bot = None
        self.orchestrator = None
        self.stealth = None
        self.fingerprint_rotator = None
        
        # State
        self.is_running = False
        self.current_campaign = None
        self.active_sessions = []
        
        # Statistics
        self.stats = {
            'total_sessions': 0,
            'successful_sessions': 0,
            'failed_sessions': 0,
            'total_watch_time': 0,
            'detection_events': 0
        }
        
        # Load configuration
        self.config = self.load_config()
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
        # Start background tasks
        self.start_background_tasks()
        
    def setup_window(self):
        """Setup main window properties"""
        if USE_CUSTOMTKINTER:
            self.root.title("YouTube HumanWatch Pro v3.0")
            self.root.geometry("1400x800")
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
        else:
            self.root.title("YouTube HumanWatch Pro v3.0")
            self.root.geometry("1400x800")
            self.root.configure(bg='#1e1e1e')
            
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open('config_advanced.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "stealth_settings": {"enabled": True},
                "behavior_settings": {"enabled": True},
                "session_settings": {"max_sessions": 3},
                "browser_settings": {"headless": False}
            }
    
    def setup_styles(self):
        """Setup GUI styles"""
        if USE_CUSTOMTKINTER:
            return  # customtkinter handles styles automatically
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        bg_color = '#1e1e1e'
        fg_color = '#ffffff'
        accent_color = '#4CAF50'
        secondary_color = '#2196F3'
        danger_color = '#f44336'
        warning_color = '#ff9800'
        
        # Configure styles
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=10)
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12))
        style.configure('Status.TLabel', font=('Segoe UI', 11, 'bold'))
        style.configure('Success.TLabel', foreground=accent_color)
        style.configure('Warning.TLabel', foreground=warning_color)
        style.configure('Error.TLabel', foreground=danger_color)
        
        # Configure frames
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, foreground=fg_color)
        style.configure('TLabelframe.Label', background=bg_color, foreground=fg_color)
        
        # Configure entry fields
        style.configure('TEntry', fieldbackground='#2d2d2d', foreground=fg_color)
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Create main container
        if USE_CUSTOMTKINTER:
            main_container = ctk.CTkFrame(self.root)
            main_container.pack(fill='both', expand=True, padx=10, pady=10)
        else:
            main_container = ttk.Frame(self.root)
            main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create header
        self.create_header(main_container)
        
        # Create notebook (tabs)
        self.create_notebook(main_container)
        
        # Create status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create header with title and quick actions"""
        
        if USE_CUSTOMTKINTER:
            header_frame = ctk.CTkFrame(parent, height=80)
            header_frame.pack(fill='x', pady=(0, 10))
            header_frame.pack_propagate(False)
            
            # Title
            title_label = ctk.CTkLabel(
                header_frame, 
                text="🎬 YouTube HumanWatch Pro",
                font=('Segoe UI', 24, 'bold')
            )
            title_label.pack(side='left', padx=20, pady=20)
            
            # Subtitle
            subtitle_label = ctk.CTkLabel(
                header_frame,
                text="Advanced Behavioral Simulation Engine | Educational Use Only",
                font=('Segoe UI', 11)
            )
            subtitle_label.pack(side='left', padx=10, pady=20)
            
            # Quick action buttons
            button_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
            button_frame.pack(side='right', padx=20, pady=20)
            
            self.quick_start_btn = ctk.CTkButton(
                button_frame,
                text="🚀 Quick Start",
                command=self.quick_start,
                width=120,
                height=35
            )
            self.quick_start_btn.pack(side='left', padx=5)
            
            self.emergency_stop_btn = ctk.CTkButton(
                button_frame,
                text="⏹️ Emergency Stop",
                command=self.emergency_stop,
                width=120,
                height=35,
                fg_color='#f44336',
                hover_color='#d32f2f'
            )
            self.emergency_stop_btn.pack(side='left', padx=5)
            self.emergency_stop_btn.configure(state='disabled')
            
        else:
            header_frame = ttk.Frame(parent, height=80)
            header_frame.pack(fill='x', pady=(0, 10))
            header_frame.pack_propagate(False)
            
            # Title
            title_label = ttk.Label(
                header_frame,
                text="🎬 YouTube HumanWatch Pro",
                style='Title.TLabel'
            )
            title_label.pack(side='left', padx=20, pady=20)
            
            # Subtitle
            subtitle_label = ttk.Label(
                header_frame,
                text="Advanced Behavioral Simulation Engine | Educational Use Only",
                style='Subtitle.TLabel'
            )
            subtitle_label.pack(side='left', padx=10, pady=20)
            
            # Quick action buttons
            button_frame = ttk.Frame(header_frame)
            button_frame.pack(side='right', padx=20, pady=20)
            
            self.quick_start_btn = ttk.Button(
                button_frame,
                text="🚀 Quick Start",
                command=self.quick_start,
                width=15
            )
            self.quick_start_btn.pack(side='left', padx=5)
            
            self.emergency_stop_btn = ttk.Button(
                button_frame,
                text="⏹️ Emergency Stop",
                command=self.emergency_stop,
                width=15,
                style='TButton'
            )
            self.emergency_stop_btn.pack(side='left', padx=5)
            self.emergency_stop_btn.configure(state='disabled')
    
    def create_notebook(self, parent):
        """Create notebook with tabs"""
        
        if USE_CUSTOMTKINTER:
            # Create tabview
            self.tabview = ctk.CTkTabview(parent)
            self.tabview.pack(fill='both', expand=True, padx=5, pady=(0, 10))
            
            # Add tabs
            self.tabview.add("🎯 Session Control")
            self.tabview.add("⚙️ Configuration")
            self.tabview.add("📊 Statistics")
            self.tabview.add("🔧 Tools")
            self.tabview.add("📋 Logs")
            self.tabview.add("ℹ️ About")
            
            # Create tab contents
            self.create_session_control_tab(self.tabview.tab("🎯 Session Control"))
            self.create_configuration_tab(self.tabview.tab("⚙️ Configuration"))
            self.create_statistics_tab(self.tabview.tab("📊 Statistics"))
            self.create_tools_tab(self.tabview.tab("🔧 Tools"))
            self.create_logs_tab(self.tabview.tab("📋 Logs"))
            self.create_about_tab(self.tabview.tab("ℹ️ About"))
            
        else:
            # Create notebook
            self.notebook = ttk.Notebook(parent)
            self.notebook.pack(fill='both', expand=True, padx=5, pady=(0, 10))
            
            # Create frames for tabs
            self.session_tab = ttk.Frame(self.notebook)
            self.config_tab = ttk.Frame(self.notebook)
            self.stats_tab = ttk.Frame(self.notebook)
            self.tools_tab = ttk.Frame(self.notebook)
            self.logs_tab = ttk.Frame(self.notebook)
            self.about_tab = ttk.Frame(self.notebook)
            
            # Add tabs
            self.notebook.add(self.session_tab, text='🎯 Session Control')
            self.notebook.add(self.config_tab, text='⚙️ Configuration')
            self.notebook.add(self.stats_tab, text='📊 Statistics')
            self.notebook.add(self.tools_tab, text='🔧 Tools')
            self.notebook.add(self.logs_tab, text='📋 Logs')
            self.notebook.add(self.about_tab, text='ℹ️ About')
            
            # Create tab contents
            self.create_session_control_tab(self.session_tab)
            self.create_configuration_tab(self.config_tab)
            self.create_statistics_tab(self.stats_tab)
            self.create_tools_tab(self.tools_tab)
            self.create_logs_tab(self.logs_tab)
            self.create_about_tab(self.about_tab)
    
    def create_session_control_tab(self, parent):
        """Create session control tab"""
        
        if USE_CUSTOMTKINTER:
            # Create scrollable frame
            canvas = ctk.CTkScrollableFrame(parent)
            canvas.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Video Configuration
            config_frame = ctk.CTkFrame(canvas)
            config_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(config_frame, text="🎬 Video Configuration", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            # URL Input
            url_frame = ctk.CTkFrame(config_frame, fg_color='transparent')
            url_frame.pack(fill='x', padx=15, pady=(0, 10))
            
            ctk.CTkLabel(url_frame, text="YouTube Video URL:", 
                         font=('Segoe UI', 12)).pack(anchor='w')
            
            self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://www.youtube.com/watch?v=...")
            self.url_entry.pack(fill='x', pady=(5, 0))
            self.url_entry.insert(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            
            # Session Settings
            settings_frame = ctk.CTkFrame(config_frame, fg_color='transparent')
            settings_frame.pack(fill='x', padx=15, pady=(0, 15))
            
            # Number of sessions
            session_frame = ctk.CTkFrame(settings_frame, fg_color='transparent')
            session_frame.pack(fill='x', pady=(0, 10))
            
            ctk.CTkLabel(session_frame, text="Number of Sessions:", 
                         font=('Segoe UI', 12)).pack(anchor='w')
            
            self.session_var = tk.IntVar(value=3)
            session_slider = ctk.CTkSlider(
                session_frame, 
                from_=1, 
                to=10, 
                variable=self.session_var,
                command=lambda v: self.session_label.configure(text=f"{int(float(v))} sessions")
            )
            session_slider.pack(fill='x', pady=(5, 0))
            
            self.session_label = ctk.CTkLabel(session_frame, text="3 sessions")
            self.session_label.pack(anchor='e')
            
            # Priority
            priority_frame = ctk.CTkFrame(settings_frame, fg_color='transparent')
            priority_frame.pack(fill='x', pady=(0, 10))
            
            ctk.CTkLabel(priority_frame, text="Stealth Priority:", 
                         font=('Segoe UI', 12)).pack(anchor='w')
            
            self.priority_var = tk.StringVar(value="medium")
            priority_options = ["high", "medium", "low", "test"]
            
            for option in priority_options:
                rb = ctk.CTkRadioButton(
                    priority_frame,
                    text=option.capitalize(),
                    variable=self.priority_var,
                    value=option,
                    font=('Segoe UI', 11)
                )
                rb.pack(anchor='w', pady=2)
            
            # Control Buttons
            control_frame = ctk.CTkFrame(canvas)
            control_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(control_frame, text="🚀 Campaign Control", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            button_container = ctk.CTkFrame(control_frame, fg_color='transparent')
            button_container.pack(fill='x', padx=15, pady=(0, 15))
            
            self.start_campaign_btn = ctk.CTkButton(
                button_container,
                text="🎬 Start Campaign",
                command=self.start_campaign,
                height=40,
                font=('Segoe UI', 13, 'bold')
            )
            self.start_campaign_btn.pack(side='left', padx=(0, 10))
            
            self.pause_campaign_btn = ctk.CTkButton(
                button_container,
                text="⏸️ Pause",
                command=self.pause_campaign,
                height=40,
                state='disabled'
            )
            self.pause_campaign_btn.pack(side='left', padx=(0, 10))
            
            self.stop_campaign_btn = ctk.CTkButton(
                button_container,
                text="⏹️ Stop",
                command=self.stop_campaign,
                height=40,
                state='disabled'
            )
            self.stop_campaign_btn.pack(side='left')
            
            # Live Monitoring
            monitor_frame = ctk.CTkFrame(canvas)
            monitor_frame.pack(fill='both', expand=True)
            
            ctk.CTkLabel(monitor_frame, text="📡 Live Monitoring", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Stats grid
            stats_grid = ctk.CTkFrame(monitor_frame, fg_color='transparent')
            stats_grid.pack(fill='x', padx=15, pady=(0, 10))
            
            # Row 1
            row1 = ctk.CTkFrame(stats_grid, fg_color='transparent')
            row1.pack(fill='x', pady=(0, 10))
            
            self.active_sessions_label = ctk.CTkLabel(
                row1,
                text="Active Sessions: 0",
                font=('Segoe UI', 12, 'bold')
            )
            self.active_sessions_label.pack(side='left', padx=(0, 20))
            
            self.success_rate_label = ctk.CTkLabel(
                row1,
                text="Success Rate: 0%",
                font=('Segoe UI', 12, 'bold')
            )
            self.success_rate_label.pack(side='left', padx=(0, 20))
            
            # Row 2
            row2 = ctk.CTkFrame(stats_grid, fg_color='transparent')
            row2.pack(fill='x', pady=(0, 10))
            
            self.total_watch_label = ctk.CTkLabel(
                row2,
                text="Total Watch Time: 0s",
                font=('Segoe UI', 12, 'bold')
            )
            self.total_watch_label.pack(side='left', padx=(0, 20))
            
            self.detection_label = ctk.CTkLabel(
                row2,
                text="Detection Events: 0",
                font=('Segoe UI', 12, 'bold')
            )
            self.detection_label.pack(side='left')
            
            # Progress
            progress_frame = ctk.CTkFrame(monitor_frame, fg_color='transparent')
            progress_frame.pack(fill='x', padx=15, pady=(0, 15))
            
            ctk.CTkLabel(progress_frame, text="Campaign Progress:", 
                         font=('Segoe UI', 12)).pack(anchor='w')
            
            self.progress_bar = ctk.CTkProgressBar(progress_frame)
            self.progress_bar.pack(fill='x', pady=(5, 0))
            self.progress_bar.set(0)
            
            self.progress_label = ctk.CTkLabel(progress_frame, text="0/0 sessions completed")
            self.progress_label.pack(anchor='e')
            
        else:
            # Standard tkinter implementation
            # Create main container with scrollbar
            canvas = tk.Canvas(parent, bg='#1e1e1e', highlightthickness=0)
            scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Video Configuration
            config_frame = ttk.LabelFrame(scrollable_frame, text="🎬 Video Configuration", padding=15)
            config_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            # URL Input
            ttk.Label(config_frame, text="YouTube Video URL:").pack(anchor='w', pady=(0, 5))
            
            self.url_entry = ttk.Entry(config_frame, width=70)
            self.url_entry.pack(fill='x', pady=(0, 15))
            self.url_entry.insert(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            
            # Session Settings
            settings_frame = ttk.Frame(config_frame)
            settings_frame.pack(fill='x', pady=(0, 10))
            
            # Number of sessions
            ttk.Label(settings_frame, text="Number of Sessions:").grid(row=0, column=0, sticky='w', pady=5)
            
            self.session_var = tk.IntVar(value=3)
            session_slider = ttk.Scale(
                settings_frame,
                from_=1,
                to=10,
                variable=self.session_var,
                orient='horizontal',
                length=300
            )
            session_slider.grid(row=0, column=1, padx=10, pady=5, sticky='w')
            
            self.session_label = ttk.Label(settings_frame, text="3 sessions")
            self.session_label.grid(row=0, column=2, padx=10, pady=5)
            
            # Priority
            ttk.Label(settings_frame, text="Stealth Priority:").grid(row=1, column=0, sticky='w', pady=5)
            
            self.priority_var = tk.StringVar(value="medium")
            priority_options = ["high", "medium", "low", "test"]
            
            for i, option in enumerate(priority_options):
                rb = ttk.Radiobutton(
                    settings_frame,
                    text=option.capitalize(),
                    variable=self.priority_var,
                    value=option
                )
                rb.grid(row=1, column=i+1, padx=5, pady=5, sticky='w')
            
            # Control Buttons
            control_frame = ttk.LabelFrame(scrollable_frame, text="🚀 Campaign Control", padding=15)
            control_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            button_container = ttk.Frame(control_frame)
            button_container.pack(fill='x', pady=(0, 10))
            
            self.start_campaign_btn = ttk.Button(
                button_container,
                text="🎬 Start Campaign",
                command=self.start_campaign,
                width=20
            )
            self.start_campaign_btn.pack(side='left', padx=(0, 10))
            
            self.pause_campaign_btn = ttk.Button(
                button_container,
                text="⏸️ Pause",
                command=self.pause_campaign,
                width=15,
                state='disabled'
            )
            self.pause_campaign_btn.pack(side='left', padx=(0, 10))
            
            self.stop_campaign_btn = ttk.Button(
                button_container,
                text="⏹️ Stop",
                command=self.stop_campaign,
                width=15,
                state='disabled'
            )
            self.stop_campaign_btn.pack(side='left')
            
            # Live Monitoring
            monitor_frame = ttk.LabelFrame(scrollable_frame, text="📡 Live Monitoring", padding=15)
            monitor_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            # Stats grid
            stats_grid = ttk.Frame(monitor_frame)
            stats_grid.pack(fill='x', pady=(0, 10))
            
            # Row 1
            row1 = ttk.Frame(stats_grid)
            row1.pack(fill='x', pady=(0, 10))
            
            self.active_sessions_label = ttk.Label(
                row1,
                text="Active Sessions: 0",
                font=('Segoe UI', 11, 'bold')
            )
            self.active_sessions_label.pack(side='left', padx=(0, 30))
            
            self.success_rate_label = ttk.Label(
                row1,
                text="Success Rate: 0%",
                font=('Segoe UI', 11, 'bold')
            )
            self.success_rate_label.pack(side='left')
            
            # Row 2
            row2 = ttk.Frame(stats_grid)
            row2.pack(fill='x', pady=(0, 10))
            
            self.total_watch_label = ttk.Label(
                row2,
                text="Total Watch Time: 0s",
                font=('Segoe UI', 11, 'bold')
            )
            self.total_watch_label.pack(side='left', padx=(0, 30))
            
            self.detection_label = ttk.Label(
                row2,
                text="Detection Events: 0",
                font=('Segoe UI', 11, 'bold')
            )
            self.detection_label.pack(side='left')
            
            # Progress
            progress_frame = ttk.Frame(monitor_frame)
            progress_frame.pack(fill='x', pady=(0, 10))
            
            ttk.Label(progress_frame, text="Campaign Progress:").pack(anchor='w')
            
            self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
            self.progress_bar.pack(fill='x', pady=(5, 0))
            
            self.progress_label = ttk.Label(progress_frame, text="0/0 sessions completed")
            self.progress_label.pack(anchor='e')
    
    def create_configuration_tab(self, parent):
        """Create configuration tab"""
        
        if USE_CUSTOMTKINTER:
            canvas = ctk.CTkScrollableFrame(parent)
            canvas.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Stealth Settings
            stealth_frame = ctk.CTkFrame(canvas)
            stealth_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(stealth_frame, text="🛡️ Stealth Settings", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Create checkboxes for stealth options
            self.stealth_vars = {}
            stealth_options = [
                ("fingerprint_rotation", "Fingerprint Rotation", True),
                ("webgl_spoofing", "WebGL Spoofing", True),
                ("canvas_spoofing", "Canvas Spoofing", True),
                ("mouse_simulation", "Mouse Movement Simulation", True),
                ("scroll_simulation", "Scroll Behavior Simulation", True),
                ("network_randomization", "Network Randomization", False),
                ("timing_randomization", "Timing Randomization", True)
            ]
            
            for key, text, default in stealth_options:
                var = tk.BooleanVar(value=default)
                self.stealth_vars[key] = var
                
                cb = ctk.CTkCheckBox(
                    stealth_frame,
                    text=text,
                    variable=var,
                    font=('Segoe UI', 12)
                )
                cb.pack(anchor='w', padx=20, pady=2)
            
            # Behavior Settings
            behavior_frame = ctk.CTkFrame(canvas)
            behavior_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(behavior_frame, text="🧠 Behavior Settings", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Viewer profiles
            ctk.CTkLabel(behavior_frame, text="Viewer Profile Distribution:", 
                         font=('Segoe UI', 12)).pack(anchor='w', padx=20, pady=(0, 5))
            
            profile_frame = ctk.CTkFrame(behavior_frame, fg_color='transparent')
            profile_frame.pack(fill='x', padx=20, pady=(0, 10))
            
            profiles = ["casual", "engaged", "fan", "distracted"]
            self.profile_vars = {}
            
            for profile in profiles:
                row = ctk.CTkFrame(profile_frame, fg_color='transparent')
                row.pack(fill='x', pady=2)
                
                ctk.CTkLabel(row, text=profile.capitalize() + ":", 
                             font=('Segoe UI', 11)).pack(side='left', padx=(0, 10))
                
                var = tk.IntVar(value=25)
                self.profile_vars[profile] = var
                
                slider = ctk.CTkSlider(
                    row,
                    from_=0,
                    to=100,
                    variable=var,
                    width=150
                )
                slider.pack(side='left')
                
                label = ctk.CTkLabel(row, text="25%")
                label.pack(side='left', padx=10)
                
                # Update label when slider changes
                slider.configure(command=lambda v, l=label: l.configure(text=f"{int(float(v))}%"))
            
            # Browser Settings
            browser_frame = ctk.CTkFrame(canvas)
            browser_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(browser_frame, text="🌐 Browser Settings", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Headless mode
            self.headless_var = tk.BooleanVar(value=False)
            headless_cb = ctk.CTkCheckBox(
                browser_frame,
                text="Headless Mode",
                variable=self.headless_var,
                font=('Segoe UI', 12)
            )
            headless_cb.pack(anchor='w', padx=20, pady=2)
            
            # Proxy settings
            self.proxy_var = tk.BooleanVar(value=False)
            proxy_cb = ctk.CTkCheckBox(
                browser_frame,
                text="Use Proxy Rotation",
                variable=self.proxy_var,
                font=('Segoe UI', 12)
            )
            proxy_cb.pack(anchor='w', padx=20, pady=2)
            
            # Save button
            save_frame = ctk.CTkFrame(canvas, fg_color='transparent')
            save_frame.pack(fill='x', pady=15)
            
            save_btn = ctk.CTkButton(
                save_frame,
                text="💾 Save Configuration",
                command=self.save_configuration,
                height=40,
                font=('Segoe UI', 13, 'bold')
            )
            save_btn.pack(pady=10)
            
        else:
            # Standard tkinter implementation
            canvas = tk.Canvas(parent, bg='#1e1e1e', highlightthickness=0)
            scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Stealth Settings
            stealth_frame = ttk.LabelFrame(scrollable_frame, text="🛡️ Stealth Settings", padding=15)
            stealth_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            self.stealth_vars = {}
            stealth_options = [
                ("fingerprint_rotation", "Fingerprint Rotation", True),
                ("webgl_spoofing", "WebGL Spoofing", True),
                ("canvas_spoofing", "Canvas Spoofing", True),
                ("mouse_simulation", "Mouse Movement Simulation", True),
                ("scroll_simulation", "Scroll Behavior Simulation", True),
                ("network_randomization", "Network Randomization", False),
                ("timing_randomization", "Timing Randomization", True)
            ]
            
            for i, (key, text, default) in enumerate(stealth_options):
                var = tk.BooleanVar(value=default)
                self.stealth_vars[key] = var
                
                cb = ttk.Checkbutton(
                    stealth_frame,
                    text=text,
                    variable=var
                )
                cb.grid(row=i, column=0, sticky='w', pady=2)
            
            # Behavior Settings
            behavior_frame = ttk.LabelFrame(scrollable_frame, text="🧠 Behavior Settings", padding=15)
            behavior_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            ttk.Label(behavior_frame, text="Viewer Profile Distribution:").grid(
                row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
            
            profiles = ["casual", "engaged", "fan", "distracted"]
            self.profile_vars = {}
            
            for i, profile in enumerate(profiles):
                ttk.Label(behavior_frame, text=profile.capitalize() + ":").grid(
                    row=i+1, column=0, sticky='w', pady=2)
                
                var = tk.IntVar(value=25)
                self.profile_vars[profile] = var
                
                slider = ttk.Scale(
                    behavior_frame,
                    from_=0,
                    to=100,
                    variable=var,
                    orient='horizontal',
                    length=200
                )
                slider.grid(row=i+1, column=1, padx=10, pady=2)
                
                label = ttk.Label(behavior_frame, text="25%")
                label.grid(row=i+1, column=2, padx=10, pady=2)
            
            # Browser Settings
            browser_frame = ttk.LabelFrame(scrollable_frame, text="🌐 Browser Settings", padding=15)
            browser_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            self.headless_var = tk.BooleanVar(value=False)
            headless_cb = ttk.Checkbutton(
                browser_frame,
                text="Headless Mode",
                variable=self.headless_var
            )
            headless_cb.grid(row=0, column=0, sticky='w', pady=2)
            
            self.proxy_var = tk.BooleanVar(value=False)
            proxy_cb = ttk.Checkbutton(
                browser_frame,
                text="Use Proxy Rotation",
                variable=self.proxy_var
            )
            proxy_cb.grid(row=1, column=0, sticky='w', pady=2)
            
            # Save button
            save_frame = ttk.Frame(scrollable_frame)
            save_frame.pack(fill='x', pady=15, padx=10)
            
            save_btn = ttk.Button(
                save_frame,
                text="💾 Save Configuration",
                command=self.save_configuration,
                width=20
            )
            save_btn.pack()
    
    def create_statistics_tab(self, parent):
        """Create statistics tab with charts"""
        
        if USE_CUSTOMTKINTER:
            # Create main container
            main_frame = ctk.CTkFrame(parent)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Top stats
            top_frame = ctk.CTkFrame(main_frame)
            top_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(top_frame, text="📈 Campaign Statistics", 
                         font=('Segoe UI', 18, 'bold')).pack(anchor='w', padx=15, pady=15)
            
            # Stats grid
            stats_grid = ctk.CTkFrame(top_frame, fg_color='transparent')
            stats_grid.pack(fill='x', padx=15, pady=(0, 15))
            
            # Create 2x2 grid of stat cards
            self.stat_cards = {}
            stat_definitions = [
                ("total_sessions", "Total Sessions", "0"),
                ("success_rate", "Success Rate", "0%"),
                ("avg_watch_time", "Avg Watch Time", "0s"),
                ("detection_rate", "Detection Rate", "0%")
            ]
            
            for i, (key, title, default) in enumerate(stat_definitions):
                row = i // 2
                col = i % 2
                
                card = ctk.CTkFrame(stats_grid, corner_radius=10)
                card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                
                # Title
                ctk.CTkLabel(card, text=title, 
                             font=('Segoe UI', 12)).pack(pady=(15, 5))
                
                # Value
                value_label = ctk.CTkLabel(card, text=default, 
                                          font=('Segoe UI', 24, 'bold'))
                value_label.pack(pady=(0, 15))
                
                self.stat_cards[key] = value_label
            
            # Configure grid weights
            stats_grid.grid_columnconfigure(0, weight=1)
            stats_grid.grid_columnconfigure(1, weight=1)
            
            # Charts frame
            charts_frame = ctk.CTkFrame(main_frame)
            charts_frame.pack(fill='both', expand=True)
            
            ctk.CTkLabel(charts_frame, text="📊 Performance Charts", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Placeholder for charts
            chart_container = ctk.CTkFrame(charts_frame)
            chart_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
            
            chart_label = ctk.CTkLabel(
                chart_container,
                text="Charts will appear here when data is available\n\nRun a campaign to see statistics!",
                font=('Segoe UI', 14),
                justify='center'
            )
            chart_label.pack(expand=True)
            
            self.chart_container = chart_container
            
            # Refresh button
            refresh_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
            refresh_frame.pack(fill='x', pady=(0, 10))
            
            refresh_btn = ctk.CTkButton(
                refresh_frame,
                text="🔄 Refresh Statistics",
                command=self.refresh_statistics,
                width=200,
                height=35
            )
            refresh_btn.pack(pady=5)
            
        else:
            # Standard tkinter implementation
            main_frame = ttk.Frame(parent)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Top stats
            top_frame = ttk.LabelFrame(main_frame, text="📈 Campaign Statistics", padding=15)
            top_frame.pack(fill='x', pady=(0, 15))
            
            # Stats grid
            stats_grid = ttk.Frame(top_frame)
            stats_grid.pack(fill='x', pady=(0, 10))
            
            self.stat_cards = {}
            stat_definitions = [
                ("total_sessions", "Total Sessions", "0"),
                ("success_rate", "Success Rate", "0%"),
                ("avg_watch_time", "Avg Watch Time", "0s"),
                ("detection_rate", "Detection Rate", "0%")
            ]
            
            for i, (key, title, default) in enumerate(stat_definitions):
                row = i // 2
                col = i % 2
                
                card = ttk.LabelFrame(stats_grid, text=title, padding=10)
                card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                
                # Value
                value_label = ttk.Label(card, text=default, 
                                       font=('Segoe UI', 20, 'bold'))
                value_label.pack(pady=10)
                
                self.stat_cards[key] = value_label
            
            # Configure grid weights
            stats_grid.grid_columnconfigure(0, weight=1)
            stats_grid.grid_columnconfigure(1, weight=1)
            
            # Charts frame
            charts_frame = ttk.LabelFrame(main_frame, text="📊 Performance Charts", padding=15)
            charts_frame.pack(fill='both', expand=True)
            
            # Placeholder for charts
            chart_container = ttk.Frame(charts_frame)
            chart_container.pack(fill='both', expand=True)
            
            chart_label = ttk.Label(
                chart_container,
                text="Charts will appear here when data is available\n\nRun a campaign to see statistics!",
                font=('Segoe UI', 12),
                justify='center'
            )
            chart_label.pack(expand=True)
            
            self.chart_container = chart_container
            
            # Refresh button
            refresh_frame = ttk.Frame(main_frame)
            refresh_frame.pack(fill='x', pady=(0, 10))
            
            refresh_btn = ttk.Button(
                refresh_frame,
                text="🔄 Refresh Statistics",
                command=self.refresh_statistics,
                width=20
            )
            refresh_btn.pack(pady=5)
    
    def create_tools_tab(self, parent):
        """Create tools tab with utilities"""
        
        if USE_CUSTOMTKINTER:
            canvas = ctk.CTkScrollableFrame(parent)
            canvas.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Fingerprint Tools
            fp_frame = ctk.CTkFrame(canvas)
            fp_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(fp_frame, text="🖥️ Fingerprint Tools", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Generate fingerprint button
            fp_btn_frame = ctk.CTkFrame(fp_frame, fg_color='transparent')
            fp_btn_frame.pack(fill='x', padx=15, pady=(0, 10))
            
            gen_fp_btn = ctk.CTkButton(
                fp_btn_frame,
                text="Generate New Fingerprint",
                command=self.generate_fingerprint,
                width=200
            )
            gen_fp_btn.pack(side='left', padx=(0, 10))
            
            view_fp_btn = ctk.CTkButton(
                fp_btn_frame,
                text="View Current Fingerprint",
                command=self.view_fingerprint,
                width=200
            )
            view_fp_btn.pack(side='left')
            
            # Proxy Tools
            proxy_frame = ctk.CTkFrame(canvas)
            proxy_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(proxy_frame, text="🌐 Proxy Tools", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            proxy_btn_frame = ctk.CTkFrame(proxy_frame, fg_color='transparent')
            proxy_btn_frame.pack(fill='x', padx=15, pady=(0, 10))
            
            test_proxy_btn = ctk.CTkButton(
                proxy_btn_frame,
                text="Test Proxy Connection",
                command=self.test_proxy,
                width=200
            )
            test_proxy_btn.pack(side='left', padx=(0, 10))
            
            rotate_proxy_btn = ctk.CTkButton(
                proxy_btn_frame,
                text="Rotate Proxy",
                command=self.rotate_proxy,
                width=200
            )
            rotate_proxy_btn.pack(side='left')
            
            # Data Tools
            data_frame = ctk.CTkFrame(canvas)
            data_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(data_frame, text="📁 Data Tools", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            data_btn_frame = ctk.CTkFrame(data_frame, fg_color='transparent')
            data_btn_frame.pack(fill='x', padx=15, pady=(0, 10))
            
            export_csv_btn = ctk.CTkButton(
                data_btn_frame,
                text="Export to CSV",
                command=lambda: self.export_data('csv'),
                width=200
            )
            export_csv_btn.pack(side='left', padx=(0, 10))
            
            export_json_btn = ctk.CTkButton(
                data_btn_frame,
                text="Export to JSON",
                command=lambda: self.export_data('json'),
                width=200
            )
            export_json_btn.pack(side='left')
            
            # System Tools
            system_frame = ctk.CTkFrame(canvas)
            system_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(system_frame, text="⚙️ System Tools", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            system_btn_frame = ctk.CTkFrame(system_frame, fg_color='transparent')
            system_btn_frame.pack(fill='x', padx=15, pady=(0, 10))
            
            clear_cache_btn = ctk.CTkButton(
                system_btn_frame,
                text="Clear Cache",
                command=self.clear_cache,
                width=200
            )
            clear_cache_btn.pack(side='left', padx=(0, 10))
            
            test_connection_btn = ctk.CTkButton(
                system_btn_frame,
                text="Test YouTube Connection",
                command=self.test_youtube_connection,
                width=200
            )
            test_connection_btn.pack(side='left')
            
        else:
            # Standard tkinter implementation
            canvas = tk.Canvas(parent, bg='#1e1e1e', highlightthickness=0)
            scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Fingerprint Tools
            fp_frame = ttk.LabelFrame(scrollable_frame, text="🖥️ Fingerprint Tools", padding=15)
            fp_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            fp_btn_frame = ttk.Frame(fp_frame)
            fp_btn_frame.pack(fill='x', pady=(0, 10))
            
            gen_fp_btn = ttk.Button(
                fp_btn_frame,
                text="Generate New Fingerprint",
                command=self.generate_fingerprint,
                width=25
            )
            gen_fp_btn.pack(side='left', padx=(0, 10))
            
            view_fp_btn = ttk.Button(
                fp_btn_frame,
                text="View Current Fingerprint",
                command=self.view_fingerprint,
                width=25
            )
            view_fp_btn.pack(side='left')
            
            # Proxy Tools
            proxy_frame = ttk.LabelFrame(scrollable_frame, text="🌐 Proxy Tools", padding=15)
            proxy_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            proxy_btn_frame = ttk.Frame(proxy_frame)
            proxy_btn_frame.pack(fill='x', pady=(0, 10))
            
            test_proxy_btn = ttk.Button(
                proxy_btn_frame,
                text="Test Proxy Connection",
                command=self.test_proxy,
                width=25
            )
            test_proxy_btn.pack(side='left', padx=(0, 10))
            
            rotate_proxy_btn = ttk.Button(
                proxy_btn_frame,
                text="Rotate Proxy",
                command=self.rotate_proxy,
                width=25
            )
            rotate_proxy_btn.pack(side='left')
            
            # Data Tools
            data_frame = ttk.LabelFrame(scrollable_frame, text="📁 Data Tools", padding=15)
            data_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            data_btn_frame = ttk.Frame(data_frame)
            data_btn_frame.pack(fill='x', pady=(0, 10))
            
            export_csv_btn = ttk.Button(
                data_btn_frame,
                text="Export to CSV",
                command=lambda: self.export_data('csv'),
                width=25
            )
            export_csv_btn.pack(side='left', padx=(0, 10))
            
            export_json_btn = ttk.Button(
                data_btn_frame,
                text="Export to JSON",
                command=lambda: self.export_data('json'),
                width=25
            )
            export_json_btn.pack(side='left')
            
            # System Tools
            system_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ System Tools", padding=15)
            system_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            system_btn_frame = ttk.Frame(system_frame)
            system_btn_frame.pack(fill='x', pady=(0, 10))
            
            clear_cache_btn = ttk.Button(
                system_btn_frame,
                text="Clear Cache",
                command=self.clear_cache,
                width=25
            )
            clear_cache_btn.pack(side='left', padx=(0, 10))
            
            test_connection_btn = ttk.Button(
                system_btn_frame,
                text="Test YouTube Connection",
                command=self.test_youtube_connection,
                width=25
            )
            test_connection_btn.pack(side='left')
    
    def create_logs_tab(self, parent):
        """Create logs tab"""
        
        if USE_CUSTOMTKINTER:
            main_frame = ctk.CTkFrame(parent)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Log controls
            control_frame = ctk.CTkFrame(main_frame)
            control_frame.pack(fill='x', pady=(0, 10))
            
            ctk.CTkLabel(control_frame, text="📝 Session Logs", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=15)
            
            # Log level selector
            log_frame = ctk.CTkFrame(control_frame, fg_color='transparent')
            log_frame.pack(fill='x', padx=15, pady=(0, 15))
            
            ctk.CTkLabel(log_frame, text="Log Level:", 
                         font=('Segoe UI', 12)).pack(side='left', padx=(0, 10))
            
            self.log_level_var = tk.StringVar(value="INFO")
            log_level_menu = ctk.CTkOptionMenu(
                log_frame,
                values=["DEBUG", "INFO", "WARNING", "ERROR"],
                variable=self.log_level_var,
                width=120
            )
            log_level_menu.pack(side='left', padx=(0, 20))
            
            # Log action buttons
            action_frame = ctk.CTkFrame(log_frame, fg_color='transparent')
            action_frame.pack(side='left')
            
            clear_logs_btn = ctk.CTkButton(
                action_frame,
                text="Clear Logs",
                command=self.clear_logs,
                width=100
            )
            clear_logs_btn.pack(side='left', padx=(0, 10))
            
            save_logs_btn = ctk.CTkButton(
                action_frame,
                text="Save Logs",
                command=self.save_logs,
                width=100
            )
            save_logs_btn.pack(side='left')
            
            # Log display
            log_display_frame = ctk.CTkFrame(main_frame)
            log_display_frame.pack(fill='both', expand=True)
            
            # Create text widget for logs
            self.log_text = scrolledtext.ScrolledText(
                log_display_frame,
                bg='#2d2d2d',
                fg='#ffffff',
                font=('Consolas', 10),
                wrap='word'
            )
            self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Add initial message
            self.log_message("System initialized", "INFO")
            
        else:
            main_frame = ttk.Frame(parent)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Log controls
            control_frame = ttk.LabelFrame(main_frame, text="📝 Session Logs", padding=15)
            control_frame.pack(fill='x', pady=(0, 10))
            
            # Log level selector
            log_frame = ttk.Frame(control_frame)
            log_frame.pack(fill='x', pady=(0, 10))
            
            ttk.Label(log_frame, text="Log Level:").pack(side='left', padx=(0, 10))
            
            self.log_level_var = tk.StringVar(value="INFO")
            log_level_menu = ttk.Combobox(
                log_frame,
                textvariable=self.log_level_var,
                values=["DEBUG", "INFO", "WARNING", "ERROR"],
                width=10,
                state='readonly'
            )
            log_level_menu.pack(side='left', padx=(0, 20))
            
            # Log action buttons
            action_frame = ttk.Frame(log_frame)
            action_frame.pack(side='left')
            
            clear_logs_btn = ttk.Button(
                action_frame,
                text="Clear Logs",
                command=self.clear_logs,
                width=12
            )
            clear_logs_btn.pack(side='left', padx=(0, 10))
            
            save_logs_btn = ttk.Button(
                action_frame,
                text="Save Logs",
                command=self.save_logs,
                width=12
            )
            save_logs_btn.pack(side='left')
            
            # Log display
            log_display_frame = ttk.Frame(main_frame)
            log_display_frame.pack(fill='both', expand=True)
            
            # Create text widget for logs
            self.log_text = scrolledtext.ScrolledText(
                log_display_frame,
                bg='#2d2d2d',
                fg='#ffffff',
                font=('Consolas', 10),
                wrap='word'
            )
            self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Add initial message
            self.log_message("System initialized", "INFO")
    
    def create_about_tab(self, parent):
        """Create about tab with information"""
        
        if USE_CUSTOMTKINTER:
            canvas = ctk.CTkScrollableFrame(parent)
            canvas.pack(fill='both', expand=True, padx=10, pady=10)
            
            # About section
            about_frame = ctk.CTkFrame(canvas)
            about_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(about_frame, text="ℹ️ About YouTube HumanWatch Pro", 
                         font=('Segoe UI', 18, 'bold')).pack(anchor='w', padx=15, pady=15)
            
            about_text = """
            YouTube HumanWatch Pro is an advanced educational tool designed for:
            
            • University projects and research
            • Learning web automation techniques
            • Understanding browser fingerprinting
            • Studying anti-detection systems
            • Educational demonstrations
            
            Version: 3.0
            Author: University Project Team
            Purpose: Educational Research Only
            
            ⚠️ IMPORTANT:
            This software is for EDUCATIONAL PURPOSES ONLY.
            DO NOT use to manipulate YouTube metrics.
            Violates YouTube Terms of Service.
            """
            
            about_label = ctk.CTkLabel(
                about_frame,
                text=about_text,
                font=('Segoe UI', 12),
                justify='left',
                wraplength=600
            )
            about_label.pack(anchor='w', padx=20, pady=(0, 15))
            
            # Features section
            features_frame = ctk.CTkFrame(canvas)
            features_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(features_frame, text="✨ Key Features", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            features_text = """
            • Advanced browser fingerprint rotation
            • Human-like behavior simulation
            • Residential proxy support
            • Real-time statistics and monitoring
            • Campaign management system
            • Risk assessment and detection avoidance
            • Educational presentation tools
            • Data export capabilities
            """
            
            features_label = ctk.CTkLabel(
                features_frame,
                text=features_text,
                font=('Segoe UI', 12),
                justify='left',
                wraplength=600
            )
            features_label.pack(anchor='w', padx=20, pady=(0, 15))
            
            # System Requirements
            req_frame = ctk.CTkFrame(canvas)
            req_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(req_frame, text="💻 System Requirements", 
                         font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))
            
            req_text = """
            • Python 3.8 or higher
            • 4GB RAM minimum (8GB recommended)
            • Stable internet connection
            • Chrome/Firefox browser installed
            • Administrator privileges for browser control
            """
            
            req_label = ctk.CTkLabel(
                req_frame,
                text=req_text,
                font=('Segoe UI', 12),
                justify='left',
                wraplength=600
            )
            req_label.pack(anchor='w', padx=20, pady=(0, 15))
            
            # Disclaimer
            disclaimer_frame = ctk.CTkFrame(canvas, fg_color='#f44336', corner_radius=5)
            disclaimer_frame.pack(fill='x', pady=(0, 15))
            
            disclaimer_text = """
            ⚠️ ETHICAL DISCLAIMER:
            
            This software is for EDUCATIONAL USE ONLY.
            Using it to manipulate YouTube metrics violates YouTube's Terms of Service
            and may result in account termination or legal action.
            
            By using this software, you agree to use it only for educational purposes
            and accept full responsibility for your actions.
            """
            
            disclaimer_label = ctk.CTkLabel(
                disclaimer_frame,
                text=disclaimer_text,
                font=('Segoe UI', 12, 'bold'),
                justify='left',
                wraplength=600,
                text_color='white'
            )
            disclaimer_label.pack(anchor='w', padx=15, pady=15)
            
        else:
            canvas = tk.Canvas(parent, bg='#1e1e1e', highlightthickness=0)
            scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # About section
            about_frame = ttk.LabelFrame(scrollable_frame, text="ℹ️ About YouTube HumanWatch Pro", padding=15)
            about_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            about_text = """
            YouTube HumanWatch Pro is an advanced educational tool designed for:
            
            • University projects and research
            • Learning web automation techniques
            • Understanding browser fingerprinting
            • Studying anti-detection systems
            • Educational demonstrations
            
            Version: 3.0
            Author: University Project Team
            Purpose: Educational Research Only
            
            ⚠️ IMPORTANT:
            This software is for EDUCATIONAL PURPOSES ONLY.
            DO NOT use to manipulate YouTube metrics.
            Violates YouTube Terms of Service.
            """
            
            about_label = ttk.Label(
                about_frame,
                text=about_text,
                font=('Segoe UI', 10),
                justify='left',
                wraplength=600
            )
            about_label.pack(anchor='w', pady=(0, 10))
            
            # Features section
            features_frame = ttk.LabelFrame(scrollable_frame, text="✨ Key Features", padding=15)
            features_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            features_text = """
            • Advanced browser fingerprint rotation
            • Human-like behavior simulation
            • Residential proxy support
            • Real-time statistics and monitoring
            • Campaign management system
            • Risk assessment and detection avoidance
            • Educational presentation tools
            • Data export capabilities
            """
            
            features_label = ttk.Label(
                features_frame,
                text=features_text,
                font=('Segoe UI', 10),
                justify='left',
                wraplength=600
            )
            features_label.pack(anchor='w', pady=(0, 10))
            
            # System Requirements
            req_frame = ttk.LabelFrame(scrollable_frame, text="💻 System Requirements", padding=15)
            req_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            req_text = """
            • Python 3.8 or higher
            • 4GB RAM minimum (8GB recommended)
            • Stable internet connection
            • Chrome/Firefox browser installed
            • Administrator privileges for browser control
            """
            
            req_label = ttk.Label(
                req_frame,
                text=req_text,
                font=('Segoe UI', 10),
                justify='left',
                wraplength=600
            )
            req_label.pack(anchor='w', pady=(0, 10))
            
            # Disclaimer
            disclaimer_frame = ttk.Frame(scrollable_frame)
            disclaimer_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            disclaimer_text = """
            ⚠️ ETHICAL DISCLAIMER:
            
            This software is for EDUCATIONAL USE ONLY.
            Using it to manipulate YouTube metrics violates YouTube's Terms of Service
            and may result in account termination or legal action.
            
            By using this software, you agree to use it only for educational purposes
            and accept full responsibility for your actions.
            """
            
            disclaimer_label = ttk.Label(
                disclaimer_frame,
                text=disclaimer_text,
                font=('Segoe UI', 10, 'bold'),
                justify='left',
                wraplength=600,
                foreground='#f44336'
            )
            disclaimer_label.pack(anchor='w', pady=(0, 10))
    
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        
        if USE_CUSTOMTKINTER:
            status_frame = ctk.CTkFrame(parent, height=30)
            status_frame.pack(fill='x', side='bottom')
            status_frame.pack_propagate(False)
            
            # Status label
            self.status_label = ctk.CTkLabel(
                status_frame,
                text="🟢 Ready",
                font=('Segoe UI', 11)
            )
            self.status_label.pack(side='left', padx=15)
            
            # Session count
            self.session_count_label = ctk.CTkLabel(
                status_frame,
                text="Sessions: 0",
                font=('Segoe UI', 11)
            )
            self.session_count_label.pack(side='right', padx=15)
            
            # Memory usage
            self.memory_label = ctk.CTkLabel(
                status_frame,
                text="Memory: --",
                font=('Segoe UI', 11)
            )
            self.memory_label.pack(side='right', padx=15)
            
            # Uptime
            self.uptime_label = ctk.CTkLabel(
                status_frame,
                text="Uptime: 00:00:00",
                font=('Segoe UI', 11)
            )
            self.uptime_label.pack(side='right', padx=15)
            
        else:
            status_frame = ttk.Frame(parent, height=30)
            status_frame.pack(fill='x', side='bottom')
            status_frame.pack_propagate(False)
            
            # Status label
            self.status_label = ttk.Label(
                status_frame,
                text="🟢 Ready",
                font=('Segoe UI', 10)
            )
            self.status_label.pack(side='left', padx=15)
            
            # Session count
            self.session_count_label = ttk.Label(
                status_frame,
                text="Sessions: 0",
                font=('Segoe UI', 10)
            )
            self.session_count_label.pack(side='right', padx=15)
            
            # Memory usage
            self.memory_label = ttk.Label(
                status_frame,
                text="Memory: --",
                font=('Segoe UI', 10)
            )
            self.memory_label.pack(side='right', padx=15)
            
            # Uptime
            self.uptime_label = ttk.Label(
                status_frame,
                text="Uptime: 00:00:00",
                font=('Segoe UI', 10)
            )
            self.uptime_label.pack(side='right', padx=15)
    
    def start_background_tasks(self):
        """Start background update tasks"""
        self.start_time = time.time()
        self.root.after(1000, self.update_status)
        self.root.after(2000, self.update_memory_usage)
        self.root.after(30000, self.auto_save_logs)
    
    def update_status(self):
        """Update status bar"""
        # Update uptime
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        self.uptime_label.configure(text=f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update session count
        self.session_count_label.configure(text=f"Sessions: {self.stats['total_sessions']}")
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def update_memory_usage(self):
        """Update memory usage display"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_label.configure(text=f"Memory: {memory_mb:.1f} MB")
        except:
            self.memory_label.configure(text="Memory: N/A")
        
        # Schedule next update
        self.root.after(5000, self.update_memory_usage)
    
    def auto_save_logs(self):
        """Auto-save logs periodically"""
        try:
            logs = self.log_text.get(1.0, tk.END)
            if logs.strip():
                with open('logs/gui_logs.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n=== Auto-save at {datetime.now()} ===\n")
                    f.write(logs[-50000:])  # Last 50KB
        except:
            pass
        
        # Schedule next auto-save
        self.root.after(300000, self.auto_save_logs)  # Every 5 minutes
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log display"""
        
        # Check log level
        log_levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        current_level = log_levels.get(self.log_level_var.get(), 1)
        message_level = log_levels.get(level, 1)
        
        if message_level < current_level:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Color coding for log levels
        colors = {
            "DEBUG": "#888888",
            "INFO": "#ffffff",
            "WARNING": "#ff9900",
            "ERROR": "#ff4444"
        }
        
        if USE_CUSTOMTKINTER:
            # Insert with color
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        else:
            # Insert with color
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
    
    # ====== Event Handlers ======
    
    def quick_start(self):
        """Quick start a test campaign"""
        self.log_message("Starting quick test campaign", "INFO")
        
        # Use default settings
        url = self.url_entry.get()
        sessions = self.session_var.get()
        priority = SessionPriority[self.priority_var.get().upper()]
        
        self.start_campaign_thread(url, sessions, priority)
    
    def start_campaign(self):
        """Start a campaign with current settings"""
        url = self.url_entry.get()
        if not url or "youtube.com" not in url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        sessions = self.session_var.get()
        priority = SessionPriority[self.priority_var.get().upper()]
        
        # Confirm before starting
        response = messagebox.askyesno(
            "Confirm Campaign",
            f"Start campaign with:\n"
            f"• URL: {url[:50]}...\n"
            f"• Sessions: {sessions}\n"
            f"• Priority: {priority.value}\n\n"
            f"Remember: For educational use only!"
        )
        
        if response:
            self.log_message(f"Starting campaign: {sessions} sessions at {priority.value} priority", "INFO")
            self.start_campaign_thread(url, sessions, priority)
    
    def start_campaign_thread(self, url: str, sessions: int, priority: SessionPriority):
        """Start campaign in background thread"""
        
        if self.is_running:
            messagebox.showwarning("Warning", "A campaign is already running!")
            return
        
        # Update UI
        self.is_running = True
        self.start_campaign_btn.configure(state='disabled')
        self.pause_campaign_btn.configure(state='normal')
        self.stop_campaign_btn.configure(state='normal')
        self.emergency_stop_btn.configure(state='normal')
        self.status_label.configure(text="🟡 Campaign running...")
        
        # Initialize bot if needed
        if not self.orchestrator:
            self.orchestrator = SessionOrchestrator()
        
        # Start campaign in background thread
        thread = threading.Thread(
            target=self.run_campaign_async,
            args=(url, sessions, priority),
            daemon=True
        )
        thread.start()
    
    def run_campaign_async(self, url: str, sessions: int, priority: SessionPriority):
        """Run campaign asynchronously"""
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            self.log_message(f"Campaign started: {sessions} sessions for {url}", "INFO")
            
            # Run campaign
            result = loop.run_until_complete(
                self.orchestrator.run_campaign(url, sessions, priority)
            )
            
            # Update UI with results
            self.root.after(0, self.campaign_completed, result)
            
        except Exception as e:
            error_msg = f"Campaign failed: {str(e)}"
            self.log_message(error_msg, "ERROR")
            self.root.after(0, lambda: messagebox.showerror("Campaign Failed", error_msg))
            self.root.after(0, self.reset_campaign_state)
        
        finally:
            loop.close()
    
    def campaign_completed(self, result: Dict[str, Any]):
        """Handle campaign completion"""
        
        success_rate = result['results']['success_rate'] * 100
        total_watch = result['results']['total_watch_time']
        
        # Update statistics
        self.stats['total_sessions'] += result['plan'].total_sessions
        self.stats['successful_sessions'] += result['results']['successful_sessions']
        self.stats['failed_sessions'] += result['results']['failed_sessions']
        self.stats['total_watch_time'] += total_watch
        self.stats['detection_events'] += result['results']['detection_events']
        
        # Update UI
        self.is_running = False
        self.start_campaign_btn.configure(state='normal')
        self.pause_campaign_btn.configure(state='disabled')
        self.stop_campaign_btn.configure(state='disabled')
        self.emergency_stop_btn.configure(state='disabled')
        self.status_label.configure(text="🟢 Campaign completed")
        
        # Update progress bar
        self.progress_bar.set(1.0)
        self.progress_label.configure(text=f"{result['plan'].total_sessions}/{result['plan'].total_sessions} sessions completed")
        
        # Update stat cards
        self.update_stat_cards()
        
        # Show completion message
        message = (
            f"Campaign completed!\n\n"
            f"• Success Rate: {success_rate:.1f}%\n"
            f"• Total Watch Time: {total_watch/60:.1f} minutes\n"
            f"• Detection Events: {result['results']['detection_events']}\n\n"
            f"View detailed results in the Logs tab."
        )
        
        self.log_message(f"Campaign completed: {success_rate:.1f}% success rate", "INFO")
        messagebox.showinfo("Campaign Complete", message)
    
    def pause_campaign(self):
        """Pause the current campaign"""
        self.log_message("Campaign paused", "WARNING")
        self.status_label.configure(text="🟡 Campaign paused")
        # Implement actual pause logic here
    
    def stop_campaign(self):
        """Stop the current campaign"""
        response = messagebox.askyesno("Stop Campaign", "Are you sure you want to stop the campaign?")
        if response:
            self.log_message("Campaign stopped by user", "WARNING")
            self.reset_campaign_state()
            messagebox.showinfo("Campaign Stopped", "Campaign has been stopped.")
    
    def emergency_stop(self):
        """Emergency stop everything"""
        response = messagebox.askyesno(
            "Emergency Stop",
            "⚠️ EMERGENCY STOP ⚠️\n\n"
            "This will immediately stop all sessions and browsers.\n"
            "Any unsaved data will be lost.\n\n"
            "Are you sure?"
        )
        
        if response:
            self.log_message("EMERGENCY STOP activated", "ERROR")
            self.reset_campaign_state()
            
            # Force kill any remaining processes
            import subprocess
            try:
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
                subprocess.run(["taskkill", "/F", "/IM", "firefox.exe"], capture_output=True)
            except:
                pass
            
            messagebox.showinfo("Emergency Stop", "All processes have been terminated.")
    
    def reset_campaign_state(self):
        """Reset campaign state"""
        self.is_running = False
        self.start_campaign_btn.configure(state='normal')
        self.pause_campaign_btn.configure(state='disabled')
        self.stop_campaign_btn.configure(state='disabled')
        self.emergency_stop_btn.configure(state='disabled')
        self.status_label.configure(text="🟢 Ready")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0/0 sessions completed")
    
    def save_configuration(self):
        """Save current configuration"""
        try:
            # Update config with GUI values
            self.config['stealth_settings']['enabled'] = True
            self.config['behavior_settings']['enabled'] = True
            self.config['session_settings']['max_sessions'] = self.session_var.get()
            self.config['browser_settings']['headless'] = self.headless_var.get()
            self.config['network_settings']['use_proxy'] = self.proxy_var.get()
            
            # Save to file
            with open('config_advanced.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.log_message("Configuration saved", "INFO")
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            self.log_message(f"Failed to save configuration: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def refresh_statistics(self):
        """Refresh statistics display"""
        try:
            # Update stat cards
            self.update_stat_cards()
            
            # Update live monitoring
            self.active_sessions_label.configure(text=f"Active Sessions: {len(self.active_sessions)}")
            
            if self.stats['total_sessions'] > 0:
                success_rate = (self.stats['successful_sessions'] / self.stats['total_sessions']) * 100
                self.success_rate_label.configure(text=f"Success Rate: {success_rate:.1f}%")
                self.total_watch_label.configure(text=f"Total Watch Time: {self.stats['total_watch_time']}s")
                self.detection_label.configure(text=f"Detection Events: {self.stats['detection_events']}")
            
            self.log_message("Statistics refreshed", "INFO")
            
        except Exception as e:
            self.log_message(f"Failed to refresh statistics: {e}", "ERROR")
    
    def update_stat_cards(self):
        """Update statistic cards"""
        if self.stats['total_sessions'] > 0:
            success_rate = (self.stats['successful_sessions'] / self.stats['total_sessions']) * 100
            avg_watch = self.stats['total_watch_time'] / self.stats['successful_sessions'] if self.stats['successful_sessions'] > 0 else 0
            detection_rate = (self.stats['detection_events'] / self.stats['total_sessions']) * 100
            
            self.stat_cards['total_sessions'].configure(text=str(self.stats['total_sessions']))
            self.stat_cards['success_rate'].configure(text=f"{success_rate:.1f}%")
            self.stat_cards['avg_watch_time'].configure(text=f"{avg_watch:.0f}s")
            self.stat_cards['detection_rate'].configure(text=f"{detection_rate:.1f}%")
    
    def generate_fingerprint(self):
        """Generate a new fingerprint"""
        try:
            if not self.fingerprint_rotator:
                self.fingerprint_rotator = create_fingerprint_rotator()
            
            fingerprint = self.fingerprint_rotator.generate_fingerprint()
            self.log_message(f"Generated fingerprint: {fingerprint.session_id}", "INFO")
            
            # Show fingerprint details
            details = (
                f"Fingerprint Generated:\n\n"
                f"• Session ID: {fingerprint.session_id}\n"
                f"• User Agent: {fingerprint.user_agent[:80]}...\n"
                f"• Screen: {fingerprint.screen_width}x{fingerprint.screen_height}\n"
                f"• Platform: {fingerprint.platform}\n"
                f"• Locale: {fingerprint.locale}\n"
                f"• Timezone: {fingerprint.timezone}"
            )
            
            messagebox.showinfo("Fingerprint Generated", details)
            
        except Exception as e:
            self.log_message(f"Failed to generate fingerprint: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to generate fingerprint: {e}")
    
    def view_fingerprint(self):
        """View current fingerprint"""
        try:
            if not self.fingerprint_rotator or not self.fingerprint_rotator.current_fingerprint:
                messagebox.showinfo("No Fingerprint", "No fingerprint has been generated yet.")
                return
            
            fp = self.fingerprint_rotator.current_fingerprint
            
            # Create a new window to display fingerprint details
            if USE_CUSTOMTKINTER:
                fp_window = ctk.CTkToplevel(self.root)
                fp_window.title("Current Fingerprint")
                fp_window.geometry("800x600")
            else:
                fp_window = tk.Toplevel(self.root)
                fp_window.title("Current Fingerprint")
                fp_window.geometry("800x600")
                fp_window.configure(bg='#1e1e1e')
            
            # Add scrollable text widget
            text_widget = scrolledtext.ScrolledText(
                fp_window,
                bg='#2d2d2d',
                fg='#ffffff',
                font=('Consolas', 10),
                wrap='word'
            )
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Format fingerprint data as JSON
            fp_dict = fp.to_dict()
            formatted_json = json.dumps(fp_dict, indent=2, default=str)
            
            text_widget.insert(1.0, formatted_json)
            text_widget.configure(state='disabled')
            
            self.log_message("Displayed current fingerprint", "INFO")
            
        except Exception as e:
            self.log_message(f"Failed to view fingerprint: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to view fingerprint: {e}")
    
    def test_proxy(self):
        """Test proxy connection"""
        self.log_message("Proxy test requested", "INFO")
        # Implement proxy testing logic here
        messagebox.showinfo("Proxy Test", "Proxy test functionality will be implemented in a future version.")
    
    def rotate_proxy(self):
        """Rotate to a new proxy"""
        self.log_message("Proxy rotation requested", "INFO")
        # Implement proxy rotation logic here
        messagebox.showinfo("Proxy Rotation", "Proxy rotation functionality will be implemented in a future version.")
    
    def export_data(self, format_type: str):
        """Export data to file"""
        try:
            # Get filename from user
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=[(f"{format_type.upper()} files", f"*.{format_type}"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            # Export data
            if format_type == 'csv':
                # Create sample data
                data = pd.DataFrame({
                    'timestamp': [datetime.now().isoformat()],
                    'sessions': [self.stats['total_sessions']],
                    'success_rate': [(self.stats['successful_sessions'] / self.stats['total_sessions'] * 100) if self.stats['total_sessions'] > 0 else 0],
                    'total_watch_time': [self.stats['total_watch_time']]
                })
                data.to_csv(filename, index=False)
                
            elif format_type == 'json':
                export_data = {
                    'statistics': self.stats,
                    'timestamp': datetime.now().isoformat(),
                    'config': self.config
                }
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
            
            self.log_message(f"Data exported to {filename}", "INFO")
            messagebox.showinfo("Export Successful", f"Data exported to:\n{filename}")
            
        except Exception as e:
            self.log_message(f"Failed to export data: {e}", "ERROR")
            messagebox.showerror("Export Failed", f"Failed to export data: {e}")
    
    def clear_cache(self):
        """Clear application cache"""
        response = messagebox.askyesno(
            "Clear Cache",
            "Clear all cached data and temporary files?\n\n"
            "This will remove:\n"
            "• Browser cache\n"
            "• Temporary files\n"
            "• Session logs\n\n"
            "Configuration files will be preserved."
        )
        
        if response:
            try:
                import shutil
                import os
                
                # Clear browser cache directories
                cache_dirs = [
                    'browser_cache',
                    'temp',
                    'logs'
                ]
                
                for dir_name in cache_dirs:
                    if os.path.exists(dir_name):
                        shutil.rmtree(dir_name)
                        os.makedirs(dir_name)
                
                # Clear log display
                self.log_text.delete(1.0, tk.END)
                self.log_message("Cache cleared", "INFO")
                
                messagebox.showinfo("Cache Cleared", "All cache has been cleared successfully.")
                
            except Exception as e:
                self.log_message(f"Failed to clear cache: {e}", "ERROR")
                messagebox.showerror("Error", f"Failed to clear cache: {e}")
    
    def test_youtube_connection(self):
        """Test connection to YouTube"""
        self.log_message("Testing YouTube connection", "INFO")
        
        # Run test in background thread
        thread = threading.Thread(target=self.test_connection_thread, daemon=True)
        thread.start()
    
    def test_connection_thread(self):
        """Test connection in background thread"""
        import requests
        
        try:
            # Update UI
            self.root.after(0, lambda: self.status_label.configure(text="🟡 Testing connection..."))
            
            # Test connection
            response = requests.get("https://www.youtube.com", timeout=10)
            
            if response.status_code == 200:
                self.root.after(0, lambda: self.status_label.configure(text="🟢 Connection successful"))
                self.root.after(0, lambda: messagebox.showinfo("Connection Test", "✅ Successfully connected to YouTube!"))
                self.log_message("YouTube connection test: SUCCESS", "INFO")
            else:
                self.root.after(0, lambda: self.status_label.configure(text="🔴 Connection failed"))
                self.root.after(0, lambda: messagebox.showerror("Connection Test", f"❌ Failed to connect to YouTube (HTTP {response.status_code})"))
                self.log_message(f"YouTube connection test: FAILED (HTTP {response.status_code})", "ERROR")
                
        except Exception as e:
            self.root.after(0, lambda: self.status_label.configure(text="🔴 Connection failed"))
            self.root.after(0, lambda: messagebox.showerror("Connection Test", f"❌ Connection error: {str(e)}"))
            self.log_message(f"YouTube connection test: ERROR - {str(e)}", "ERROR")
        
        finally:
            self.root.after(3000, lambda: self.status_label.configure(text="🟢 Ready"))
    
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Logs cleared", "INFO")
    
    def save_logs(self):
        """Save logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
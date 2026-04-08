import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import time
import collections

# ===================== UI CONSTANTS =====================
BG_MAIN = "#0d1117"        # Dark Navy (GitHub style)
BG_CARD = "#161b22"        # Lighter Navy for cards
HEADER_BG = "#21262d"      # Header gray
TEXT_PRIMARY = "#c9d1d9"   # Off-white text
ACCENT_BLUE = "#58a6ff"    # INFO / Latency
ACCENT_RED = "#da3633"     # ERROR / DROPPED
ACCENT_GREEN = "#238636"   # SUCCESS / WRITTEN
ACCENT_YELLOW = "#d29922"  # WARN
# ========================================================

class EnterpriseNOC:
    def __init__(self, root):
        self.root = root
        self.root.title("PES Distributed Analytics Console - V6.0 Enterprise")
        self.root.geometry("1600x950")
        self.root.configure(bg=BG_MAIN)

        # Persistence & State Tracking
        self.log_file = "aggregated_logs.txt"
        self.last_pos = 0
        self.processed = 0
        self.dropped = 0
        self.latency_history = collections.deque(maxlen=60)
        self.throughput_history = collections.deque(maxlen=50)
        self.machine_data = {}  # {machine_id: {'total': 0, 'errors': 0, 'last_seen': ''}}
        self.is_running = True
        self.last_rollup = time.time()

        self.setup_ui()
        self.start_log_polling()

    def setup_ui(self):
        """Builds a high-density, professional command center interface."""
        
        # --- 1. Top Navigation Bar ---
        header = tk.Frame(self.root, bg=HEADER_BG, height=70)
        header.pack(fill="x", side="top")
        
        tk.Label(header, text="SYSTEM NETWORK OPERATIONS CENTER", 
                 font=("Consolas", 22, "bold"), fg=ACCENT_BLUE, bg=HEADER_BG).pack(side="left", padx=30, pady=15)

        # Control Cluster
        ctrl_frame = tk.Frame(header, bg=HEADER_BG)
        ctrl_frame.pack(side="right", padx=25)

        tk.Label(ctrl_frame, text="SEARCH:", fg=TEXT_PRIMARY, bg=HEADER_BG, font=("Arial", 9, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(ctrl_frame, textvariable=self.search_var, bg=BG_MAIN, 
                 fg="white", insertbackground="white", bd=0, width=20).pack(side="left", padx=10, pady=15)

        self.filter_var = tk.StringVar(value="ALL LEVELS")
        ttk.Combobox(ctrl_frame, textvariable=self.filter_var, 
                     values=["ALL LEVELS", "INFO", "WARN", "ERROR"], width=12).pack(side="left", padx=10)

        self.pause_btn = tk.Button(ctrl_frame, text="PAUSE TELEMETRY", command=self.toggle_pause, 
                                   bg=ACCENT_YELLOW, font=("Arial", 9, "bold"), relief="flat", padx=10)
        self.pause_btn.pack(side="left", padx=10)

        # --- 2. KPI Metrics Ribbon (Top Cards) ---
        kpi_frame = tk.Frame(self.root, bg=BG_MAIN)
        kpi_frame.pack(fill="x", padx=15, pady=10)

        self.card_total = self.create_card(kpi_frame, "TOTAL PROCESSED", "white")
        self.card_dropped = self.create_card(kpi_frame, "PACKETS DROPPED", ACCENT_RED)
        self.card_latency = self.create_card(kpi_frame, "AVG JITTER (MS)", ACCENT_BLUE)
        self.card_health = self.create_card(kpi_frame, "SYSTEM HEALTH", ACCENT_GREEN)

        # --- 3. Main Data Workspace (Dual Pane) ---
        workspace = tk.Frame(self.root, bg=BG_MAIN)
        workspace.pack(fill="both", expand=True, padx=15)

        # LHS Pane: Incoming Stream
        l_frame = tk.Frame(workspace, bg=BG_CARD, bd=1, relief="flat")
        l_frame.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(l_frame, text="LHS: RAW INCOMING STREAM", bg=BG_CARD, fg="#8b949e", font=("Arial", 10, "bold")).pack(pady=5)
        self.lhs_box = scrolledtext.ScrolledText(l_frame, bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Consolas", 10), bd=0)
        self.lhs_box.pack(fill="both", expand=True, padx=2, pady=2)

        # RHS Pane: Processing Stream
        r_frame = tk.Frame(workspace, bg=BG_CARD, bd=1, relief="flat")
        r_frame.pack(side="right", fill="both", expand=True, padx=5)
        tk.Label(r_frame, text="RHS: FINAL VERDICT STREAM", bg=BG_CARD, fg=ACCENT_GREEN, font=("Arial", 10, "bold")).pack(pady=5)
        self.rhs_box = scrolledtext.ScrolledText(r_frame, bg=BG_MAIN, fg=TEXT_PRIMARY, font=("Consolas", 10), bd=0)
        self.rhs_box.pack(fill="both", expand=True, padx=2, pady=2)

        # Color Formatting
        for box in (self.lhs_box, self.rhs_box):
            box.tag_config("INFO", foreground=ACCENT_BLUE)
            box.tag_config("WARN", foreground=ACCENT_YELLOW)
            box.tag_config("ERROR", foreground=ACCENT_RED)
            box.tag_config("DROP", foreground=ACCENT_RED, background="#2d1414")

        # --- 4. Bottom Analytics Workspace ---
        bottom_workspace = tk.Frame(self.root, bg=BG_MAIN, height=300)
        bottom_workspace.pack(fill="x", padx=15, pady=10)

        # Machine Data Health Box
        self.machine_monitor = tk.Text(bottom_workspace, bg=BG_CARD, fg=TEXT_PRIMARY, font=("Consolas", 9), width=50, bd=0)
        self.machine_monitor.pack(side="left", fill="y", padx=5)

        # Dual Analytics Charts
        self.fig, (self.ax_jitter, self.ax_throughput) = plt.subplots(1, 2, figsize=(10, 2.8))
        self.fig.patch.set_facecolor(BG_CARD)
        for ax in (self.ax_jitter, self.ax_throughput):
            ax.set_facecolor(BG_MAIN)
            ax.tick_params(colors="white", labelsize=7)
            ax.spines['bottom'].set_color('#30363d')
            ax.spines['left'].set_color('#30363d')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=bottom_workspace)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True, padx=5)

    def create_card(self, parent, title, color):
        f = tk.Frame(parent, bg=BG_CARD, padx=20, pady=15, bd=1, relief="flat")
        f.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(f, text=title, font=("Arial", 8, "bold"), fg="#8b949e", bg=BG_CARD).pack()
        l = tk.Label(f, text="0", font=("Consolas", 22, "bold"), fg=color, bg=BG_CARD)
        l.pack(); return l

    def toggle_pause(self):
        self.is_running = not self.is_running
        self.pause_btn.config(text="RESUME FEED" if not self.is_running else "PAUSE TELEMETRY",
                              bg=ACCENT_GREEN if not self.is_running else ACCENT_YELLOW)

    def start_log_polling(self):
        """Main loop to tail the log file and update UI sub-systems."""
        if self.is_running and os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                f.seek(self.last_pos)
                chunk = f.readlines()
                self.last_pos = f.tell()

                search_term = self.search_var.get().lower()
                lvl_filter = self.filter_var.get().split()[0] # Gets 'INFO', 'WARN', etc.

                for line in chunk:
                    line = line.strip()
                    if not line: continue
                    
                    # Filtering Engine
                    if search_term and search_term not in line.lower(): continue
                    if lvl_filter != "ALL" and lvl_filter not in line: continue

                    # Identify Level for Coloring
                    tag = "ERROR" if "ERROR" in line else ("WARN" if "WARN" in line else "INFO")

                    # Route to correct Pane
                    if "RAW |" in line:
                        # LHS: Remove status column as requested
                        display_line = line.replace("RAW | ", "")
                        self.lhs_box.insert(tk.END, display_line + "\n", tag)
                    
                    elif "DROPPED |" in line:
                        self.dropped += 1
                        self.rhs_box.insert(tk.END, line + "\n", "DROP")
                    
                    elif "WRITTEN |" in line:
                        self.processed += 1
                        self.rhs_box.insert(tk.END, line + "\n", tag)
                        
                        # Extract Data for Analytics
                        try:
                            parts = line.split("|")
                            m_id = parts[2].strip()
                            if m_id not in self.machine_data:
                                self.machine_data[m_id] = {'count': 0, 'err': 0}
                            self.machine_data[m_id]['count'] += 1
                            if tag == "ERROR": self.machine_data[m_id]['err'] += 1
                            
                            if "latency=" in line:
                                lat_val = float(line.split("latency=")[1].split("ms")[0])
                                self.latency_history.append(lat_val)
                        except: pass

                if chunk:
                    self.lhs_box.see(tk.END)
                    self.rhs_box.see(tk.END)
                    self.update_telemetry_ui()

        # Update machine health box every 3 seconds
        if time.time() - self.last_rollup >= 3:
            self.refresh_machine_monitor()
            self.last_rollup = time.time()

        self.root.after(100, self.start_log_polling)

    def update_telemetry_ui(self):
        """Updates numeric KPI cards and Matplotlib charts."""
        self.card_total.config(text=str(self.processed))
        self.card_dropped.config(text=str(self.dropped))
        
        avg_jitter = sum(self.latency_history)/len(self.latency_history) if self.latency_history else 0
        self.card_latency.config(text=f"{avg_jitter:.1f}")
        
        # System Health Logic
        h_text = "OPTIMAL" if self.dropped == 0 else "OVERLOADED"
        h_color = ACCENT_GREEN if self.dropped == 0 else ACCENT_RED
        self.card_health.config(text=h_text, fg=h_color)

        # Chart 1: Latency Jitter
        self.ax_jitter.clear(); self.ax_jitter.set_facecolor(BG_MAIN)
        self.ax_jitter.plot(list(self.latency_history), color=ACCENT_BLUE, linewidth=1.5)
        self.ax_jitter.set_title("Network Latency Jitter (ms)", color="white", fontsize=8)

        # Chart 2: Total Throughput
        self.throughput_history.append(self.processed)
        self.ax_throughput.clear(); self.ax_throughput.set_facecolor(BG_MAIN)
        self.ax_throughput.fill_between(range(len(self.throughput_history)), list(self.throughput_history), color=ACCENT_GREEN, alpha=0.3)
        self.ax_throughput.plot(list(self.throughput_history), color=ACCENT_GREEN, linewidth=1.5)
        self.ax_throughput.set_title("Accumulated Record Throughput", color="white", fontsize=8)
        
        self.canvas.draw()

    def refresh_machine_monitor(self):
        """Updates the node-wise data table in the bottom panel."""
        stats = "--- DISTRIBUTED NODE HEALTH TRACKER ---\n"
        stats += f"{'MACHINE ID':<15} | {'LOAD':<12} | {'ERRORS':<8}\n"
        stats += "-" * 45 + "\n"
        for m, data in sorted(self.machine_data.items(), key=lambda x: x[1]['count'], reverse=True)[:15]:
            stats += f"{m:<15} | {data['count']:<12} | {data['err']:<8}\n"
        
        self.machine_monitor.delete("1.0", tk.END)
        self.machine_monitor.insert(tk.END, stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = EnterpriseNOC(root)
    root.mainloop()
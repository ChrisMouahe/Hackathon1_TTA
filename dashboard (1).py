import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import date
from collections import Counter
from matplotlib.patches import Patch

from models import Session, User, Program
from data_manager import DataManager, clean_dataset, generate_simulated_users, generate_simulated_data, weekly_analysis, type_stats, exercise_frequency
from workout_generator import recommend_session
from scipy_analysis import test_anova_calories, regress_progress, ttest_paired

# CustomTkinter setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Constants & Colors
COL_BG          = "#10141A"
COL_SIDEBAR     = "#161B22"
COL_ACCENT      = "#39E991"
COL_ACCENT_HOV  = "#27B374"
COL_CARD        = "#1C2128"
COL_CARD_BORDER = "#2A313C"
COL_TEXT        = "#F2F4F7"
COL_TEXT_DIM    = "#9AA4B2"
COL_DANGER      = "#FF5C5C"
COL_WARNING     = "#FFC857"
COL_SUCCESS     = "#39E991"

CHART_COLORS = {
    'yoga':        '#A855F7',
    'running':     '#F97316',
    'hiit':        '#EF4444',
    'musculation': '#3B82F6',
    'natation':    '#06B6D4',
    'marche':      '#22C55E',
    'accent':      '#39E991',
    'secondary':   '#FFC857',
    'gradient_1':  '#6366F1',
    'gradient_2':  '#EC4899',
}

class FitnessDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("⚡ DATA FITNESS — IFI Fitness IA")
        self.geometry("1280x800")
        self.configure(fg_color=COL_BG)
        
        # Data Management
        self.dm = DataManager()
        self.df_clean = clean_dataset()
        
        if len(self.dm.load_historic_raw()) == 0:
            generate_simulated_users()
            generate_simulated_data(days_nb=30)
            self.df_clean = clean_dataset()
            
        self.current_user = None
        
        # UI Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.setup_sidebar()
        
        # Main Content Frame
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color=COL_BG)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        self.current_frame = None
        
        self.show_page("ACCUEIL")
        
        self.show_toast(f"📊 Données chargées — {len(self.df_clean)} séances disponibles")
        
    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=COL_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        # Logo
        logo = ctk.CTkLabel(self.sidebar, text="⚡ DATA FITNESS", font=ctk.CTkFont(size=24, weight="bold"), text_color=COL_ACCENT)
        logo.grid(row=0, column=0, padx=20, pady=(30, 40))
        
        # Navigation
        pages = ["ACCUEIL", "PROFIL / CONNEXION", "NOUVELLE SÉANCE", "DASHBOARD ANALYTIQUE", "PROGRAMME SEMAINE", "HISTORIQUE"]
        for i, page in enumerate(pages):
            btn = ctk.CTkButton(self.sidebar, text=page, fg_color="transparent", text_color=COL_TEXT, 
                                hover_color=COL_CARD_BORDER, anchor="w",
                                command=lambda p=page: self.show_page(p))
            btn.grid(row=i+1, column=0, padx=20, pady=5, sticky="ew")
            
        # User Badge
        self.user_badge = ctk.CTkLabel(self.sidebar, text="VISITEUR", text_color=COL_TEXT_DIM, fg_color=COL_CARD, corner_radius=8)
        self.user_badge.grid(row=8, column=0, padx=20, pady=20, sticky="ew", ipady=10)
        
    def update_user_badge(self):
        if self.current_user:
            bmi = self.current_user.calculate_bmi()
            self.user_badge.configure(text=f"👤 {self.current_user.name}\nObjectif: {self.current_user.goal}\nIMC: {bmi}")
        else:
            self.user_badge.configure(text="VISITEUR")
            
    def show_toast(self, message):
        toast = ctk.CTkLabel(self, text=message, fg_color=COL_SUCCESS, text_color=COL_BG, corner_radius=8, font=ctk.CTkFont(weight="bold"))
        toast.place(relx=0.5, rely=0.05, anchor="center")
        self.after(3000, toast.destroy)

    def show_page(self, page_name):
        if self.current_frame:
            for widget in self.current_frame.winfo_children():
                widget.destroy()
        else:
            self.current_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            self.current_frame.grid(row=0, column=0, sticky="nsew")
            self.current_frame.grid_columnconfigure(0, weight=1)
            
        if page_name == "ACCUEIL":
            self.build_accueil()
        elif page_name == "PROFIL / CONNEXION":
            self.build_profil()
        elif page_name == "NOUVELLE SÉANCE":
            self.build_nouvelle_seance()
        elif page_name == "DASHBOARD ANALYTIQUE":
            self.build_dashboard()
        elif page_name == "PROGRAMME SEMAINE":
            self.build_programme()
        elif page_name == "HISTORIQUE":
            self.build_historique()

    # Helpers
    def apply_chart_style(self, fig, ax, title, xlabel, ylabel):
        fig.patch.set_facecolor(COL_BG)
        ax.set_facecolor(COL_CARD)
        ax.grid(color=COL_CARD_BORDER, linestyle="--", linewidth=0.7, alpha=0.8)
        ax.tick_params(colors=COL_TEXT, labelsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor(COL_CARD_BORDER)
        ax.set_title(title, color=COL_TEXT, fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel(xlabel, color=COL_TEXT_DIM, fontsize=9)
        ax.set_ylabel(ylabel, color=COL_TEXT_DIM, fontsize=9)

    def get_user_data(self):
        if self.current_user:
            return self.df_clean[self.df_clean['user_id'] == self.current_user.user_id]
        return self.df_clean

    def build_accueil(self):
        df_view = self.get_user_data()
        
        # KPIs
        kpi_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1)
            
        total_sessions = len(df_view)
        total_cal = int(df_view['calories'].sum()) if not df_view.empty else 0
        avg_cal = int(df_view['calories'].mean()) if not df_view.empty else 0
        top_type = df_view['workout_type'].mode()[0] if not df_view.empty else "N/A"
        
        kpis = [
            ("Total séances", total_sessions),
            ("Calories totales", total_cal),
            ("Moyenne cal/séance", avg_cal),
            ("Type le + pratiqué", str(top_type).capitalize() if top_type != "N/A" else "N/A")
        ]
        
        for i, (label, val) in enumerate(kpis):
            card = ctk.CTkFrame(kpi_frame, fg_color=COL_CARD, corner_radius=10)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            ctk.CTkLabel(card, text=str(val), font=ctk.CTkFont(size=28, weight="bold"), text_color=COL_ACCENT).pack(pady=(15, 0))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12), text_color=COL_TEXT_DIM).pack(pady=(0, 15))
            
        # Chart 1: Calories over time
        chart1_frame = ctk.CTkFrame(self.current_frame, fg_color=COL_CARD, corner_radius=10)
        chart1_frame.grid(row=1, column=0, sticky="ew", pady=10)
        
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        if not df_view.empty:
            df_time = df_view.groupby('date')['calories'].sum().reset_index().sort_values('date')
            dates = df_time['date']
            cals = df_time['calories']
            
            ax1.plot(dates, cals, color=CHART_COLORS['gradient_1'], alpha=0.4, linewidth=1)
            
            df_time['rolling'] = df_time['calories'].rolling(window=7, min_periods=1).mean()
            ax1.plot(dates, df_time['rolling'], color=CHART_COLORS['accent'], linewidth=2.5, label='Moyenne 7j')
            ax1.fill_between(dates, df_time['rolling'], alpha=0.15, color=CHART_COLORS['accent'])
            
            if len(dates) > 0:
                ax1.scatter(dates[::7], cals[::7], color=CHART_COLORS['secondary'], zorder=5, label='Points clés')
            
            ax1.legend(facecolor=COL_BG, edgecolor=COL_CARD_BORDER, labelcolor=COL_TEXT)
            
        self.apply_chart_style(fig1, ax1, "Calories dans le temps", "Date", "Calories")
        canvas1 = FigureCanvasTkAgg(fig1, chart1_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bottom Row: Donut + Freq
        bottom_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        
        # Chart 4: Donut
        chart4_frame = ctk.CTkFrame(bottom_frame, fg_color=COL_CARD, corner_radius=10)
        chart4_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        fig4, ax4 = plt.subplots(figsize=(4, 4))
        if not df_view.empty:
            freq = df_view['workout_type'].value_counts()
            colors = [CHART_COLORS.get(t, COL_TEXT) for t in freq.index]
            explode = [0.05 if i == 0 else 0 for i in range(len(freq))]
            
            wedges, texts = ax4.pie(freq.values, colors=colors, explode=explode, wedgeprops=dict(width=0.5))
            ax4.text(0, 0, f"{total_sessions}", ha='center', va='center', fontsize=20, fontweight='bold', color=COL_TEXT)
            ax4.legend(wedges, freq.index, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), facecolor=COL_BG, edgecolor=COL_CARD_BORDER, labelcolor=COL_TEXT)
            
        self.apply_chart_style(fig4, ax4, "Répartition des exercices", "", "")
        canvas4 = FigureCanvasTkAgg(fig4, chart4_frame)
        canvas4.draw()
        canvas4.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chart 2: Horizontal Bar
        chart2_frame = ctk.CTkFrame(bottom_frame, fg_color=COL_CARD, corner_radius=10)
        chart2_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        if not df_view.empty:
            freq = df_view['workout_type'].value_counts().sort_values(ascending=True)
            colors = [CHART_COLORS.get(t, COL_TEXT) for t in freq.index]
            bars = ax2.barh(freq.index, freq.values, height=0.6, color=colors)
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + 0.3, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                         ha='left', va='center', color=COL_TEXT, fontweight='bold')
                         
        self.apply_chart_style(fig2, ax2, "Fréquence des exercices", "Nombre de séances", "")
        canvas2 = FigureCanvasTkAgg(fig2, chart2_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def build_profil(self):
        if self.current_user:
            # Show profile
            info_frame = ctk.CTkFrame(self.current_frame, fg_color=COL_CARD, corner_radius=10)
            info_frame.pack(fill="x", pady=20)
            ctk.CTkLabel(info_frame, text=f"Profil de {self.current_user.name}", font=ctk.CTkFont(size=20, weight="bold"), text_color=COL_ACCENT).pack(pady=10)
            ctk.CTkLabel(info_frame, text=f"Objectif: {self.current_user.goal}", text_color=COL_TEXT).pack()
            bmi = self.current_user.calculate_bmi()
            cat = self.current_user.bmi_category()
            ctk.CTkLabel(info_frame, text=f"IMC: {bmi} ({cat})", text_color=COL_TEXT).pack(pady=10)
            
            ctk.CTkButton(info_frame, text="SE DÉCONNECTER", fg_color=COL_DANGER, hover_color="#CC0000",
                          command=self.logout).pack(pady=20)
        else:
            # Login Form
            form = ctk.CTkFrame(self.current_frame, fg_color=COL_CARD, corner_radius=10)
            form.pack(pady=40, padx=200, fill="both", expand=True)
            
            ctk.CTkLabel(form, text="Connexion / Création", font=ctk.CTkFont(size=20, weight="bold"), text_color=COL_ACCENT).pack(pady=20)
            
            entries = {}
            for field in ["Nom", "Âge", "Poids (kg)", "Taille (cm)"]:
                e = ctk.CTkEntry(form, placeholder_text=field)
                e.pack(pady=10, padx=50, fill="x")
                entries[field] = e
                
            goal_var = ctk.StringVar(value="perte_poids")
            ctk.CTkOptionMenu(form, variable=goal_var, values=["perte_poids", "force", "cardio"]).pack(pady=10, padx=50, fill="x")
            
            gender_var = ctk.StringVar(value="M")
            ctk.CTkOptionMenu(form, variable=gender_var, values=["M", "F"]).pack(pady=10, padx=50, fill="x")
            
            def login_or_create():
                name = entries["Nom"].get()
                if not name: return
                user = self.dm.find_user_by_name(name)
                if user:
                    self.current_user = user
                    self.show_toast(f"Bienvenue {user.name} !")
                else:
                    try:
                        u = User(user_id=self.dm.get_next_user_id(), name=name, age=int(entries["Âge"].get()), 
                                 weight=float(entries["Poids (kg)"].get()), height=float(entries["Taille (cm)"].get()), 
                                 goal=goal_var.get(), gender=gender_var.get())
                        self.dm.save_user(u)
                        self.current_user = u
                        self.show_toast("Profil créé !")
                    except Exception as e:
                        self.show_toast("Erreur dans les champs")
                        return
                self.update_user_badge()
                self.show_page("PROFIL / CONNEXION")
                
            ctk.CTkButton(form, text="SE CONNECTER / CRÉER", command=login_or_create, fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOV, text_color=COL_BG).pack(pady=20)

    def logout(self):
        self.current_user = None
        self.update_user_badge()
        self.show_page("PROFIL / CONNEXION")
        self.show_toast("Déconnecté")

    def build_nouvelle_seance(self):
        if not self.current_user:
            ctk.CTkLabel(self.current_frame, text="Veuillez vous connecter pour ajouter une séance.", text_color=COL_WARNING).pack(pady=50)
            return
            
        form = ctk.CTkFrame(self.current_frame, fg_color=COL_CARD, corner_radius=10)
        form.pack(pady=20, padx=200, fill="both", expand=True)
        
        ctk.CTkLabel(form, text="Nouvelle Séance", font=ctk.CTkFont(size=20, weight="bold"), text_color=COL_ACCENT).pack(pady=20)
        
        type_var = ctk.StringVar(value="running")
        ctk.CTkOptionMenu(form, variable=type_var, values=['yoga', 'running', 'hiit', 'musculation', 'natation', 'marche']).pack(pady=10, padx=50, fill="x")
        
        entries = {}
        for field in ["Durée (min)", "Calories", "Pas"]:
            e = ctk.CTkEntry(form, placeholder_text=field)
            e.pack(pady=10, padx=50, fill="x")
            entries[field] = e
            
        intensity_var = ctk.StringVar(value="modérée")
        ctk.CTkOptionMenu(form, variable=intensity_var, values=['faible', 'modérée', 'élevée']).pack(pady=10, padx=50, fill="x")
        
        def save_session():
            try:
                s = Session(user_id=self.current_user.user_id, workout_type=type_var.get(), 
                            duration=int(entries["Durée (min)"].get()), intensity=intensity_var.get(), 
                            calories=int(entries["Calories"].get()), steps=int(entries["Pas"].get() or 0))
                self.dm.save_session(s)
                self.df_clean = clean_dataset()
                self.show_toast("✅ Séance enregistrée !")
                for e in entries.values(): e.delete(0, 'end')
            except Exception as e:
                self.show_toast("Erreur de saisie")
                
        ctk.CTkButton(form, text="ENREGISTRER", command=save_session, fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOV, text_color=COL_BG).pack(pady=30)

    def build_dashboard(self):
        df_view = self.get_user_data()
        
        # Row 1: 3 charts side by side
        row1 = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        row1.pack(fill="x", pady=10)
        for i in range(3): row1.grid_columnconfigure(i, weight=1)
        
        # Chart 1: Cal/temps mini
        c1_frame = ctk.CTkFrame(row1, fg_color=COL_CARD)
        c1_frame.grid(row=0, column=0, padx=5, sticky="nsew")
        fig1, ax1 = plt.subplots(figsize=(3, 3))
        if not df_view.empty:
            df_time = df_view.groupby('date')['calories'].sum().reset_index()
            ax1.plot(df_time['date'], df_time['calories'], color=CHART_COLORS['accent'])
        self.apply_chart_style(fig1, ax1, "Calories", "", "")
        FigureCanvasTkAgg(fig1, c1_frame).get_tk_widget().pack(fill="both", expand=True)
        
        # Chart 2: Freq mini
        c2_frame = ctk.CTkFrame(row1, fg_color=COL_CARD)
        c2_frame.grid(row=0, column=1, padx=5, sticky="nsew")
        fig2, ax2 = plt.subplots(figsize=(3, 3))
        if not df_view.empty:
            freq = df_view['workout_type'].value_counts()
            ax2.barh(freq.index, freq.values, color=[CHART_COLORS.get(t, COL_TEXT) for t in freq.index])
        self.apply_chart_style(fig2, ax2, "Fréquence", "", "")
        FigureCanvasTkAgg(fig2, c2_frame).get_tk_widget().pack(fill="both", expand=True)
        
        # Chart 3: Progression
        c3_frame = ctk.CTkFrame(row1, fg_color=COL_CARD)
        c3_frame.grid(row=0, column=2, padx=5, sticky="nsew")
        fig3, ax3 = plt.subplots(figsize=(3, 3))
        if not df_view.empty and 'week' in df_view.columns:
            prog = df_view.groupby('week')['calories'].sum()
            colors = [COL_SUCCESS if v >= 2000 else CHART_COLORS['running'] for v in prog.values]
            bars = ax3.bar(prog.index.astype(str), prog.values, color=colors)
            ax3.axhline(y=2000, color=COL_DANGER, linestyle='--', linewidth=1.5)
            for bar in bars:
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{int(bar.get_height())}', 
                         ha='center', va='bottom', color=COL_TEXT, fontsize=8)
        self.apply_chart_style(fig3, ax3, "Progression (Cible 2000)", "", "")
        FigureCanvasTkAgg(fig3, c3_frame).get_tk_widget().pack(fill="both", expand=True)
        
        # Row 2: SciPy cards
        row2 = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        row2.pack(fill="x", pady=10)
        for i in range(3): row2.grid_columnconfigure(i, weight=1)
        
        def run_test(test_type, frame):
            for w in frame.winfo_children(): w.destroy()
            if test_type == "anova":
                res = test_anova_calories(df_view)
                val = f"F = {res.get('F_statistic', 'N/A')}"
                sig = res.get('significatif', False)
                pval = res.get('p_value', 'N/A')
            elif test_type == "ttest":
                res = ttest_paired(df_view)
                val = f"Δ = {res.get('delta', 'N/A')}"
                sig = res.get('significatif', False)
                pval = res.get('p_value', 'N/A')
            
            ctk.CTkLabel(frame, text=test_type.upper(), text_color=COL_TEXT_DIM).pack(pady=5)
            ctk.CTkLabel(frame, text=val, font=ctk.CTkFont(size=24, weight="bold"), text_color=COL_ACCENT).pack()
            ctk.CTkLabel(frame, text=f"p = {pval}", text_color=COL_TEXT).pack()
            color = COL_SUCCESS if sig else COL_WARNING
            text = "✅ Significatif" if sig else "⚠️ Non significatif"
            ctk.CTkLabel(frame, text=text, text_color=color).pack(pady=5)
            
        t1 = ctk.CTkFrame(row2, fg_color=COL_CARD, corner_radius=10)
        t1.grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(t1, text="▶ Lancer ANOVA", command=lambda: run_test("anova", t1), fg_color="transparent", border_width=1).pack(pady=20)
        
        t2 = ctk.CTkFrame(row2, fg_color=COL_CARD, corner_radius=10)
        t2.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(t2, text="▶ Lancer T-Test", command=lambda: run_test("ttest", t2), fg_color="transparent", border_width=1).pack(pady=20)
        
        # Row 3: Regression Chart
        c5_frame = ctk.CTkFrame(self.current_frame, fg_color=COL_CARD)
        c5_frame.pack(fill="x", pady=10)
        fig5, ax5 = plt.subplots(figsize=(10, 3))
        if not df_view.empty and len(df_view) > 2:
            try:
                res = regress_progress(df_view)
                df_sorted = df_view.sort_values('date').reset_index()
                x = np.arange(len(df_sorted))
                y = df_sorted['calories'].values
                ax5.scatter(x, y, color=CHART_COLORS['gradient_1'], alpha=0.6, s=40, edgecolors='white', linewidth=0.5)
                ax5.plot(x, res['pente'] * x + res['intercept'], color=COL_ACCENT, linewidth=2)
                ax5.text(0.02, 0.85, f"R² = {res['r_squared']}", transform=ax5.transAxes, color=COL_TEXT, fontweight='bold')
            except Exception:
                pass
        self.apply_chart_style(fig5, ax5, "Régression Linéaire", "Jours", "Calories")
        FigureCanvasTkAgg(fig5, c5_frame).get_tk_widget().pack(fill="both", expand=True)
        
        # Row 4: IA Reco
        if self.current_user:
            reco = recommend_session(self.current_user, df_view)
            reco_frame = ctk.CTkFrame(self.current_frame, fg_color=COL_CARD, corner_radius=10)
            reco_frame.pack(fill="x", pady=10)
            ctk.CTkLabel(reco_frame, text="Recommandation IA", font=ctk.CTkFont(weight="bold"), text_color=COL_ACCENT).pack(pady=5)
            ctk.CTkLabel(reco_frame, text=f"💡 {reco['exercise'].capitalize()} - {reco['duration']} min", font=ctk.CTkFont(size=18)).pack()
            ctk.CTkLabel(reco_frame, text=f"Niveau: {reco['activity_level'].upper()}", text_color=COL_WARNING).pack()
            ctk.CTkLabel(reco_frame, text=f'"{reco["message"]}"', text_color=COL_TEXT_DIM, font=ctk.CTkFont(slant="italic")).pack(pady=5)

    def build_programme(self):
        if not self.current_user:
            ctk.CTkLabel(self.current_frame, text="Veuillez vous connecter pour voir votre programme.", text_color=COL_WARNING).pack(pady=50)
            return
            
        prog = Program(self.current_user).generate_program()
        emojis = {'running': '🏃', 'yoga': '🧘', 'hiit': '🔥', 'musculation': '💪', 'natation': '🏊', 'marche': '🚶', 'strength': '💪', 'swimming': '🏊', 'walking': '🚶'}
        colors = {'faible': COL_SUCCESS, 'modérée': COL_WARNING, 'élevée': COL_DANGER, 'low': COL_SUCCESS, 'moderate': COL_WARNING, 'high': COL_DANGER}
        
        ctk.CTkLabel(self.current_frame, text="Programme de la semaine", font=ctk.CTkFont(size=24, weight="bold"), text_color=COL_ACCENT).pack(pady=20)
        
        cards_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20)
        for i in range(5): cards_frame.grid_columnconfigure(i, weight=1)
        
        for i, day in enumerate(prog):
            card = ctk.CTkFrame(cards_frame, fg_color=COL_CARD, corner_radius=10)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            ctk.CTkLabel(card, text=day['day'], font=ctk.CTkFont(weight="bold"), text_color=COL_ACCENT).pack(pady=10)
            ex = day['exercise']
            ctk.CTkLabel(card, text=emojis.get(ex, '⚡'), font=ctk.CTkFont(size=30)).pack()
            ctk.CTkLabel(card, text=ex.capitalize(), text_color=COL_TEXT).pack(pady=5)
            ctk.CTkLabel(card, text=f"{day['duration']} min", fg_color=COL_CARD_BORDER, corner_radius=5).pack(pady=5)
            intensity = day['intensity']
            ctk.CTkLabel(card, text=intensity.upper(), text_color=colors.get(intensity, COL_TEXT)).pack(pady=10)

    def build_historique(self):
        df_view = self.get_user_data().sort_values('date', ascending=False)
        
        header = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        header.pack(fill="x", pady=10)
        ctk.CTkLabel(header, text="Historique des séances", font=ctk.CTkFont(size=20, weight="bold"), text_color=COL_ACCENT).pack(side="left")
        ctk.CTkButton(header, text="📥 Exporter CSV", command=lambda: self.dm.export_csv(), fg_color=COL_CARD_BORDER, hover_color=COL_CARD).pack(side="right")
        
        if df_view.empty:
            ctk.CTkLabel(self.current_frame, text="Aucune séance enregistrée.", text_color=COL_TEXT_DIM).pack(pady=50)
            return
            
        cols = ["Date", "Type", "Durée", "Intensité", "Calories", "Pas"]
        table = ctk.CTkFrame(self.current_frame, fg_color=COL_CARD, corner_radius=10)
        table.pack(fill="both", expand=True, pady=10)
        
        for i, c in enumerate(cols):
            ctk.CTkLabel(table, text=c, font=ctk.CTkFont(weight="bold"), text_color=COL_TEXT_DIM).grid(row=0, column=i, padx=10, pady=10, sticky="w")
            
        for row_idx, (_, row) in enumerate(df_view.iterrows(), start=1):
            bg = "transparent" if row_idx % 2 == 0 else COL_CARD_BORDER
            row_frame = ctk.CTkFrame(table, fg_color=bg, corner_radius=0)
            row_frame.grid(row=row_idx, column=0, columnspan=6, sticky="ew")
            for i in range(6): row_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(row_frame, text=str(row['date'])[:10]).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            type_lbl = ctk.CTkLabel(row_frame, text=str(row['workout_type']).upper(), text_color=CHART_COLORS.get(row['workout_type'], COL_TEXT))
            type_lbl.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(row_frame, text=f"{row['duration']} min").grid(row=0, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row_frame, text=str(row['intensity'])).grid(row=0, column=3, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row_frame, text=str(row['calories'])).grid(row=0, column=4, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(row_frame, text=str(row['steps'])).grid(row=0, column=5, padx=10, pady=5, sticky="w")

if __name__ == "__main__":
    app = FitnessDashboard()
    app.mainloop()

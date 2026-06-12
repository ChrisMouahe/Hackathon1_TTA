# -*- coding: utf-8 -*-
import customtkinter as ctk

from models import User, Program
from data_manager import DataManager, clean_dataset, weekly_analysis, generate_simulated_users, generate_simulated_data
from workout_generator import recommend_session
from scipy_analysis import test_anova_calories, regress_progress, ttest_paired

# =============================================================================
# THEME / PALETTE — "Fitness Energy"
# =============================================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

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

FONT_TITLE   = ("Segoe UI", 26, "bold")
FONT_LOGO    = ("Segoe UI", 22, "bold")
FONT_CARD    = ("Segoe UI", 16, "bold")
FONT_BODY    = ("Segoe UI", 13)
FONT_MENU    = ("Segoe UI", 13, "bold")
FONT_MONO    = ("Consolas", 11)


class ModernFitnessDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.dm = DataManager()
        self.df_clean = clean_dataset()
        self.current_user = None

        self.title("⚡ IFI FITNESS IA — Dashboard")
        self.geometry("1200x720")
        self.configure(fg_color=COL_BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # SIDEBAR
        # =====================================================================
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COL_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.accent_bar = ctk.CTkFrame(self.sidebar, height=4, corner_radius=0, fg_color=COL_ACCENT)
        self.accent_bar.pack(fill="x", side="top")

        self.logo = ctk.CTkLabel(self.sidebar, text="⚡ IFI FITNESS", font=FONT_LOGO, text_color=COL_ACCENT)
        self.logo.pack(pady=(28, 0), padx=10)

        self.subtitle = ctk.CTkLabel(
            self.sidebar, text="Intelligence Artificielle • Fitness",
            font=("Segoe UI", 11), text_color=COL_TEXT_DIM
        )
        self.subtitle.pack(pady=(0, 15), padx=10)

        self.badge_session = ctk.CTkFrame(self.sidebar, corner_radius=20, fg_color=COL_CARD)
        self.badge_session.pack(pady=(0, 20), padx=20, fill="x")
        self.badge_session_label = ctk.CTkLabel(
            self.badge_session, text="● VISITEUR",
            font=("Segoe UI", 12, "bold"), text_color=COL_WARNING
        )
        self.badge_session_label.pack(pady=8)

        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=COL_CARD_BORDER)
        sep.pack(fill="x", padx=20, pady=(0, 10))

        # CORRECTION 1 : deux zones séparées pour les boutons du haut et le bouton logout en bas
        self.menu_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.menu_container.pack(fill="both", expand=True)

        self.logout_container = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=70)
        self.logout_container.pack(fill="x", side="bottom", pady=(0, 10))
        self.logout_container.pack_propagate(False)

        # =====================================================================
        # ZONE CENTRALE
        # =====================================================================
        self.main_content = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(1, weight=1)

        self.mettre_a_jour_menu_dynamique()
        self.afficher_vue_accueil()

    # =========================================================================
    # NAVIGATION
    # =========================================================================
    def mettre_a_jour_menu_dynamique(self):
        for widget in self.menu_container.winfo_children():
            widget.destroy()
        for widget in self.logout_container.winfo_children():
            widget.destroy()

        if self.current_user is None:
            self.badge_session_label.configure(text="● VISITEUR", text_color=COL_WARNING)
            self.creer_bouton_menu("🏠  Accueil", self.afficher_vue_accueil)
            self.creer_bouton_menu("📝  Inscription", self.afficher_vue_inscription)
            self.creer_bouton_menu("🔑  Connexion", self.afficher_vue_connexion)
            self.creer_bouton_menu("📊  Stats Hebdo Globales", self.afficher_vue_stats_globales)
            self.creer_bouton_menu("🔬  Analyses SciPy", self.afficher_vue_scipy)
            self.creer_bouton_menu("🤖  Injecter Données Démo", self.action_generer_demo)
        else:
            self.badge_session_label.configure(
                text=f"● {self.current_user.name.upper()}", text_color=COL_SUCCESS
            )
            self.creer_bouton_menu("🏋️  Recommandation du Jour", self.afficher_vue_recommandation)
            self.creer_bouton_menu("📅  Programme Semaine", self.afficher_vue_programme_semaine)
            self.creer_bouton_menu("📜  Mon Historique Personnel", self.afficher_vue_historique_personnel)
            self.creer_bouton_menu("📊  Stats Hebdo Globales", self.afficher_vue_stats_globales)
            self.creer_bouton_menu("🔬  Voir mon évolution", self.afficher_vue_scipy)

            # CORRECTION 1 : logout dans son propre conteneur fixe en bas
            btn_logout = ctk.CTkButton(
                self.logout_container, text="🚪  Se Déconnecter", anchor="center",
                fg_color="transparent", text_color=COL_DANGER,
                hover_color=COL_CARD, border_width=1, border_color=COL_DANGER,
                font=FONT_MENU, height=40, corner_radius=10,
                command=self.action_deconnexion
            )
            btn_logout.pack(pady=10, padx=15, fill="x")

    def creer_bouton_menu(self, texte, commande):
        btn = ctk.CTkButton(
            self.menu_container, text=texte, anchor="w",
            fg_color="transparent", text_color=COL_TEXT,
            hover_color=COL_CARD,
            font=FONT_MENU, height=42, corner_radius=10,
            command=commande
        )
        btn.pack(pady=3, padx=15, fill="x")

    def nettoyer_zone_droite(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def creer_carte_blanche(self, ligne, colonne, titre, columnspan=1):
        outer = ctk.CTkFrame(self.main_content, fg_color=COL_CARD, corner_radius=14,
                              border_width=1, border_color=COL_CARD_BORDER)
        outer.grid(row=ligne, column=colonne, columnspan=columnspan, padx=10, pady=10, sticky="nsew")

        accent = ctk.CTkFrame(outer, height=4, corner_radius=14, fg_color=COL_ACCENT)
        accent.pack(fill="x", side="top")

        lbl = ctk.CTkLabel(outer, text=titre, font=FONT_CARD, text_color=COL_TEXT)
        lbl.pack(anchor="w", padx=18, pady=(14, 10))
        return outer

    # =========================================================================
    # VUES
    # =========================================================================
    def afficher_vue_accueil(self):
        self.nettoyer_zone_droite()

        # CORRECTION 2 : header en row=0, carte en row=1 (cohérent avec toutes les autres vues)
        header = ctk.CTkLabel(self.main_content, text="Tableau de bord principal",
                               font=FONT_TITLE, text_color=COL_TEXT)
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))

        carte_intro = self.creer_carte_blanche(1, 0, "🏁  Statut de votre Tracker", columnspan=2)
        intro_txt = "Bienvenue sur l'application Fitness Tracker IA !\n\n"
        if self.current_user is None:
            intro_txt += ("🔴 Vous êtes actuellement en mode Visiteur. Utilisez le menu de gauche "
                           "pour vous connecter à votre espace ou créer un compte afin de débloquer "
                           "vos recommandations personnalisées de sport.")
        else:
            intro_txt += (f"🟢 Session active au nom de {self.current_user.name}. Vos modules de "
                           f"calculs d'IMC, d'historiques et de plannings hebdomadaires sur-mesure "
                           f"sont prêts à être consultés !")

        lbl = ctk.CTkLabel(carte_intro, text=intro_txt, justify="left",
                            font=FONT_BODY, text_color=COL_TEXT_DIM, wraplength=850)
        lbl.pack(anchor="w", padx=18, pady=(0, 18))

    def afficher_vue_inscription(self):
        self.nettoyer_zone_droite()
        carte_form = self.creer_carte_blanche(0, 0, "📝  Création de profil", columnspan=2)

        self.ent_name = ctk.CTkEntry(carte_form, placeholder_text="Nom complet", width=320, height=38, corner_radius=10)
        self.ent_name.pack(pady=6)
        self.ent_age = ctk.CTkEntry(carte_form, placeholder_text="Âge (ex: 28)", width=320, height=38, corner_radius=10)
        self.ent_age.pack(pady=6)
        self.ent_gender = ctk.CTkComboBox(carte_form, values=["M", "F"], width=320, height=38, corner_radius=10,
                                           fg_color=COL_BG, button_color=COL_ACCENT, border_color=COL_CARD_BORDER)
        self.ent_gender.pack(pady=6)
        self.ent_weight = ctk.CTkEntry(carte_form, placeholder_text="Poids en kg (ex: 68.2)", width=320, height=38, corner_radius=10)
        self.ent_weight.pack(pady=6)
        self.ent_height = ctk.CTkEntry(carte_form, placeholder_text="Taille en cm (ex: 172)", width=320, height=38, corner_radius=10)
        self.ent_height.pack(pady=6)
        self.ent_goal = ctk.CTkComboBox(carte_form, values=["perte_poids", "force", "cardio"], width=320, height=38, corner_radius=10,
                                         fg_color=COL_BG, button_color=COL_ACCENT, border_color=COL_CARD_BORDER)
        self.ent_goal.pack(pady=6)

        btn_valider = ctk.CTkButton(carte_form, text="Créer mon compte", command=self.action_inscription,
                                     fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOV, text_color="#0B1410",
                                     font=FONT_MENU, height=42, corner_radius=10, width=320)
        btn_valider.pack(pady=18)

        # CORRECTION 3 : message d'erreur dans la carte (pack), pas dans main_content (grid)
        self.lbl_err_inscription = ctk.CTkLabel(carte_form, text="", text_color=COL_DANGER, font=FONT_BODY)
        self.lbl_err_inscription.pack(pady=(0, 8))

    def action_inscription(self):
        try:
            name = self.ent_name.get().strip()
            age = int(self.ent_age.get().strip())
            gender = self.ent_gender.get()
            weight = float(self.ent_weight.get().strip())
            height = int(self.ent_height.get().strip())
            goal = self.ent_goal.get()

            if not name:
                raise ValueError("Nom vide")

            new_user = User(user_id=self.dm.get_next_user_id(), name=name, age=age,
                            weight=weight, height=height, goal=goal, gender=gender)
            self.dm.save_user(new_user)
            self.current_user = new_user

            self.nettoyer_zone_droite()
            carte_success = self.creer_carte_blanche(0, 0, "✅  Inscription réussie !", columnspan=2)
            res_txt = (f"Bonjour {name} ! Votre compte est configuré.\n\n"
                       f"• Votre IMC : {new_user.calculate_bmi()} ({new_user.bmi_category()})\n"
                       f"• Dépense journalière estimée : {new_user.daily_calories()} kcal")
            ctk.CTkLabel(carte_success, text=res_txt, justify="left", font=FONT_BODY,
                         text_color=COL_TEXT_DIM).pack(padx=18, pady=(0, 18))

            self.mettre_a_jour_menu_dynamique()

        except ValueError:
            # CORRECTION 3 : on affiche l'erreur dans le label prévu dans la carte
            self.lbl_err_inscription.configure(text="❌ Formulaire incomplet ou valeurs invalides.")

    def afficher_vue_connexion(self):
        self.nettoyer_zone_droite()
        carte_login = self.creer_carte_blanche(0, 0, "🔑  Identifiez-vous", columnspan=2)

        self.ent_login = ctk.CTkEntry(carte_login, placeholder_text="Entrez votre nom",
                                       width=320, height=38, corner_radius=10)
        self.ent_login.pack(pady=15)

        btn_go = ctk.CTkButton(carte_login, text="Entrer", command=self.action_connexion,
                                fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOV, text_color="#0B1410",
                                font=FONT_MENU, height=42, corner_radius=10, width=320)
        btn_go.pack(pady=(0, 10))

        # CORRECTION 3 (même logique) : label d'erreur dans la carte
        self.lbl_err_connexion = ctk.CTkLabel(carte_login, text="", text_color=COL_DANGER, font=FONT_BODY)
        self.lbl_err_connexion.pack(pady=(0, 8))

    def action_connexion(self):
        name = self.ent_login.get().strip()
        user_trouve = self.dm.find_user_by_name(name)
        if user_trouve:
            self.current_user = user_trouve
            self.mettre_a_jour_menu_dynamique()
            self.afficher_vue_recommandation()
        else:
            self.lbl_err_connexion.configure(
                text="❌ Utilisateur introuvable. Avez-vous créé votre compte ?"
            )

    def action_deconnexion(self):
        self.current_user = None
        self.mettre_a_jour_menu_dynamique()
        self.afficher_vue_accueil()

    def afficher_vue_recommandation(self):
        self.nettoyer_zone_droite()

        header = ctk.CTkLabel(self.main_content, text=f"Espace de {self.current_user.name}",
                               font=FONT_TITLE, text_color=COL_TEXT)
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))

        carte_rec = self.creer_carte_blanche(1, 0, "💡  Conseil du Jour (IA)")
        df_user = self.dm.get_user_history(self.current_user.user_id, self.df_clean)

        tb1 = ctk.CTkTextbox(carte_rec, height=160, fg_color=COL_BG, border_width=1,
                              border_color=COL_CARD_BORDER, corner_radius=10,
                              font=FONT_BODY, text_color=COL_TEXT)
        tb1.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        if df_user is None or df_user.empty:
            if self.current_user.goal == "perte_poids":
                msg = "Profil Débutant détecté :\n• Séance préconisée : Marche active (30 min)"
            elif self.current_user.goal == "force":
                msg = "Profil Débutant détecté :\n• Séance préconisée : Renforcement musculaire léger"
            else:
                msg = "Profil Débutant détecté :\n• Séance préconisée : Jogging d'endurance fondamentale (20 min)"
        else:
            rec = recommend_session(self.current_user, df_user)
            msg = f"Exercice cible : {rec['exercise'].capitalize()}\nDurée idéale : {rec['duration']} min\n\nNote IA : {rec['message']}"

        tb1.insert("0.0", msg)
        tb1.configure(state="disabled")

        carte_physique = self.creer_carte_blanche(1, 1, "📋  Vos Paramètres")
        meta = (f"• Objectif ciblé : {self.current_user.goal}\n"
                f"• IMC Calculé : {self.current_user.calculate_bmi()}\n"
                f"• Métabolisme : {self.current_user.daily_calories()} kcal/jour")
        lbl_meta = ctk.CTkLabel(carte_physique, text=meta, justify="left",
                                 font=FONT_BODY, text_color=COL_TEXT_DIM)
        lbl_meta.pack(anchor="w", padx=18, pady=(0, 20))

    def afficher_vue_programme_semaine(self):
        self.nettoyer_zone_droite()
        carte_prog = self.creer_carte_blanche(0, 0, "📅  Calendrier Hebdomadaire", columnspan=2)

        days_frame = ctk.CTkFrame(carte_prog, fg_color="transparent")
        days_frame.pack(fill="x", padx=18, pady=(0, 18))

        prog = Program(self.current_user)
        for idx, jour in enumerate(prog.generate_program()):
            days_frame.grid_columnconfigure(idx, weight=1)
            box = ctk.CTkFrame(days_frame, fg_color=COL_BG, height=130, corner_radius=10,
                                border_width=1, border_color=COL_CARD_BORDER)
            box.grid(row=0, column=idx, padx=4, sticky="nsew")
            ctk.CTkLabel(box, text=jour['day'], font=("Segoe UI", 12, "bold"),
                         text_color=COL_ACCENT).pack(pady=(10, 4))
            ctk.CTkLabel(box, text=f"{jour['exercise']}\n⏱️ {jour['duration']}m\n⚡ {jour['intensity']}",
                         font=("Segoe UI", 10), text_color=COL_TEXT_DIM, justify="center").pack(pady=5)

    def afficher_vue_historique_personnel(self):
        self.nettoyer_zone_droite()
        carte_hist = self.creer_carte_blanche(0, 0, "📜  Vos séances passées enregistrées", columnspan=2)

        history = self.dm.get_user_history(self.current_user.user_id, self.df_clean)
        tb = ctk.CTkTextbox(carte_hist, height=260, font=FONT_MONO, fg_color=COL_BG,
                             border_width=1, border_color=COL_CARD_BORDER, corner_radius=10,
                             text_color=COL_TEXT)
        tb.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        if history is None or history.empty:
            tb.insert("0.0", "Aucune activité présente dans votre historique.")
        else:
            tb.insert("0.0", history.to_string(index=False))
        tb.configure(state="disabled")

    def afficher_vue_stats_globales(self):
        self.nettoyer_zone_droite()
        carte_stats = self.creer_carte_blanche(0, 0, "📊  Rapport d'analyse du jeu de données", columnspan=2)

        tb = ctk.CTkTextbox(carte_stats, height=260, font=FONT_MONO, fg_color=COL_BG,
                             border_width=1, border_color=COL_CARD_BORDER, corner_radius=10,
                             text_color=COL_TEXT)
        tb.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        if self.df_clean is None or self.df_clean.empty:
            tb.insert("0.0", "Aucun historique global dans le système.")
        else:
            tb.insert("0.0", weekly_analysis(self.df_clean).to_string(index=False))
        tb.configure(state="disabled")

    def afficher_vue_scipy(self):
        self.nettoyer_zone_droite()
        carte_sci = self.creer_carte_blanche(0, 0, "🔬  Calculs Mathématiques Avancés (SciPy)", columnspan=2)

        tb = ctk.CTkTextbox(carte_sci, height=360, font=FONT_MONO, fg_color=COL_BG,
                             border_width=1, border_color=COL_CARD_BORDER, corner_radius=10,
                             text_color=COL_TEXT)
        tb.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        if self.df_clean is None or self.df_clean.empty:
            tb.insert("0.0", "Erreur : Base de données vide, calculs mathématiques impossibles.")
        else:
            res = f"--- ANOVA CALORIES PAIRES ---\n{test_anova_calories(self.df_clean)}\n\n"
            res += f"--- REGRESSION LINEAIRE PROGRESSION ---\n{regress_progress(self.df_clean, 'calories')}\n\n"
            res += f"--- STUDENT T-TEST APPARIÉ ---\n{ttest_paired(self.df_clean, 'calories')}"
            tb.insert("0.0", res)
        tb.configure(state="disabled")

    def action_generer_demo(self):
        self.nettoyer_zone_droite()
        generate_simulated_users(5)
        generate_simulated_data(days_nb=30)
        self.df_clean = clean_dataset()

        carte_confirm = self.creer_carte_blanche(0, 0, "🤖  Système synchronisé", columnspan=2)
        ctk.CTkLabel(
            carte_confirm,
            text="✅ Succès ! 5 profils virtuels et 30 entraînements fictifs injectés dans data/.\nLes modules statistiques sont désormais actifs.",
            text_color=COL_SUCCESS, font=("Segoe UI", 13, "bold")
        ).pack(padx=18, pady=(0, 18))


if __name__ == "__main__":
    app = ModernFitnessDashboard()
    app.mainloop()
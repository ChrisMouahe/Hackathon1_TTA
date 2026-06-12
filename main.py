# -*- coding: utf-8 -*-
"""
Création du fichier main.py qui est le point d'entrée unique. 
Il importe tous les modules et expose un menu console interactif où chaque option appelle une fonction bien isolée.
"""

from models import User, Session, Program
from data_manager import DataManager, generate_simulated_data, generate_simulated_users, clean_dataset, weekly_analysis
from workout_generator import recommend_session
from scipy_analysis import test_anova_calories, regress_progress, ttest_paired
from visualizations import (graph_calories_over_time, graph_workout_frequency, graph_weekly_progression, generate_all_graphs)

current_user = None

def register_user(dm):

  HEALTH_CONDITIONS = [
    None,
    "maladie_cardiaque",
    "probleme_genoux",
    "probleme_cheville",
    "arthrite",
    "ulcere"
  ]
    print('--- Inscription ---')
    name = input('Nom : ').strip()

    for i in range(3):
        age_input = input('Âge : ').strip()
        if age_input.isdigit() and 0 < int(age_input) < 120:
            age = int(age_input)
            break
        else:
            print("Âge invalide. Veuillez entrer un nombre entre 1 et 119.")
    else:
        try:
            age = int(input('Âge : ').strip())
        except ValueError:
            print("Âge invalide, valeur par défaut fixée à 30 ans.")
            age = 30

    gender = input('Genre (M/F) : ').strip().upper()

    for i in range(3):
        weight_input = input('Poids (kg) : ').strip()
        try:
            weight = float(weight_input)
            if weight > 0:
                break
            else:
                print("Poids doit être un nombre positif.")
        except ValueError:
            print("Poids invalide. Veuillez entrer un nombre.")
    else:
        try:
            weight = float(input('Poids (kg) : ').strip())
        except ValueError:
            print("Poids invalide, valeur par défaut fixée à 70 kg.")
            weight = 70.0

    try:
        height = int(input('Taille (cm) : ').strip())
    except ValueError:
        print("Taille invalide, valeur par défaut fixée à 175 cm.")
        height = 175

    goal = input('Objectif (perte_poids, force, cardio) : ').strip()
    if goal in ['perte_poids', 'force']:
        target_weight = input('Quelle masse souhaitez-vous atteindre (kg) : ').strip()
        try:
            target_weight = float(target_weight)
        except ValueError:
            print("Objectif de masse invalide, valeur par défaut fixée à None.")
            target_weight = None

  #Vérifier les conditions médicales de l'utilisateur
    print("\nConditions médicales :")
    print("1. Aucune")
    print("2. Maladie cardiaque")
    print("3. Problème de genoux")
    print("4. Problème de cheville")
    print("5. Arthrite")
    print("6. Ulcère")

    choix = input("Choix : ")
    mapping = {
    "1": None,
    "2": "maladie_cardiaque",
    "3": "probleme_genoux",
    "4": "probleme_cheville",
    "5": "arthrite",
    "6": "ulcere"
  }

    health_condition = mapping.get(choix)

    new_user = User(user_id=dm.get_next_user_id(), name=name, age=age, weight=weight, height=height, goal=goal, gender=gender, health_condition=health_condition, target_weight=target_weight)

    print(f' Fitness Tracker IA — Bonjour {new_user.name} !')
    print(' IMC :', new_user.calculate_bmi(), '—', new_user.bmi_category())
    print(' Calories journalières estimées :', new_user.daily_calories())
    print('='*50)
    return new_user

#Suivi de la masse cible
def progress_to_target(user):
  difference = (user.weight - user.target_weight)
  
  return {
    "remaining_kg": round(abs(difference),1),
    "target_reached":
        abs(difference) < 1
    }


def menu():
    global current_user
    dm = DataManager()
    df_clean = clean_dataset()

    while True:
        print('\n' + '='*50)

        if current_user is None:
            print(" [ MODE VISITEUR ]")
            print(' 1. Inscription')
            print(' 2. Connexion')
            print(' 0. Quitter')
        else:
            print(f" [ SESSION : {current_user.name.upper()} ]")
            print(' 1. Voir ma recommandation du jour')
            print(' 2. Mon programme de la semaine')
            print(' 3. Voir mon historique d\'activités')
            print(' 4. Mes statistiques hebdomadaires')
            print(' 5. Mes analyses statistiques')
            print(' 6. Générer mes graphiques de progression')
            print(' 7. Consulter mes graphiques ')
            print(' 8. Voir ma progression vers mon objectif')
            print(' 9. Consulter mes analyses enregistrées')
            print(' 10. Se déconnecter')
            print(' 0. Quitter')

        choix = input('\nVotre choix : ').strip()

        # =====================================================================
        # MODE DÉCONNECTÉ
        # =====================================================================
        if current_user is None:

            if choix == '1':
                user = register_user(dm)
                dm.save_user(user)
                current_user = user
                print(f"Inscription réussie. Vous êtes maintenant connecté.")

            elif choix == '2':
                print('--- Connexion ---')
                while not current_user:
                    name = input("Entrez votre nom pour vous connecter (ou 'q' pour annuler) : ").strip()
                    if name.lower() == 'q':
                        break
                    current_user = dm.find_user_by_name(name)
                    if current_user:
                        print(f'Bienvenue de nouveau, {current_user.name} !')
                    else:
                        print('Utilisateur non trouvé. Essayez à nouveau.')

            elif choix == '0':
                print('Au revoir !')
                break

        # =====================================================================
        # MODE CONNECTÉ
        # =====================================================================
        else:

            if choix == '1':
                if df_clean is None or 'user_id' not in df_clean.columns:
                    print("Aucune donnée utilisateur trouvée dans les séances.")
                    continue
                df_user = dm.get_user_history(current_user.user_id, df_clean)
                if df_user is None or df_user.empty:
                    if current_user.goal == "perte_poids":
                        print("Programme débutant : marche rapide 30 min")
                    elif current_user.goal == "force":
                        print("Programme débutant : musculation légère")
                    elif current_user.goal == "cardio":
                        print("Programme débutant : jogging 20 min")
                else:
                    rec = recommend_session(current_user, df_user)
                    print(f'\nRecommandation : {rec["exercise"].capitalize()} — {rec["duration"]} min')
                    print(f'Conseil : {rec["message"]}')

            elif choix == '2':
                if df_clean is None or 'user_id' not in df_clean.columns:
                    print("Aucune donnée utilisateur trouvée dans les séances.")
                    continue
                prog = Program(current_user)
                for jour in prog.generate_program():
                    print(f" {jour['day']:10} {jour['exercise']:15} {jour['duration']} min — {jour['intensity']}")

            elif choix == '3':
                if df_clean is None or df_clean.empty:
                    print("Aucune donnée disponible dans le système.")
                    continue
                history = dm.get_user_history(current_user.user_id, df_clean)
                if history is None or history.empty:
                    print("Aucune activité enregistrée pour votre profil.")
                else:
                    print("\n=== HISTORIQUE D'ACTIVITES ===")
                    print(history.to_string(index=False))

            elif choix == '4':
                if df_clean is None or df_clean.empty:
                    print("Aucune donnée disponible pour l'analyse.")
                    continue
                print(weekly_analysis(df_clean).to_string(index=False))

            elif choix == '5':
              df_user = dm.get_user_history(current_user.user_id, df_clean)
                if df_clean is None or df_clean.empty:
                    print("Aucune donnée disponible pour modéliser les graphiques.")
                    continue
                anova = test_anova_calories(df_user)
                regression = regress_progress(df_user)
                ttest = ttest_paired(df_user)
                
                #Construction du rapport
                from datetime import datetime
                report = {

                    "date_analyse":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        ),

                    "user_id":
                        current_user.user_id,

                    "anova":
                        anova,

                    "regression":
                        regression,

                    "ttest":
                        ttest
                }
                dm.save_user_report(current_user.user_id, report)
                print('\nAnalyse enregistrée')

            elif choix == '6':
                
            elif choix == '6':
                if current_user is None:
                    print("Veuillez vous connecter.")
                    continue
            
                df_user = dm.get_user_history(current_user.user_id, df)
                df_user = dm.get_user_history(current_user.user_id, df)
                graph_workout_frequency(df_user, f"{folder}/frequency.png")

                graph_weekly_progression(df_user, f"{folder}/progression.png")
                graph_calories_over_time(df_user, f"{folder}/calories.png")
                print(f"Graphiques enregistrés dans {folder}")

                dm.save_graph_metadata(current_user.user_id)

            elif choix == '6':
                print(f"Déconnexion réussie. Au revoir {current_user.name} !")
                current_user = None
                menu()

            elif choix == '0':
                print('Au revoir !')
                break


if __name__ == '__main__':
    menu()
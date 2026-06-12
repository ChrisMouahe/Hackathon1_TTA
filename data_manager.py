# -*- coding: utf-8 -*-

"""Creation du fichier data_manager.py (Gestion des données) qui est le coeur de la gestion de données.

Ce système devra :
- Sauvegarder les séances dans un fichier JSON
- Charger les séances depuis le JSON
- Transformer les données en DataFrame Pandas
- Générer les données fictives pour les démonstrations
- Produire des statistiques avec Pandas
"""

#Création de la class DataManager qui va gérer tous les accès au fichier JSON
import os, json
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from datetime import datetime, timedelta, date
from models import Session, User

class DataManager:
    def __init__(self, path='data/sessions.json', path_users='data/users.json', reports_dir):
        self.path = path
        self.path_users = path_users
        self.reports_dir = "data/user_reports"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        os.makedirs(os.path.dirname(path_users), exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    #Créer la méthode save_session qui charge l'historique actuel, ajoute la nouvelle session et réécrit le JSON
    def save_session(self, session):
        historic = self.load_historic_raw()
        historic.append(session.to_dict())
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(historic, f, ensure_ascii=False, indent=2)

    #Créer la méthode load_historic_raw qui retourne la liste brute de dicts depuis json
    def load_historic_raw(self):
        if not os.path.exists(self.path):
            return []

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    #Créer la méthode load_dataframe qui convertit tout l'historique en un dataframe pandas
    #JSON --> Liste de dictionnaire --> Dataframe Pandas
    def load_dataframe(self):
        data = self.load_historic_raw()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # Vérifier que la colonne 'date' existe avant de la convertir
        if 'date' not in df.columns:
            return pd.DataFrame()

        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Supprimer les lignes dont la date est invalide
        df = df.dropna(subset=['date'])

        df['week'] = df['date'].dt.isocalendar().week.astype(int)
        df['day'] = df['date'].dt.day_name()

        return df

#Configuration du dataset USER 
    #Méthode pour sauvegarder les informations de l'utilisateur dans un fichier JSON séparé
    def save_user(self, user):
        #Vérifie si l'utilisateur existe déjà pour éviter les doublons
        if self.user_exists(
            user.name, 
            user.age, 
            user.gender
            ):
            print(f"Utilisateur {user.name} déjà enregistré.")
            return False

        #Si l'utilisateur n'existe pas, ajoute-le au fichier JSON
        users = self.load_users_raw()
        users.append(user.to_dict())
        with open(self.path_users, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        print(f"Utilisateur {user.name} enregistré avec succès.")
        return True

    #Méthode pour générer automatiquement un user_id unique basé sur le nombre d'utilisateurs déjà enregistrés
    
    def get_next_user_id(self):
        users = self.load_users_raw()
        if not users:
            return 1
        else:
            return len(users) + 1

    
    #Méthode pour charger les données utilisateur depuis le JSON
    def load_users_raw(self):
        if not os.path.exists(self.path_users):
            return []
        try:
            with open(self.path_users, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []


    #Créer une methode de recherche qui vérifie si un utilisateur existe déjà dans le JSON pour éviter les doublons
    def user_exists(self, name, age, genre):
        users = self.load_users_raw()

        for user in users:

            if (
                user['name'].lower() == name.lower()
                and user['age'] == age
                and user['gender'] == genre
            ):
                return True

        return False


    #Méthode qui recherche un utilisateur par son nom et retourne ses informations sous forme de dictionnaire
    def find_user_by_name(self, name):
        users = self.load_users_raw()

        for user in users:
            if user['name'].lower() == name.lower():
                return User(
                    user_id=user['user_id'],
                    name=user['name'],
                    age=user['age'],
                    weight=user['weight'],
                    height=user['height'],
                    goal=user['goal'],
                    gender=user['gender'],
                    health_condition=user['health_condition']
                )

        return None
    #Méthode qui enregistre l'historique de chaque utilisateur    
    def get_user_history(self, user_id, df_clean=None):

        if df_clean is None or df_clean.empty:
            return pd.DataFrame()
        
        if 'user_id' not in df_clean.columns:
            return pd.DataFrame()
        
        return df_clean[
                df_clean['user_id'].astype(str) == str(user_id)
                ].reset_index(drop=True)
        """ sessions = self.load_historic_raw()

        user_sessions = []

        for session in sessions:

            if "user_id" not in session:
                continue

            if str(session["user_id"]) == str(user_id):
                user_sessions.append(session)

        return pd.DataFrame(user_sessions) """
    
    #Créer une méthode pour sauvegarder un rapport
    def save_user_report(self, user_id, report):
        def save_user_report(
    self,
    user_id,
    report
    ):

    path = (
        f"{self.reports_dir}/"
        f"user_{user_id}_report.json"
    )

    reports = []

    if os.path.exists(path):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            reports = json.load(f)

    reports.append(report)

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            reports,
            f,
            indent=2,
            ensure_ascii=False
        )

    def load_user_reports(self, user_id):

        path = (
            f"{self.reports_dir}/"
            f"user_{user_id}_report.json"
        )

        if not os.path.exists(path):
            return []

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    #Méthode
    def get_user_graph_dir(self, user_id):
        folder = f"graphs/user_{user_id}"

        os.makedirs(folder, exist_ok=True)

        return folder

    #Créer la méthode export_csv pour permettre à l'utilisateur d'avoir export.csv
    def export_csv(self, file_name='data/export.csv'):
        df = self.load_dataframe()
        if not df.empty:
            df.to_csv(file_name, index=False, encoding='utf-8')
        print(f'Export csv : {file_name}')

#Méthode pour sauvegarder les métadonnées des graphiques
def save_graph_metadata(self, user_id):

    folder = self.get_user_graph_dir(user_id)

    metadata = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "graphs": []
    }

    for file in os.listdir(folder):

        if file.endswith(".png"):

            metadata["graphs"].append(file)

    with open(
        f"{folder}/graphs.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=2,
            ensure_ascii=False
        )

#Méthode pour lire les données
def load_graph_metadata(self, user_id):

    folder = self.get_user_graph_dir(user_id)

    path = f"{folder}/graphs.json"

    if not os.path.exists(path):
        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

    #Generer des données utilisateur fictives pour les démonstrations
def generate_simulated_users(user_nb=5, seed=42):
    np.random.seed(seed)

    dm = DataManager()

    first_names = [
        "Kouassi", "Kouame", "Yao", "Aya", "Aminata",
        "Fatou", "Koffi", "Awa", "Mariam", "Bamba"
    ]
    health_conditions = [
        None,
        "maladie_cardiaque",
        "probleme_genoux",
        "probleme_cheville",
        "arthrite",
        "ulcere"
        ]

    goals = ["perte_poids", "force", "cardio"]

    for i in range(user_nb):

        gender = np.random.choice(["M", "F"])
        goal = np.random.choice(goals)
        user = User(
            user_id=dm.get_next_user_id(),
            name=f"{np.random.choice(first_names)}_{i+1}",
            age=int(np.random.randint(18, 60)),
            weight=round(float(np.random.uniform(50, 110)), 1),
            height=int(np.random.randint(150, 200)),
            goal=goal,
            gender=gender,
            health_condition=np.random.choice(health_conditions, p=[0.7, 0.05, 0.08, 0.05, 0.07, 0.05]), # 70% sans condition, 30% avec différentes conditions
            target_weight= round(float(np.random.uniform(50, 110)), 1) if goal in ['perte_poids', 'force'] else None

        )

        dm.save_user(user)

    print(f"{user_nb} utilisateurs simulés enregistrés.")

    


"""
Création d'un dataset 'sale' qui contient des valeurs manquantes, aberrantes et négatives
Méthode inject_anomalies pour injecter des valeurs problématiques dans le dataset
"""

def inject_anomalies(session, dm):

    #Valeurs manquantes : injecter 8% dans le dataset
    if np.random.random() < 0.08: 
        session.calories = np.nan
    if np.random.random() < 0.08:
        session.steps = np.nan

    #Valeurs aberrantes : injecter 3% dans le dataset
    if np.random.random() < 0.03:
        session.calories = 5000
    if np.random.random() < 0.03:
        session.steps = 100000

    #Valeurs négatives : injecter 2% dans le dataset
    if np.random.random() < 0.02:
        session.calories = -100
    if np.random.random() < 0.02:
        session.steps = -1000

    #Valeurs incohérentes (Soucis de casse) : Injecter 5% dans le dataset
    if np.random.random() < 0.05:
        session.workout_type = session.workout_type.upper()

    #Sauvegarde de la session
    dm.save_session(session)

    # Injecter 5% de doublons : Après la sauvegarde normale pour faire enregistrer certaines lignes 2 fois.
    if np.random.random() < 0.05:
        dm.save_session(session)

    # df charge ici avant d'etre utilisé

"""Générer les données simulées"""

def generate_simulated_data(days_nb=5, seed=42):
    np.random.seed(seed) #Pour avoir toujours les mêmes résultats
    dm = DataManager()
    sessions = dm.load_historic_raw()

    
    df = dm.load_dataframe() # Charger les données existantes pour éviter de les écraser à chaque génération
    types_exercise = ['yoga', 'running', 'hiit', 'musculation', 'natation', 'marche']

    # Calories moyennes par type (min, max)
    calories_map = {
        'yoga':        (150, 250),
        'running':     (280, 420),
        'hiit':        (350, 500),
        'musculation': (200, 350),
        'marche':      (100, 200),
        'natation':    (300, 450)
    }

    today = date.today()
    users = dm.load_users_raw()

    for user in users:
        user_id = user["user_id"]
        for i in range(days_nb):
            seance_date = today - timedelta(days=days_nb - i)
            type_ex = np.random.choice(types_exercise)
            min_cal, max_cal = calories_map[type_ex]
            session = Session(
                user_id      = user_id,
                workout_type = type_ex,
                duration     = int(np.random.randint(15, 60)),
                intensity    = np.random.choice(['faible', 'modérée', 'élevée']),
                calories     = round(float(np.random.uniform(min_cal, max_cal))),
                steps        = int(np.random.randint(2000, 12000)),
                date_str     = str(seance_date)
            )
            inject_anomalies(session, dm)

    df = dm.load_dataframe()

    print(
        f"{days_nb} séances simulées pour chaque utilisateur enregistrées."
    )

    print("\n====== Taille du dataset ======")
    print(df.shape)

    print("\n====== 5 premières lignes ======")
    print(df.head())

    if not df.empty:

        print("\n====== Résumé statistique ======")
        print(df.describe())

        print("\n====== Données manquantes ======")
        print(df.isna().sum())

        print("\n====== Doublons ======")
        print(df.duplicated().sum())

    return df


#Prétraitement et nettoyage du dataset 'sale'
def clean_dataset():
    dm = DataManager()
    df = dm.load_dataframe()

    # Vérifier que df n'est pas vide après le chargement
    if df is None or df.empty:
        return pd.DataFrame()
    else:
        # 1. Supprimer les doublons
        df = df.drop_duplicates()

        # 2. Uniformiser les catégories
        # Vérifier si la colonne 'workout_type' existe avant de la traiter
        if 'workout_type' in df.columns:
            df["workout_type"] = df["workout_type"].str.lower()

        # 3. Convertir les colonnes numériques
        df["calories"] = pd.to_numeric(df["calories"], errors="coerce")
        df["steps"]    = pd.to_numeric(df["steps"],    errors="coerce")

        # 4. Remplacer les valeurs manquantes
        df["calories"] = SimpleImputer(strategy="median").fit_transform(df[["calories"]])
        df["steps"]    = SimpleImputer(strategy="median").fit_transform(df[["steps"]])

        # 5. Harmoniser les valeurs incohérentes
        df["workout_type"] = df["workout_type"].str.lower()

        # 5. Retirer les valeurs aberrantes
        Q1  = df["calories"].quantile(0.25)
        Q3  = df["calories"].quantile(0.75)
        IQR = Q3 - Q1
        df  = df[(df["calories"] >= Q1 - 1.5 * IQR) & (df["calories"] <= Q3 + 1.5 * IQR)]

        q1  = df["steps"].quantile(0.25)
        q3  = df["steps"].quantile(0.75)
        iqr = q3 - q1
        df  = df[(df["steps"] >= q1 - 1.5 * iqr) & (df["steps"] <= q3 + 1.5 * iqr)]

    return df

"""Création des méthodes pour l'analyse hebdomadaire"""

#Méthode weekly_analysis pour calculer les totaux par semaine
def weekly_analysis(df):
    weekly = df.groupby('week').agg(
        total_calories=('calories', 'sum'),
        total_steps=('steps', 'sum')
    ).reset_index()
    return weekly

#Méthode type_stats pour calculer les statistiques descriptives par type d'exercice
def type_stats(df):
    return df.groupby('workout_type')['calories'].agg(
        mean_calories='mean',
        std_calories='std',
        min_calories='min',
        max_calories='max',
        count_calories='count'
    ).round(1)

#Méthode exercise_frequency pour calculer la fréquence de chaque type d'exercice
def exercise_frequency(df):
    freq = df['workout_type'].value_counts().reset_index()
    freq.columns = ['workout_type', 'frequency']
    return freq


if __name__ == '__main__': #Cette ligne teste si le fichier est exécuté directement.
    generate_simulated_users() 
    generate_simulated_data() #sinon il ignore cette ligne pour ne pas générer des données non voulues si le fichier est importé et exécuté ailleurs
    reponse = input('Enclanchez le nettoyage du dataset ? (oui/non) : ').strip().lower()
    if reponse == 'oui':
        clean_dataset()
        df_clean = clean_dataset()
        print('\n=== DATASET NETTOYE ===')
        print(df_clean.shape)
        print(df_clean.head())
        print('\nTotal des données manquantes par colonne :\n', df_clean.isna().sum())
        print('\nStatistiques descriptives après nettoyage :\n', df_clean.describe())
        print(df_clean.info())
        print('valeurs dupliquées :', df_clean.duplicated().sum())
    
    else:
        print('Dataset non nettoyé. Certaines analyses et visualisations peuvent être affectées par les anomalies présentes dans les données.')

    

    
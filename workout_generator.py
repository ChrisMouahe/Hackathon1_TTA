import pandas as pd
from datetime import date, timedelta

# ============================================================
# THRESHOLDS — Niveaux d'activité basés sur les calories moyennes des 7 derniers jours
# ============================================================

THRESHOLDS = {
    'faible': 200,      # moins de 200 cal/day → Activité faible
    'modéré': 350, # entre 200 et 350   → Activité modérée
    'élevé': 400       # plus de 350             → Activité élevée
}

# ============================================================
# RESTRICTIONS MÉDICALES — Types d'exercices à éviter selon les conditions de santé
# ============================================================

MEDICAL_RESTRICTIONS = {

    "maladie_cardiaque":
        ["running", "hiit"],

    "probleme_genoux":
        ["running"],

    "probleme_cheville":
        ["running", "hiit"],

    "arthrite":
        ["running", "hiit"],

    "ulcere":
        []
}


# ============================================================
# RECOMMENDATIONS — (Objectif, niveau) → (exercice, durée, message)
# ============================================================

RECOMMENDATIONS = {
    # Weight loss
    ('weight_loss', 'faible'):      ('marche',  30, 'Activité légère pour reprendre doucement. Essayez une marche de 30 min.'),
    ('weight_loss', 'modéré'):      ('hiit',     25, 'Excellent rythme ! Essayez une session HIIT de 25 min.'),
    ('weight_loss', 'élevé'):       ('yoga',     40, 'Récupération active recommandée : 40 min de yoga pour étirer les muscles.'),

    # Strength
    ('strength', 'faible'):         ('musculation', 40, 'Reprenez avec une session de musculation modérée. 40 min suffisent pour stimuler les muscles.'),
    ('strength', 'modéré'):         ('musculation', 50, 'Super ! Poussez un peu plus avec 50 min de musculation.'),
    ('strength', 'élevé'):          ('marche',  30, 'Récupération active recommandée : 30 min de marche pour favoriser la récupération.'),

    # Cardio
    ('cardio', 'faible'):           ('running',  30, 'Recommencez avec une session de jogging léger de 30 min.'),
    ('cardio', 'modéré'):           ('natation', 35, 'alternez avec 35 min de natation pour un cardio complet.'),
    ('cardio', 'élevé'):            ('yoga',     30, 'Etirez et récupérez avec 30 min de yoga. Votre corps vous remerciera !'),
}


# ============================================================
# FUNCTION 1 : Determine le niveau d'activité et recommander une session
# ============================================================

def activity_level(df_7days):
    """
    Détermine le niveau d'activité (faible, modéré, élevé) basé sur les calories moyennes
    des 7 derniers jours.

    paramètres :
    df_7days : DataFrame filtré sur les 7 derniers jours

    retourne : 'faible', 'modéré' ou 'élevé'
    """
    # Pas assez de données pour évaluer → considérer comme faible ('faible')
    if df_7days.empty:
        return 'faible'

    # calculer la moyenne des calories sur les 7 derniers jours
    avg_calories = df_7days['calories'].mean()

    if avg_calories < THRESHOLDS['faible']:
        return 'faible'
    elif avg_calories < THRESHOLDS['modéré']:
        return 'modéré'
    else:
        return 'élevé'


# ============================================================
# FUNCTION 2 : Recommander une session personnalisée
# ============================================================

def recommend_session(user, df):
    """
    Retourne une recommandation d'exercice basée sur l'objectif de l'utilisateur et son niveau d'activité récent.

    paramètres :
        user : objet User avec les informations de l'utilisateur
        df : DataFrame avec les données d'activité de l'utilisateur (de data_manager.py)

    retourne : 
        dict avec 'exercise', 'duration', 'message', 'activity_level' et 'avg_calories_7days'
    """
    # filtre les données sur les 7 derniers jours
    limit = pd.Timestamp(date.today() - timedelta(days=7))
    df_7days = df[df['date'] >= limit]

    # détermine le niveau d'activité
    level = activity_level(df_7days)

    # crée la clé pour obtenir la recommandation basée sur l'objectif et le niveau d'activité
    key = (user.goal, level)
    fallback_key = ('cardio', level)  # default if goal not found

    # obtenir la recommandation correspondante
    exercise, duration, message = RECOMMENDATIONS.get(
        key, RECOMMENDATIONS[fallback_key]
    )

    # Calcule la moyenne des calories sur les 7 derniers jours pour fournir un feedback à l'utilisateur
    avg_cal = round(df_7days['calories'].mean(), 1) if not df_7days.empty else 0

    # Appliquer les restrictions médicales
    if user.health_condition:

    interdits = MEDICAL_RESTRICTIONS.get(
        user.health_condition,
        []
    )

    if exercise in interdits:

        exercise = "marche"

        duration = 20

        message = (
            "Programme adapté à votre condition médicale."
        )
    return {
        'exercise': exercise,
        'duration': duration,
        'message': message,
        'activity_level': level,
        'avg_calories_7days': avg_cal
    }


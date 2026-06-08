import pandas as pd
from datetime import date, timedelta

# ============================================================
# THRESHOLDS — Niveaux d'activité basés sur les calories moyennes des 7 derniers jours
# ============================================================

THRESHOLDS = {
    'low': 200,      # moins de 200 cal/day → Activité faible
    'moderate': 350  # entre 200 et 350   → Activité modérée
}                    # plus de 350             → Activité élevée


# ============================================================
# RECOMMENDATIONS — (Objectif, niveau) → (exercice, durée, message)
# ============================================================

RECOMMENDATIONS = {
    # Weight loss
    ('weight_loss', 'low'):      ('marche',  30, 'Activité légère pour reprendre doucement. Essayez une marche de 30 min.'),
    ('weight_loss', 'moderate'): ('hiit',     25, 'Excellent rythme ! Essayez une session HIIT de 25 min.'),
    ('weight_loss', 'high'):     ('yoga',     40, 'Récupération active recommandée : 40 min de yoga pour étirer les muscles.'),

    # Strength
    ('strength', 'low'):         ('musculation', 40, 'Reprenez avec une session de musculation modérée. 40 min suffisent pour stimuler les muscles.'),
    ('strength', 'moderate'):    ('musculation', 50, 'Super ! Poussez un peu plus avec 50 min de musculation.'),
    ('strength', 'high'):        ('marche',  30, 'Récupération active recommandée : 30 min de marche pour favoriser la récupération.'),

    # Cardio
    ('cardio', 'low'):           ('running',  30, 'Recommencez avec une session de jogging léger de 30 min.'),
    ('cardio', 'moderate'):      ('natation', 35, 'alternez avec 35 min de natation pour un cardio complet.'),
    ('cardio', 'high'):          ('yoga',     30, 'Etirez et récupérez avec 30 min de yoga. Votre corps vous remerciera !'),
}


# ============================================================
# FUNCTION 1 : Determine le niveau d'activité et recommander une session
# ============================================================

def activity_level(df_7days):
    """
    Détermine le niveau d'activité (low, moderate, high) basé sur les calories moyennes
    des 7 derniers jours.

    paramètres :
    df_7days : DataFrame filtré sur les 7 derniers jours

    retourne : 'low', 'moderate' ou 'high'
    """
    # Pas assez de données pour évaluer → considérer comme faible ('low')
    if df_7days.empty:
        return 'low'

    # calculer la moyenne des calories sur les 7 derniers jours
    avg_calories = df_7days['calories'].mean()

    if avg_calories < THRESHOLDS['low']:
        return 'low'
    elif avg_calories < THRESHOLDS['moderate']:
        return 'moderate'
    else:
        return 'high'


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

    return {
        'exercise': exercise,
        'duration': duration,
        'message': message,
        'activity_level': level,
        'avg_calories_7days': avg_cal
    }


# ============================================================
# QUICK TEST — exécutez ce bloc pour tester rapidement la recommandation
# ============================================================

if __name__ == '__main__':
    from models import User

    # Create a test user
    alice = User('Alice', 30, 62.0, 165, 'weight_loss', 'F')

    # Simulate a small DataFrame
    data = {
        'date': pd.to_datetime([
            str(date.today() - timedelta(days=i)) for i in range(7)
        ]),
        'calories': [300, 250, 320, 280, 310, 290, 305],
        'workout_type': ['running', 'yoga', 'hiit', 'walking',
                         'running', 'swimming', 'hiit']
    }
    df_test = pd.DataFrame(data)

    # Test activity_level
    print('=== ACTIVITY LEVEL ===')
    level = activity_level(df_test)
    print('Level :', level)

    # Test recommend_session
    print('\n=== RECOMMENDATION ===')
    rec = recommend_session(alice, df_test)
    print(f"Exercise     : {rec['exercise']}")
    print(f"Duration     : {rec['duration']} min")
    print(f"Message      : {rec['message']}")
    print(f"Activity     : {rec['activity_level']}")
    print(f"Avg calories : {rec['avg_calories_7days']} cal/day")
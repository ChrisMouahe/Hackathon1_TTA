from datetime import date


# ============================================================
# CLASS 1 : User profile
# ============================================================

class User:
    """Représente un utilisateur du tracker fitness."""

    def __init__(self, user_id, name, age, weight, height, goal, gender='M', masse_goal=None):
        self.user_id = user_id
        self.name = name            
        self.age = age              
        self.weight = weight     
        self.height = height     
        self.goal = goal            
        self.gender = gender        
        self.masse_goal = masse_goal
        self.journal = []           

    def calculate_bmi(self):
        """BMI = weight (kg) / height (m)²"""
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 1)

    def bmi_category(self):
        """Returns BMI category based on WHO standards."""
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal weight'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    def daily_calories(self):
        """Estimation des besoins caloriques quotidiens."""
        if self.gender == 'M':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return round(bmr * 1.55)

    def to_dict(self):
        """Convertis l'objet User en dictionnaire pour la sauvegarde JSON."""
        return {
            'name': self.name,
            'age': self.age,
            'weight': self.weight,
            'height': self.height,
            'goal': self.goal,
            'gender': self.gender,
            'user_id': self.user_id,
            'masse_goal': self.masse_goal
        }


# ============================================================
# CLASS 2 : Workout session
# ============================================================

class Session:
    """Représente une session de workout individuelle."""

    VALID_TYPES = ['yoga', 'running', 'hiit', 'musculation', 'natation', 'marche']

    def __init__(self, user_id, workout_type, duration, intensity, calories,
                 steps=0, date_str=None):
        self.user_id = user_id
        self.workout_type = workout_type.lower()
        self.duration = duration
        self.intensity = intensity
        self.calories = calories
        self.steps = steps
        self.date = date_str or str(date.today())

    def to_dict(self):
        """Convertit l'objet Session en dictionnaire pour la sauvegarde JSON."""
        return {
            'user_id': self.user_id,
            'date': self.date,
            'workout_type': self.workout_type,
            'duration': self.duration,
            'intensity': self.intensity,
            'calories': self.calories,
            'steps': self.steps            
        }

    @classmethod
    def from_dict(cls, d):
        """Reconstruit l'objet à partir d'un dictionnaire (chargement JSON)."""
        return cls(
            d['user_id'],
            d['workout_type'],
            d['duration'],
            d['intensity'],
            d['calories'],
            d.get('steps', 0),
            d.get('date')
        )


# ============================================================
# CLASS 3 : Weekly training program
# ============================================================

class Program:
    """Générer un plan d'entraînement hebdomadaire personnalisé."""

    PLANS = {
        'weight_loss': {
            'sessions': ['running', 'hiit', 'walking', 'yoga', 'hiit'],
            'durations': [30, 25, 45, 40, 30],
            'intensities': ['moderate', 'high', 'low', 'low', 'high']
        },
        'strength': {
            'sessions': ['strength', 'strength', 'yoga', 'strength', 'walking'],
            'durations': [45, 45, 30, 50, 30],
            'intensities': ['high', 'high', 'low', 'high', 'low']
        },
        'cardio': {
            'sessions': ['running', 'swimming', 'running', 'hiit', 'swimming'],
            'durations': [35, 40, 30, 25, 45],
            'intensities': ['moderate', 'moderate', 'high', 'high', 'moderate']
        }
    }

    def __init__(self, user):
        self.user = user
        self.plan = self.PLANS.get(user.goal, self.PLANS['cardio'])

    def generate_program(self):
        """Retourne une liste de dicts avec le plan hebdomadaire."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        return [
            {
                'day': days[i],
                'exercise': self.plan['sessions'][i],
                'duration': self.plan['durations'][i],
                'intensity': self.plan['intensities'][i]
            }
            for i in range(len(days))
        ]



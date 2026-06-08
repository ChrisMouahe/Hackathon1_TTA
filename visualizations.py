import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

# ============================================================
# GLOBAL STYLE
# ============================================================

plt.style.use('seaborn-v0_8-whitegrid')

# Colors for each workout type
COLORS = {
    'yoga':     '#7B68EE',
    'running':  '#FF7F50',
    'hiit':     '#DC143C',
    'strength': '#4682B4',
    'walking':  '#3CB371',
    'swimming': '#20B2AA'
}


# ============================================================
# GRAPH 1 : Calories over time (line chart)
# ============================================================

def graph_calories_over_time(df, output='data/calories_over_time.png'):
    """
    Line chart showing calories burned over time
    + 7-day moving average.

    Parameter:
        df     : full DataFrame
        output : path to save the image
    """
    # Check data is not empty
    if df.empty:
        print('No data available for graph 1.')
        return

    # Sort by date
    df_sorted = df.sort_values('date')

    fig, ax = plt.subplots(figsize=(10, 5))

    # Raw data line (light blue)
    ax.plot(
        df_sorted['date'],
        df_sorted['calories'],
        alpha=0.4,
        color='#4682B4',
        linewidth=1,
        label='Calories per session'
    )

    # 7-day moving average (red)
    df_indexed = df_sorted.set_index('date')
    moving_avg = df_indexed['calories'].rolling('7D').mean()

    ax.plot(
        moving_avg.index,
        moving_avg.values,
        color='#DC143C',
        linewidth=2.5,
        label='7-day moving average'
    )

    # Titles and labels
    ax.set_title('Calories Burned Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Calories')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    plt.xticks(rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Graph 1 saved : {output}')


# ============================================================
# GRAPH 2 : Workout frequency (horizontal bar chart)
# ============================================================

def graph_workout_frequency(df, output='data/workout_frequency.png'):
    """
    Horizontal bar chart showing number of sessions
    per workout type.

    Parameter:
        df     : full DataFrame
        output : path to save the image
    """
    # Check data is not empty
    if df.empty:
        print('No data available for graph 2.')
        return

    # Count sessions per workout type
    frequency = df['workout_type'].value_counts()

    # Get colors for each type
    colors = [COLORS.get(t, '#888888') for t in frequency.index]

    fig, ax = plt.subplots(figsize=(8, 5))

    # Horizontal bars
    bars = ax.barh(
        frequency.index,
        frequency.values,
        color=colors,
        edgecolor='white'
    )

    # Add value labels on each bar
    for bar, val in zip(bars, frequency.values):
        ax.text(
            bar.get_width() + 0.2,
            bar.get_y() + bar.get_height() / 2,
            str(val),
            va='center',
            fontweight='bold'
        )

    # Titles and labels
    ax.set_title('Workout Type Frequency', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of sessions')
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Graph 2 saved : {output}')


# ============================================================
# GRAPH 3 : Weekly progression (bar chart)
# ============================================================

def graph_weekly_progression(df, output='data/weekly_progression.png'):
    """
    Bar chart showing total calories per week
    + target line.

    Parameter:
        df     : full DataFrame
        output : path to save the image
    """
    # Check data is not empty
    if df.empty:
        print('No data available for graph 3.')
        return

    # Calculate total calories per week
    weekly = df.groupby('week')['calories'].sum().reset_index()

    # Weekly calorie target
    target = 2000

    # Green if target reached, orange if not
    bar_colors = [
        '#3CB371' if val >= target else '#FF7F50'
        for val in weekly['calories']
    ]

    fig, ax = plt.subplots(figsize=(9, 5))

    # Bars
    ax.bar(
        weekly['week'].astype(str),
        weekly['calories'],
        color=bar_colors,
        edgecolor='white',
        label='Total calories'
    )

    # Target line
    ax.axhline(
        y=target,
        color='#DC143C',
        linestyle='--',
        linewidth=1.5,
        label=f'Target : {target} cal/week'
    )

    # Titles and labels
    ax.set_title('Weekly Calorie Progression', fontsize=14, fontweight='bold')
    ax.set_xlabel('Week number')
    ax.set_ylabel('Total calories')
    ax.legend()

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Graph 3 saved : {output}')


# ============================================================
# GENERATE ALL GRAPHS AT ONCE
# ============================================================

def generate_all_graphs(df):
    """Generates all 3 graphs at once."""
    graph_calories_over_time(df)
    graph_workout_frequency(df)
    graph_weekly_progression(df)
    print('\nAll graphs saved in data/')


# ============================================================
# QUICK TEST — run this file directly to check
# ============================================================

if __name__ == '__main__':
    from datetime import date, timedelta

    # Simulate test data
    np.random.seed(42)
    nb_days = 30
    today = date.today()

    dates = [today - timedelta(days=nb_days - i) for i in range(nb_days)]
    workout_types = ['yoga', 'running', 'hiit', 'strength', 'walking']

    data = {
        'date': pd.to_datetime(dates),
        'calories': np.random.uniform(150, 500, nb_days).round(1),
        'workout_type': np.random.choice(workout_types, nb_days)
    }

    df_test = pd.DataFrame(data)
    df_test['week'] = df_test['date'].dt.isocalendar().week.astype(int)

    # Generate all graphs
    generate_all_graphs(df_test)
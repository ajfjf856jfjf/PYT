import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from datetime import datetime, timedelta

def create_calendar_events(data_handler, selected_month=None):
    """
    Create calendar events for the streamlit-calendar component.
    
    Args:
        data_handler: Instance of HabitDataHandler
        selected_month: Month to create events for (YYYY-MM format)
        
    Returns:
        list: Calendar events in the required format
    """
    if not selected_month:
        # Use current month if none provided
        now = datetime.now()
        selected_month = f"{now.year}-{now.month:02d}"
    
    # Parse the selected month
    year, month = map(int, selected_month.split('-'))
    
    # Create events for the calendar
    events = []
    
    # Loop through all habits
    for habit in data_handler.habits:
        habit_id = habit["id"]
        name = habit["name"]
        category = habit["category"]
        
        # Color mapping for categories
        color_map = {
            "Health": "#28a745",
            "Fitness": "#fd7e14",
            "Work": "#007bff",
            "Personal": "#6610f2",
            "Education": "#17a2b8",
            "Mindfulness": "#20c997",
            "Social": "#e83e8c",
            "Other": "#6c757d"
        }
        
        color = color_map.get(category, "#6c757d")
        
        # Get check-ins for this habit
        habit_id_str = str(habit_id)
        checkins = data_handler.checkins.get(habit_id_str, {})
        
        # Loop through all days in the month
        current_date = datetime(year, month, 1)
        while current_date.month == month:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Check if this habit should be done on this day (based on frequency)
            day_of_week = current_date.strftime("%A")
            
            if day_of_week in habit["frequency"]:
                # Create an event
                completed = checkins.get(date_str, False)
                
                event = {
                    "id": f"{habit_id}_{date_str}",
                    "title": name,
                    "start": date_str,
                    "end": date_str,
                    "backgroundColor": color if completed else "#f8f9fa",
                    "borderColor": color,
                    "textColor": "#ffffff" if completed else "#212529",
                    "extendedProps": {
                        "habit_id": habit_id,
                        "date": date_str,
                        "completed": completed
                    }
                }
                
                events.append(event)
            
            # Move to next day
            current_date += timedelta(days=1)
    
    return events

def create_habit_completion_chart(data_handler, habits, days=30):
    """
    Create a chart showing habit completion rates for the selected habits.
    
    Args:
        data_handler: Instance of HabitDataHandler
        habits: List of habits to include
        days: Number of days to analyze
        
    Returns:
        altair.Chart: Completion rate chart
    """
    # Get completion rate data
    chart_data = []
    
    for habit in habits:
        completion_rate = data_handler.get_completion_rate(habit["id"], days)
        chart_data.append({
            "habit": habit["name"],
            "completion_rate": completion_rate,
            "category": habit["category"]
        })
    
    # Create dataframe
    df = pd.DataFrame(chart_data)
    
    if df.empty:
        return None
    
    # Color mapping for categories
    color_scale = alt.Scale(
        domain=["Health", "Fitness", "Work", "Personal", "Education", "Mindfulness", "Social", "Other"],
        range=["#28a745", "#fd7e14", "#007bff", "#6610f2", "#17a2b8", "#20c997", "#e83e8c", "#6c757d"]
    )
    
    # Create chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('habit:N', title='Habit', sort='-y'),
        y=alt.Y('completion_rate:Q', title='Completion Rate (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('category:N', scale=color_scale, title='Category'),
        tooltip=['habit', 'completion_rate', 'category']
    ).properties(
        width=600,
        height=400,
        title=f'Habit Completion Rates (Last {days} Days)'
    )
    
    return chart

def create_streak_chart(data_handler, habits):
    """
    Create a chart showing current streaks for habits.
    
    Args:
        data_handler: Instance of HabitDataHandler
        habits: List of habits to include
        
    Returns:
        altair.Chart: Streak chart
    """
    # Get streak data
    streak_data = []
    
    for habit in habits:
        streak = data_handler.calculate_streak(habit["id"])
        streak_data.append({
            "habit": habit["name"],
            "streak": streak,
            "category": habit["category"]
        })
    
    # Create dataframe
    df = pd.DataFrame(streak_data)
    
    if df.empty:
        return None
    
    # Color mapping for categories
    color_scale = alt.Scale(
        domain=["Health", "Fitness", "Work", "Personal", "Education", "Mindfulness", "Social", "Other"],
        range=["#28a745", "#fd7e14", "#007bff", "#6610f2", "#17a2b8", "#20c997", "#e83e8c", "#6c757d"]
    )
    
    # Create chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('habit:N', title='Habit', sort='-y'),
        y=alt.Y('streak:Q', title='Current Streak (Days)'),
        color=alt.Color('category:N', scale=color_scale, title='Category'),
        tooltip=['habit', 'streak', 'category']
    ).properties(
        width=600,
        height=400,
        title='Current Habit Streaks'
    )
    
    return chart

def create_heatmap(data_handler, habit_id, year=None):
    """
    Create a year heatmap for a habit.
    
    Args:
        data_handler: Instance of HabitDataHandler
        habit_id: ID of the habit to display
        year: Year to display (default: current year)
        
    Returns:
        altair.Chart: Heatmap of habit completion
    """
    if not year:
        year = datetime.now().year
    
    # Get the habit
    habit = data_handler.get_habit_by_id(habit_id)
    if not habit:
        return None
    
    # Get check-ins for this habit
    habit_id_str = str(habit_id)
    checkins = data_handler.checkins.get(habit_id_str, {})
    
    # Create a dataframe with all days in the year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    # Generate all dates in the year
    dates = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        dates.append(date_str)
        current_date += timedelta(days=1)
    
    # Create dataframe
    df_data = []
    for date_str in dates:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Check if this habit should be done on this day
        day_of_week = date_obj.strftime("%A")
        should_do = day_of_week in habit["frequency"]
        
        # Status:
        # 0: Not scheduled
        # 1: Scheduled but not completed
        # 2: Completed
        status = 0
        if should_do:
            status = 2 if checkins.get(date_str, False) else 1
        
        df_data.append({
            "date": date_str,
            "day": date_obj.day,
            "month": date_obj.month,
            "status": status,
            "weekday": date_obj.weekday()
        })
    
    # Create dataframe
    df = pd.DataFrame(df_data)
    
    # Create heatmap
    # Define color scale
    color_scale = alt.Scale(
        domain=[0, 1, 2],
        range=["#f8f9fa", "#dc3545", "#28a745"]
    )
    
    # Create month names for x-axis
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # Create weekday names for y-axis
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Create chart
    chart = alt.Chart(df).mark_rect().encode(
        x=alt.X('month:O', title='Month', scale=alt.Scale(domain=list(range(1, 13))), axis=alt.Axis(labelExpr="['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][datum.value-1]")),
        y=alt.Y('weekday:O', title='Day', scale=alt.Scale(domain=list(range(7))), axis=alt.Axis(labelExpr="['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][datum.value]")),
        color=alt.Color('status:O', scale=color_scale, legend=None),
        tooltip=['date', alt.Tooltip('status:N', title='Status')]
    ).transform_calculate(
        status=alt.datum.status == 0 ? 'Not Scheduled' : 
               alt.datum.status == 1 ? 'Not Completed' : 'Completed'
    ).properties(
        width=800,
        height=300,
        title=f'Habit Tracking: {habit["name"]} ({year})'
    )
    
    # Create legend
    legend_data = pd.DataFrame([
        {"status": 0, "label": "Not Scheduled"},
        {"status": 1, "label": "Not Completed"},
        {"status": 2, "label": "Completed"}
    ])
    
    legend = alt.Chart(legend_data).mark_rect().encode(
        y=alt.Y('label:N', axis=alt.Axis(title=None)),
        color=alt.Color('status:O', scale=color_scale, legend=None)
    ).properties(
        width=150,
        height=100
    )
    
    # Combine chart and legend
    final_chart = alt.hconcat(chart, legend)
    
    return final_chart

def create_weekly_overview(data_handler):
    """
    Create a weekly overview chart showing habit completion.
    
    Args:
        data_handler: Instance of HabitDataHandler
        
    Returns:
        altair.Chart: Weekly overview chart
    """
    # Get weekly data
    weekly_data = data_handler.get_completion_data_for_period("week")
    
    # Prepare data for visualization
    chart_data = []
    
    for habit_id, data in weekly_data.items():
        habit = data["habit"]
        completions = data["completions"]
        
        for date_str, completed in completions.items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
            
            chart_data.append({
                "habit": habit["name"],
                "category": habit["category"],
                "day": day_name,
                "completed": "Completed" if completed else "Not Completed",
                "day_num": date_obj.weekday(),  # 0 = Monday, 6 = Sunday
                "habit_id": habit_id
            })
    
    # Create dataframe
    df = pd.DataFrame(chart_data)
    
    if df.empty:
        return None
    
    # Sort habits by name
    habits_sorted = sorted(set(df["habit"]))
    
    # Color mapping
    color_scale = alt.Scale(
        domain=["Not Completed", "Completed"],
        range=["#dc3545", "#28a745"]
    )
    
    # Days order
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Create chart
    chart = alt.Chart(df).mark_rect().encode(
        x=alt.X('day:N', title='Day', sort=days_order),
        y=alt.Y('habit:N', title='Habit', sort=habits_sorted),
        color=alt.Color('completed:N', scale=color_scale),
        tooltip=['habit', 'day', 'completed', 'category']
    ).properties(
        width=600,
        height=300,
        title='Weekly Habit Overview'
    )
    
    return chart

def create_monthly_overview(data_handler):
    """
    Create a monthly overview chart showing habit completion rates.
    
    Args:
        data_handler: Instance of HabitDataHandler
        
    Returns:
        altair.Chart: Monthly overview chart
    """
    # Get monthly data
    monthly_data = data_handler.get_completion_data_for_period("month")
    
    # Prepare data for category completion rates
    chart_data = []
    
    # Group habits by category
    category_habits = {}
    
    for habit_id, data in monthly_data.items():
        habit = data["habit"]
        category = habit["category"]
        completions = data["completions"]
        
        if category not in category_habits:
            category_habits[category] = []
        
        # Calculate completion rate for this habit
        total = len(completions)
        completed = sum(1 for completed in completions.values() if completed)
        
        if total > 0:
            completion_rate = (completed / total) * 100
        else:
            completion_rate = 0
        
        # Add to category data
        category_habits[category].append({
            "habit": habit["name"],
            "completion_rate": completion_rate
        })
    
    # Calculate average completion rate per category
    for category, habits in category_habits.items():
        if habits:
            avg_rate = sum(h["completion_rate"] for h in habits) / len(habits)
            
            chart_data.append({
                "category": category,
                "completion_rate": avg_rate
            })
    
    # Create dataframe
    df = pd.DataFrame(chart_data)
    
    if df.empty:
        return None
    
    # Color scale for categories
    color_scale = alt.Scale(
        domain=["Health", "Fitness", "Work", "Personal", "Education", "Mindfulness", "Social", "Other"],
        range=["#28a745", "#fd7e14", "#007bff", "#6610f2", "#17a2b8", "#20c997", "#e83e8c", "#6c757d"]
    )
    
    # Create chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('category:N', title='Category'),
        y=alt.Y('completion_rate:Q', title='Average Completion Rate (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('category:N', scale=color_scale),
        tooltip=['category', alt.Tooltip('completion_rate:Q', format='.1f', title='Avg. Completion Rate (%)')]
    ).properties(
        width=600,
        height=400,
        title='Monthly Habit Completion by Category'
    )
    
    return chart
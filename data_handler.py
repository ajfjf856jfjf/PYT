import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

class HabitDataHandler:
    """
    Class to handle data operations for the habit tracking app.
    Manages storing, retrieving, and manipulating habit data.
    """
    
    def __init__(self):
        """Initialize the data handler with default paths and data structures."""
        self.habits_file = "habits.json"
        self.checkins_file = "checkins.json"
        
        # Load or initialize habit and check-in data
        self.habits = self._load_habits()
        self.checkins = self._load_checkins()
    
    def _load_habits(self):
        """Load habits from file or return empty default if file doesn't exist."""
        if os.path.exists(self.habits_file):
            try:
                with open(self.habits_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _load_checkins(self):
        """Load check-ins from file or return empty default if file doesn't exist."""
        if os.path.exists(self.checkins_file):
            try:
                with open(self.checkins_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_habits(self):
        """Save habits to file."""
        with open(self.habits_file, "w") as f:
            json.dump(self.habits, f)
    
    def save_checkins(self):
        """Save check-ins to file."""
        with open(self.checkins_file, "w") as f:
            json.dump(self.checkins, f)
    
    def add_habit(self, name, category, frequency, description=""):
        """
        Add a new habit to the tracking system.
        
        Args:
            name (str): Name of the habit
            category (str): Category of the habit
            frequency (list): Days of the week for the habit
            description (str): Optional description
            
        Returns:
            int: ID of the newly created habit
        """
        habit_id = 1
        if self.habits:
            habit_id = max([h["id"] for h in self.habits]) + 1
            
        habit = {
            "id": habit_id,
            "name": name,
            "category": category,
            "frequency": frequency,
            "description": description,
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.habits.append(habit)
        self.save_habits()
        return habit_id
    
    def update_habit(self, habit_id, name, category, frequency, description=""):
        """Update an existing habit."""
        for i, habit in enumerate(self.habits):
            if habit["id"] == habit_id:
                self.habits[i].update({
                    "name": name,
                    "category": category,
                    "frequency": frequency,
                    "description": description
                })
                self.save_habits()
                return True
        return False
    
    def delete_habit(self, habit_id):
        """Delete a habit and its check-ins."""
        self.habits = [h for h in self.habits if h["id"] != habit_id]
        
        # Also remove any check-ins for this habit
        habit_key = str(habit_id)
        if habit_key in self.checkins:
            del self.checkins[habit_key]
        
        self.save_habits()
        self.save_checkins()
        return True
    
    def check_in_habit(self, habit_id, date, completed=True):
        """Record a habit check-in for a specific date."""
        habit_id_str = str(habit_id)
        
        if habit_id_str not in self.checkins:
            self.checkins[habit_id_str] = {}
            
        self.checkins[habit_id_str][date] = completed
        self.save_checkins()
        return True
    
    def get_habit_by_id(self, habit_id):
        """Get a habit by its ID."""
        for habit in self.habits:
            if habit["id"] == habit_id:
                return habit
        return None
    
    def get_habit_categories(self):
        """Get all unique habit categories."""
        return list(set(habit["category"] for habit in self.habits))
    
    def get_checkins_for_habit(self, habit_id, start_date=None, end_date=None):
        """
        Get check-ins for a specific habit within a date range.
        
        Args:
            habit_id: The habit ID
            start_date: Start date string in format 'YYYY-MM-DD'
            end_date: End date string in format 'YYYY-MM-DD'
            
        Returns:
            dict: Date-to-completion mapping
        """
        habit_id_str = str(habit_id)
        
        if habit_id_str not in self.checkins:
            return {}
            
        checkins = self.checkins[habit_id_str]
        
        if not start_date and not end_date:
            return checkins
            
        filtered_checkins = {}
        
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        
        for date_str, completed in checkins.items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            if start_date_obj and date_obj < start_date_obj:
                continue
                
            if end_date_obj and date_obj > end_date_obj:
                continue
                
            filtered_checkins[date_str] = completed
            
        return filtered_checkins
    
    def get_all_habits_checkins(self, start_date=None, end_date=None):
        """Get check-ins for all habits within a date range."""
        result = {}
        
        for habit in self.habits:
            habit_id = habit["id"]
            result[habit_id] = self.get_checkins_for_habit(
                habit_id, start_date, end_date
            )
            
        return result
    
    def calculate_streak(self, habit_id):
        """Calculate the current streak for a habit."""
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return 0
            
        habit_id_str = str(habit_id)
        if habit_id_str not in self.checkins:
            return 0
            
        checkins = self.checkins[habit_id_str]
        if not checkins:
            return 0
            
        # Get dates sorted in descending order
        dates = sorted([datetime.strptime(date, "%Y-%m-%d") 
                        for date in checkins.keys()], reverse=True)
        
        # Check if the most recent check-in is today or yesterday
        today = datetime.now().date()
        most_recent = dates[0].date()
        
        if (today - most_recent).days > 1:
            return 0  # Streak broken if most recent check-in is more than 1 day ago
            
        # Count consecutive days
        streak = 1
        for i in range(len(dates)-1):
            current_date = dates[i].date()
            prev_date = dates[i+1].date()
            
            # If dates are consecutive, continue the streak
            if (current_date - prev_date).days == 1:
                streak += 1
            else:
                break
                
        return streak
    
    def get_completion_rate(self, habit_id, days=30):
        """Calculate habit completion rate for the last N days."""
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return 0
            
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get the dates that the habit should be done based on frequency
        frequency = habit["frequency"]
        expected_dates = []
        
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.strftime("%A")
            if day_of_week in frequency:
                expected_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
            
        if not expected_dates:
            return 0
            
        # Check how many of the expected dates were completed
        habit_id_str = str(habit_id)
        if habit_id_str not in self.checkins:
            return 0
            
        checkins = self.checkins[habit_id_str]
        completed_count = sum(1 for date in expected_dates if date in checkins and checkins[date])
        
        # Calculate completion rate
        completion_rate = (completed_count / len(expected_dates)) * 100
        return completion_rate
    
    def get_completion_data_for_period(self, period_type="week"):
        """
        Get completion data for all habits in the current period.
        
        Args:
            period_type: 'week' or 'month'
            
        Returns:
            dict: Habit completion data for the period
        """
        today = datetime.now().date()
        
        if period_type == "week":
            # Start date is the beginning of current week (Monday)
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        else:  # month
            # Start date is the beginning of current month
            start_date = today.replace(day=1)
            # End date is the last day of current month
            if today.month == 12:
                end_date = today.replace(day=31)
            else:
                end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        result = {}
        for habit in self.habits:
            habit_id = habit["id"]
            frequency = habit["frequency"]
            
            # Get dates in the period when habit should be done
            expected_dates = []
            current_date = start_date
            while current_date <= end_date:
                day_of_week = current_date.strftime("%A")
                if day_of_week in frequency:
                    expected_dates.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
            
            # Get actual completion data
            habit_id_str = str(habit_id)
            completions = {}
            
            if habit_id_str in self.checkins:
                for date_str in expected_dates:
                    if date_str in self.checkins[habit_id_str]:
                        completions[date_str] = self.checkins[habit_id_str][date_str]
                    else:
                        completions[date_str] = False
            else:
                for date_str in expected_dates:
                    completions[date_str] = False
            
            result[habit_id] = {
                "habit": habit,
                "expected_dates": expected_dates,
                "completions": completions
            }
        
        return result
    
    def export_data(self):
        """Export all data for backup or transfer."""
        return {
            "habits": self.habits,
            "checkins": self.checkins
        }
    
    def import_data(self, data):
        """Import data from backup."""
        if "habits" in data and "checkins" in data:
            self.habits = data["habits"]
            self.checkins = data["checkins"]
            self.save_habits()
            self.save_checkins()
            return True
        return False

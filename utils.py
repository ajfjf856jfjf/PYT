import streamlit as st
import pandas as pd
import numpy as np
import json
import base64
from datetime import datetime, timedelta
from io import BytesIO

def get_category_emoji(category):
    """Get an emoji for a given habit category."""
    emoji_map = {
        "Health": "🍎",
        "Fitness": "💪",
        "Work": "💼",
        "Personal": "🏠",
        "Education": "📚",
        "Mindfulness": "🧘",
        "Social": "👥",
        "Other": "🔄"
    }
    return emoji_map.get(category, "📌")

def get_category_color(category):
    """Get a color for a given habit category."""
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
    return color_map.get(category, "#6c757d")

def format_date(date_str):
    """Format a date string to a more readable format."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%b %d, %Y")
    except:
        return date_str

def get_day_of_week(date_str):
    """Get the day of the week for a date string."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%A")
    except:
        return ""

def get_week_dates():
    """Get dates for the current week (Monday-Sunday)."""
    today = datetime.now().date()
    
    # Start date is Monday of current week
    monday = today - timedelta(days=today.weekday())
    
    # Generate the dates for the week
    dates = []
    for i in range(7):
        date = monday + timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    
    return dates

def get_week_labels():
    """Get labels for days of the week."""
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def days_between(start_date, end_date):
    """Calculate the number of days between two date strings."""
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    return (end - start).days

def get_downloadable_link(data, filename, text):
    """
    Generate a link to download data as a file.
    
    Args:
        data: Data to download
        filename: Name of the file
        text: Text for the download link
        
    Returns:
        str: HTML for download link
    """
    json_str = json.dumps(data)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'data:file/json;base64,{b64}'
    return f'<a href="{href}" download="{filename}">{text}</a>'

def create_export_data(data_handler):
    """Create export data from the data handler."""
    export_data = data_handler.export_data()
    return export_data

def parse_import_data(uploaded_file):
    """Parse imported data from an uploaded file."""
    try:
        content = uploaded_file.read().decode('utf-8')
        data = json.loads(content)
        return data
    except Exception as e:
        st.error(f"Error parsing import data: {str(e)}")
        return None

def calculate_completion_stats(data_handler):
    """Calculate overall completion statistics."""
    stats = {
        "total_habits": len(data_handler.habits),
        "total_checkins": 0,
        "completion_rate": 0,
        "categories": {}
    }
    
    # Calculate total check-ins
    for habit_id, checkins in data_handler.checkins.items():
        completed_checkins = sum(1 for completed in checkins.values() if completed)
        stats["total_checkins"] += completed_checkins
    
    # Calculate completion rate
    if data_handler.habits:
        total_rate = 0
        for habit in data_handler.habits:
            rate = data_handler.get_completion_rate(habit["id"])
            total_rate += rate
        
        stats["completion_rate"] = total_rate / len(data_handler.habits)
    
    # Calculate categories
    categories = {}
    for habit in data_handler.habits:
        category = habit["category"]
        if category not in categories:
            categories[category] = {"count": 0, "completion_rate": 0}
        
        categories[category]["count"] += 1
        categories[category]["completion_rate"] += data_handler.get_completion_rate(habit["id"])
    
    # Calculate average completion rate per category
    for category, data in categories.items():
        if data["count"] > 0:
            data["completion_rate"] /= data["count"]
    
    stats["categories"] = categories
    
    return stats

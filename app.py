import streamlit as st
import pandas as pd
import numpy as np
import json
import io
from datetime import datetime, timedelta
import altair as alt

# Import custom modules
from data_handler import HabitDataHandler
from visualization import (
    create_calendar_events, create_habit_completion_chart,
    create_streak_chart, create_heatmap,
    create_weekly_overview, create_monthly_overview
)
from utils import (
    get_category_emoji, get_category_color, format_date,
    get_day_of_week, get_week_dates, get_week_labels,
    days_between, get_downloadable_link, create_export_data,
    parse_import_data, calculate_completion_stats
)

# Page configuration
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data handler
@st.cache_resource
def get_data_handler():
    return HabitDataHandler()

data_handler = get_data_handler()

# Initialize session state variables
if "current_view" not in st.session_state:
    st.session_state.current_view = "dashboard"

if "selected_habit" not in st.session_state:
    st.session_state.selected_habit = None

if "edit_habit" not in st.session_state:
    st.session_state.edit_habit = None

# Define navigation functions
def set_view(view):
    st.session_state.current_view = view
    st.session_state.selected_habit = None
    st.session_state.edit_habit = None

# Sidebar - Navigation
st.sidebar.title("Habit Tracker")
st.sidebar.markdown("---")

# Navigation
view = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Habits", "Calendar", "Statistics", "Settings"],
    key="nav"
)

if view == "Dashboard":
    st.session_state.current_view = "dashboard"
elif view == "Habits":
    st.session_state.current_view = "habits"
elif view == "Calendar":
    st.session_state.current_view = "calendar"
elif view == "Statistics":
    st.session_state.current_view = "statistics"
elif view == "Settings":
    st.session_state.current_view = "settings"

# Sidebar - Habits List
st.sidebar.markdown("---")
st.sidebar.subheader("Your Habits")

# Display the list of habits in the sidebar
habits = data_handler.habits
habits_by_category = {}

for habit in habits:
    category = habit["category"]
    if category not in habits_by_category:
        habits_by_category[category] = []
    habits_by_category[category].append(habit)

for category, category_habits in habits_by_category.items():
    with st.sidebar.expander(f"{get_category_emoji(category)} {category} ({len(category_habits)})"):
        for habit in category_habits:
            if st.button(habit["name"], key=f"sb_habit_{habit['id']}"):
                st.session_state.selected_habit = habit["id"]
                st.session_state.current_view = "habit_detail"

# Add "Create New Habit" button
st.sidebar.markdown("---")
if st.sidebar.button("Create New Habit", key="create_new_habit"):
    st.session_state.current_view = "create_habit"

# Main Content
if st.session_state.current_view == "dashboard":
    st.title("Dashboard")
    
    # Display stats
    stats = calculate_completion_stats(data_handler)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Habits", stats["total_habits"])
    
    with col2:
        st.metric("Total Check-ins", stats["total_checkins"])
    
    with col3:
        st.metric("Overall Completion Rate", f"{stats['completion_rate']:.1f}%")
    
    st.markdown("---")
    
    # Weekly overview
    st.subheader("Weekly Overview")
    
    weekly_chart = create_weekly_overview(data_handler)
    if weekly_chart:
        st.altair_chart(weekly_chart, use_container_width=True)
    else:
        st.info("No data available for weekly overview. Start by adding habits and checking them off!")
    
    st.markdown("---")
    
    # Habit streaks
    st.subheader("Current Streaks")
    
    streak_chart = create_streak_chart(data_handler, habits)
    if streak_chart:
        st.altair_chart(streak_chart, use_container_width=True)
    else:
        st.info("No streak data available. Start building your streaks!")
    
    # Today's habits
    st.markdown("---")
    st.subheader("Today's Habits")
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_day = datetime.now().strftime("%A")
    
    today_habits = [habit for habit in habits if today_day in habit["frequency"]]
    
    if today_habits:
        for habit in today_habits:
            habit_id = habit["id"]
            completed = False
            
            habit_id_str = str(habit_id)
            if habit_id_str in data_handler.checkins and today in data_handler.checkins[habit_id_str]:
                completed = data_handler.checkins[habit_id_str][today]
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{habit['name']}** ({get_category_emoji(habit['category'])} {habit['category']})")
                st.write(f"*{habit['description']}*" if habit['description'] else "")
            
            with col2:
                if completed:
                    if st.button("✓ Completed", key=f"uncheck_{habit_id}"):
                        data_handler.check_in_habit(habit_id, today, False)
                        st.rerun()
                else:
                    if st.button("Mark Complete", key=f"check_{habit_id}"):
                        data_handler.check_in_habit(habit_id, today, True)
                        st.rerun()
    else:
        st.info(f"No habits scheduled for today ({today_day}).")

elif st.session_state.current_view == "habits":
    st.title("Habits")
    
    if st.button("+ Create New Habit"):
        st.session_state.current_view = "create_habit"
        st.rerun()
    
    st.markdown("---")
    
    # Display habits grouped by category
    for category, category_habits in habits_by_category.items():
        with st.expander(f"{get_category_emoji(category)} {category} ({len(category_habits)})", expanded=True):
            for habit in category_habits:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{habit['name']}**")
                    if habit['description']:
                        st.write(f"*{habit['description']}*")
                    st.write(f"Frequency: {', '.join(habit['frequency'])}")
                
                with col2:
                    if st.button("Details", key=f"details_{habit['id']}"):
                        st.session_state.selected_habit = habit["id"]
                        st.session_state.current_view = "habit_detail"
                        st.rerun()
                
                with col3:
                    if st.button("Edit", key=f"edit_{habit['id']}"):
                        st.session_state.edit_habit = habit["id"]
                        st.session_state.current_view = "edit_habit"
                        st.rerun()
                
                st.markdown("---")

elif st.session_state.current_view == "create_habit":
    st.title("Create New Habit")
    
    with st.form(key="create_habit_form"):
        name = st.text_input("Habit Name*")
        
        categories = ["Health", "Fitness", "Work", "Personal", 
                      "Education", "Mindfulness", "Social", "Other"]
        category = st.selectbox("Category", categories)
        
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                         "Friday", "Saturday", "Sunday"]
        frequency = st.multiselect("Frequency*", days_of_week)
        
        description = st.text_area("Description (Optional)")
        
        submitted = st.form_submit_button("Create Habit")
        
        if submitted:
            if not name:
                st.error("Please enter a habit name.")
            elif not frequency:
                st.error("Please select at least one day for frequency.")
            else:
                data_handler.add_habit(name, category, frequency, description)
                st.success(f"Habit '{name}' created successfully!")
                st.session_state.current_view = "habits"
                st.rerun()
    
    if st.button("Cancel"):
        st.session_state.current_view = "habits"
        st.rerun()

elif st.session_state.current_view == "edit_habit":
    habit_id = st.session_state.edit_habit
    habit = data_handler.get_habit_by_id(habit_id)
    
    if not habit:
        st.error("Habit not found.")
        st.session_state.current_view = "habits"
        st.rerun()
    
    st.title(f"Edit Habit: {habit['name']}")
    
    with st.form(key="edit_habit_form"):
        name = st.text_input("Habit Name*", value=habit["name"])
        
        categories = ["Health", "Fitness", "Work", "Personal", 
                      "Education", "Mindfulness", "Social", "Other"]
        category = st.selectbox("Category", categories, index=categories.index(habit["category"]) if habit["category"] in categories else 0)
        
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                         "Friday", "Saturday", "Sunday"]
        frequency = st.multiselect("Frequency*", days_of_week, default=habit["frequency"])
        
        description = st.text_area("Description (Optional)", value=habit["description"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("Update Habit")
        
        with col2:
            delete_button = st.form_submit_button("Delete Habit", type="secondary")
        
        if submitted:
            if not name:
                st.error("Please enter a habit name.")
            elif not frequency:
                st.error("Please select at least one day for frequency.")
            else:
                data_handler.update_habit(habit_id, name, category, frequency, description)
                st.success(f"Habit '{name}' updated successfully!")
                st.session_state.current_view = "habits"
                st.rerun()
        
        if delete_button:
            data_handler.delete_habit(habit_id)
            st.success(f"Habit '{habit['name']}' deleted successfully!")
            st.session_state.current_view = "habits"
            st.rerun()
    
    if st.button("Cancel"):
        st.session_state.current_view = "habits"
        st.rerun()

elif st.session_state.current_view == "habit_detail":
    habit_id = st.session_state.selected_habit
    habit = data_handler.get_habit_by_id(habit_id)
    
    if not habit:
        st.error("Habit not found.")
        st.session_state.current_view = "habits"
        st.rerun()
    
    st.title(f"{habit['name']}")
    st.subheader(f"{get_category_emoji(habit['category'])} {habit['category']}")
    
    if habit['description']:
        st.write(f"*{habit['description']}*")
    
    st.write(f"**Frequency:** {', '.join(habit['frequency'])}")
    st.write(f"**Created:** {format_date(habit['created_at'])}")
    
    # Display streak
    streak = data_handler.calculate_streak(habit_id)
    st.write(f"**Current Streak:** {streak} days")
    
    # Display completion rate
    completion_rate = data_handler.get_completion_rate(habit_id)
    st.write(f"**Completion Rate (30 days):** {completion_rate:.1f}%")
    
    st.markdown("---")
    
    # Display check-in calendar for current month
    st.subheader("Check-in History")
    
    # Get year and month for calendar visualization
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Year selector for heatmap
    selected_year = st.selectbox("Select Year", 
                                list(range(current_year-3, current_year+1)), 
                                index=3)  # Default to current year
    
    # Create and display yearly heatmap
    heatmap = create_heatmap(data_handler, habit_id, selected_year)
    if heatmap:
        st.altair_chart(heatmap, use_container_width=True)
    else:
        st.info("No data available for visualization.")
    
    st.markdown("---")
    
    # Edit/Delete buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Edit Habit"):
            st.session_state.edit_habit = habit_id
            st.session_state.current_view = "edit_habit"
            st.rerun()
    
    with col2:
        if st.button("Delete Habit", type="secondary"):
            data_handler.delete_habit(habit_id)
            st.success(f"Habit '{habit['name']}' deleted successfully!")
            st.session_state.current_view = "habits"
            st.rerun()
    
    if st.button("Back to Habits"):
        st.session_state.current_view = "habits"
        st.rerun()

elif st.session_state.current_view == "calendar":
    st.title("Calendar View")
    
    # Select month for calendar view
    today = datetime.now()
    current_month = f"{today.year}-{today.month:02d}"
    
    # Create a list of months for selection (6 months back, current month, 6 months forward)
    months = []
    for i in range(-6, 7):
        month_date = today.replace(day=1) + timedelta(days=i*30)
        month_str = f"{month_date.year}-{month_date.month:02d}"
        month_label = month_date.strftime("%B %Y")
        months.append((month_str, month_label))
    
    # Default to current month
    selected_month_index = 6  # Middle of the list (current month)
    selected_month = st.selectbox(
        "Select Month",
        [month[1] for month in months],
        index=selected_month_index
    )
    
    # Get the month string based on selection
    selected_month_str = months[[month[1] for month in months].index(selected_month)][0]
    
    st.markdown("---")
    
    # Current month overview
    st.subheader("Current Month Progress")
    
    # Check if streamlit-calendar is available
    try:
        from streamlit_calendar import calendar
        
        # Create calendar events for habits
        events = create_calendar_events(data_handler, selected_month_str)
        
        # Calendar view options
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth"
            },
            "initialView": "dayGridMonth",
            "validRange": {
                "start": f"{selected_month_str}-01",
                "end": f"{int(selected_month_str.split('-')[0]) + (int(selected_month_str.split('-')[1]) + 1) // 13}-{(int(selected_month_str.split('-')[1]) % 12) + 1:02d}-01"
            },
            "initialDate": f"{selected_month_str}-01",
            "navLinks": False,
            "editable": False,
            "dayMaxEvents": True,
            "selectable": True,
            "eventDisplay": "block",
            "displayEventTime": False,
        }
        
        calendar_events = calendar(
            events=events,
            options=calendar_options,
            key=f"calendar_{selected_month_str}"
        )
        
        if calendar_events and calendar_events.get("eventClick"):
            # User clicked an event, handle check-in toggling
            event_data = calendar_events["eventClick"]["extendedProps"]
            habit_id = int(event_data["habit_id"])
            date = event_data["date"]
            completed = event_data["completed"]
            
            # Toggle completion status
            data_handler.check_in_habit(habit_id, date, not completed)
            st.rerun()
    
    except ImportError:
        st.error("The streamlit-calendar component is not available. Using alternative calendar view.")
        
        # Alternative: Show weekly grid for habits
        year, month = map(int, selected_month_str.split('-'))
        
        # Get all days in the selected month
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Create a grid of days
        days = []
        current_day = first_day
        while current_day <= last_day:
            days.append(current_day)
            current_day += timedelta(days=1)
        
        # Create a grid of weeks
        weeks = []
        week = []
        
        # Add empty days for first week
        first_weekday = first_day.weekday()  # 0 = Monday, 6 = Sunday
        for _ in range(first_weekday):
            week.append(None)
        
        # Add all days in month
        for day in days:
            week.append(day)
            if len(week) == 7:
                weeks.append(week)
                week = []
        
        # Add empty days for last week
        if week:
            while len(week) < 7:
                week.append(None)
            weeks.append(week)
        
        # Display calendar header
        st.write(f"### {first_day.strftime('%B %Y')}")
        
        # Create calendar grid
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        # Display day names
        cols = st.columns(7)
        for i, col in enumerate(cols):
            col.write(f"**{day_names[i]}**")
        
        # Display calendar
        for week in weeks:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day:
                    day_str = day.strftime("%Y-%m-%d")
                    day_num = day.day
                    
                    # Get habits scheduled for this day
                    day_of_week = day.strftime("%A")
                    days_habits = [habit for habit in habits if day_of_week in habit["frequency"]]
                    
                    with cols[i]:
                        st.write(f"**{day_num}**")
                        
                        for habit in days_habits:
                            habit_id = habit["id"]
                            completed = False
                            
                            habit_id_str = str(habit_id)
                            if habit_id_str in data_handler.checkins and day_str in data_handler.checkins[habit_id_str]:
                                completed = data_handler.checkins[habit_id_str][day_str]
                            
                            # Display habit with completion status
                            if completed:
                                st.write(f"- ✓ {habit['name']}")
                            else:
                                if st.button(f"□ {habit['name']}", key=f"cal_{habit_id}_{day_str}"):
                                    data_handler.check_in_habit(habit_id, day_str, True)
                                    st.rerun()
                else:
                    cols[i].write("")  # Empty cell
    
    # Weekly view
    st.markdown("---")
    st.subheader("Weekly Habit View")
    
    weekly_chart = create_weekly_overview(data_handler)
    if weekly_chart:
        st.altair_chart(weekly_chart, use_container_width=True)
    else:
        st.info("No data available for weekly view.")
        
elif st.session_state.current_view == "statistics":
    st.title("Statistics & Insights")
    
    # Overall completion rates
    st.subheader("Overall Completion Rates")
    
    # Time period selector
    period = st.radio(
        "Time Period",
        ["Last 30 Days", "Last 60 Days", "Last 90 Days"],
        horizontal=True
    )
    
    days = 30
    if period == "Last 60 Days":
        days = 60
    elif period == "Last 90 Days":
        days = 90
    
    # Create completion rate chart
    completion_chart = create_habit_completion_chart(data_handler, habits, days)
    if completion_chart:
        st.altair_chart(completion_chart, use_container_width=True)
    else:
        st.info("No data available for visualization.")
    
    # Streaks
    st.markdown("---")
    st.subheader("Current Streaks")
    
    streak_chart = create_streak_chart(data_handler, habits)
    if streak_chart:
        st.altair_chart(streak_chart, use_container_width=True)
    else:
        st.info("No streak data available.")
    
    # Monthly overview
    st.markdown("---")
    st.subheader("Monthly Category Performance")
    
    monthly_chart = create_monthly_overview(data_handler)
    if monthly_chart:
        st.altair_chart(monthly_chart, use_container_width=True)
    else:
        st.info("No data available for monthly overview.")
    
    # Habit insights
    st.markdown("---")
    st.subheader("Habit Insights")
    
    # Calculate some insights
    insights = []
    
    for habit in habits:
        habit_id = habit["id"]
        
        # Get completion rate
        completion_rate = data_handler.get_completion_rate(habit_id)
        
        # Get streak
        streak = data_handler.calculate_streak(habit_id)
        
        insights.append({
            "habit": habit["name"],
            "category": habit["category"],
            "completion_rate": completion_rate,
            "streak": streak
        })
    
    # Sort insights by completion rate (descending)
    insights.sort(key=lambda x: x["completion_rate"], reverse=True)
    
    # Display best and worst performing habits
    if insights:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Best Performing Habits**")
            best_habits = insights[:min(3, len(insights))]
            for habit in best_habits:
                st.write(f"- {habit['habit']}: {habit['completion_rate']:.1f}% completion rate")
        
        with col2:
            st.write("**Needs Improvement**")
            worst_habits = insights[-min(3, len(insights)):]
            worst_habits.reverse()  # Show worst first
            for habit in worst_habits:
                st.write(f"- {habit['habit']}: {habit['completion_rate']:.1f}% completion rate")
        
        # Longest streaks
        st.write("**Longest Streaks**")
        streak_insights = sorted(insights, key=lambda x: x["streak"], reverse=True)
        for habit in streak_insights[:min(3, len(streak_insights))]:
            if habit["streak"] > 0:
                st.write(f"- {habit['habit']}: {habit['streak']} day streak")
    else:
        st.info("No data available for insights. Start by adding habits and checking them off!")

elif st.session_state.current_view == "settings":
    st.title("Settings")
    
    # Export/Import data
    st.subheader("Export/Import Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Export Data**")
        if st.button("Export All Data"):
            export_data = create_export_data(data_handler)
            download_link = get_downloadable_link(
                export_data,
                "habit_tracker_export.json",
                "Download JSON"
            )
            st.markdown(download_link, unsafe_allow_html=True)
    
    with col2:
        st.write("**Import Data**")
        uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
        
        if uploaded_file and st.button("Import Data"):
            import_data = parse_import_data(uploaded_file)
            if import_data:
                if data_handler.import_data(import_data):
                    st.success("Data imported successfully!")
                    st.rerun()
                else:
                    st.error("Failed to import data. Invalid format.")
    
    # Clear all data
    st.markdown("---")
    st.subheader("Danger Zone")
    
    with st.expander("Clear All Data"):
        st.warning("This will delete all your habits and check-in data. This action cannot be undone!")
        
        if st.button("Clear All Data", type="primary"):
            # Reset data
            data_handler.habits = []
            data_handler.checkins = {}
            data_handler.save_habits()
            data_handler.save_checkins()
            
            st.success("All data has been cleared!")
            st.session_state.current_view = "dashboard"
            st.rerun()

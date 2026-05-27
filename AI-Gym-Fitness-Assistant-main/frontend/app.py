"""
frontend/app.py – Streamlit UI for the AI Gym & Fitness Assistant.

Run with:
    streamlit run frontend/app.py
"""
import sys
import os

# Ensure the repo root is on sys.path so local modules resolve correctly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database.db import init_db, SessionLocal
from database import models as db_models
from models.diet_planner import DietPlanner
from models.habit_tracker import HabitTracker
from models.gym_buddy import GymBuddy, simple_sentiment
from models.performance_analyzer import PerformanceAnalyzer
from models.gym_recommender import GymRecommender
from models.iot_simulator import IoTSimulator
from utils.bmi_calculator import calculate_bmi, bmi_category, ideal_weight_range
from utils.calorie_tracker import calculate_bmr, calculate_tdee, goal_calories, macro_split
from utils.helpers import get_motivational_message, format_duration

# ---------------------------------------------------------------------------
# App config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Gym & Fitness Assistant",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialise DB on first run
init_db()

# ---------------------------------------------------------------------------
# CSS theming
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .main {background-color: #0e1117;}
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab"] {font-size: 16px; font-weight: 600;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------

def _init_state():
    defaults = {
        "user_id": None,
        "chat_history": [],
        "buddy": GymBuddy(),
        "iot_sim": IoTSimulator(),
        "iot_readings": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ---------------------------------------------------------------------------
# Sidebar – user profile
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/dumbbell.png", width=80)
    st.title("💪 AI Gym Assistant")
    st.markdown("---")

    st.subheader("👤 Your Profile")
    name = st.text_input("Name", value="Alex")
    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age", min_value=10, max_value=100, value=25)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=75.0, step=0.5)
    with col_b:
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=175.0, step=0.5)
        gender = st.selectbox("Gender", ["Male", "Female"])

    goal = st.selectbox("Fitness Goal", ["lose", "gain", "maintain"],
                        format_func=lambda x: {"lose": "🏃 Lose Weight",
                                               "gain": "💪 Build Muscle",
                                               "maintain": "⚖️ Maintain"}[x])
    activity = st.selectbox("Activity Level",
                             ["sedentary", "light", "moderate", "active", "very_active"],
                             index=2,
                             format_func=lambda x: x.replace("_", " ").title())

    if st.button("💾 Save Profile", use_container_width=True):
        db = SessionLocal()
        try:
            user = db_models.User(
                name=name, age=age, weight_kg=weight,
                height_cm=height, goal=goal, activity_level=activity,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            st.session_state["user_id"] = user.id
            st.session_state["iot_sim"] = IoTSimulator(age=age)
            st.success(f"Profile saved (ID: {user.id})")
        finally:
            db.close()

    st.markdown("---")
    st.caption(f"💡 {get_motivational_message()}")

# ---------------------------------------------------------------------------
# Main content – tabbed layout
# ---------------------------------------------------------------------------

tabs = st.tabs([
    "🏠 Dashboard",
    "🤸 Workout Trainer",
    "🥗 Diet Planner",
    "📊 Performance",
    "🤖 Gym Buddy",
    "📡 IoT Monitor",
    "🧠 Habit Tracker",
    "🏋️ Recommender",
])

is_male = (gender == "Male")
bmi = calculate_bmi(weight, height)
bmi_cat = bmi_category(bmi)
bmr = calculate_bmr(weight, height, age, is_male)
tdee = calculate_tdee(bmr, activity)
target_cals = goal_calories(tdee, goal)
macros = macro_split(target_cals, goal)

# ===========================================================================
# TAB 1 – Dashboard
# ===========================================================================

with tabs[0]:
    st.header(f"👋 Welcome back, {name}!")
    st.subheader("Your Fitness Overview")

    # Key metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("BMI", bmi, bmi_cat)
    m2.metric("Daily Calories", f"{target_cals} kcal")
    m3.metric("Protein Target", f"{macros['protein_g']} g")
    m4.metric("Carbs Target", f"{macros['carbs_g']} g")
    m5.metric("Fat Target", f"{macros['fat_g']} g")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 BMI Gauge")
        fig_bmi = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=bmi,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "BMI"},
            gauge={
                "axis": {"range": [10, 45]},
                "bar": {"color": "royalblue"},
                "steps": [
                    {"range": [10, 18.5], "color": "lightblue"},
                    {"range": [18.5, 25], "color": "lightgreen"},
                    {"range": [25, 30], "color": "orange"},
                    {"range": [30, 45], "color": "red"},
                ],
                "threshold": {"line": {"color": "white", "width": 4},
                               "thickness": 0.75, "value": bmi},
            },
        ))
        fig_bmi.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)",
                              font_color="white")
        st.plotly_chart(fig_bmi, use_container_width=True)

    with col2:
        st.subheader("🥧 Macro Split")
        fig_macro = px.pie(
            values=[macros["protein_g"] * 4, macros["carbs_g"] * 4, macros["fat_g"] * 9],
            names=["Protein", "Carbs", "Fat"],
            color_discrete_sequence=["#00b4d8", "#90e0ef", "#caf0f8"],
            hole=0.4,
        )
        fig_macro.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)",
                                 font_color="white", showlegend=True)
        st.plotly_chart(fig_macro, use_container_width=True)

    # Simulated weekly activity chart
    st.subheader("📅 Simulated Weekly Activity")
    dates = [(datetime.utcnow() - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    cals_chart = [random.randint(200, 600) for _ in range(7)]
    df_activity = pd.DataFrame({"Day": dates, "Calories Burned": cals_chart})
    fig_act = px.bar(df_activity, x="Day", y="Calories Burned",
                     color="Calories Burned", color_continuous_scale="Blues")
    fig_act.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=250)
    st.plotly_chart(fig_act, use_container_width=True)


# ===========================================================================
# TAB 2 – Workout Trainer (Pose Detection Simulation)
# ===========================================================================

with tabs[1]:
    st.header("🤸 AI Workout Trainer")
    st.info(
        "**Live camera mode** requires a local environment with a webcam. "
        "Use the simulation below to explore rep counting and posture feedback."
    )

    exercise = st.selectbox("Select Exercise", ["Bicep Curl", "Squat", "Push-up"])
    col_w1, col_w2 = st.columns([2, 1])

    with col_w1:
        st.subheader("Simulated Rep Counter")
        if "sim_reps" not in st.session_state:
            st.session_state["sim_reps"] = 0
            st.session_state["sim_angle"] = 160
            st.session_state["sim_stage"] = "down"

        st.metric("Reps", st.session_state["sim_reps"])
        st.metric("Current Angle", f"{st.session_state['sim_angle']}°")
        st.metric("Stage", st.session_state["sim_stage"])

        if st.button("▶️ Simulate Rep", use_container_width=True):
            # Toggle angle to simulate a rep
            if st.session_state["sim_stage"] == "down":
                st.session_state["sim_angle"] = 35
                st.session_state["sim_stage"] = "up"
                st.session_state["sim_reps"] += 1
                st.success("✅ Rep counted! Good form.")
            else:
                st.session_state["sim_angle"] = 160
                st.session_state["sim_stage"] = "down"
                st.info("↩️ Return to starting position.")

        if st.button("🔄 Reset Counter", use_container_width=True):
            st.session_state["sim_reps"] = 0
            st.session_state["sim_angle"] = 160
            st.session_state["sim_stage"] = "down"

    with col_w2:
        st.subheader("Posture Tips")
        tips_map = {
            "Bicep Curl": [
                "Keep elbows fixed at your sides",
                "Don't swing your torso",
                "Control the eccentric (lowering) phase",
                "Full range of motion – all the way up and down",
            ],
            "Squat": [
                "Feet shoulder-width apart",
                "Chest up, back straight",
                "Knees track over toes",
                "Depth: thighs parallel to floor",
            ],
            "Push-up": [
                "Body forms a straight line",
                "Elbows at ~45° angle",
                "Full range – chest near floor",
                "Core braced throughout",
            ],
        }
        for tip in tips_map[exercise]:
            st.markdown(f"✔️ {tip}")

    st.markdown("---")
    st.subheader("📝 Log This Workout")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        log_reps = st.number_input("Reps Completed", min_value=0, value=st.session_state["sim_reps"])
    with col_l2:
        log_dur = st.number_input("Duration (seconds)", min_value=0, value=120)
    with col_l3:
        log_issues = st.text_input("Posture Issues (comma-separated)", value="")

    if st.button("💾 Save Workout", use_container_width=True):
        if st.session_state["user_id"]:
            analyzer = PerformanceAnalyzer()
            issues = [i.strip() for i in log_issues.split(",") if i.strip()]
            score = analyzer.score_session(exercise, log_reps, log_dur, issues)
            db = SessionLocal()
            try:
                session = db_models.WorkoutSession(
                    user_id=st.session_state["user_id"],
                    exercise=exercise,
                    reps=log_reps,
                    duration_sec=log_dur,
                    performance_score=score["score"],
                    posture_issues=log_issues,
                )
                db.add(session)
                db.commit()
                st.success(f"Workout saved! Score: **{score['score']}/100** (Grade: {score['grade']})")
            finally:
                db.close()
        else:
            st.warning("Please save your profile first (sidebar).")


# ===========================================================================
# TAB 3 – Diet Planner
# ===========================================================================

with tabs[2]:
    st.header("🥗 AI Dietician & Calorie Coach")

    planner = DietPlanner()
    plan = planner.get_diet_plan(weight, height, age, is_male, goal, activity)

    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("BMI", plan["bmi"], plan["bmi_category"])
    col_d2.metric("BMR", f"{plan['bmr']} kcal")
    col_d3.metric("TDEE", f"{plan['tdee']} kcal")
    col_d4.metric("Target", f"{plan['target_calories']} kcal")

    st.markdown("---")
    st.subheader("📋 Today's Meal Plan")

    meal_icons = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙", "snack": "🍎"}
    cols = st.columns(4)
    for idx, (slot, meal) in enumerate(plan["meal_plan"].items()):
        with cols[idx]:
            st.markdown(f"**{meal_icons[slot]} {slot.title()}**")
            st.info(meal["name"])
            st.caption(
                f"🔥 {meal['calories']} kcal  |  "
                f"💪 {meal['protein_g']}g protein  |  "
                f"🌾 {meal['carbs_g']}g carbs  |  "
                f"🫒 {meal['fat_g']}g fat"
            )

    st.markdown("---")
    col_tip, col_log = st.columns(2)

    with col_tip:
        st.subheader("💡 Diet Tip")
        st.success(planner.diet_tip(goal))

    with col_log:
        st.subheader("📝 Log a Meal")
        meal_name = st.text_input("Meal name")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        m_cals = mcol1.number_input("kcal", min_value=0, value=400)
        m_prot = mcol2.number_input("Protein g", min_value=0, value=30)
        m_carb = mcol3.number_input("Carbs g", min_value=0, value=50)
        m_fat = mcol4.number_input("Fat g", min_value=0, value=10)

        if st.button("💾 Log Meal"):
            if st.session_state["user_id"] and meal_name:
                db = SessionLocal()
                try:
                    entry = db_models.DietLog(
                        user_id=st.session_state["user_id"],
                        meal_name=meal_name, calories=m_cals,
                        protein_g=m_prot, carbs_g=m_carb, fat_g=m_fat,
                    )
                    db.add(entry)
                    db.commit()
                    st.success("Meal logged!")
                finally:
                    db.close()
            else:
                st.warning("Save your profile and enter a meal name first.")

    # Today's calorie bar
    st.markdown("---")
    st.subheader("📊 Today's Calorie Progress")
    total_meal_cals = plan["meal_plan_calories"]
    fig_cal = go.Figure(go.Bar(
        x=["Planned Meals", "Target"],
        y=[total_meal_cals, plan["target_calories"]],
        marker_color=["#00b4d8", "#0077b6"],
    ))
    fig_cal.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                          height=250, yaxis_title="Calories")
    st.plotly_chart(fig_cal, use_container_width=True)


# ===========================================================================
# TAB 4 – Performance Analyzer
# ===========================================================================

with tabs[3]:
    st.header("📊 Pose-to-Performance Analyzer")

    db = SessionLocal()
    try:
        user_id = st.session_state.get("user_id")
        if user_id:
            sessions = (
                db.query(db_models.WorkoutSession)
                .filter(db_models.WorkoutSession.user_id == user_id)
                .order_by(db_models.WorkoutSession.session_date.desc())
                .limit(30)
                .all()
            )
            rows = [
                {
                    "exercise": s.exercise, "reps": s.reps,
                    "duration_sec": s.duration_sec,
                    "performance_score": s.performance_score,
                    "session_date": s.session_date,
                }
                for s in sessions
            ]
        else:
            # Demo data
            rows = _demo_sessions = [
                {"exercise": ex, "reps": random.randint(8, 20),
                 "duration_sec": random.randint(60, 300),
                 "performance_score": random.uniform(50, 95),
                 "session_date": datetime.utcnow() - timedelta(days=i)}
                for i, ex in enumerate(["Bicep Curl", "Squat", "Push-up", "Squat",
                                        "Bicep Curl", "Push-up", "Squat"])
            ]
    finally:
        db.close()

    analyzer = PerformanceAnalyzer()
    summary = analyzer.weekly_progress(rows)

    pa1, pa2, pa3, pa4 = st.columns(4)
    pa1.metric("Total Sessions", summary["total_sessions"])
    pa2.metric("Total Reps", summary["total_reps"])
    pa3.metric("Avg Score", f"{summary['avg_score']}/100")
    pa4.metric("Best Score", f"{summary['best_score']}/100")

    st.markdown("---")

    if rows:
        df_rows = pd.DataFrame(rows)
        df_rows["session_date"] = pd.to_datetime(df_rows["session_date"])
        df_rows["date_str"] = df_rows["session_date"].dt.strftime("%Y-%m-%d")

        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.subheader("📈 Score Over Time")
            fig_score = px.line(
                df_rows.sort_values("session_date"),
                x="date_str", y="performance_score",
                color="exercise", markers=True,
            )
            fig_score.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                                    height=300, xaxis_title="Date",
                                    yaxis_title="Score")
            st.plotly_chart(fig_score, use_container_width=True)

        with col_p2:
            st.subheader("🏋️ Reps by Exercise")
            ex_summary = df_rows.groupby("exercise")["reps"].sum().reset_index()
            fig_reps = px.bar(ex_summary, x="exercise", y="reps",
                              color="exercise")
            fig_reps.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                                   height=300, showlegend=False)
            st.plotly_chart(fig_reps, use_container_width=True)

        st.subheader("📋 Session Log")
        st.dataframe(
            df_rows[["date_str", "exercise", "reps", "duration_sec", "performance_score"]]
            .rename(columns={"date_str": "Date", "exercise": "Exercise",
                             "reps": "Reps", "duration_sec": "Duration (s)",
                             "performance_score": "Score"}),
            use_container_width=True,
        )
    else:
        st.info("No sessions logged yet. Complete a workout to see your performance data.")


# ===========================================================================
# TAB 5 – Virtual Gym Buddy Chatbot
# ===========================================================================

with tabs[4]:
    st.header("🤖 Virtual Gym Buddy")
    st.caption("Ask me anything about fitness, workouts, nutrition, and more!")

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

    user_input = st.chat_input("Type your fitness question…")
    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        reply = st.session_state["buddy"].chat(user_input)
        sentiment = simple_sentiment(user_input)
        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("🗑️ Clear Chat"):
        st.session_state["chat_history"] = []
        st.session_state["buddy"].clear_history()
        st.rerun()

    st.markdown("---")
    st.subheader("💬 Quick Questions")
    quick = [
        "How do I lose weight fast?",
        "What should I eat before a workout?",
        "How many reps should I do?",
        "I feel tired and unmotivated today",
        "What's the best exercise for beginners?",
    ]
    qcols = st.columns(len(quick))
    for i, q in enumerate(quick):
        if qcols[i].button(q, key=f"quick_{i}"):
            st.session_state["chat_history"].append({"role": "user", "content": q})
            reply = st.session_state["buddy"].chat(q)
            st.session_state["chat_history"].append({"role": "assistant", "content": reply})
            st.rerun()


# ===========================================================================
# TAB 6 – IoT Monitor
# ===========================================================================

with tabs[5]:
    st.header("📡 Smart Gym Assistant – IoT Monitor")
    st.caption("Simulated real-time sensor data for heart rate, calories, and equipment load.")

    iot_col1, iot_col2 = st.columns([1, 2])

    with iot_col1:
        st.subheader("📟 Sensor Controls")
        if st.button("🔄 Get Reading", use_container_width=True):
            reading = st.session_state["iot_sim"].get_reading()
            rec = st.session_state["iot_sim"].recommend_intensity(reading)
            st.session_state["iot_readings"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "hr": reading.heart_rate,
                "calories": reading.calories_burned,
                "load": reading.equipment_load,
                "zone": rec["zone"],
                "action": rec["action"],
            })

        if st.button("♻️ Reset Session", use_container_width=True):
            st.session_state["iot_sim"].reset()
            st.session_state["iot_readings"] = []
            st.success("Session reset.")

        if st.session_state["iot_readings"]:
            latest = st.session_state["iot_readings"][-1]
            st.metric("Heart Rate", f"{latest['hr']} bpm")
            st.metric("Calories Burned", f"{latest['calories']} kcal")
            st.metric("Equipment Load", f"{latest['load']} %")

            zone_color = {
                "resting": "🔵", "warm_up": "🟢", "fat_burn": "🟡",
                "cardio": "🟠", "peak": "🔴", "max_effort": "⚫",
            }
            st.markdown(
                f"**Zone:** {zone_color.get(latest['zone'], '⚪')} {latest['zone'].replace('_', ' ').title()}"
            )
            action_color = {"increase": "🔼", "maintain": "➡️", "decrease": "🔽"}
            st.markdown(f"**Action:** {action_color.get(latest['action'], '')} {latest['action'].title()}")

    with iot_col2:
        st.subheader("📈 Live Sensor Charts")
        if st.session_state["iot_readings"]:
            df_iot = pd.DataFrame(st.session_state["iot_readings"])
            fig_hr = px.line(df_iot, x="time", y="hr", title="Heart Rate (bpm)",
                             markers=True, line_shape="spline")
            fig_hr.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                                 height=200, showlegend=False)
            st.plotly_chart(fig_hr, use_container_width=True)

            fig_load = px.area(df_iot, x="time", y="load", title="Equipment Load (%)",
                               color_discrete_sequence=["#0077b6"])
            fig_load.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                                   height=200, showlegend=False)
            st.plotly_chart(fig_load, use_container_width=True)
        else:
            st.info("Press **Get Reading** to start monitoring.")


# ===========================================================================
# TAB 7 – Habit Tracker
# ===========================================================================

with tabs[6]:
    st.header("🧠 Fitness Habit Tracker")

    tracker_model = HabitTracker()

    ht_col1, ht_col2 = st.columns(2)

    with ht_col1:
        st.subheader("📋 Today's Check-in")
        ht_mood = st.slider("Mood (1=low, 10=great)", 1, 10, 6)
        ht_sleep = st.slider("Sleep hours", 0.0, 12.0, 7.0, 0.5)
        ht_stress = st.slider("Stress level (1=low, 10=high)", 1, 10, 4)
        ht_done = st.checkbox("Did I work out today?")

        if st.button("📤 Submit Check-in", use_container_width=True):
            prob = tracker_model.predict_skip_probability(ht_mood, ht_sleep, ht_stress)
            nudge = tracker_model.get_nudge(prob)
            st.session_state["last_skip_prob"] = prob
            st.session_state["last_nudge"] = nudge

            if st.session_state["user_id"]:
                db = SessionLocal()
                try:
                    rec_db = db_models.HabitRecord(
                        user_id=st.session_state["user_id"],
                        workout_done=ht_done,
                        mood=ht_mood,
                        sleep_hours=ht_sleep,
                        stress_level=ht_stress,
                    )
                    db.add(rec_db)
                    db.commit()
                finally:
                    db.close()

        if "last_skip_prob" in st.session_state:
            prob = st.session_state["last_skip_prob"]
            colour = "🔴" if prob > 0.70 else ("🟡" if prob > 0.40 else "🟢")
            st.metric("Skip Probability", f"{colour} {round(prob * 100, 1)}%")
            st.info(st.session_state["last_nudge"])

    with ht_col2:
        st.subheader("📊 Weekly Habit Summary")
        # Use DB data if user logged in, otherwise generate demo
        if st.session_state["user_id"]:
            db = SessionLocal()
            try:
                records = (
                    db.query(db_models.HabitRecord)
                    .filter(db_models.HabitRecord.user_id == st.session_state["user_id"])
                    .order_by(db_models.HabitRecord.record_date.desc())
                    .limit(7)
                    .all()
                )
                rows_habit = [
                    {"workout_done": r.workout_done, "mood": r.mood,
                     "sleep_hours": r.sleep_hours, "stress_level": r.stress_level}
                    for r in records
                ]
            finally:
                db.close()
        else:
            rng = random.Random(42)
            rows_habit = [
                {"workout_done": rng.choice([True, False]),
                 "mood": rng.randint(4, 9),
                 "sleep_hours": round(rng.uniform(5, 9), 1),
                 "stress_level": rng.randint(2, 8)}
                for _ in range(7)
            ]

        summary_habit = tracker_model.weekly_summary(rows_habit)

        s1, s2 = st.columns(2)
        s1.metric("Workouts Completed", summary_habit["workouts_completed"])
        s2.metric("Completion Rate", f"{summary_habit['completion_rate']}%")
        s1.metric("Avg Mood", summary_habit["avg_mood"])
        s2.metric("Avg Sleep", f"{summary_habit['avg_sleep']} hrs")
        s1.metric("Avg Stress", summary_habit["avg_stress"])

        if rows_habit:
            df_habit = pd.DataFrame(rows_habit)
            df_habit["day"] = [f"Day {i+1}" for i in range(len(df_habit))]
            fig_habit = px.line(df_habit, x="day", y=["mood", "sleep_hours", "stress_level"],
                                markers=True)
            fig_habit.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                                    height=250, yaxis_title="Score")
            st.plotly_chart(fig_habit, use_container_width=True)


# ===========================================================================
# TAB 8 – Recommender
# ===========================================================================

with tabs[7]:
    st.header("🏋️ Gym & Workout Recommender")

    rec_engine = GymRecommender()

    rec_col1, rec_col2 = st.columns(2)

    with rec_col1:
        st.subheader("🏃 Workout Recommendations")
        r_level = st.selectbox("Fitness Level", ["beginner", "intermediate", "advanced"], key="r_level")
        r_type = st.selectbox("Workout Type", ["any", "strength", "cardio", "flexibility"], key="r_type")
        r_duration = st.slider("Max Duration (min)", 15, 120, 60, key="r_dur")

        workouts = rec_engine.recommend_workouts(
            goal=goal,
            fitness_level=r_level,
            workout_type=None if r_type == "any" else r_type,
            max_duration=r_duration,
            top_n=5,
        )

        for w in workouts:
            with st.expander(f"⭐ {w['relevance']*100:.0f}%  |  {w['name']}"):
                wc1, wc2, wc3 = st.columns(3)
                wc1.markdown(f"**Level:** {w['level'].title()}")
                wc2.markdown(f"**Duration:** {w['duration_min']} min")
                wc3.markdown(f"**Calories:** ~{w['calories_burned']} kcal")
                st.markdown(f"**Equipment:** {w['equipment'].title()}  |  **Type:** {w['type'].title()}")

    with rec_col2:
        st.subheader("🏢 Gym Recommendations")
        g_focus = st.selectbox("Training Focus", ["strength", "cardio", "flexibility"], key="g_focus")
        g_price = st.selectbox("Budget", ["any", "low", "mid", "high", "none"], key="g_price")

        gyms = rec_engine.recommend_gyms(
            focus=g_focus,
            price_tier=None if g_price == "any" else g_price,
            top_n=4,
        )

        for g in gyms:
            with st.expander(f"⭐ {g['rating']}  |  {g['name']}"):
                gc1, gc2 = st.columns(2)
                gc1.markdown(f"**Type:** {g['type'].title()}")
                gc2.markdown(f"**Price:** {g['price_tier'].title()}")
                amenities = g["amenities"] if isinstance(g["amenities"], list) else [g["amenities"]]
                st.markdown(f"**Amenities:** {', '.join(amenities)}")
                st.progress(min(1.0, g["relevance"]))

    st.markdown("---")
    st.subheader("📊 Workout Comparison")
    if workouts:
        df_wout = pd.DataFrame(workouts)
        fig_compare = px.scatter(
            df_wout,
            x="duration_min", y="calories_burned",
            size="relevance", color="type",
            hover_name="name",
            size_max=40,
        )
        fig_compare.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                                   height=300)
        st.plotly_chart(fig_compare, use_container_width=True)

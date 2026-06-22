"""
The Register — Student & Staff Records
A Streamlit front end for the JSON-backed student/teacher management system.

Run with:
    streamlit run app.py
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Data layer (same model as the original script)
# ---------------------------------------------------------------------------

DATABASE = "school_data.json"


def load_data():
    if Path(DATABASE).exists():
        with open(DATABASE, "r") as f:
            content = f.read()
            if content:
                return json.loads(content)
    return {"students": [], "teachers": []}


def save_data(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


def persist():
    save_data(data)


class Persons(ABC):
    @abstractmethod
    def get_role(self):
        pass

    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email and email.index("@") < email.rindex(".")


class Student(Persons):
    def get_role(self):
        return "student"

    def register(self, name, age, email, roll_no):
        if not Persons.validate_email(email):
            return False, "Invalid email address."
        if any(s["roll_no"] == roll_no for s in data["students"]):
            return False, f"A student with roll number {roll_no} already exists."
        data["students"].append(
            {"name": name, "age": age, "email": email, "roll_no": roll_no, "grades": {}}
        )
        persist()
        return True, f"Student {name} registered."

    def add_grade(self, roll_no, subject, marks):
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                s["grades"][subject] = marks
                persist()
                return True, "Grade added."
        return False, "Student not found."

    def remove_grade(self, roll_no, subject):
        for s in data["students"]:
            if s["roll_no"] == roll_no and subject in s["grades"]:
                del s["grades"][subject]
                persist()
                return True
        return False

    def delete(self, roll_no):
        data["students"] = [s for s in data["students"] if s["roll_no"] != roll_no]
        persist()


class Teacher(Persons):
    def get_role(self):
        return "teacher"

    def register(self, name, age, email, emp_id, subject):
        if not Persons.validate_email(email):
            return False, "Invalid email address."
        if any(t["emp_id"] == emp_id for t in data["teachers"]):
            return False, f"A teacher with employee ID {emp_id} already exists."
        data["teachers"].append(
            {"name": name, "age": age, "email": email, "emp_id": emp_id, "subject": subject}
        )
        persist()
        return True, f"Teacher {name} registered."

    def delete(self, emp_id):
        data["teachers"] = [t for t in data["teachers"] if t["emp_id"] != emp_id]
        persist()


stud = Student()
tech = Teacher()


def average(grades: dict):
    if not grades:
        return None
    return sum(grades.values()) / len(grades)


def grade_letter(avg):
    if avg is None:
        return "—"
    if avg >= 90:
        return "A"
    if avg >= 80:
        return "B"
    if avg >= 70:
        return "C"
    if avg >= 60:
        return "D"
    return "F"


GRADE_COLOR = {
    "A": "#6F8B63",
    "B": "#8FA374",
    "C": "#C9A94A",
    "D": "#C1432E",
    "F": "#C1432E",
    "—": "transparent",
}

# ---------------------------------------------------------------------------
# Look & feel — ledger / school-register styling
# ---------------------------------------------------------------------------

st.set_page_config(page_title="The Register", page_icon="📋", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Fraunces', serif;
    }
    .stApp {
        background-color: #F7F3E9;
        background-image: repeating-linear-gradient(transparent 0 31px, #C9BFA5 31px 32px);
    }
    .block-container { padding-top: 2rem; max-width: 1100px; }

    .masthead-title {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-weight: 600;
        font-size: 44px;
        color: #1B2A4A;
        margin-bottom: 0;
    }
    .masthead-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #3A4A6B;
    }
    hr {
        border-top: 3px solid #1B2A4A !important;
    }

    .reg-card {
        background: #EFE8D8;
        border: 1.5px solid #1B2A4A;
        border-radius: 6px;
        padding: 14px 16px 10px;
        margin-bottom: 12px;
        box-shadow: 2px 3px 0 rgba(27,42,74,0.08);
    }
    .reg-card h4 {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 18px;
        color: #1B2A4A;
        margin: 4px 0 2px;
    }
    .reg-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #3A4A6B;
    }
    .reg-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 9.5px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: #C1432E;
        color: #F7F3E9;
        padding: 2px 7px;
        border-radius: 3px;
    }
    .reg-tag.teacher { background: #1B2A4A; }

    .grade-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px; height: 30px;
        border-radius: 50%;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 13px;
        color: white;
        border: 2px solid #1B2A4A;
    }

    .section-title {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-weight: 600;
        font-size: 22px;
        color: #1B2A4A;
        margin: 10px 0 14px;
    }

    .stButton button {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        background-color: #1B2A4A;
        color: #F7F3E9;
        border-radius: 4px;
        border: 2px solid #1B2A4A;
    }
    .stButton button:hover {
        background-color: #3A4A6B;
        border-color: #3A4A6B;
        color: #F7F3E9;
    }
    label, .stTextInput label, .stNumberInput label, .stSelectbox label {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #3A4A6B !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="masthead-title">The Register</div>', unsafe_allow_html=True)
st.markdown('<div class="masthead-sub">Student &amp; Staff Records · Form B-7</div>', unsafe_allow_html=True)
st.markdown("---")

tab_students, tab_teachers, tab_grades = st.tabs(["📇 Students", "🧑‍🏫 Staff", "📊 Grades"])

# ---------------------------------------------------------------------------
# Students tab
# ---------------------------------------------------------------------------

with tab_students:
    st.markdown('<div class="section-title">Enroll a student</div>', unsafe_allow_html=True)

    with st.form("add_student_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name", placeholder="Asha Patil")
            email = st.text_input("Email", placeholder="asha@school.edu")
        with c2:
            age = st.number_input("Age", min_value=1, max_value=120, step=1, value=15)
            roll_no = st.text_input("Roll number", placeholder="R-014")

        submitted = st.form_submit_button("Add to register")
        if submitted:
            if not name.strip() or not roll_no.strip():
                st.error("Name and roll number are required.")
            else:
                ok, msg = stud.register(name.strip(), int(age), email.strip(), roll_no.strip())
                (st.success if ok else st.error)(msg)

    st.markdown("---")
    st.markdown(
        f'<div class="section-title">Current roll <span class="reg-tag" style="background:#1B2A4A;">{len(data["students"])}</span></div>',
        unsafe_allow_html=True,
    )

    if not data["students"]:
        st.info("No students enrolled yet. Add one above.")
    else:
        roll_lookup = {s["roll_no"]: s for s in data["students"]}
        list_col, detail_col = st.columns([1, 1])

        with list_col:
            for s in data["students"]:
                avg = average(s["grades"])
                letter = grade_letter(avg)
                color = GRADE_COLOR[letter]
                st.markdown(
                    f"""
                    <div class="reg-card">
                        <span class="reg-tag">Student</span>
                        <h4>{s['name']}</h4>
                        <div class="reg-meta">Roll {s['roll_no']} · Age {s['age']}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                            <span class="reg-meta">{len(s['grades'])} subject(s) graded</span>
                            <span class="grade-badge" style="background:{color}; border-color:{color if letter!='—' else '#C9BFA5'};">{letter}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with detail_col:
            selected_roll = st.selectbox(
                "View student record",
                options=list(roll_lookup.keys()),
                format_func=lambda r: f"{r} — {roll_lookup[r]['name']}",
            )
            s = roll_lookup[selected_roll]
            avg = average(s["grades"])
            letter = grade_letter(avg)

            st.markdown(f"### {s['name']}")
            st.markdown(f'<span class="reg-meta">{s["email"]}</span>', unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Age", s["age"])
            m2.metric("Subjects", len(s["grades"]))
            m3.metric("Average", f"{avg:.1f}" if avg is not None else "—", letter)

            if s["grades"]:
                st.table(
                    {"Subject": list(s["grades"].keys()), "Marks": list(s["grades"].values())}
                )
                remove_subj = st.selectbox(
                    "Remove a grade", options=["—"] + list(s["grades"].keys()), key="rm_grade"
                )
                if remove_subj != "—" and st.button("Remove selected grade"):
                    stud.remove_grade(s["roll_no"], remove_subj)
                    st.rerun()
            else:
                st.caption("No grades recorded yet — add one from the Grades tab.")

            st.markdown("")
            if st.button("🗑️ Remove student from register", key="del_student"):
                stud.delete(s["roll_no"])
                st.rerun()

# ---------------------------------------------------------------------------
# Teachers tab
# ---------------------------------------------------------------------------

with tab_teachers:
    st.markdown('<div class="section-title">Add a staff member</div>', unsafe_allow_html=True)

    with st.form("add_teacher_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            t_name = st.text_input("Full name", placeholder="Mrs. Kulkarni")
            t_email = st.text_input("Email", placeholder="kulkarni@school.edu")
        with c2:
            t_age = st.number_input("Age", min_value=18, max_value=120, step=1, value=35)
            t_emp_id = st.text_input("Employee ID", placeholder="T-009")
        with c3:
            t_subject = st.text_input("Subject taught", placeholder="Mathematics")

        t_submitted = st.form_submit_button("Add to staff roll")
        if t_submitted:
            if not t_name.strip() or not t_emp_id.strip() or not t_subject.strip():
                st.error("Name, employee ID, and subject are required.")
            else:
                ok, msg = tech.register(
                    t_name.strip(), int(t_age), t_email.strip(), t_emp_id.strip(), t_subject.strip()
                )
                (st.success if ok else st.error)(msg)

    st.markdown("---")
    st.markdown(
        f'<div class="section-title">Staff roll <span class="reg-tag" style="background:#1B2A4A;">{len(data["teachers"])}</span></div>',
        unsafe_allow_html=True,
    )

    if not data["teachers"]:
        st.info("No teachers registered yet. Add one above.")
    else:
        for t in data["teachers"]:
            st.markdown(
                f"""
                <div class="reg-card">
                    <span class="reg-tag teacher">Teacher</span>
                    <h4>{t['name']}</h4>
                    <div class="reg-meta">ID {t['emp_id']} · Age {t['age']} · Teaches {t['subject']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        del_emp = st.selectbox(
            "Remove a staff member",
            options=["—"] + [t["emp_id"] for t in data["teachers"]],
            format_func=lambda e: e if e == "—" else f"{e} — {next(t['name'] for t in data['teachers'] if t['emp_id']==e)}",
        )
        if del_emp != "—" and st.button("🗑️ Remove from staff roll"):
            tech.delete(del_emp)
            st.rerun()

# ---------------------------------------------------------------------------
# Grades tab
# ---------------------------------------------------------------------------

with tab_grades:
    st.markdown('<div class="section-title">Record a grade</div>', unsafe_allow_html=True)

    if not data["students"]:
        st.info("Enroll a student first before recording grades.")
    else:
        roll_lookup = {s["roll_no"]: s for s in data["students"]}
        with st.form("add_grade_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                g_roll = st.selectbox(
                    "Student",
                    options=list(roll_lookup.keys()),
                    format_func=lambda r: f"{r} — {roll_lookup[r]['name']}",
                )
            with c2:
                g_subject = st.text_input("Subject", placeholder="Physics")
            with c3:
                g_marks = st.number_input("Marks (0–100)", min_value=0.0, max_value=100.0, step=1.0)

            g_submitted = st.form_submit_button("Record grade")
            if g_submitted:
                if not g_subject.strip():
                    st.error("Subject is required.")
                else:
                    ok, msg = stud.add_grade(g_roll, g_subject.strip(), g_marks)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()

        st.markdown("---")
        st.markdown('<div class="section-title">Gradebook overview</div>', unsafe_allow_html=True)

        cols = st.columns(3)
        for i, s in enumerate(data["students"]):
            avg = average(s["grades"])
            letter = grade_letter(avg)
            color = GRADE_COLOR[letter]
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div class="reg-card">
                        <span class="reg-tag">Student</span>
                        <h4>{s['name']}</h4>
                        <div class="reg-meta">Roll {s['roll_no']}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                            <span class="reg-meta">Avg: {f'{avg:.1f}' if avg is not None else '—'}</span>
                            <span class="grade-badge" style="background:{color}; border-color:{color if letter!='—' else '#C9BFA5'};">{letter}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
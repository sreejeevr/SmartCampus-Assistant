from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "SmartCampus_Secret_Key_2026")

DATABASE = "database.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_database():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    user_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(users)").fetchall()
    }

    if "subject" not in user_columns:
        connection.execute(
            "ALTER TABLE users ADD COLUMN subject TEXT"
        )


    connection.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(student_id, subject, attendance_date),
            FOREIGN KEY(student_id) REFERENCES users(id)
        )
    """)

    # Student profile table used by the Faculty Students section.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            student_id TEXT,
            register_no TEXT,
            campus_id TEXT,
            phone TEXT,
            course TEXT,
            semester TEXT,
            batch TEXT,
            division TEXT,
            roll_number TEXT,
            date_of_birth TEXT,
            gender TEXT,
            address TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            deadline_date TEXT,
            questions TEXT NOT NULL DEFAULT '',
            created_by INTEGER,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(created_by) REFERENCES users(id)
        )
    """)

    assignment_count = connection.execute(
        "SELECT COUNT(*) AS count FROM assignments"
    ).fetchone()["count"]

    if assignment_count == 0:
        for assignment in assignments:
            questions_text = "\n".join(assignment.get("questions", []))
            connection.execute(
                """
                INSERT INTO assignments
                (subject, title, deadline_date, questions, created_by)
                VALUES (?, ?, ?, ?, NULL)
                """,
                (
                    assignment["subject"],
                    assignment["title"],
                    assignment["deadline_date"] or None,
                    questions_text
                )
            )


    # Ensure the separate Admin account always exists with known credentials.
    # This is intentionally NOT exposed through public registration.
    admin_email = "admin@smartcampus.com"
    admin_password = "Admin@123"

    admin_user = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        (admin_email,)
    ).fetchone()

    admin_hash = generate_password_hash(admin_password)

    if admin_user is None:
        connection.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, 'admin')
            """,
            ("System Administrator", admin_email, admin_hash)
        )
    else:
        connection.execute(
            """
            UPDATE users
            SET name = ?, password = ?, role = 'admin'
            WHERE email = ?
            """,
            ("System Administrator", admin_hash, admin_email)
        )


    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS faculty_announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(faculty_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# COLLEGE TIMETABLE
# ============================================================

timetable = {

    "Monday": [
        {
            "period": "Period 1",
            "time": "9:00 AM - 10:00 AM",
            "subject": "Progressive Web App - T",
            "faculty": "Ms. Amrin",
            "room": ""
        },
        {
            "period": "Period 2",
            "time": "10:00 AM - 11:00 AM",
            "subject": "POV / OSS / IOT / R Programming",
            "faculty": "Ms. Anjana / Ms. Abhirami / Mr. RK / Ms. Nagavaralakshmi",
            "room": "LH-9 / LH-3 / LH-2 / LH-6, 3rd Floor"
        },
        {
            "period": "Break",
            "time": "11:00 AM - 11:15 AM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 3",
            "time": "11:15 AM - 12:15 PM",
            "subject": "Deep Learning (T)",
            "faculty": "Ms. Geethanjali",
            "room": ""
        },
        {
            "period": "Period 4",
            "time": "12:15 PM - 1:00 PM",
            "subject": "NLP",
            "faculty": "Ms. Nagavaralakshmi",
            "room": ""
        },
        {
            "period": "Break",
            "time": "1:00 PM - 2:00 PM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 5",
            "time": "2:00 PM - 3:00 PM",
            "subject": "Software Engineering",
            "faculty": "Ms. Anjana",
            "room": ""
        },
        {
            "period": "Period 6",
            "time": "3:00 PM - 3:45 PM",
            "subject": "Placement Training",
            "faculty": "",
            "room": ""
        }
    ],

    "Tuesday": [
        {
            "period": "Period 1",
            "time": "9:00 AM - 10:00 AM",
            "subject": "Professional Development",
            "faculty": "Ms. Pooja",
            "room": ""
        },
        {
            "period": "Period 2",
            "time": "10:00 AM - 11:00 AM",
            "subject": "Progressive Web App - T",
            "faculty": "Ms. Amrin",
            "room": ""
        },
        {
            "period": "Break",
            "time": "11:00 AM - 11:15 AM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 3 & 4",
            "time": "11:15 AM - 1:00 PM",
            "subject": "Deep Learning - LAB",
            "faculty": "Ms. Geethanjali",
            "room": ""
        },
        {
            "period": "Break",
            "time": "1:00 PM - 2:00 PM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 5",
            "time": "2:00 PM - 3:00 PM",
            "subject": "NLP",
            "faculty": "Ms. Nagavaralakshmi",
            "room": ""
        },
        {
            "period": "Period 6",
            "time": "3:00 PM - 3:45 PM",
            "subject": "Software Engineering",
            "faculty": "Ms. Anjana",
            "room": ""
        }
    ],

    "Wednesday": [
        {
            "period": "Period 1",
            "time": "9:00 AM - 10:00 AM",
            "subject": "POV / OSS / IOT / R Programming",
            "faculty": "Ms. Anjana / Ms. Abhirami / Mr. RK / Ms. Nagavaralakshmi",
            "room": "LH-9 / LH-3 / LH-2 / LH-6, 3rd Floor"
        },
        {
            "period": "Period 2",
            "time": "10:00 AM - 11:00 AM",
            "subject": "Placement Training",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Break",
            "time": "11:00 AM - 11:15 AM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 3",
            "time": "11:15 AM - 12:15 PM",
            "subject": "Progressive Web App - T",
            "faculty": "Ms. Amrin",
            "room": ""
        },
        {
            "period": "Period 4",
            "time": "12:15 PM - 1:00 PM",
            "subject": "Software Engineering",
            "faculty": "Ms. Anjana",
            "room": ""
        },
        {
            "period": "Break",
            "time": "1:00 PM - 2:00 PM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 5",
            "time": "2:00 PM - 3:00 PM",
            "subject": "Deep Learning (T)",
            "faculty": "Ms. Geethanjali",
            "room": ""
        },
        {
            "period": "Period 6",
            "time": "3:00 PM - 3:45 PM",
            "subject": "PET",
            "faculty": "",
            "room": ""
        }
    ],

    "Thursday": [
        {
            "period": "Period 1",
            "time": "9:00 AM - 10:00 AM",
            "subject": "NLP",
            "faculty": "Ms. Nagavaralakshmi",
            "room": ""
        },
        {
            "period": "Period 2",
            "time": "10:00 AM - 11:00 AM",
            "subject": "Professional Development",
            "faculty": "Ms. Pooja",
            "room": ""
        },
        {
            "period": "Break",
            "time": "11:00 AM - 11:15 AM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 3",
            "time": "11:15 AM - 12:15 PM",
            "subject": "POV / OSS / IOT / R Programming",
            "faculty": "Ms. Anjana / Ms. Abhirami / Mr. RK / Ms. Nagavaralakshmi",
            "room": "LH-9 / LH-3 / LH-2 / LH-6, 3rd Floor"
        },
        {
            "period": "Period 4",
            "time": "12:15 PM - 1:00 PM",
            "subject": "Software Engineering",
            "faculty": "Ms. Anjana",
            "room": ""
        },
        {
            "period": "Break",
            "time": "1:00 PM - 2:00 PM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 5 & 6",
            "time": "2:00 PM - 3:45 PM",
            "subject": "Progressive Web App - LAB",
            "faculty": "Ms. Amrin",
            "room": ""
        }
    ],

    "Friday": [
        {
            "period": "Period 1 & 2",
            "time": "9:00 AM - 11:00 AM",
            "subject": "Deep Learning - LAB",
            "faculty": "Ms. Geethanjali",
            "room": ""
        },
        {
            "period": "Break",
            "time": "11:00 AM - 11:15 AM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 3",
            "time": "11:15 AM - 12:30 PM",
            "subject": "Professional Development",
            "faculty": "Ms. Pooja",
            "room": ""
        },
        {
            "period": "Break",
            "time": "12:30 PM - 2:00 PM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 5",
            "time": "2:00 PM - 3:00 PM",
            "subject": "Software Engineering",
            "faculty": "Ms. Anjana",
            "room": ""
        },
        {
            "period": "Period 6",
            "time": "3:00 PM - 3:45 PM",
            "subject": "PET",
            "faculty": "",
            "room": ""
        }
    ],

    "Saturday": [
        {
            "period": "Period 1",
            "time": "9:00 AM - 10:00 AM",
            "subject": "POV / OSS / IOT / R Programming",
            "faculty": "Ms. Anjana / Ms. Abhirami / Mr. RK / Ms. Nagavaralakshmi",
            "room": "LH-9 / LH-3 / LH-2 / LH-6, 3rd Floor"
        },
        {
            "period": "Period 2",
            "time": "10:00 AM - 11:00 AM",
            "subject": "Placement Training",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Break",
            "time": "11:00 AM - 11:15 AM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 3 & 4",
            "time": "11:15 AM - 1:00 PM",
            "subject": "Club Activities",
            "faculty": "Ms. Nagavaralakshmi / Ms. Amrin / Ms. Geethanjali",
            "room": ""
        },
        {
            "period": "Break",
            "time": "1:00 PM - 2:00 PM",
            "subject": "BREAK",
            "faculty": "",
            "room": ""
        },
        {
            "period": "Period 5 & 6",
            "time": "2:00 PM - 3:45 PM",
            "subject": "Progressive Web App - LAB",
            "faculty": "Ms. Amrin",
            "room": ""
        }
    ]
}


# ============================================================
# ASSIGNMENTS
# ============================================================

assignments = [

    {
        "subject": "Progressive Web App",
        "short_subject": "PWA",
        "title": "Assignment - 2",
        "deadline": "30-09-2026",
        "deadline_date": "2026-09-30",
        "total_questions": 6,
        "questions": [
            "Illustrate the various display properties (block, inline, inline-block, none, flex, grid). Explain how they affect the placement of elements on a webpage.",
            "Explain pseudo-classes and pseudo-elements in CSS with examples. How do they improve webpage styling?",
            "Develop a small program to show the effect of display: block, inline, and inline-block using <div> and <span> tags.",
            "Demonstrate the code to create a Bootstrap button with class .btn.",
            "Design a Bootstrap form for student registration (Name, Email, Gender, Course, Submit button) with proper form controls. Provide the code.",
            "Explain Bootstrap Components with Example."
        ]
    },

    {
        "subject": "Deep Learning",
        "short_subject": "Deep Learning",
        "title": "Assignment - 2",
        "deadline": "30-09-2026",
        "deadline_date": "2026-09-30",
        "total_questions": 4,
        "questions": [
            "A bank wants to automatically read handwritten numbers from forms. Develop a Convolutional Neural Network (CNN) for handwritten digit classification using the MNIST dataset, preprocessing and normalization, convolution, pooling, flatten and dense layers, training, accuracy/loss graphs, sample-image testing, predicted versus actual digit display, and classification performance.",
            "An online pet store wants to automatically classify uploaded pet images as Cat or Dog. Develop a CNN-based binary image classification model using a Cat and Dog dataset, resizing, normalization, training/testing split, CNN training, an appropriate binary-classification activation function, accuracy/loss graphs, new-image testing, predicted class display, confusion matrix and classification report.",
            "A telecommunications company wants to identify customers likely to leave the company. Develop a Deep Neural Network (DNN) for customer churn prediction using customer information such as monthly charges, contract type, tenure and internet service. Handle missing values, encode categorical data, normalize numerical features, split the data, build multiple hidden layers, train using an appropriate optimizer, evaluate classification metrics, plot training/validation curves, and identify overfitting or underfitting.",
            "An e-commerce company wants to identify whether customer reviews are positive or negative. Develop a deep learning sentiment-classification model using a review dataset, text cleaning, tokenization, sequences, padding, an Embedding layer and LSTM, training, accuracy/loss graphs, new-review testing and positive/negative prediction."
        ]
    },

    {
        "subject": "Natural Language Processing",
        "short_subject": "NLP",
        "title": "Assessment - 2",
        "deadline": "24-09-2026",
        "deadline_date": "2026-09-24",
        "total_questions": 6,
        "questions": [
            "Explain the process of LSA. Discuss how LSA improves document clustering and IR over word-matching methods.",
            "Compare LSA and Topic Modeling with respect to their objectives, representations, and applications in text analysis.",
            "Analyze the role of dependency paths and semantic roles in extracting structured knowledge from unstructured text.",
            "Discuss the Dependency-Path Kernel method for Relation Extraction. Explain how dependency trees are used, the role of shortest paths, and why this method improves accuracy.",
            "Describe how Diagnostic Text Reports are mined using NLP techniques. Include the purpose, challenges, and benefits of automating diagnostic report analysis.",
            "List and explain key concepts of word matching and give its applications."
        ]
    },

    {
        "subject": "Software Engineering",
        "short_subject": "Software Engineering",
        "title": "Assignment - 2",
        "deadline": "03-10-2026",
        "deadline_date": "2026-10-03",
        "total_questions": 6,
        "questions": [
            "Discuss in detail the Software Design Process. Explain the phases: Interface Design, Architectural Design, and Detailed Design with examples.",
            "What is Software Architecture? Explain various Architectural Styles such as Monolithic, Layered, Client-Server, Microservices, Event-Driven, and Pipe-Filter with examples.",
            "Discuss the various UML diagrams: Class Diagram, Sequence Diagram, Collaboration Diagram, Use Case Diagram, and Component Diagram with their importance and applications.",
            "Explain the key aspects of Software Design Quality. How do these aspects contribute to building effective and maintainable software?",
            "Discuss the importance of Requirement Engineering in software development. What are its advantages and disadvantages?",
            "Compare black-box and white-box testing with suitable examples. Mention the advantages and limitations of each."
        ]
    },

    {
        "subject": "Internet of Things",
        "short_subject": "IoT",
        "title": "No Assignment Given",
        "deadline": "",
        "deadline_date": "",
        "total_questions": 0,
        "questions": []
    }
]


# ============================================================
# GET ASSIGNMENT STATUS
# ============================================================

def get_assignment_status(deadline_date):

    if not deadline_date:
        return "No Assignment"

    today = date.today()
    deadline = datetime.strptime(
        deadline_date,
        "%Y-%m-%d"
    ).date()

    if deadline < today:
        return "Overdue"

    if deadline == today:
        return "Due Today"

    return "Upcoming"


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return render_template("index.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            ""
        ).strip().lower()

        if not name or not email or not password or not role:

            flash(
                "Please fill in all fields.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        if role not in [
            "student",
            "faculty"
        ]:

            flash(
                "Invalid role selected.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        connection = get_db_connection()

        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:

            connection.close()

            flash(
                "Email already registered.",
                "warning"
            )

            return render_template(
                "register.html"
            )

        hashed_password = generate_password_hash(
            password
        )

        connection.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                hashed_password,
                role
            )
        )

        connection.commit()
        connection.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Please enter email and password.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            if user["role"] == "faculty":
                return redirect(
                    url_for("faculty_dashboard")
                )

            return redirect(
                url_for("student_dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )



# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        if session.get("role") == "faculty":
            return redirect(url_for("faculty_dashboard"))
        return redirect(url_for("student_dashboard"))

    connection = get_db_connection()

    student_count = connection.execute(
        "SELECT COUNT(*) AS count FROM users WHERE role = 'student'"
    ).fetchone()["count"]

    faculty_count = connection.execute(
        "SELECT COUNT(*) AS count FROM users WHERE role = 'faculty'"
    ).fetchone()["count"]

    attendance_count = connection.execute(
        "SELECT COUNT(*) AS count FROM attendance"
    ).fetchone()["count"]

    assignment_count = connection.execute(
        "SELECT COUNT(*) AS count FROM assignments"
    ).fetchone()["count"]

    faculty = connection.execute(
        """
        SELECT id, name, email, subject
        FROM users
        WHERE role = 'faculty'
        ORDER BY name COLLATE NOCASE
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_dashboard.html",
        student_count=student_count,
        faculty_count=faculty_count,
        attendance_count=attendance_count,
        assignment_count=assignment_count,
        faculty=faculty
    )


# ============================================================
# ADMIN - ADD FACULTY
# ============================================================

@app.route("/admin/faculty/add", methods=["POST"])
def admin_add_faculty():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("student_dashboard"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "faculty").strip().lower()
    subject = request.form.get("subject", "").strip()

    allowed_subjects = [
        "Progressive Web App",
        "Software Engineering",
        "Deep Learning",
        "Natural Language Processing (NLP)",
        "Internet of Things (IoT)"
    ]

    if role not in ("faculty", "student"):
        flash("Invalid account type selected.", "danger")
        return redirect(url_for("admin_dashboard"))

    if role == "faculty" and subject not in allowed_subjects:
        flash("Please select a subject for the faculty member.", "danger")
        return redirect(url_for("admin_dashboard"))

    if not name or not email or not password:
        flash("Name, email and password are required.", "danger")
        return redirect(url_for("admin_dashboard"))

    if len(password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()

    existing = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if existing:
        connection.close()
        flash("Email is already registered.", "warning")
        return redirect(url_for("admin_dashboard"))

    connection.execute(
        """
        INSERT INTO users (name, email, password, role, subject)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            generate_password_hash(password),
            role,
            subject if role == "faculty" else None
        )
    )

    connection.commit()
    connection.close()

    account_name = "Faculty" if role == "faculty" else "Student"
    flash(f"{account_name} account created successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/faculty-announcements", methods=["GET", "POST"])
def admin_faculty_announcements():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("student_dashboard"))

    connection = get_db_connection()

    if request.method == "POST":
        faculty_id = request.form.get("faculty_id", "").strip()
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()

        if not faculty_id or not title or not message:
            connection.close()
            flash("Faculty, title and message are required.", "danger")
            return redirect(url_for("admin_faculty_announcements"))

        # "ALL" sends the same private announcement to every
        # currently registered faculty account.
        if faculty_id.upper() == "ALL":
            all_faculty = connection.execute(
                """
                SELECT id, name
                FROM users
                WHERE role = 'faculty'
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()

            if not all_faculty:
                connection.close()
                flash("No registered faculty accounts found.", "warning")
                return redirect(url_for("admin_faculty_announcements"))

            connection.executemany(
                """
                INSERT INTO faculty_announcements
                (faculty_id, title, message)
                VALUES (?, ?, ?)
                """,
                [(member["id"], title, message) for member in all_faculty]
            )

            connection.commit()
            connection.close()

            flash(
                f"Announcement sent to all {len(all_faculty)} registered faculty members.",
                "success"
            )
            return redirect(url_for("admin_faculty_announcements"))

        faculty = connection.execute(
            """
            SELECT id, name
            FROM users
            WHERE id = ? AND role = 'faculty'
            """,
            (faculty_id,)
        ).fetchone()

        if faculty is None:
            connection.close()
            flash("Selected faculty member was not found.", "danger")
            return redirect(url_for("admin_faculty_announcements"))

        connection.execute(
            """
            INSERT INTO faculty_announcements
            (faculty_id, title, message)
            VALUES (?, ?, ?)
            """,
            (faculty_id, title, message)
        )

        connection.commit()
        connection.close()

        flash(f"Announcement sent to {faculty['name']} successfully.", "success")
        return redirect(url_for("admin_faculty_announcements"))

    faculty = connection.execute(
        """
        SELECT id, name, email, subject
        FROM users
        WHERE role = 'faculty'
        ORDER BY name COLLATE NOCASE
        """
    ).fetchall()

    sent_announcements = connection.execute(
        """
        SELECT
            fa.id,
            fa.title,
            fa.message,
            fa.created_at,
            u.name AS faculty_name,
            u.email AS faculty_email
        FROM faculty_announcements fa
        JOIN users u ON u.id = fa.faculty_id
        ORDER BY fa.created_at DESC, fa.id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_faculty_announcements.html",
        faculty=faculty,
        sent_announcements=sent_announcements
    )


# ============================================================
# ADMIN - DELETE FACULTY
# ============================================================

@app.route("/admin/faculty/delete/<int:faculty_id>", methods=["POST"])
def admin_delete_faculty(faculty_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("student_dashboard"))

    connection = get_db_connection()

    faculty = connection.execute(
        """
        SELECT id, name
        FROM users
        WHERE id = ? AND role = 'faculty'
        """,
        (faculty_id,)
    ).fetchone()

    if faculty is None:
        connection.close()
        flash("Faculty account not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    connection.execute(
        "DELETE FROM users WHERE id = ? AND role = 'faculty'",
        (faculty_id,)
    )

    connection.commit()
    connection.close()

    flash(f"Faculty account '{faculty['name']}' deleted.", "success")
    return redirect(url_for("admin_dashboard"))


# ============================================================
# ADMIN - CHANGE FACULTY PASSWORD
# ============================================================

@app.route("/admin/faculty/password/<int:faculty_id>", methods=["POST"])
def admin_change_faculty_password(faculty_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("student_dashboard"))

    password = request.form.get("password", "").strip()

    if len(password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin_dashboard"))

    connection = get_db_connection()

    faculty = connection.execute(
        """
        SELECT id
        FROM users
        WHERE id = ? AND role = 'faculty'
        """,
        (faculty_id,)
    ).fetchone()

    if faculty is None:
        connection.close()
        flash("Faculty account not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    connection.execute(
        """
        UPDATE users
        SET password = ?
        WHERE id = ? AND role = 'faculty'
        """,
        (generate_password_hash(password), faculty_id)
    )

    connection.commit()
    connection.close()

    flash("Faculty password updated successfully.", "success")
    return redirect(url_for("admin_dashboard"))



# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/student-dashboard")
def student_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("role") != "student":

        return redirect(
            url_for("faculty_dashboard")
        )

    connection = get_db_connection()

    attendance_rows = connection.execute(
        """
        SELECT
            subject,
            COUNT(*) AS total,
            SUM(
                CASE
                    WHEN status = 'Present'
                    THEN 1
                    ELSE 0
                END
            ) AS present,
            SUM(
                CASE
                    WHEN status = 'Absent'
                    THEN 1
                    ELSE 0
                END
            ) AS absent

        FROM attendance

        WHERE student_id = ?

        GROUP BY subject

        ORDER BY subject
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    attendance = []

    total_classes = 0
    total_present = 0
    total_absent = 0

    for row in attendance_rows:

        total = row["total"]

        present = row["present"] or 0

        absent = row["absent"] or 0

        percentage = (
            present / total * 100
            if total > 0
            else 0
        )

        required_classes = max(
            0,
            3 * total - 4 * present
        )

        attendance.append({

            "subject": row["subject"],

            "total": total,

            "present": present,

            "absent": absent,

            "percentage": round(
                percentage,
                2
            ),

            "required_classes":
                required_classes

        })

        total_classes += total

        total_present += present

        total_absent += absent

    overall_percentage = (
        total_present /
        total_classes *
        100
        if total_classes > 0
        else 0
    )

    overall_required_classes = max(
        0,
        3 * total_classes -
        4 * total_present
    )

    return render_template(

        "student_dashboard.html",

        attendance=attendance,

        overall_percentage=round(
            overall_percentage,
            2
        ),

        total_present=total_present,

        total_absent=total_absent,

        total_classes=total_classes,

        overall_required_classes=
            overall_required_classes
    )


# ============================================================
# STUDENT ATTENDANCE
# ============================================================

@app.route("/attendance")
def student_attendance():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("faculty_dashboard"))

    canonical_subjects = [
        "Progressive Web App",
        "Software Engineering",
        "Deep Learning",
        "Natural Language Processing (NLP)",
        "Internet of Things (IoT)"
    ]

    connection = get_db_connection()

    rows = connection.execute(
        """
        SELECT
            subject,
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent
        FROM attendance
        WHERE student_id = ?
        GROUP BY subject
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    stored = {
        row["subject"]: {
            "total": row["total"],
            "present": row["present"] or 0,
            "absent": row["absent"] or 0
        }
        for row in rows
    }

    attendance = []

    for subject in canonical_subjects:
        data = stored.get(
            subject,
            {"total": 0, "present": 0, "absent": 0}
        )

        total = data["total"]
        present = data["present"]
        absent = data["absent"]

        percentage = present / total * 100 if total > 0 else 0
        required_classes = max(0, 3 * total - 4 * present) if total > 0 else 0

        attendance.append({
            "subject": subject,
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": round(percentage, 2),
            "required_classes": required_classes
        })

    total_classes = sum(item["total"] for item in attendance)
    total_present = sum(item["present"] for item in attendance)
    total_absent = sum(item["absent"] for item in attendance)

    overall_percentage = (
        total_present / total_classes * 100
        if total_classes > 0
        else 0
    )

    return render_template(
        "attendance.html",
        attendance=attendance,
        overall_percentage=round(overall_percentage, 2),
        total_classes=total_classes,
        total_present=total_present,
        total_absent=total_absent
    )


# ============================================================
# FACULTY DASHBOARD
# ============================================================

@app.route("/faculty-dashboard")
def faculty_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("role") != "faculty":

        return redirect(
            url_for("admin_dashboard")
            if session.get("role") == "admin"
            else url_for("student_dashboard")
        )

    connection = get_db_connection()

    student_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM users
        WHERE role = 'student'
        """
    ).fetchone()["count"]

    connection.close()

    return render_template(
        "faculty_dashboard.html",
        student_count=student_count
    )


# ============================================================
# FACULTY ATTENDANCE
# ============================================================

@app.route(
    "/faculty/attendance",
    methods=["GET", "POST"]
)
def faculty_attendance():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("role") != "faculty":

        return redirect(
            url_for("student_dashboard")
        )

    connection = get_db_connection()

    students = connection.execute(
        """
        SELECT
            id,
            name,
            email

        FROM users

        WHERE role = 'student'

        ORDER BY name
        """
    ).fetchall()

    if request.method == "POST":

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        attendance_date = request.form.get(
            "attendance_date",
            ""
        ).strip()

        if not subject or not attendance_date:

            connection.close()

            flash(
                "Please select subject and date.",
                "danger"
            )

            return render_template(
                "faculty_attendance.html",
                students=students,
                today=date.today().isoformat()
            )

        for student in students:

            status = request.form.get(
                f"status_{student['id']}",
                "Absent"
            )

            if status not in [
                "Present",
                "Absent"
            ]:

                status = "Absent"

            connection.execute(
                """
                INSERT INTO attendance
                (
                    student_id,
                    subject,
                    attendance_date,
                    status
                )

                VALUES (?, ?, ?, ?)

                ON CONFLICT(
                    student_id,
                    subject,
                    attendance_date
                )

                DO UPDATE SET
                    status = excluded.status
                """,
                (
                    student["id"],
                    subject,
                    attendance_date,
                    status
                )
            )

        connection.commit()

        connection.close()

        flash(
            "Attendance saved successfully.",
            "success"
        )

        return redirect(
            url_for("faculty_attendance")
        )

    connection.close()

    return render_template(
        "faculty_attendance.html",
        students=students,
        today=date.today().isoformat()
    )


# ============================================================
# FACULTY - STUDENT DATABASE
# ============================================================

@app.route("/faculty/students")
def faculty_students():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "faculty":
        return redirect(url_for("admin_dashboard") if session.get("role") == "admin" else url_for("student_dashboard"))

    connection = get_db_connection()

    students = connection.execute(
        """
        SELECT
            s.id,
            s.user_id,
            COALESCE(NULLIF(TRIM(s.register_no), ''), s.student_id) AS register_no,
            s.campus_id,
            s.phone,
            s.course,
            s.semester,
            s.batch,
            s.division,
            s.roll_number,
            s.date_of_birth,
            s.gender,
            s.address,
            u.name,
            u.email,
            COUNT(a.id) AS total_classes,
            COALESCE(
                SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END),
                0
            ) AS present,
            COALESCE(
                SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END),
                0
            ) AS absent
        FROM students s
        JOIN users u ON u.id = s.user_id
        LEFT JOIN attendance a ON a.student_id = s.user_id
        WHERE u.role = 'student'
        GROUP BY
            s.id, s.user_id, s.student_id, s.register_no, s.campus_id,
            s.phone, s.course, s.semester, s.batch, s.division,
            s.roll_number, s.date_of_birth, s.gender, s.address,
            u.name, u.email
        ORDER BY u.name COLLATE NOCASE
        """
    ).fetchall()

    connection.close()

    subjects = [
        "Progressive Web App",
        "Software Engineering",
        "Deep Learning",
        "Natural Language Processing (NLP)",
        "Internet of Things (IoT)"
    ]

    return render_template(
        "faculty_students.html",
        students=students,
        subjects=subjects
    )



# ============================================================
# FACULTY - ADD STUDENT
# ============================================================

@app.route("/faculty/students/add", methods=["GET", "POST"])
def faculty_add_student():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "faculty":
        return redirect(
            url_for("admin_dashboard")
            if session.get("role") == "admin"
            else url_for("student_dashboard")
        )

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        register_no = request.form.get("register_no", "").strip()
        campus_id = request.form.get("campus_id", "").strip()
        phone = request.form.get("phone", "").strip()
        course = request.form.get("course", "").strip()
        semester = request.form.get("semester", "").strip()
        batch = request.form.get("batch", "").strip()
        division = request.form.get("division", "").strip()
        roll_number = request.form.get("roll_number", "").strip()
        date_of_birth = request.form.get("date_of_birth", "").strip()
        gender = request.form.get("gender", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not email or not password:
            connection.close()
            flash("Name, email and password are required.", "danger")
            return redirect(url_for("faculty_add_student"))

        if len(password) < 6:
            connection.close()
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("faculty_add_student"))

        existing_user = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            connection.close()
            flash("Email is already registered.", "warning")
            return redirect(url_for("faculty_add_student"))

        try:
            cursor = connection.execute(
                """
                INSERT INTO users (name, email, password, role, subject)
                VALUES (?, ?, ?, 'student', NULL)
                """,
                (name, email, generate_password_hash(password))
            )

            user_id = cursor.lastrowid

            connection.execute(
                """
                INSERT INTO students (
                    user_id, student_id, register_no, campus_id, phone,
                    course, semester, batch, division, roll_number,
                    date_of_birth, gender, address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id, register_no, register_no, campus_id, phone,
                    course, semester, batch, division, roll_number,
                    date_of_birth, gender, address
                )
            )

            connection.commit()

        except sqlite3.IntegrityError:
            connection.rollback()
            connection.close()
            flash("Unable to create the student. The email or student profile may already exist.", "danger")
            return redirect(url_for("faculty_add_student"))

        connection.close()

        flash("Student account created successfully.", "success")
        return redirect(url_for("faculty_students"))

    connection.close()
    return render_template("faculty_add_student.html")


# ============================================================
# FACULTY / ADMIN - VIEW ONE STUDENT
# ============================================================

@app.route("/faculty/students/view/<int:student_id>")
def faculty_student_view(student_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "faculty":
        return redirect(url_for("admin_dashboard") if session.get("role") == "admin" else url_for("student_dashboard"))

    connection = get_db_connection()

    # student_id is the primary key from the students table.
    # Join students + users so the View page receives the complete profile.
    student = connection.execute(
        """
        SELECT
            s.id,
            s.user_id,
            COALESCE(NULLIF(TRIM(s.register_no), ''), s.student_id) AS register_no,
            s.student_id,
            s.campus_id,
            s.phone,
            s.course,
            s.semester,
            s.batch,
            s.division,
            s.roll_number,
            s.date_of_birth,
            s.gender,
            s.address,
            u.name,
            u.email
        FROM students s
        JOIN users u ON u.id = s.user_id
        WHERE s.id = ? AND u.role = 'student'
        """,
        (student_id,)
    ).fetchone()

    if student is None:
        connection.close()
        flash("Student details not found.", "danger")
        return redirect(url_for("faculty_students"))

    attendance_rows = connection.execute(
        """
        SELECT
            subject,
            COUNT(*) AS total,
            COALESCE(
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END),
                0
            ) AS present,
            COALESCE(
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END),
                0
            ) AS absent
        FROM attendance
        WHERE student_id = ?
        GROUP BY subject
        ORDER BY subject
        """,
        (student["user_id"],)
    ).fetchall()

    connection.close()

    attendance = []

    for row in attendance_rows:
        total = row["total"] or 0
        present = row["present"] or 0
        absent = row["absent"] or 0

        percentage = (
            present / total * 100
            if total > 0
            else 0
        )

        attendance.append({
            "subject": row["subject"],
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": round(percentage, 2)
        })

    total_classes = sum(item["total"] for item in attendance)
    total_present = sum(item["present"] for item in attendance)
    total_absent = sum(item["absent"] for item in attendance)

    overall_percentage = (
        total_present / total_classes * 100
        if total_classes > 0
        else 0
    )

    return render_template(
        "faculty_student_view.html",
        student=student,
        attendance=attendance,
        total_classes=total_classes,
        total_present=total_present,
        total_absent=total_absent,
        overall_percentage=round(overall_percentage, 2)
    )


# ============================================================
# STUDENT PROFILE
# ============================================================

@app.route("/student/profile")
def student_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("faculty_dashboard"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT
            u.id AS user_id,
            u.name,
            u.email,
            COALESCE(NULLIF(TRIM(s.register_no), ''), s.student_id) AS register_no,
            s.campus_id,
            s.phone,
            s.course,
            s.semester,
            s.batch,
            s.division,
            s.roll_number,
            s.date_of_birth,
            s.gender,
            s.address
        FROM users u
        LEFT JOIN students s ON s.user_id = u.id
        WHERE u.id = ? AND u.role = 'student'
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    if student is None:
        session.clear()
        flash("Student account not found.", "danger")
        return redirect(url_for("login"))

    return render_template(
        "student_profile.html",
        student=student,
        subjects=["IoT", "SE", "NLP", "PWA", "DL"]
    )


# ============================================================
# TIMETABLE
# ============================================================

@app.route("/timetable")
def student_timetable():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("role") != "student":

        return redirect(
            url_for("faculty_dashboard")
        )

    today_name = datetime.now().strftime(
        "%A"
    )

    return render_template(
        "timetable.html",
        timetable=timetable,
        today_name=today_name
    )


# ============================================================
# ASSIGNMENTS
# ============================================================

@app.route("/assignments")
def student_assignments():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("faculty_dashboard"))

    connection = get_db_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM assignments
        ORDER BY
            CASE WHEN deadline_date IS NULL THEN 1 ELSE 0 END,
            deadline_date
        """
    ).fetchall()

    connection.close()

    assignment_list = []

    for row in rows:
        questions = [
            question.strip()
            for question in (row["questions"] or "").split("\n")
            if question.strip()
        ]

        deadline_display = ""
        if row["deadline_date"]:
            deadline_display = datetime.strptime(
                row["deadline_date"], "%Y-%m-%d"
            ).strftime("%d-%m-%Y")

        assignment_list.append({
            "id": row["id"],
            "subject": row["subject"],
            "short_subject": row["subject"],
            "title": row["title"],
            "deadline": deadline_display,
            "deadline_date": row["deadline_date"] or "",
            "total_questions": len(questions),
            "questions": questions,
            "status": get_assignment_status(row["deadline_date"])
        })

    return render_template(
        "assignments.html",
        assignments=assignment_list
    )


# ============================================================
# FACULTY ASSIGNMENT MANAGEMENT
# ============================================================

@app.route("/faculty/assignments", methods=["GET", "POST"])
def faculty_assignments():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "faculty":
        return redirect(url_for("admin_dashboard") if session.get("role") == "admin" else url_for("student_dashboard"))

    connection = get_db_connection()

    if request.method == "POST":

        subject = request.form.get("subject", "").strip()
        title = request.form.get("title", "").strip()
        deadline_date = request.form.get("deadline_date", "").strip()
        questions = request.form.get("questions", "").strip()

        if not subject or not title:
            flash("Subject and assignment title are required.", "danger")
        else:
            connection.execute(
                """
                INSERT INTO assignments
                (subject, title, deadline_date, questions, created_by)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    subject,
                    title,
                    deadline_date or None,
                    questions,
                    session["user_id"]
                )
            )
            connection.commit()
            flash("Assignment added successfully.", "success")

    rows = connection.execute(
        """
        SELECT *
        FROM assignments
        ORDER BY
            CASE WHEN deadline_date IS NULL THEN 1 ELSE 0 END,
            deadline_date
        """
    ).fetchall()

    connection.close()

    assignment_list = []
    for row in rows:
        questions = [
            question.strip()
            for question in (row["questions"] or "").split("\n")
            if question.strip()
        ]
        assignment_list.append({
            "id": row["id"],
            "subject": row["subject"],
            "title": row["title"],
            "deadline_date": row["deadline_date"] or "",
            "questions": questions
        })

    return render_template(
        "faculty_assignments.html",
        assignments=assignment_list
    )


@app.route("/faculty/assignments/edit/<int:assignment_id>", methods=["GET", "POST"])
def faculty_assignment_edit(assignment_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "faculty":
        return redirect(url_for("admin_dashboard") if session.get("role") == "admin" else url_for("student_dashboard"))

    connection = get_db_connection()

    assignment = connection.execute(
        "SELECT * FROM assignments WHERE id = ?",
        (assignment_id,)
    ).fetchone()

    if assignment is None:
        connection.close()
        flash("Assignment not found.", "danger")
        return redirect(url_for("faculty_assignments"))

    if request.method == "POST":

        subject = request.form.get("subject", "").strip()
        title = request.form.get("title", "").strip()
        deadline_date = request.form.get("deadline_date", "").strip()
        questions = request.form.get("questions", "").strip()

        if not subject or not title:
            connection.close()
            flash("Subject and assignment title are required.", "danger")
            return render_template(
                "faculty_assignment_edit.html",
                assignment=assignment
            )

        connection.execute(
            """
            UPDATE assignments
            SET subject = ?,
                title = ?,
                deadline_date = ?,
                questions = ?,
                created_by = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                subject,
                title,
                deadline_date or None,
                questions,
                session["user_id"],
                assignment_id
            )
        )

        connection.commit()
        connection.close()

        flash("Assignment updated successfully.", "success")
        return redirect(url_for("faculty_assignments"))

    connection.close()

    return render_template(
        "faculty_assignment_edit.html",
        assignment=assignment
    )



# ============================================================
# FACULTY ANNOUNCEMENTS
# ============================================================

@app.route("/faculty/announcements")
def faculty_announcements():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "faculty":
        return redirect(
            url_for("admin_dashboard")
            if session.get("role") == "admin"
            else url_for("student_dashboard")
        )

    connection = get_db_connection()

    faculty_announcements = connection.execute(
        """
        SELECT id, title, message, created_at
        FROM faculty_announcements
        WHERE faculty_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "faculty_announcements.html",
        announcements=faculty_announcements
    )


# ============================================================
# ANNOUNCEMENTS
# ============================================================

announcements = [
    {
        "title": "Last Working Day",
        "date": "24 October 2026",
        "date_sort": "2026-10-24",
        "message": "24 October 2026 is the last working day.",
        "type": "Important"
    },
    {
        "title": "Semester Examination Starts",
        "date": "12 November 2026",
        "date_sort": "2026-11-12",
        "message": "Semester examinations start on 12 November 2026.",
        "type": "Important"
    }
]


@app.route("/announcements")
def student_announcements():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "student":
        return redirect(url_for("faculty_dashboard"))

    sorted_announcements = sorted(
        announcements,
        key=lambda item: item["date_sort"]
    )

    return render_template(
        "announcements.html",
        announcements=sorted_announcements
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True
    )
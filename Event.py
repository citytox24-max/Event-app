import flet as ft
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect("events.db")
c = conn.cursor()

# tables for database
c.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    date TEXT,
    time TEXT,
    venue TEXT,
    capacity INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    event_id INTEGER,
    registration_date TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    user_email TEXT,
    rating INTEGER,
    comment TEXT,
    feedback_date TEXT
)
""")
conn.commit()


c.execute("SELECT COUNT(*) FROM events")
if c.fetchone()[0] == 0:
    events_data = [
        ("Tech Conference", "A conference on latest tech trends", "2026-03-15", "10:00 AM", "Nairobi Convention Center", 100),
        ("Startup Meetup", "Networking for entrepreneurs", "2026-03-20", "2:00 PM", "Westlands Hub", 50),
    ]
    c.executemany("INSERT INTO events (name, description, date, time, venue, capacity) VALUES (?, ?, ?, ?, ?, ?)", events_data)
    conn.commit()

# main UI
def main(page: ft.Page):
    page.title = "Smart Event Registration"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    def show_confirmation(name, event_name):
        page.dialog = ft.AlertDialog(
            title=ft.Text("Registration Successful!"),
            content=ft.Column([
                ft.Text(f"Thank you {name}"),
                ft.Text(f"You are registered for {event_name}")
            ]),
            actions=[ft.TextButton("Close", on_click=lambda e: page.dialog.close())]
        )
        page.dialog.open = True
        page.update()

    def register_event(e):
        selected_event_id = int(event_dropdown.value)
        name = name_input.value.strip()
        email = email_input.value.strip()
        phone = phone_input.value.strip()
        if not name or not email or not phone:
            status_text.value = "All fields are required."
            page.update()
            return
        c.execute("INSERT INTO registrations (name, email, phone, event_id, registration_date) VALUES (?, ?, ?, ?, ?)",
                  (name, email, phone, selected_event_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        
        c.execute("SELECT name FROM events WHERE id=?", (selected_event_id,))
        event_name = c.fetchone()[0]
        show_confirmation(name, event_name)
        status_text.value = ""
        page.update()

    def submit_feedback(e):
        event_id = int(feedback_event_dropdown.value)
        user_email = feedback_email.value.strip()
        rating = int(rating_input.value)
        comment = feedback_comment.value.strip()
        if not user_email or not comment:
            feedback_status.value = "Email and comment required."
            page.update()
            return
        c.execute("INSERT INTO feedback (event_id, user_email, rating, comment, feedback_date) VALUES (?, ?, ?, ?, ?)",
                  (event_id, user_email, rating, comment, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        feedback_status.value = "Feedback submitted successfully!"
        feedback_email.value = ""
        rating_input.value = "5"
        feedback_comment.value = ""
        page.update()

    def refresh_events_list():
        c.execute("SELECT id, name, date, time, venue FROM events")
        events = c.fetchall()
        event_cards.controls.clear()
        event_dropdown.options.clear()
        feedback_event_dropdown.options.clear()
        for e_id, e_name, e_date, e_time, e_venue in events:
            event_cards.controls.append(ft.Card(
                content=ft.Column([
                    ft.Text(e_name, weight="bold"),
                    ft.Text(f"{e_date} at {e_time}"),
                    ft.Text(f"Venue: {e_venue}"),
                ]),
                elevation=3,
                margin=ft.Margin(5,5,5,5)
            ))
            event_dropdown.options.append(ft.dropdown.Option(str(e_id), e_name))
            feedback_event_dropdown.options.append(ft.dropdown.Option(str(e_id), e_name))
        event_cards.update()
        event_dropdown.update()
        feedback_event_dropdown.update()

    # UI Components
    page.add(ft.Text("Register for Event", size=20, weight="bold"))
    name_input = ft.TextField(label="Name")
    email_input = ft.TextField(label="Email")
    phone_input = ft.TextField(label="Phone")
    event_dropdown = ft.Dropdown(label="Select Event")
    status_text = ft.Text("", color="red")
    register_btn = ft.ElevatedButton("Register", on_click=register_event)

    page.add(ft.Column([name_input, email_input, phone_input, event_dropdown, register_btn, status_text]))

    page.add(ft.Divider())

    page.add(ft.Text("Event Details", size=20, weight="bold"))
    event_cards = ft.Column()
    page.add(event_cards)

    page.add(ft.Divider())

    page.add(ft.Text("Submit Feedback", size=20, weight="bold"))
    feedback_event_dropdown = ft.Dropdown(label="Select Event")
    feedback_email = ft.TextField(label="Your Email")
    rating_input = ft.TextField(label="Rating (1-5)", value="5")
    feedback_comment = ft.TextField(label="Comment", multiline=True)
    feedback_status = ft.Text("", color="green")
    feedback_btn = ft.ElevatedButton("Submit Feedback", on_click=submit_feedback)
    page.add(ft.Column([feedback_event_dropdown, feedback_email, rating_input, feedback_comment, feedback_btn, feedback_status]))

    refresh_events_list()

if __name__ == "__main__":
    ft.app(target=main)

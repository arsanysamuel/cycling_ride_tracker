import os
import datetime
import sqlite3

from helpers import dict_factory

class DB():
    def __init__(self, db_filename ="database.db"):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_filename)

        # Check if database doesn't exist, create the database
        if not os.path.exists(self.db_path):
            self.create_database()

    def create_database(self):
        """ Create database tables """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        rides INTEGER DEFAULT 0
                    )
                    """)
            cur.execute("""
                    CREATE TABLE rides (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        user_id INTEGER NOT NULL,
                        title TEXT,
                        start_time INTEGER NOT NULL,
                        end_time INTEGER,
                        total_time INTEGER,
                        moving_time INTEGER,
                        distance REAL,
                        avg_speed REAL,
                        max_speed REAL,
                        notes TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                    """)
            cur.execute("""
                    CREATE TABLE points (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        ride_id INTEGER NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        timestamp INTEGER NOT NULL,
                        speed REAL,
                        FOREIGN KEY(ride_id) REFERENCES rides(id)
                    )
                    """)
            conn.commit()

    def get_user(self, username):
        """ Query for user info """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            user = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return user

    def add_user(self, username, pass_hash):
        """ Add new user to database """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,pass_hash,))
            conn.commit()
            return cur.lastrowid

    def add_ride(self, ride, user_id):
        """ Log ride dict into database """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            cur.execute("UPDATE users SET rides = rides + 1")  # Increment user rides

            # Processing some ride info
            start_time = int(ride["pts"][0]["timestamp"])
            end_time = int(ride["pts"][-1]["timestamp"])
            speeds = [float(pt["speed"]) for pt in ride["pts"]]
            avg_speed = round(sum(speeds) / len(speeds), 1)
            max_speed = max(speeds)
            ride_title = ride["title"]
            if not ride["title"] or len(ride["title"]) == 0:  # If the user didn't provide a ride title
                hour = datetime.datetime.fromtimestamp(start_time / 1000).hour  # JS to UNIX epochs
                if hour in [23, 0, 2]:
                    ride_title = "Midnight ride"
                elif hour in range(3, 7):
                    ride_title = "Dawn ride"
                elif hour in range (7, 11):
                    ride_title = "Morning ride"
                elif hour in range(11, 14):
                    ride_title = "Noon ride"
                elif hour in range(11, 19):
                    ride_title = "Afternoon ride"
                elif hour in range(19, 23):
                    ride_title = "Evening ride"

            # Add ride to rides table
            cur.execute("""
                        INSERT INTO rides (user_id, title, start_time, end_time, total_time, moving_time, distance, avg_speed, max_speed, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (user_id, ride_title, start_time, end_time, ride["totalSec"], ride["movingSec"], ride["distance"], avg_speed, max_speed, ride["notes"]))
            ride_id = cur.lastrowid

            # Add route points
            for pt in ride["pts"]:
                cur.execute("""
                            INSERT INTO points (ride_id, latitude, longitude, timestamp, speed) VALUES (?, ?, ?, ?, ?)
                            """, (ride_id, pt["latitude"], pt["longitude"], pt["timestamp"], pt["speed"]))

            conn.commit()

    def get_history(self, user_id):
        """ Get all rides history for listing """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            rides = cur.execute("SELECT id, title, start_time FROM rides WHERE user_id = ?", (user_id,)).fetchall()
            return rides

    def get_ride(self, ride_id):
        """ Get ride data and route points using the ride id """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = dict_factory
            cur = conn.cursor()
            ride = cur.execute("SELECT * FROM rides WHERE id = ?", (ride_id,)).fetchone()
            ride["pts"] = cur.execute("SELECT * FROM points WHERE ride_id = ?", (ride_id,)).fetchall()
            return ride


import datetime
from functools import wraps

from flask import session, redirect


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/2.2.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def epochs_to_datetime(epochs):
    """ JINJA filter: Convert UNIX epochs to datetime format """
    x = datetime.datetime.fromtimestamp(epochs / 1000)  # Geolocation stores epochs in milliseconds
    return x.strftime("%I:%M%p - %a %d %b %Y")  # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

def dict_factory(cursor, row):
    """
    Convert sqlite query rows lists to dictionaries
    https://docs.python.org/3/library/sqlite3.html#how-to-create-and-use-row-factories
    """
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def format_time(s):
    """ JINJA filter: Convert number of seconds to formatted time """
    hr = int(int(s) / 3600)
    min = int(int(s) / 60)
    sec = int(int(s) % 60)
    return f"{hr:02d}:{min:02d}:{sec:02d}"


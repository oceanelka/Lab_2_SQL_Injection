import sqlite3
import os
from abc import ABC, abstractmethod


SORT_COLUMNS = {"1": "year", "2": "title", "3": "technique_type"}


def initialise_database(path="data.db"):
    """
    Create the database tables and seed data if they do not already exist.

    Checks whether the data.db file already exists before doing anything.
    If it does, returns immediately. Otherwise creates the phreakers and
    techniques tables and inserts the default seed records.

    Parameters:
        path -- path to the SQLite database file (default 'data.db')
    """
    if os.path.exists(path):
        return
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE phreakers (
            id INTEGER PRIMARY KEY,
            handle TEXT NOT NULL,
            password TEXT NOT NULL,
            region TEXT,
            joined INTEGER
        );
        CREATE TABLE techniques (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            technique_type TEXT,
            target_system TEXT,
            year INTEGER,
            submitted_by INTEGER,
            submitted_by_handle TEXT
        );
        INSERT INTO phreakers VALUES (1,'capn_static','tone99','midwest',1987);
        INSERT INTO phreakers VALUES (2,'bluebox_88','bell123','west_coast',1988);
        INSERT INTO phreakers VALUES (3,'ringmaster','pbx456','east_coast',1985);
        INSERT INTO phreakers VALUES (4,'dial_ghost','trunk77','south',1991);
        INSERT INTO techniques VALUES (1,'2600 Hz Trunk Seizure','tone_signaling','AT&T long distance',1971,1,'capn_static');
        INSERT INTO techniques VALUES (2,'Red Box Payphone Bypass','hardware','Bell payphone',1982,1,'capn_static');
        INSERT INTO techniques VALUES (3,'Lineman Handset Tap','hardware','outside plant',1984,1,'capn_static');
        INSERT INTO techniques VALUES (4,'Blue Box MF Signaling','tone_signaling','AT&T long distance',1968,2,'bluebox_88');
        INSERT INTO techniques VALUES (5,'PBX Default Credentials','social_engineering','PBX system',1986,2,'bluebox_88');
        INSERT INTO techniques VALUES (6,'SF Signaling on International Trunks','tone_signaling','international gateway',1973,2,'bluebox_88');
        INSERT INTO techniques VALUES (7,'Dumpster Dive for Internal Docs','social_engineering','Bell operating company',1983,3,'ringmaster');
        INSERT INTO techniques VALUES (8,'Loop Around Test Lines','trunk_manipulation','local exchange',1979,3,'ringmaster');
        INSERT INTO techniques VALUES (9,'Tandem Switch Exploitation','trunk_manipulation','AT&T tandem',1975,3,'ringmaster');
        INSERT INTO techniques VALUES (10,'ANI Spoofing via Operator','social_engineering','operator services',1988,4,'dial_ghost');
        INSERT INTO techniques VALUES (11,'COCOT Vulnerability Survey','hardware','independent payphone',1991,4,'dial_ghost');
        INSERT INTO techniques VALUES (12,'Voice Mailbox Social Engineering','social_engineering','voicemail system',1990,4,'dial_ghost');
    """)
    conn.commit()
    conn.close()


class DatabaseConnection:
    """
    Manages a single shared connection to the SQLite database.

    Uses the Singleton pattern so only one connection is created for the
    lifetime of the application.
    """
    _instance = None

    def __new__(cls, path="data.db"):
        """
        Return the existing instance if one exists, otherwise create a new one
        and open the database connection.

        Parameters:
            path -- path to the SQLite database file (default 'data.db')
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = sqlite3.connect(path)
            cls._instance._conn.row_factory = sqlite3.Row
        return cls._instance

    def execute(self, query, params=()):
        """
        Run an INSERT, UPDATE, or DELETE query and commit the change.

        Parameters:
            query  -- the SQL query string, using ? placeholders for values
            params -- a tuple of values to substitute into the query
        """
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        self._conn.commit()

    def fetchall(self, query, params=()):
        """
        Run a SELECT query and return all matching rows.

        Returns a list of Row objects that can be accessed like dicts.

        Parameters:
            query  -- the SQL query string, using ? placeholders for values
            params -- a tuple of values to substitute into the query
        """
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


class Repository(ABC):
    """
    Base class for all repository classes.

    Provides a shared database connection and defines the interface that all
    repositories must implement.
    """
    def __init__(self, db):
        """
        Store the database connection for use by subclass methods.

        Parameters:
            db -- a DatabaseConnection instance
        """
        self._db = db

    @abstractmethod
    def find_by_id(self, record_id):
        """Look up and return records matching the given primary key."""
        pass

    @abstractmethod
    def search(self, term):
        """Search records by a given term and return matching results."""
        pass


class PhreakerRepository(Repository):
    """Handles all database operations for the phreakers table."""

    def login(self, handle, password):
        """
        Look up a phreaker by handle and password and return the matching row.

        Returns the first matching row as a Row object if credentials match,
        or None if no match is found or a database error occurs.

        Parameters:
            handle   -- the submitted handle string
            password -- the submitted plain text password string
        """
        query = "SELECT * FROM phreakers WHERE handle = ? AND password =?"
        try:
            results = self._db.fetchall(query, (handle,password))
            return results[0] if results else None
        except Exception as e:
            print(f"[DB ERROR] {e}")
            return None

    def find_by_id(self, record_id):
        """
        Return all phreaker records matching the given ID.

        Parameters:
            record_id -- the integer primary key of the phreaker
        """
        return self._db.fetchall(
            "SELECT * FROM phreakers WHERE id = ?", (record_id,)
        )

    def search(self, term):
        """
        Return phreakers whose handle contains the given term.

        Returns only handle, region, and joined columns.

        Parameters:
            term -- the search string to match against phreaker handles
        """
        return self._db.fetchall(
            "SELECT handle, region, joined FROM phreakers WHERE handle LIKE ?",
            ("%" + term + "%",)
        )

    def _build_region_update(self, region, user_id):
        """
        Build the UPDATE query string for changing a phreaker's region.

        Parameters:
            region  -- the new region string
            user_id -- the integer primary key of the phreaker to update
        """
        return f"UPDATE phreakers SET region = '{region}' WHERE id = {user_id}"

    def update_region(self, region, user_id):
        """
        Update the region field for the phreaker with the given ID.

        Parameters:
            region  -- the new region string
            user_id -- the integer primary key of the phreaker to update
        """
        query = self._build_region_update(region, user_id)
        self._db.execute(query, ())


class TechniqueRepository(Repository):
    """Handles all database operations for the techniques table."""

    def find_by_id(self, record_id):
        """
        Return all technique records matching the given ID.

        Parameters:
            record_id -- the technique ID string as entered by the user
        """
        query = "SELECT * FROM techniques WHERE id = ? "
        try:
            return self._db.fetchall(query, (record_id,))
        except Exception:
            return []

    def search(self, term):
        """
        Return techniques whose title contains the given search term.

        Parameters:
            term -- the search string to match against technique titles
        """
        return self._db.fetchall(
            "SELECT * FROM techniques WHERE title LIKE ?",
            ("%" + term + "%",)
        )

    def find_by_handle(self, handle, sort_col="year"):
        """
        Return all techniques submitted by the phreaker with the given handle.

        The results are sorted by the given column. The sort_col value is
        concatenated directly into the ORDER BY clause.

        Parameters:
            handle   -- the handle string of the submitting phreaker
            sort_col -- the column name string to sort by (default 'year')
        """
        query = ("SELECT * FROM techniques WHERE submitted_by_handle = ? ORDER BY "
                 + sort_col)
        return self._db.fetchall(query, (handle,))

    def find_by_user_id(self, user_id):
        """
        Return all techniques submitted by the phreaker with the given user ID.

        Parameters:
            user_id -- the integer primary key of the submitting phreaker
        """
        return self._db.fetchall(
            "SELECT * FROM techniques WHERE submitted_by = ?", (user_id,)
        )

    def find_by_type(self, technique_type):
        """
        Return all techniques matching the given type.

        Parameters:
            technique_type -- the technique type string to filter by
        """
        query = f"SELECT * FROM techniques WHERE technique_type = ? "
        return self._db.fetchall(query, (technique_type,))

    def find_by_era(self, year):
        """
        Return all techniques from the given year.

        Parameters:
            year -- the year value as entered by the user
        """
        return self._db.fetchall(
            "SELECT * FROM techniques WHERE year = ?", (year,)
        )

    def get_sorted(self, user_id):
        """
        Return all techniques submitted by the given user, sorted by year descending.

        Parameters:
            user_id -- the integer primary key of the submitting phreaker
        """
        return self._db.fetchall(
            "SELECT * FROM techniques WHERE submitted_by = ? ORDER BY year DESC",
            (user_id,)
        )


class App:
    """
    The main application class.

    Manages the top-level menu loop and delegates to sub-menus for browsing
    and account management. Holds the current logged-in user in state.
    """

    def __init__(self):
        """Set up the database connection and repository instances."""
        db = DatabaseConnection()
        self._phreakers = PhreakerRepository(db)
        self._techniques = TechniqueRepository(db)
        self._current_user = None

    def _header(self):
        """Print the application header with the current login status."""
        print("\n" + "=" * 32)
        print("  PHREAK ARCHIVE v1.0")
        if self._current_user:
            print(f"  [CONNECTED AS: {self._current_user['handle']}]")
        else:
            print("  [CONNECTED - NOT LOGGED IN]")
        print("=" * 32)

    def _print_results(self, rows):
        """
        Print a list of database rows to the console.

        Prints each row as a pipe-separated line. Prints 'No results.'
        if the list is empty or None.

        Parameters:
            rows -- a list of Row objects to display
        """
        if not rows:
            print("  No results.")
            return
        for row in rows:
            print("  " + "  |  ".join(str(value) for value in row))

    def _require_login(self):
        """
        Check that a user is logged in.

        Prints an error message and returns False if no user is logged in.
        Returns True if a user is present in the session.
        """
        if not self._current_user:
            print("You must be logged in to access this area.")
            return False
        return True

    def _handle_login(self):
        """
        Prompt for credentials and attempt to log in.

        On success, stores the user row in self._current_user and prints
        a welcome message. On failure, prints an error.
        """
        handle = input("Handle: ").strip()
        password = input("Password: ").strip()
        user = self._phreakers.login(handle, password)
        if user:
            self._current_user = user
            print(f"Access granted. Welcome, {user['handle']}.")
        else:
            print("Invalid credentials.")

    def _browse_menu(self):
        """
        Run the browse archive sub-menu loop.

        Presents options to search, filter, and view techniques. Returns
        to the main menu when the user selects Back.
        """
        while True:
            print("\n-- BROWSE ARCHIVE --")
            print("1. Search techniques")
            print("2. Browse by type")
            print("3. Browse by era")
            print("4. Look up by ID")
            print("5. View a phreaker's submissions")
            print("6. Back")
            choice = input("> ").strip()
            if choice == "1":
                term = input("Search term: ").strip()
                self._print_results(self._techniques.search(term))
            elif choice == "2":
                print("Types: tone_signaling / hardware / social_engineering / trunk_manipulation")
                technique_type = input("Type: ").strip()
                self._print_results(self._techniques.find_by_type(technique_type))
            elif choice == "3":
                year = input("Year: ").strip()
                self._print_results(self._techniques.find_by_era(year))
            elif choice == "4":
                id_input = input("Technique ID: ").strip()
                self._print_results(self._techniques.find_by_id(id_input))
            elif choice == "5":
                handle = input("Phreaker handle: ").strip()
                print("Sort by:")
                print("  1. Year")
                print("  2. Title")
                print("  3. Technique type")
                sort_choice = input("> ").strip()
                sort_col = SORT_COLUMNS.get(sort_choice, sort_choice)
                self._print_results(self._techniques.find_by_handle(handle, sort_col))
            elif choice == "6":
                break
            else:
                print("Invalid option.")

    def _account_menu(self):
        """
        Run the account management sub-menu loop.

        Requires login. Presents options to view profile, submissions,
        update region, and sort submissions. Returns to the main menu
        when the user selects Back.
        """
        if not self._require_login():
            return
        while True:
            print("\n-- MY ACCOUNT --")
            print("1. View my profile")
            print("2. My submissions")
            print("3. Update my region")
            print("4. Sort my submissions")
            print("5. Back")
            choice = input("> ").strip()
            if choice == "1":
                self._print_results(self._phreakers.find_by_id(self._current_user["id"]))
            elif choice == "2":
                self._print_results(self._techniques.find_by_user_id(self._current_user["id"]))
            elif choice == "3":
                region = input("New region: ").strip()
                self._phreakers.update_region(region, self._current_user["id"])
                print("Region updated.")
            elif choice == "4":
                self._print_results(self._techniques.get_sorted(self._current_user["id"]))
            elif choice == "5":
                break
            else:
                print("Invalid option.")

    def run(self):
        """
        Run the main application loop.

        Displays the header and top-level menu on each iteration.
        Exits when the user selects option 4.
        """
        while True:
            self._header()
            print("1. Log in")
            print("2. Browse archive")
            print("3. My account")
            print("4. Exit")
            choice = input("> ").strip()
            if choice == "1":
                self._handle_login()
            elif choice == "2":
                self._browse_menu()
            elif choice == "3":
                self._account_menu()
            elif choice == "4":
                print("Disconnecting.")
                break
            else:
                print("Invalid option.")


if __name__ == "__main__":
    initialise_database()
    print("=" * 60)
    print("  PHREAK ARCHIVE v1.0")
    print("  Telephone phreaking flourished from the late 1960s")
    print("  through the 1980s. Practitioners discovered that")
    print("  audio tones could manipulate AT&T switching systems,")
    print("  granting access to restricted lines and free long-")
    print("  distance calls. Findings were shared in trusted")
    print("  circles through printed newsletters and BBS systems.")
    print("=" * 60)
    print()
    App().run()
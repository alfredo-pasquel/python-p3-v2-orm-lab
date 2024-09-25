from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        if not isinstance(year, int) or year < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000.")
        if not summary or not isinstance(summary, str):
            raise ValueError("Summary must be a non-empty string.")
        sql = "SELECT * FROM employees WHERE id = ?"
        employee = CURSOR.execute(sql, (employee_id,)).fetchone()
        if not employee:
            raise ValueError("Invalid employee_id.")
        self._validate_employee_id(employee_id)
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )
    
    def _validate_employee_id(self, employee_id):
        """Helper method to validate that employee_id exists in employees table."""
        sql = "SELECT * FROM employees WHERE id = ?"
        employee = CURSOR.execute(sql, (employee_id,)).fetchone()
        if not employee:
            raise ValueError(f"Invalid employee_id: {employee_id}")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, new_employee_id):
        """Setter for employee_id with validation."""
        self._validate_employee_id(new_employee_id)
        self._employee_id = new_employee_id

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

        # Clear the cache when a new table is created
        cls.all = {}

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

        # Clear the cache when the table is dropped
        cls.all = {}

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        if self.id:
            sql = '''
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
            '''
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        else:
            sql = '''
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
            '''
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid  # Get the last inserted ID

        CONN.commit()
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        review_id = row[0]
        if review_id in cls.all:
            return cls.all[review_id]
        review = cls(row[1], row[2], row[3], review_id)
        cls.all[review_id] = review
        return review
   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None


    def update(self):
        """Update the table row corresponding to the current Review instance."""
        pass

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        Review.all.pop(self.id, None)
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

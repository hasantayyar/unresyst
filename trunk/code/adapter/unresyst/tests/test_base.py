"""The base classes for the tests used in unresyst"""

from django.test import TestCase

class DBTestCase(TestCase):
    """A base class for all tests which need database testing data"""

    def setUp(self):
        """Insert data into the database"""

        # insert test data
        from demo.save_data import save_data
        save_data()

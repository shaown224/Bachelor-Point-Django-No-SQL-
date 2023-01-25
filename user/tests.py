from django.test import TestCase

import unittest
from .views import *

class TestConnection(unittest.TestCase):

    connection = None

    def setUp(self):
        DBConnect
        self.connection = mysql.connector.connect(**config)

    def tearDown(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()

    def test_connection(self):
        self.assertTrue(self.connection.is_connected())
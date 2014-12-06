# Create your tests here.
from django.test.simple import DjangoTestSuiteRunner
from django.test import TestCase
from mongoengine import connect
from mongoengine import connect

class NoSQLTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self):
         global _running_test
         _running_test = True
         db_name = 'testsuite'
         connect(db_name)
         print 'Creating test-database: ' + db_name
         return db_name
    def teardown_databases(self, *args):
        pass

class NoSQLTestCase(TestCase):
    def _fixture_setup(self):
        pass
    def _fixture_teardown(self):
        pass
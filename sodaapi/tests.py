from django.test import TestCase
from sodaapi import api


# For a real app I'd probably mock out the api and such
# but for now just making sure I'm getting back the fields
# I expect should suffice

class ApiTests(TestCase):
    def test_data_retrieved(self):
        data = api.get_crime_data()
        self.assertIsNotNone(data)
        self.assertListEqual(
            ['cad_cdw_id', 'event_clearance_date', 'event_clearance_group'],
            data[1],
            msg="Response list did not have the expected columns"
            )



class ViewTests(TestCase):
    def test_view(self):
        self.assertTrue(False)

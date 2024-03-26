import os,sys
import unittest
import requests
from unittest.mock import patch


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)

from alg_resolve_address import lookup_address_google  # Replace 'your_module' with the actual name of your module


#0v1# JC  Jan 21, 2024  Basic test

"""
"""


class TestLookupAddressGoogle(unittest.TestCase):

    @patch('alg_resolve_address.requests.get')
    def test_valid_address(self, mock_get):
        # Mock a successful API response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "geometry": {
                        "location": {
                            "lat": 37.4224764,
                            "lng": -122.0842499
                        }
                    },
                    "formatted_address": "1600 Amphitheatre Parkway, Mountain View, CA",
                    "place_id": "ChIJ2eUgeAK6j4ARbn5u_wAGqWA"
                }
            ]
        }

        # Test with a valid address
        place, meta = lookup_address_google("1600 Amphitheatre Parkway, Mountain View, CA")
        self.assertIsNotNone(place)
        self.assertTrue(meta['is_like_address'])
        self.assertEqual(place['lat'], 37.4224764)
        self.assertEqual(place['lng'], -122.0842499)

    @patch('alg_resolve_address.requests.get')
    def test_invalid_address(self, mock_get):
        # Mock a failed API response
        mock_response = mock_get.return_value
        mock_response.status_code = 404
        mock_response.json.return_value = {"results": []}

        # Test with an invalid address
        place, meta = lookup_address_google("Invalid Address")
        self.assertFalse(place)
        self.assertFalse(meta['is_like_address'])

    # Additional tests can be written for other scenarios like exceptions, network issues, etc.


    def test_real_request_valid_address(self):
        # Use a known valid address
        place, meta = lookup_address_google("1600 Amphitheatre Parkway, Mountain View, CA")
        self.assertIsNotNone(place)
        self.assertTrue(meta['is_like_address'])
        self.assertIsNotNone(place.get('lat'))
        self.assertIsNotNone(place.get('lng'))

    def test_real_request_invalid_address(self):
        # Use a known invalid address
        place, meta = lookup_address_google("This is not a real address")
        self.assertFalse(place)
        self.assertFalse(meta['is_like_address'])

        
if __name__ == '__main__':
    unittest.main()

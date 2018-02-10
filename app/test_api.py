import unittest
import os
import json
from app import create

class BackApiTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create()
        self.client = self.app.test_client
        self.games = [{'name': 'dota2', 'id': 1},
                      {'name': 'cs-go', 'id': 2},
                      {'name': 'lol', 'id': 3},
                      {'name': 'heartstone', 'id': 4},
                      {'name': 'overwatch', 'id': 5}]

    def test_api_can_get_all_games(self):
        """Test API can get a bucketlist (GET request)."""
        res = self.client().get('/games/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, self.games)

    def test_api_can_get_game_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        result = self.client().get('/games/1')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(str(result.data), 'dota2')
        result = self.client().get('/games/0')
        self.assertEqual(result.status_code, 204)
        result = self.client().get('/games/6')
        self.assertEqual(result.status_code, 204)

    '''
    def test_api_can_post_team(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        rv = self.client().post('/games/1/teams',data={'name': 'team1', 'country': 'russia'})
        self.assertEqual(rv.status_code, 201)
        results = self.client().get('/games/1/teams/'+id)
        self.assertIn('Dont just eat', str(results.data))

    def tearDown(self):
        """teardown all initialized variables."""
    '''

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
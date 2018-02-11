import unittest
from app import create
import ast
import json


class BackApiTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create(debug=True, testing=True)
        self.client = self.app.test_client
        self.games = [{'name': 'dota2', 'id': 1},
                      {'name': 'cs-go', 'id': 2},
                      {'name': 'lol', 'id': 3},
                      {'name': 'hearthstone', 'id': 4},
                      {'name': 'overwatch', 'id': 5}]

    def test_api_can_get_all_games(self):
        """Test API can get a bucketlist (GET request)."""
        res = self.client().get('/games')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(ast.literal_eval(res.data)['games'], self.games)

    def test_api_can_get_game_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        result = self.client().get('/games/1')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(ast.literal_eval(result.data)['id'], 1)
        self.assertEqual(ast.literal_eval(result.data)['name'], 'dota2')
        result = self.client().get('/games/0')
        self.assertEqual(result.status_code, 204)
        result = self.client().get('/games/6')
        self.assertEqual(result.status_code, 204)

    def test_api_can_post_team(self):
        """Test API can edit an existing bucketlist. (PUT request)"""
        data_to_put = {'name': 'team1', 'country': 'russia'}
        rv = self.client().post('/games/1/teams',
                                data=json.dumps(data_to_put),
                                headers={'Content-Type':'application/json',
                                         'Accept':'application/json'})

        self.assertEqual(rv.status_code, 201)
        results = self.client().get('/games/1/teams/'+str(ast.literal_eval(rv.data)['id']))
        self.assertEqual(results.status_code, 200)
        self.assertEqual(ast.literal_eval(results.data)['name'], data_to_put['name'])
        self.assertEqual(ast.literal_eval(results.data)['country'], data_to_put['country'])
        rv = self.client().post('/games/1/teams',
                                data=json.dumps(data_to_put),
                                headers={'Content-Type':'application/json',
                                         'Accept':'application/json'})
        self.assertEqual(rv.status_code, 400)

    def tearDown(self):
        """teardown all initialized variables."""

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
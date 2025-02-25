import unittest
from model import GeoSQLAgent

class TestGeoSQLAgent(unittest.TestCase):
    def setUp(self):
        self.agent = GeoSQLAgent()

    def test_query_response(self):
        # Test with a dummy natural language query
        query = "Find all regions intersecting a given bounding box."
        result = self.agent.run_query(query)
        self.assertIsNotNone(result)
        # Further checks can be implemented based on expected structure

if __name__ == "__main__":
    unittest.main()
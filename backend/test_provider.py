import unittest
from provider import scan_nearby
class ExistingUnavailableContract(unittest.TestCase):
    def test_current_unavailable_provider(self):
        result=scan_nearby(45.0,-93.0,1.0,30,10)
        self.assertFalse(result['available'])
        self.assertEqual(result['properties'],[])
if __name__=='__main__': unittest.main()

import unittest


class TestAPIBasic(unittest.TestCase):
    def setUp(self):
        print ("Sample test_local")

    def test_something(self):
        self.assertEqual(2+2, 4)
#        self.assertEqual(2+1, 4)

if __name__ == "__main__":
    unittest.main()



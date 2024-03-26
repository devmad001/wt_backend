import unittest
from ai_record import AI_Record  # replace with your module name

class TestAI_Record(unittest.TestCase):

    def test_init(self):
        record = AI_Record(1)
        self.assertEqual(record.id, 1)

    def test_init_fields(self):
        record = AI_Record(1)
        record.init_fields({'name': 'John'})
        self.assertEqual(record.fields, { 'name': 'John'})

    def test_identify_needs(self):
        record = AI_Record(1)
        record.init_fields({'name': [{'value': 'John', 'timestamp': '2024-09-03T10:00:00', 'strategy_version': '1', 'strategy_name': 'Manual', 'parameters': None}], 'age': []})
        needs = record.identify_needs()
        self.assertEqual(needs, ['age'])

    def test_manual_set_field(self):
        record = AI_Record(1)
        record.manual_set_field('name', 'John')
        self.assertEqual(record.fields['name'][-1]['value'], 'John')

    def test_latest_values(self):
        record = AI_Record(1)
        record.manual_set_field('name', 'John')
        self.assertEqual(record.latest_values(), {'name': 'John'})

    def test_get(self):
        record = AI_Record(1)
        record.manual_set_field('name', 'John')
        self.assertEqual(record.get('name'), 'John')

    def test_to_dict(self):
        record = AI_Record(1)
        record_dict = record.to_dict()
        self.assertEqual(record_dict, {'id': 1, 'fields': {}})


if __name__ == '__main__':
    unittest.main()

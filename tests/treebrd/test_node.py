from unittest import TestCase

from rapt.treebrd.errors import RelationReferenceError

from rapt.treebrd.node import Node, Operator, RelationNode
from rapt.treebrd.attributes import AttributeList
from rapt.treebrd.schema import Schema


class TestNode(TestCase):
    def test_operator_from_init(self):
        expected = Operator.relation
        actual = Node(Operator.relation, None).operator
        self.assertEqual(expected, actual)

    def test_name_when_init_has_none(self):
        node = Node(Operator.relation, None)
        self.assertIsNone(node.name)

    def test_name_when_init_has_name(self):
        expected = 'wall-e'
        actual = Node(Operator.relation, 'wall-e').name
        self.assertEqual(expected, actual)

    def test_attributes_from_init(self):
        actual = Node(Operator.relation, None).attributes
        self.assertIsNone(actual)


class TestNodeEquality(TestCase):
    def test_equality_when_identical(self):
        node = Node(Operator.relation, 'borg')
        same = node
        self.assertTrue(node == same)

    def test_equality_when_same_operator_and_name(self):
        node = Node(Operator.relation, 'borg')
        twin = Node(Operator.relation, 'borg')
        self.assertTrue(node == twin)

    def test_non_equality_when_different_operator_and_name(self):
        node = Node(Operator.relation, 'borg')
        other = Node(Operator.project, 'psy')
        self.assertTrue(node != other)

    def test_non_equality_when_different_operator(self):
        node = Node(Operator.relation, 'psy')
        other = Node(Operator.project, 'psy')
        self.assertTrue(node != other)

    def test_non_equality_when_different_name(self):
        node = Node(Operator.relation, 'borg')
        other = Node(Operator.relation, 'psy')
        self.assertTrue(node != other)


class TestRelationNode(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = Schema({
            'Question': ['id', 'question'],
            'Answer': ['id', 'question', 'answer'],
        })

    def test_operator_from_init(self):
        expected = Operator.relation
        actual = RelationNode('Question', self.schema).operator
        self.assertEqual(expected, actual)

    def test_exception_raised_when_name_not_in_schema(self):
        self.assertRaises(RelationReferenceError, RelationNode, 'Unknown',
                          self.schema)

    def test_attributes_when_name_is_in_schema(self):
        expected = AttributeList(self.schema.get_attributes('Answer'),
                                 'Answer').to_list()
        node = RelationNode('Answer', self.schema)
        self.assertEqual(expected, node.attributes.to_list())
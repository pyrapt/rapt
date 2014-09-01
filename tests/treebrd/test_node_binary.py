from unittest import TestCase

from rapt.treebrd.node import RelationNode, UnionNode, DifferenceNode, BinaryNode, \
    IntersectNode, CrossJoinNode
from rapt.treebrd.errors import InputError
from rapt.treebrd.node import Operator
from rapt.treebrd.schema import Schema


class BinaryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = Schema({
            'Questions': ['id', 'question'],
            'Answers': ['id', 'question', 'answer'],
            'Ambiguous': ['twin', 'odd', 'twin']
        })

    def setUp(self):
        self.questions = RelationNode('Questions', self.schema)
        self.answers = RelationNode('Answers', self.schema)
        self.answers_twin = RelationNode('Answers', self.schema)


class TestBinaryNode(BinaryTestCase):
    def test_binary_children(self):
        node = BinaryNode(Operator.union, self.questions, self.answers)
        self.assertEqual(self.questions, node.left)
        self.assertEqual(self.answers, node.right)


class TestUnionNode(BinaryTestCase):
    def test_operator_on_init(self):
        node = UnionNode(self.questions, self.questions)
        self.assertEqual(Operator.union, node.operator)

    def test_children_on_init(self):
        node = UnionNode(self.answers, self.answers_twin)
        self.assertEqual(self.answers, node.left)
        self.assertEqual(self.answers_twin, node.right)

    def test_attributes(self):
        node = UnionNode(self.questions, self.questions)
        expected = ['id', 'question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_mismatch(self):
        self.assertRaises(InputError, UnionNode, self.questions, self.answers)


class TestDifferenceNode(BinaryTestCase):
    def test_operator_on_init(self):
        node = DifferenceNode(self.questions, self.questions)
        self.assertEqual(Operator.difference, node.operator)

    def test_name_on_init(self):
        node = DifferenceNode(self.questions, self.questions)
        self.assertIsNone(node.name)

    def test_children_on_init(self):
        node = DifferenceNode(self.answers, self.answers_twin)
        self.assertEqual(self.answers, node.left)
        self.assertEqual(self.answers_twin, node.right)

    def test_attributes(self):
        node = DifferenceNode(self.questions, self.questions)
        expected = ['id', 'question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_mismatch(self):
        self.assertRaises(InputError, DifferenceNode, self.questions,
                          self.answers)


class TestIntersectionNode(BinaryTestCase):
    def test_operator_on_init(self):
        node = IntersectNode(self.questions, self.questions)
        self.assertEqual(Operator.intersect, node.operator)

    def test_children_on_init(self):
        node = IntersectNode(self.answers, self.answers_twin)
        self.assertEqual(self.answers, node.left)
        self.assertEqual(self.answers_twin, node.right)

    def test_attributes(self):
        node = IntersectNode(self.questions, self.questions)
        expected = ['id', 'question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_mismatch(self):
        self.assertRaises(InputError, IntersectNode, self.questions,
                          self.answers)


class TestJoinNode(BinaryTestCase):
    def test_operator_on_init(self):
        node = CrossJoinNode(self.questions, self.questions)
        self.assertEqual(Operator.cross_join, node.operator)

    def test_children_on_init(self):
        node = CrossJoinNode(self.questions, self.answers)
        self.assertEqual(self.questions, node.left)
        self.assertEqual(self.answers, node.right)

    def test_attributes_on_init(self):
        node = CrossJoinNode(self.questions, self.answers)
        expected = ['Questions.id', 'Questions.question', 'Answers.id',
                    'Answers.question', 'Answers.answer']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_left_child_is_join(self):
        left = CrossJoinNode(self.questions, self.answers)
        node = CrossJoinNode(left, self.questions)
        expected = ['Questions.id', 'Questions.question', 'Answers.id',
                    'Answers.question', 'Answers.answer', 'Questions.id',
                    'Questions.question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_right_child_is_join(self):
        right = CrossJoinNode(self.answers, self.questions)
        node = CrossJoinNode(self.questions, right)
        expected = ['Questions.id', 'Questions.question', 'Answers.id',
                    'Answers.question', 'Answers.answer', 'Questions.id',
                    'Questions.question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_both_children_are_join(self):
        left = CrossJoinNode(self.answers, self.questions)
        right = CrossJoinNode(self.answers, self.questions)
        node = CrossJoinNode(left, right)
        expected = ['Answers.id', 'Answers.question', 'Answers.answer',
                    'Questions.id', 'Questions.question', 'Answers.id',
                    'Answers.question', 'Answers.answer', 'Questions.id',
                    'Questions.question']
        self.assertEqual(expected, node.attributes.to_list())
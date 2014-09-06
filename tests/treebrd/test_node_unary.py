from copy import copy
from unittest import TestCase

from rapt.treebrd.errors import (AttributeReferenceError, InputError,
                                   InputReferenceError)
from rapt.treebrd.node import (ProjectNode, RenameNode, SelectNode,
                          UnaryNode, Operator, RelationNode, AssignNode, Node)
from rapt.treebrd.attributes import AttributeList
from rapt.treebrd.schema import Schema


class UnaryTestCase(TestCase):
    def setUp(self):
        self.schema = Schema({
            'Question': ['id', 'question'],
            'Answer': ['id', 'question', 'answer'],
            'Ambiguous': ['twin', 'odd', 'twin']
        })
        self.question = RelationNode('Question', self.schema)
        self.answer = RelationNode('Answer', self.schema)


class TestUnaryNode(UnaryTestCase):
    def test_operator_from_init(self):
        actual = UnaryNode(Operator.select, self.question).operator
        self.assertEqual(Operator.select, actual)

    def test_name_when_init_has_none_is_child_name(self):
        node = UnaryNode(Operator.relation, self.question)
        expected = 'Question'
        self.assertEqual(expected, node.name)

    def test_name_when_init_has_name(self):
        node = UnaryNode(Operator.relation, self.question, 'jasmine')
        self.assertEqual('jasmine', node.name)

    def test_child_after_init(self):
        node = UnaryNode(Operator.relation, self.question)
        self.assertEqual(self.question, node.child)

    def test_attributes_are_copied_from_child_when_init(self):
        expected = AttributeList(self.schema.get_attributes('Answer'),
                                 'Answer').to_list()
        node = UnaryNode(Operator.relation, self.answer, self.schema)
        self.assertEqual(expected, node.attributes.to_list())


class TestUnaryNodeEquality(TestCase):
    def test_equality_when_identical(self):
        node = UnaryNode(Operator.relation, Node(Operator.relation))
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


class TestSelect(UnaryTestCase):
    def test_operator_is_correct(self):
        actual = SelectNode(self.question, '"time"=10000').operator
        self.assertEqual(Operator.select, actual)

    def test_exception_when_first_attribute_in_condition_is_wrong(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.question,
                          'void="aladdin"')

    def test_exception_when_second_attribute_in_condition_is_wrong(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.question,
                          '"void"=aladdin')

    def test_exception_when_both_attributes_in_condition_are_wrong(self):
        self.assertRaises(AttributeReferenceError, SelectNode, self.question,
                          'void=aladdin')

    def test_condition_when_init_has_condition(self):
        condition = 'question="street rat?"'
        actual = SelectNode(self.question, condition).conditions
        self.assertEqual(condition, actual)

    def test_condition_when_multiple_conditions(self):
        node = SelectNode(self.question,
                          'id=id and question="Life?"')
        expected = 'id=id and question="Life?"'
        self.assertEqual(expected, node.conditions)

    def test_condition_when_with_prefix(self):
        node = SelectNode(self.question,
                          'Question.id=id and question="Life?"', )
        expected = 'Question.id=id and question="Life?"'
        self.assertEqual(expected, node.conditions)


class TestProject(UnaryTestCase):
    def test_operator_is_correct(self):
        actual = ProjectNode(self.question, []).operator
        self.assertEqual(Operator.project, actual)

    def test_attributes_when_init_with_empty_list(self):
        node = ProjectNode(self.answer, [])
        self.assertEqual([], node.attributes.to_list())

    def test_attributes_when_init_with_all_attributes(self):
        expected = AttributeList(self.schema.get_attributes('Answer'),
                                 'Answer').to_list()
        node = ProjectNode(self.answer, ['id', 'question', 'answer'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_init_with_some_attributes(self):
        expected = ['Answer.question', 'Answer.answer']
        node = ProjectNode(self.answer, ['question', 'answer'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_init_with_some_attributes_different_order(self):
        expected = ['Answer.answer', 'Answer.id']
        node = ProjectNode(self.answer, ['answer', 'id'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_init_with_single_attribute(self):
        expected = ['Answer.answer']
        node = ProjectNode(self.answer, ['answer'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_init_with_project_child(self):
        expected = ['Answer.answer']
        child = ProjectNode(self.answer, ['id', 'answer'])
        node = ProjectNode(child, ['answer'])
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_prefixed(self):
        node = ProjectNode(self.answer, ['Answer.id', 'Answer.question'])
        expected = ['Answer.id', 'Answer.question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_attributes_when_mixed(self):
        node = ProjectNode(self.answer, ['Answer.id', 'question'])
        expected = ['Answer.id', 'Answer.question']
        self.assertEqual(expected, node.attributes.to_list())

    def test_exception_when_attribute_does_not_exist(self):
        self.assertRaises(AttributeReferenceError, ProjectNode, self.question,
                          ['void'])

    def test_exception_when_attribute_no_longer_exists(self):
        child = ProjectNode(self.answer, ['question', 'answer'])
        self.assertRaises(AttributeReferenceError, ProjectNode, child,
                          ['id'])

    def test_exception_when_prefix_is_wrong(self):
        self.assertRaises(InputReferenceError, ProjectNode, self.answer,
                          ['Answering.id'])


class TestRename(TestUnaryNode):
    def test_operator_is_correct(self):
        actual = RenameNode(self.question, 'ali', [], self.schema).operator
        self.assertEqual(Operator.rename, actual)

    def test_name_when_renamed(self):
        actual = RenameNode(self.question, 'ali', [], self.schema).name
        self.assertEqual('ali', actual)

    def test_attributes_when_renamed(self):
        node = RenameNode(self.question, None, ['a', 'b'], self.schema)
        expected = ['Question.a', 'Question.b']
        self.assertEqual(expected, node.attributes.to_list())

    def test_name_when_name_is_not_renamed(self):
        node = RenameNode(self.question, None, ['a', 'b'], self.schema)
        self.assertEqual('Question', node.name)

    def test_name_when_name_and_attributes_renamed(self):
        node = RenameNode(self.question, 'Quest', ['a', 'b'], self.schema)
        self.assertEqual('Quest', node.name)

    def test_attributes_when_name_and_attributes_renamed(self):
        node = RenameNode(self.question, 'Quest', ['a', 'b'], self.schema)
        expected = ['Quest.a', 'Quest.b']
        self.assertEqual(expected, node.attributes.to_list())

    def test_exception_when_too_few_attributes(self):
        self.assertRaises(InputError, RenameNode, self.question,
                          None, ['a'], self.schema)

    def test_exception_when_too_many_attributes(self):
        self.assertRaises(InputError, RenameNode, self.question,
                          None, ['a', 'b', 'c'], self.schema)

    def test_exception_when_name_conflicts(self):
        self.assertRaises(InputError, RenameNode, self.question,
                          'Answer', ['a', 'b'], self.schema)

    def test_when_ambiguous_attributes(self):
        self.assertRaises(InputError, RenameNode, self.answer, 'Argon',
                          ['Alpha', 'Alpha'], self.schema)


class TestAssignment(TestUnaryNode):
    def test_operator_is_correct(self):
        actual = AssignNode(self.question, 'ali', [], self.schema).operator
        self.assertEqual(Operator.assign, actual)

    def test_name_when_given(self):
        actual = AssignNode(self.question, 'ali', [], self.schema).name
        self.assertEqual('ali', actual)

    def test_attributes_when_renamed(self):
        node = AssignNode(self.question, 'ali', ['a', 'b'], self.schema)
        expected = ['ali.a', 'ali.b']
        self.assertEqual(expected, node.attributes.to_list())

    def test_ambiguous_attributes_in_child(self):
        child = RelationNode('Ambiguous', self.schema)
        node = AssignNode(child, 'Apex', ['a', 'b', 'c'], self.schema)
        expected = ['Apex.a', 'Apex.b', 'Apex.c']
        self.assertEqual(expected, node.attributes.to_list())

    def test_schema_is_updated_after_assign_with_no_explicit_attributes(self):
        child = RelationNode('Answer', self.schema)
        AssignNode(child, 'Apex', [], self.schema)
        self.assertTrue(self.schema.contains('Apex'))
        self.assertEqual(self.schema.get_attributes('Answer'),
                         self.schema.get_attributes('Apex'))
        self.assertEqual(self.schema.get_attributes('Answer'),
                         self.schema.get_attributes('Apex'))

    def test_schema_is_updated_after_assign_with_attributes(self):
        child = RelationNode('Answer', self.schema)
        AssignNode(child, 'Apex', ['a', 'b', 'c'], self.schema)
        self.assertTrue(self.schema.contains('Apex'))
        self.assertEqual(['a', 'b', 'c'], self.schema.get_attributes('Apex'))

    def test_exception_when_missing_name(self):
        self.assertRaises(InputError, AssignNode, self.question,
                          None, ['a'], self.schema)

    def test_exception_when_too_few_attributes(self):
        self.assertRaises(InputError, AssignNode, self.question,
                          'ali', ['a'], self.schema)

    def test_exception_when_too_many_attributes(self):
        self.assertRaises(InputError, AssignNode, self.question,
                          'ali', ['a', 'b', 'c'], self.schema)

    def test_when_ambiguous_attributes(self):
        self.assertRaises(InputError, AssignNode, self.answer, 'Argon',
                          ['Alpha', 'Alpha'], self.schema)

    def test_exception_when_name_conflicts(self):
        self.assertRaises(InputError, RenameNode, self.question,
                          'Answer', ['a', 'b'], self.schema)

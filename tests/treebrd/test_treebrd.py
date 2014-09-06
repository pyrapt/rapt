import functools
from unittest import TestCase

from rapt.treebrd.grammars import CoreGrammar, ExtendedGrammar
from rapt.treebrd.node import RelationNode, ProjectNode, \
    CrossJoinNode, SelectNode, RenameNode, JoinNode, NaturalJoinNode, \
    ThetaJoinNode
from rapt.treebrd.schema import Schema
from rapt.treebrd.treebrd import TreeBRD


class TreeBRDTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = None

    @classmethod
    def create_build_function(cls, schema):
        builder = TreeBRD(ExtendedGrammar())
        return functools.partial(builder.build, schema=schema)


class TestRelation(TreeBRDTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.definition = {'letters': ['position', 'value'],
                          'numbers': ['value', 'prime']}
        cls.schema = Schema(cls.definition)
        cls.build = cls.create_build_function(cls.definition)

    def test_build_when_instring_is_single_relation(self):
        forest = self.build('letters;')
        self.assertEqual(1, len(forest))
        expected = RelationNode('letters', self.schema)
        self.assertEqual(expected, forest[0])

    def test_build_when_instring_has_multiple_relations(self):
        instring = 'numbers; letters;'
        forest = self.build(instring)
        self.assertEqual(2, len(forest))
        first = RelationNode('numbers', self.schema)
        second = RelationNode('letters', self.schema)
        self.assertEqual(first, forest[0])
        self.assertEqual(second, forest[1])


class TestProject(TreeBRDTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.definition = {'magic_wand': ['owner', 'manufacturer', 'wood',
                                         'core', 'length', 'rigidity']}
        cls.schema = Schema(cls.definition)
        cls.build = cls.create_build_function(cls.definition)

    def test_project_with_single_attr(self):
        instring = '\project_{owner} magic_wand;'
        forest = self.build(instring)
        child = RelationNode('magic_wand', self.schema)
        expected = ProjectNode(child, ['owner'])
        self.assertEqual(expected, forest[0])

    def test_project_with_two_attr(self):
        instring = '\project_{owner, wood} magic_wand;'
        forest = self.build(instring)
        child = RelationNode('magic_wand', self.schema)
        expected = ProjectNode(child, ['owner', 'wood'])
        self.assertEqual(expected, forest[0])

    def test_project_with_all_but_one_attr(self):
        attr = self.schema.get_attributes('magic_wand')
        attr.remove('rigidity')
        instring = '\project_{' + ', '.join(attr) + '} magic_wand;'
        forest = self.build(instring)
        child = RelationNode('magic_wand', self.schema)
        expected = ProjectNode(child, attr)
        self.assertEqual(expected, forest[0])

    def test_project_with_all_attr(self):
        attr = self.schema.get_attributes('magic_wand')
        instring = '\\project_{' + ', '.join(attr) + '} magic_wand;'
        forest = self.build(instring)
        child = RelationNode('magic_wand', self.schema)
        expected = ProjectNode(child, attr)
        self.assertEqual(expected, forest[0])

    def test_project_with_all_attr_shuffled(self):
        attr = self.schema.get_attributes('magic_wand')
        attr.sort()
        instring = '\\project_{' + ', '.join(attr) + '} magic_wand;'
        forest = self.build(instring)
        child = RelationNode('magic_wand', self.schema)
        expected = ProjectNode(child, attr)
        self.assertEqual(expected, forest[0])


class TestJoins(TreeBRDTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.definition = {'alpha': ['a1'],
                          'beta': ['b1', 'b2'],
                          'gamma': ['c1', 'c2', 'c3']}
        cls.schema = Schema(cls.definition)
        cls.build = cls.create_build_function(cls.definition)

    def test_join_with_natural_join(self):
        instring = 'alpha \\join beta \\natural_join gamma;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        middle = RelationNode('beta', self.schema)
        right = RelationNode('gamma', self.schema)
        intermediate = CrossJoinNode(left, middle)
        expected = NaturalJoinNode(intermediate, right)
        self.assertEqual(expected, forest[0])

    def test_natural_join_with_join(self):
        instring = 'alpha \\natural_join beta \\join gamma;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        middle = RelationNode('beta', self.schema)
        right = RelationNode('gamma', self.schema)
        intermediate = NaturalJoinNode(left, middle)
        expected = CrossJoinNode(intermediate, right)
        self.assertEqual(expected, forest[0])

    def test_join_with_theta_join(self):
        instring = 'alpha \\join beta \\theta_join_{a1 = c1} gamma;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        middle = RelationNode('beta', self.schema)
        right = RelationNode('gamma', self.schema)
        intermediate = CrossJoinNode(left, middle)
        expected = ThetaJoinNode(intermediate, right, 'a1 = c1')
        self.assertEqual(expected, forest[0])

    def test_theta_join_with_join(self):
        instring = 'alpha \\theta_join_{a1 = b1} beta \\join gamma;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        middle = RelationNode('beta', self.schema)
        right = RelationNode('gamma', self.schema)
        intermediate = ThetaJoinNode(left, middle, 'a1 = b1')
        expected = CrossJoinNode(intermediate, right)
        self.assertEqual(expected, forest[0])


class TestCrossJoin(TestJoins):
    def test_join_two_separate_relations(self):
        instring = 'alpha \\join beta;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        right = RelationNode('beta', self.schema)
        expected = CrossJoinNode(left, right)
        self.assertEqual(expected, forest[0])

    def test_join_two_identical_relations(self):
        instring = 'alpha \\join alpha;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        right = RelationNode('alpha', self.schema)
        expected = CrossJoinNode(left, right)
        self.assertEqual(expected, forest[0])
        self.fail('Should not pass.')

    def test_join_three_separate_relations(self):
        instring = 'alpha \\join beta \\join gamma;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        middle = RelationNode('beta', self.schema)
        right = RelationNode('gamma', self.schema)
        intermediate = CrossJoinNode(left, middle)
        expected = CrossJoinNode(intermediate, right)
        self.assertEqual(expected, forest[0])


class TestThetaJoin(TestJoins):
    def test_join_two_separate_relations(self):
        instring = 'alpha \\theta_join_{a1 = b1} beta;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        right = RelationNode('beta', self.schema)
        expected = ThetaJoinNode(left, right, 'a1 = b1')
        self.assertEqual(expected, forest[0])

    def test_join_two_identical_relations(self):
        instring = 'alpha \\theta_join_{a1 = a1} alpha;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        right = RelationNode('alpha', self.schema)
        expected = ThetaJoinNode(left, right, 'a1 = a1')
        self.assertEqual(expected, forest[0])
        self.fail('Should not pass.')

    def test_join_three_separate_relations(self):
        instring = 'alpha \\theta_join_{a1 = b1} beta ' \
                   '\\theta_join_{a1 = b1} gamma;'
        forest = self.build(instring)
        left = RelationNode('alpha', self.schema)
        middle = RelationNode('beta', self.schema)
        right = RelationNode('gamma', self.schema)
        intermediate = ThetaJoinNode(left, middle, 'a1 = b1')
        expected = ThetaJoinNode(intermediate, right, 'a1 = b1')
        self.assertEqual(expected, forest[0])


class TestMystery(TreeBRDTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.definition = {'magic_wand': ['owner', 'manufacturer', 'wood',
                                         'core', 'length', 'rigidity']}
        cls.schema = Schema(cls.definition)
        cls.build = cls.create_build_function(cls.definition)

    def test_single_project_single_attr(self):
        instring = '' \
                   '\\project_{m1.manufacturer} ' \
                   '\\select_{m2.manufacturer=1} ' \
                   '(\\rename_{m1} magic_wand ' \
                   '\\join ' \
                   '\\rename_{m2} magic_wand);'
        forest = self.build(instring)
        l = RelationNode('magic_wand', self.schema)
        r1 = RenameNode(l, 'm1', [], self.schema)
        r2 = RenameNode(l, 'm2', [], self.schema)
        j = CrossJoinNode(r1, r2)
        s = SelectNode(j, 'm2.manufacturer = 1')
        expected = ProjectNode(s, ['m1.manufacturer'])
        self.assertEqual(expected, forest[0])
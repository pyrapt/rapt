from unittest import skip
from rapt.rapt import Rapt

from rapt.transformers.qtree.constants import *
from rapt.treebrd.grammars.extended_grammar import ExtendedGrammar
from tests.transformers.test_transfomer import TestTransformer


class TestQTreeTransformer(TestTransformer):
    def setUp(self):
        self.translate = self.translate_func(Rapt(
            grammar='Extended Grammar').to_qtree)


class TestRelation(TestQTreeTransformer):
    def test_single_relation(self):
        ra = 'Alpha;'
        expected = ['\Tree[.$Alpha$ ]']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = 'Alpha; Beta;'
        expected = ['\Tree[.$Alpha$ ]', '\Tree[.$Beta$ ]']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestSelect(TestQTreeTransformer):
    def test_simple(self):
        ra = '\\select_{a1=a2} Alpha;'
        expected = ['\Tree[.${}_{{a1 = a2}}$ [.$Alpha$ ] ]'.format(SELECT_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestProject(TestQTreeTransformer):
    def test_simple(self):
        ra = '\\project_{a1, a2, a3} Alpha;'
        expected = [
            '\Tree[.${}_{{a1, a2, a3}}$ [.$Alpha$ ] ]'.format(PROJECT_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestRename(TestQTreeTransformer):
    @skip('Fix me after the Node with no attributes is implemented')
    def test_rename_relation(self):
        ra = '\\rename_{Apex} Alpha;'
        expected = ['\Tree[.${}_{{Apex}}$ [.$Alpha$ ] ]'.format(RENAME_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    @skip('Fix me after the Node with no attributes is implemented')
    def test_rename_attributes(self):
        ra = '\\rename_{(a, b, c)} Alpha;'
        expected = ['\Tree[.${}_{{(a, b, c)}}$ [.$Alpha$ ] ]'.format(SELECT_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_relation_and_attributes(self):
        ra = '\\rename_{Apex(a, b, c)} Alpha;'
        expected = [
            '\Tree[.${}_{{Apex(a, b, c)}}$ [.$Alpha$ ] ]'.format(RENAME_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestAssignment(TestQTreeTransformer):
    @skip('Fix me after the Node with no attributes is implemented')
    def test_relation(self):
        ra = 'NewAlpha := Alpha;'
        expected = ['\Tree[.$NewAlpha$ [.$Alpha$ ] ]']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_relation_with_attributes(self):
        ra = 'NewAlpha(a, b, c) := Alpha;'
        expected = ['\Tree[.$NewAlpha(a,b,c)$ [.$Alpha$ ] ]']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestJoin(TestQTreeTransformer):
    def test_relation(self):
        ra = 'Alpha \\join Beta;'
        expected = ['\Tree[.${}$ [.$Alpha$ ] [.$Beta$ ] ]'.format(JOIN_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestNaturalJoin(TestQTreeTransformer):
    grammar = ExtendedGrammar

    def test_relation(self):
        ra = 'Alpha \\natural_join Beta;'
        expected = [
            '\Tree[.${}$ [.$Alpha$ ] [.$Beta$ ] ]'.format(NATURAL_JOIN_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestThetaJoin(TestQTreeTransformer):
    grammar = ExtendedGrammar

    def test_relation(self):
        ra = 'Alpha \\join_{a1 = b1} Beta;'
        expected = ['\Tree[.${}_{{a1 = b1}}$ [.$Alpha$ ] [.$Beta$ ] ]'.format(
            THETA_JOIN_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestUnion(TestQTreeTransformer):
    def test_simple(self):
        ra = 'Gamma \\union GammaTwin;'
        expected = [
            '\Tree[.${}$ [.$Gamma$ ] [.$GammaTwin$ ] ]'.format(UNION_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestIntersect(TestQTreeTransformer):
    grammar = ExtendedGrammar

    def test_simple(self):
        ra = 'Gamma \\intersect GammaTwin;'
        expected = [
            '\Tree[.${}$ [.$Gamma$ ] [.$GammaTwin$ ] ]'.format(INTERSECT_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestDifference(TestQTreeTransformer):
    def test_simple(self):
        ra = 'Gamma \\difference GammaTwin;'
        expected = [
            '\Tree[.${}$ [.$Gamma$ ] [.$GammaTwin$ ] ]'.format(DIFFERENCE_OP)]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)
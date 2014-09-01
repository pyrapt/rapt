import functools
from unittest import TestCase


class TestTransformer(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'AlphaTwin': ['a1', 'a2', 'a3'],
            'AlphaPrime': ['a1', 'a4', 'a5'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2'],
            'GammaPrime': ['g1', 'g2'],
            'GammaTwin': ['g1', 'g2'],
            'Delta': ['d1', 'd2'],
            'Ambiguous': ['a', 'a', 'b']
        }

    def translate_func(self, func, schema=None):
        schema = schema or self.schema
        return functools.partial(func, schema=schema)

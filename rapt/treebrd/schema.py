import copy

from rapt.treebrd.errors import RelationReferenceError


class Schema:
    """
    A Schema is a description of relational data.
    """

    def __init__(self, definition):
        self._data = copy.deepcopy(definition)
        self._temp = {}

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        if self.to_dict() != other.to_dict():
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def contains(self, name):
        """
        Return true if the Schema contains a relation with the specified name.
        :param name: A name of a relation.
        :return: True if the Schema contains a relation with the specified name.
        """
        return name in self._data or name in self._temp

    def to_dict(self):
        """
        Return a dictionary containing the name-attribute pairs in this Schema.
        :return: A dictionary of name-attribute pairs.
        """
        schema = copy.deepcopy(self._data)
        for name, attributes in self._temp:
            schema[name] = attributes[:]
        return schema

    def get_attributes(self, name):
        """
        Return the list of attributes associated with the specified relation.
        :param name: A name of a relation in the Schema.
        :return: A list of attributes.
        :raise RelationReferenceError: Raised if the name does not exist.
        """
        attributes = self._data.get(name, None) or self._temp.get(name, None)
        if not attributes:
            raise RelationReferenceError(
                'Relation \'{name}\' does not exist.'.format(name=name))
        return attributes[:]

    def add(self, name, attributes, is_temporary=False):
        """
        Add the relation to the Schema.
        :param name: The name of a relation.
        :param attributes: A list of attributes for the relation.
        :param is_temporary: If true, the relation is stored until the next
        call to clear. Else, the relation persists for the lifetime of the
        Schema.
        :raise RelationReferenceError: Raised if the name already exists.
        """
        store = self._temp if is_temporary else self._data
        if name in store:
            raise RelationReferenceError(
                'Relation \'{name}\' already exists.'.format(name=name))
        store[name] = attributes[:]

    def clear_temporary(self):
        """
        Remove temporary relations from the Schema.
        """
        self._temp = {}
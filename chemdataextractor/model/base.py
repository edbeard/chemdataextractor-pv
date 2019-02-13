# -*- coding: utf-8 -*-
"""
Data model for extracted information.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
from abc import ABCMeta
from collections import MutableSequence
import json
import logging

import six

from ..utils import python_2_unicode_compatible
from ..parse.elements import Any

log = logging.getLogger(__name__)


class MutableAttribute():

    def __init__(self, default):
        """

        :param default: (Optional) The default value for this field if none is set.
        :param bool null: (Optional) Include in serialized output even if value is None. Default False.
        :param bool required: (Optional) Whether a value is required. Default False.
        :param bool contextual: (Optional) Whether this value is contextual. Default False.
        """
        self.default = copy.copy(default)
        self._value = copy.copy(self.default)

    def __get__(self, instance, owner):
        """Descriptor for retrieving a value from a field in a Model."""
        # Check if Model class is being called, rather than Model instance
        if instance is None:
            return self
        return self._value

    def __set__(self, instance, value):
        self._value = value
        if instance.has('set_parsers_need_update'):
            instance.set_parsers_need_update()

    def reset(self):
        self._value = copy.copy(self.default)


class BaseType(six.with_metaclass(ABCMeta)):

    # This is assigned by ModelMeta to match the attribute on the Model
    name = None

    def __init__(self, default=None, null=False, required=False, contextual=False, parse_expression=None):
        """

        :param default: (Optional) The default value for this field if none is set.
        :param bool null: (Optional) Include in serialized output even if value is None. Default False.
        :param bool required: (Optional) Whether a value is required. Default False.
        :param bool contextual: (Optional) Whether this value is contextual. Default False.
        :param parse_expression: (Optional) Expression for parsing, instance of a subclass of BaseParserElement
        """
        self.default = copy.deepcopy(default)
        self.null = null
        self.required = required
        self.contextual = contextual
        self.parse_expression = parse_expression

    def __get__(self, instance, owner):
        """Descriptor for retrieving a value from a field in a Model."""
        # Check if Model class is being called, rather than Model instance
        if instance is None:
            return self
        # Get value from Model instance if available
        value = instance._values.get(self.name)
        # If value is None or empty string then return the default value, if set
        # if value in [None, ''] and self.default is not None:
        #     return self.default
        return value

    def __set__(self, instance, value):
        """Descriptor for assigning a value to a field in a Model."""
        instance._values[self.name] = self.process(value)

    def process(self, value):
        """Convert an assigned value into the desired data format."""
        return value

    def serialize(self, value, primitive=False):
        """Serialize this field."""
        if hasattr(value, 'serialize'):
            # i.e. value is a nested model
            return value.serialize(primitive=primitive)
        else:
            return value


class StringType(BaseType):
    """"""

    def process(self, value):
        """Convert value to a unicode string. Useful in case lxml _ElementUnicodeResult are passed from parser."""
        return six.text_type(value) if value is not None else None


class FloatType(BaseType):
    """An floating point number field."""

    def process(self, value):
        """Convert value to a float."""
        if value is not None:
            return float(value)

        return None


class ModelType(BaseType):

    def __init__(self, model, **kwargs):
        self.model_class = model
        self.model_name = self.model_class.__name__
        super(ModelType, self).__init__(**kwargs)

    def serialize(self, value, primitive=False):
        """Serialize this field."""
        return value.serialize(primitive=primitive)


class ListType(BaseType):

    def __init__(self, field, default=None, **kwargs):
        super(ListType, self).__init__(**kwargs)
        self.field = field
        self.default = default if default is not None else []

    # def __get__(self, instance, owner):
    #     """Descriptor for retrieving a value from a field in a Model."""
    #     # Check if Model class is being called, rather than Model instance
    #     if instance is None:
    #         return self
    #     # Get value from Model instance if available
    #     value = instance._values.get(self.name)
    #     # If value is None or empty string then return the default value, if set
    #     if value in [None, '', []]:
    #         return self.default if self.default is not None else []
    #     return value

    def __set__(self, instance, value):
        """Descriptor for assigning a value to a ListField in a Model."""
        # Run process for the nested field type for each value in list
        if value is None:
            instance._values[self.name] = None
        else:
            instance._values[self.name] = [self.field.process(v) for v in value]

    def serialize(self, value, primitive=False):
        """Serialize this field."""
        return [self.field.serialize(v, primitive=primitive) for v in value]


class ModelMeta(ABCMeta):
    """"""

    def __new__(mcs, name, bases, attrs):
        fields = {}
        for attr_name, attr_value in six.iteritems(attrs):
            if isinstance(attr_value, BaseType):
                # Set the name attribute on the Type to the attribute name on the Model
                attr_value.name = six.text_type(attr_name)
                fields[attr_name] = attr_value
        cls = super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.fields = cls.fields.copy()
        cls.fields.update(fields)
        for parser in cls.parsers:
            parser.model = cls
        return cls

    def __setattr__(cls, key, value):
        if isinstance(value, BaseType):
            value.name = six.text_type(key)
            cls.fields[key] = value
        return super(ModelMeta, cls).__setattr__(key, value)


@python_2_unicode_compatible
class BaseModel(six.with_metaclass(ModelMeta)):
    """"""

    fields = {}
    parsers = []
    specifier = None

    def __init__(self, **raw_data):
        """"""
        self._values = {}
        for key, value in six.iteritems(raw_data):
            setattr(self, key, value)
        # Set defaults
        for key, field in six.iteritems(self.fields):
            if key not in raw_data:
                setattr(self, key, copy.copy(field.default))

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def __str__(self):
        return '<%s>' % (self.__class__.__name__,)

    def __eq__(self, other):
        # TODO: Check this actually works as expected (what about default values?)
        if isinstance(other, self.__class__):
            return self._values == other._values
        return False

    def __iter__(self):
        return iter(self.fields)

    def __delattr__(self, attr):
        """Handle deletion of field values by setting to default if specified."""
        # Set to default value
        if attr in self.fields:
            setattr(self, attr, self.fields[attr].default)
        else:
            super(BaseModel, self).__delattr__(attr)

    def __getitem__(self, key):
        """Redirect dictionary-style field access to attribute-style."""
        try:
            if key in self.fields:
                return getattr(self, key)
        except AttributeError:
            pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        """Redirect dictionary-style field setting to attribute-style."""
        if key not in self.fields:
            raise KeyError(key)
        return setattr(self, key, value)

    def __contains__(self, name):
        try:
            val = getattr(self, name)
            return val is not None
        except AttributeError:
            return False

    @classmethod
    def reset_mutables(cls):
        for key, field in six.iteritems(cls.fields):
            if isinstance(field, MutableAttribute):
                field.reset()

    @classmethod
    def set_parsers_need_update(cls):
        for parser in cls.parsers:
            parser.needs_update = True

    def keys(self):
        return list(iter(self))

    def items(self):
        return [(k, getattr(self, k)) for k in self]

    def values(self):
        return [getattr(self, k) for k in self]

    def get(self, key, default=None):
        return getattr(self, key, default)

    # def validate(self):
    #     """"""
    #     for field_name in self:
    #         self.fields[field_name].validate()

    @property
    def is_contextual(self):
        for k in self:
            value = getattr(self, k)
            field = self.fields.get(k)
            # Not contextual if any contextual=False field has a value
            if value not in [None, '', []]:
                # If a ListType, it depends on the contained type
                if isinstance(field, ListType):
                    # If a list of Models, not contextual if any of them isn't
                    if isinstance(field.field, ModelType):
                        for model_value in value:
                            if not model_value.is_contextual:
                                return False
                    elif not field.field.contextual:
                        return False
                else:
                    # If a single Model type, not contextual if it isn't
                    if isinstance(field, ModelType):
                        if not value.is_contextual:
                            return False
                    elif not field.contextual:
                        return False
        return True

    def serialize(self, primitive=False):
        """Convert Model to python dictionary."""
        # Serialize fields to a dict
        data = {}
        for field_name in self:
            value = getattr(self, field_name)
            field = self.fields.get(field_name)
            if value is not None:
                value = field.serialize(value, primitive=primitive)
            # Skip empty fields unless field.null
            if not field.null and value in [None, '', []]:
                continue
            data[field.name] = value
        return data

    def to_json(self, *args, **kwargs):
        """Convert Model to JSON."""
        return json.dumps(self.serialize(primitive=True), *args, **kwargs)


@python_2_unicode_compatible
class ModelList(MutableSequence):
    """Wrapper around a list of Models objects to facilitate operations on all at once."""

    def __init__(self, *models):
        self.models = list(models)

    def __getitem__(self, index):
        return self.models[index]

    def __setitem__(self, index, value):
        self.models[index] = value

    def __delitem__(self, index):
        del self.models[index]

    def __len__(self):
        return len(self.models)

    def __repr__(self):
        return self.models.__repr__()

    def __str__(self):
        return self.models.__str__()

    def insert(self, index, value):
        self.models.insert(index, value)

    def serialize(self):
        """Serialize to a list of python dictionaries."""
        return [e.serialize() for e in self.models]

    def to_json(self, *args, **kwargs):
        """Convert ModelList to JSON."""
        return json.dumps(self.serialize(), *args, **kwargs)




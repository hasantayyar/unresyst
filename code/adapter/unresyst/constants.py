"""The constants used in Unresyst"""

_ = lambda x: x

MAX_LENGTH_NAME = 40
"""The maximum length of the name in the universal representation."""

MAX_LENGTH_CLASS_NAME = 20
"""The maximum length of the class name."""

MAX_LENGTH_ENTITY_TYPE = 2
"""The maximum length of the entity type string"""

MAX_LENGTH_RELATIONSHIP_TYPE = 5
"""The maximum length of the relationship type string"""

ENTITY_TYPE_CHOICES = (
    # a subject:
    ('S', _('Subject')),
    
    # an object:
    ('O', _('Object')),
    
    # when subject domain is the same as object domain
    ('SO', _('Subject == Object')),
)
"""Choices for the entity_type field"""

RELATIONSHIP_TYPE_CHOICES = (
    # a subject-object relationship
    ('S-O', _('Subejct-Object')),
    
    # a subject-subject relationship
    ('S-S', _('Subject-Subject')),
    
    # an object-object relationship
    ('O-O', _('Object-Object')),
    
    # a relationship for recommender where subject domain equals object domain
    ('SO-SO', _('SubjectObject-SubjectObject')),
)
"""Choices for the relationship_type field"""

DEFAULT_RECOMMENDATION_COUNT = 10
"""The defaul count of the obtained recommended objects"""

"""The constants used in Unresyst"""

_ = lambda x: x

MAX_LENGTH_NAME = 80
"""The maximum length of the name in the universal representation."""

MAX_LENGTH_CLASS_NAME = 20
"""The maximum length of the class name."""

MAX_LENGTH_ENTITY_TYPE = 2
"""The maximum length of the entity type string"""

MAX_LENGTH_RELATIONSHIP_TYPE = 5
"""The maximum length of the relationship type string"""

MAX_LENGTH_ID = 50
"""The maximum length of the id in parent system"""

ENTITY_TYPE_SUBJECT = 'S'
"""The subject entity type"""

ENTITY_TYPE_OBJECT = 'O'
"""The object entity type"""

ENTITY_TYPE_SUBJECTOBJECT = 'SO'
"""The subject object entity type"""

ENTITY_TYPE_CHOICES = (
    # a subject:
    (ENTITY_TYPE_SUBJECT, _('Subject')),
    
    # an object:
    (ENTITY_TYPE_OBJECT, _('Object')),
    
    # when subject domain is the same as object domain
    (ENTITY_TYPE_SUBJECTOBJECT, _('Subject == Object')),
)
"""Choices for the entity_type field"""

RELATIONSHIP_TYPE_SEPARATOR = '-'

RELATIONSHIP_TYPE_SUBJECT_OBJECT = \
    ENTITY_TYPE_SUBJECT + RELATIONSHIP_TYPE_SEPARATOR + ENTITY_TYPE_OBJECT
"""Subject-object relationship type"""

RELATIONSHIP_TYPE_SUBJECT_SUBJECT = \
    ENTITY_TYPE_SUBJECT + RELATIONSHIP_TYPE_SEPARATOR + ENTITY_TYPE_SUBJECT   
"""Subject-subject relationship type"""

RELATIONSHIP_TYPE_OBJECT_OBJECT = \
    ENTITY_TYPE_OBJECT + RELATIONSHIP_TYPE_SEPARATOR + ENTITY_TYPE_OBJECT
"""Object-object relatioship type"""

RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT = \
    ENTITY_TYPE_SUBJECTOBJECT + RELATIONSHIP_TYPE_SEPARATOR + ENTITY_TYPE_SUBJECTOBJECT
"""Subjectobject-subjectobject relatioship type"""

RELATIONSHIP_TYPE_CHOICES = (
    # a subject-object relationship
    (RELATIONSHIP_TYPE_SUBJECT_OBJECT, _('Subejct-Object')),
    
    # a subject-subject relationship
    (RELATIONSHIP_TYPE_SUBJECT_SUBJECT, _('Subject-Subject')),
    
    # an object-object relationship
    (RELATIONSHIP_TYPE_OBJECT_OBJECT, _('Object-Object')),
    
    # a relationship for recommender where subject domain equals object domain
    (RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT, _('SubjectObject-SubjectObject')),
)
"""Choices for the relationship_type field"""

FORMAT_STR_SUBJECT = "subject"
FORMAT_STR_OBJECT = "object"
FORMAT_STR_SUBJECT1 = "subject1"
FORMAT_STR_SUBJECT2 = "subject2"
FORMAT_STR_OBJECT1 =  "object1"
FORMAT_STR_OBJECT2 = "object2"
FORMAT_STR_SUBJECTOBJECT1 =  "subjectobject1"
FORMAT_STR_SUBJECTOBJECT2 = "subjectobject2"
"""Format strings used in the explanation field."""

DEFAULT_RECOMMENDATION_COUNT = 10
"""The defaul count of the obtained recommended objects"""

UNCERTAIN_PREDICTION_VALUE = 0.5
"""The value that is returned when the prediction for the pair isn't 
available"""

ALREADY_IN_REL_PREDICTION_VALUE = 1.0
"""The value that is returned when the pair already is in the 
predicted_relationship"""

MIN_WEIGHT = 0.0
MAX_WEIGHT = 1.0
"""Weight limits"""

"""The module defines base class for the abstractor package."""

class BaseAbstractor(object):
    """The base (abstract) class for all abstractors. Defines the interface."""
    
    # Build phase:
    #
    
    @classmethod
    def create_subjectobjects(cls, recommender, subjects, objects):
        """Create abstract representation of subjects and objects.
        
        @type recommender: models.Recommender
        @param recommender: the recommender model instance
        
        @type subjects: django.db.models.manager.Manager
        @param subjects: the manager above the subject model
        
        @type objects: django.db.models.manager.Manager
        @param objects: the manager above the object model
        
        """
        pass
        
    
    @classmethod            
    def create_predicted_relationship_instances(cls, recommender, predicted_relationship):
        """Create the instances of the predicted relationship.
        
        Create bindings on subject-object pairs for pairs between which there's
        the predicted relationship.

        @type recommender: models.Recommender
        @param recommender: the recommender model instance        
        
        @type predicted_relationship: rules.Relationship
        @param predicted_relationship: the definition of relationship to be predicted        
        """
        pass

    
    @classmethod        
    def create_relationship_instances(cls, recommender, relationships):
        """Create the instances of relationships relevant for recommendation.
        
        Create bindings on pairs of subject/objects, for pairs between where 
        the relationship is.
        
        @type recommender: models.Recommender
        @param recommender: the recommender model instance        
        
        @type relationships: list of rules._WeightedRelationship subclass instances
        @param relatioships: recommender relationships to be instantiated        
        """
        pass

    
    @classmethod
    def create_rule_instances(cls, recommender, rules):
        """Create the instances of rules.
        
        Create bindings on pairs of subject/objects, for pairs between where 
        the rule applies.

        @type recommender: models.Recommender
        @param recommender: the recommender model instance                
        
        @type rules: list of rules._BaseRule subclass instances
        @param rules: recommender rules to be instantiated
        """
        pass
    
    
    # Recommend phase:
    #
    
    @classmethod
    def get_dn_subject(cls, recommender, subject):
        """Get a domain neutral SubjectObject for the given domain-specific
        subject.
        
        @rtype: SubjectObject
        @return: the domain neutral subject
        """
        pass
        
    @classmethod
    def get_dn_object(cls, recommender, object_):
        """Get a domain neutral SubjectObject for the given domain-specific
        object.
        
        @rtype: SubjectObject
        @return: the domain neutral object
        """
        pass
        
    @classmethod        
    def get_subject(cls, recommender, dn_subject):
        """Get a domain specific subject for the given SubjectObject.
        
        @rtype: domain specific Subject
        @return: the domain specific subject
        """
        pass
    
    @classmethod
    def get_object(cls, recommender, dn_object):
        """Get the domain specific object for the given SubjectObject.
        
        @rtype: domain specific Object
        @return: the domain specific object
        """
        pass

    # Update phase:
    # 
    
    @classmethod
    def add_subject(cls, recommender, subject):
        """Add the subject to the abstract subjects, to the relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass
    
    @classmethod
    def add_object(cls, recommender, object_):
        """Add the object to the abstract objects, to the relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass
    
    @classmethod
    def update_subject(cls, recommender, subject):
        """Update the subject in the abstract subjects, in the relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass
    
    @classmethod
    def update_object(cls, recommender, object_):
        """Update the object in the abstract objects, in the relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass    
        
    @classmethod
    def remove_subject(cls, recommender, subject):
        """Remove the subject from the abstract subjects, its relationships and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass
    
    @classmethod
    def remove_object(cls, recommender, object_):
        """Update the object from the abstract objects, its relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass    
        
                

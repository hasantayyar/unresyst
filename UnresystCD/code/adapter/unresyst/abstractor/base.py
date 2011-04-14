"""The module defines base class for the abstractor package."""

class BaseAbstractor(object):
    """The base (abstract) class for all abstractors. Defines the interface."""
    
    # Build phase:
    #
    
    
    def create_subjectobjects(self, recommender_model, subjects, objects):
        """Create abstract representation of subjects and objects.
        
        @type recommender_model: models.Recommender
        @param recommender_model: the recommender model instance
        
        @type subjects: django.db.models.manager.Manager
        @param subjects: the manager above the subject model
        
        @type objects: django.db.models.manager.Manager
        @param objects: the manager above the object model
        
        """
        pass
        
    
                
    def create_predicted_relationship_instances(self, predicted_relationship):
        """Create the instances of the predicted relationship.
        
        Create bindings on subject-object pairs for pairs between which there's
        the predicted relationship.
        
        @type predicted_relationship: rules.Relationship
        @param predicted_relationship: the definition of relationship to be predicted        
        """
        pass

    
            
    def create_relationship_instances(self, relationships):
        """Create the instances of relationships relevant for recommendation.
        
        Create bindings on pairs of subject/objects, for pairs between where 
        the relationship is.        
        
        @type relationships: list of rules._WeightedRelationship subclass instances
        @param relatioships: recommender relationships to be instantiated  

        @raise ConfigurationError: if the weight of some relatioship is
            outside [0, 1]      
        """
        pass

    
    
    def create_rule_instances(self, rules):
        """Create the instances of rules.
        
        Create bindings on pairs of subject/objects, for pairs between where 
        the rule applies.

        @type rules: list of rules._BaseRule subclass instances
        @param rules: recommender rules to be instantiated
        
        @raise ConfigurationError: if the weight of some rule is outside [0, 1]
            or some confidence function returns a value outside [0, 1].
        """
        pass

    
        
    
    def create_clusters(self, cluster_sets):
        """Create clusters defined in the given sets
        
        Crates the cluster sets in the database, their clusters, bindings 
        of subjectobjects to the clusters.
        
        @type cluster_sets: a list of clusters.BaseClusterSet subclass instances
        @param cluster_sets: recommender cluster sets to be evaluated
        
        @raise ConfigurationError: if the weight of some cluster set is outside [0, 1]
            or some cluster member confidence is outside [0, 1].
        """
        pass
        
    
    def create_biases(self, biases):
        """Create biases defined by the user.
        
        Creates bias definitions and instances in the database.
        
        @type biases: a list of bias._BaseBias instances
        @param biases: biases to be evaluated
        
        @raise ConfigurationError: if the weight of some cluster set is outside [0, 1]
            or some cluster member confidence is outside [0, 1].                 
        """
        pass

    
    # Update phase:
    # 
    
    
    def add_subject(self, recommender, subject):
        """Add the subject to the abstract subjects, to the relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass
    
    
    def add_object(self, recommender, object_):
        """Add the object to the abstract objects, to the relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass
    
    
    def update_subject(self, recommender, subject):
        """Update the subject in the abstract subjects, in the relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass
    
    
    def update_object(self, recommender, object_):
        """Update the object in the abstract objects, in the relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass    
        
    
    def remove_subject(self, recommender, subject):
        """Remove the subject from the abstract subjects, its relationships and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass
    
    
    def remove_object(self, recommender, object_):
        """Update the object from the abstract objects, its relationship and
        rule instances.
        
        @rtype: uvidime
        @return: the changes performed on the rule and relationship instances.
        """
        pass    
        
                

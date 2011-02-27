"""The classes for defining clusters by users"""

from unresyst.models.abstractor import ClusterSet, Cluster, ClusterMember
from unresyst.models.common import SubjectObject
from unresyst.exceptions import ConfigurationError
from unresyst.constants import *

class BaseClusterSet(object):
    """The base class for all clusters sets. Cluster set is a set of clusters,
    e.g. cluster set 'Gender' contains clusters 'Male', 'Female'."""
    
    entity_type = None
    """The type of the entities in the clusters"""
    
    def __init__(self, name, weight, filter_entities, get_cluster_confidence_pairs):
        """The initializer"""

        self.name = name
        """The name of the rule/relationship."""
        
        self.weight = weight
        """The significance of the similarity inferred from two subject/objects
        belonging to the same cluster. A number from [0, 1]"""
        
        self.filter_entities = filter_entities
        """A queryset of all entities of the given type (s/o/so) belonging
        to some cluster.
        """
        
        self.get_cluster_confidence_pairs = get_cluster_confidence_pairs
        """A generator returning pairs of cluster, confidence for the given entity.
        E.g. for 'Liars' it returns (('Punk', 0.41), ('Indie', 0.72))
        Parameters: domain specific entity
        Return: the pairs: (name of the cluster, confidence - number from [0, 1])
        """
   
    def evaluate(self):
        """Crate the cluster set in the database, its clusters, bindings 
        of subjectobjects to the clusters.
        """
        
        if not (MIN_WEIGHT <= self.weight <= MAX_WEIGHT):
            raise ConfigurationError(
                message=("The set '%s' provides weight %f," + 
                    " should be between 0 and 1. ."
                    ) % (self.name, self.weight),
                recommender=self.recommender,
                parameter_name="Recommender.cluster_sets",
                parameter_value=(self.recommender.cluster_sets)
            )
            
        recommender_model = self.recommender._get_recommender_model()

        # create the cluster set in the database
        cluster_set = ClusterSet(
            name=self.name,
            recommender=recommender_model,
            entity_type=self.entity_type,
            weight=self.weight)
        
        cluster_set.save()
        
        # go through the entities create clusters on demand
        #
        
        for ds_entity in self.filter_entities:
            
            # get entity cluster-confidence pairs
            cluster_conf_pairs = self.get_cluster_confidence_pairs(ds_entity)
            
            # convert the entity to universal
            dn_entity = SubjectObject.get_domain_neutral_entity(
                domain_specific_entity=ds_entity, 
                entity_type=self.entity_type, 
                recommender=recommender_model)
            
            # go through the entity clusters
            for cluster_name, confidence in cluster_conf_pairs:
                
                # if confidence invalid through an error
                if not (MIN_CONFIDENCE <= confidence <= MAX_CONFIDENCE):
                    raise ConfigurationError(
                        message=("The cluster set '%s' provides confidence %f," + 
                            " should be between 0 and 1. For cluster %s."
                            ) % (self.name, confidence, cluster_name),
                        recommender=self.recommender,
                        parameter_name="Recommender.cluster_sets",
                        parameter_value=(self.recommender.cluster_sets)
                    )
                
                # get or create the cluster 
                cluster, x = Cluster.objects.get_or_create(
                    name=cluster_name,
                    cluster_set=cluster_set)
                
                # save the binding of the cluster to the dn_entity
                member = ClusterMember.objects.create(
                    cluster=cluster,
                    member=dn_entity,
                    confidence=confidence)
        
        
   

class SubjectClusterSet(BaseClusterSet):
    """Cluster set for subjects"""
    
    entity_type = ENTITY_TYPE_SUBJECT

    
class ObjectClusterSet(BaseClusterSet):
    """Cluster set for objects"""
    
    entity_type = ENTITY_TYPE_OBJECT

    
class SubjectObjectClusterSet(BaseClusterSet):
    """Clusters for recommenders where subject domain == object domain"""
    
    entity_type = ENTITY_TYPE_SUBJECTOBJECT
    
        
        

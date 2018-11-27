from django.db import models


class TeamProjectManager(models.Manager):
    pass


class ParentManager(models.Manager):
    '''
    A manager for ParentModel.
    '''
    @property
    def parents(self):
        return self.filter(parent_id=None)

    @property
    def children(self):
        return self.exclude(parent_id=None)

    @property
    def children_related_name(self):
        '''
        Returns related name for reverse-children relation.
        '''
        return self.model._meta.get_field('parent').related_query_name()


class TranslationManager(ParentManager):
    '''
    A manager for TranslationModel
    '''
    @property
    def translations(self):
        return super(TranslationManager, self).children

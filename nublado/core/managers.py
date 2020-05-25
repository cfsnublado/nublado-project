from django.db import models, transaction
from django.db.models import F, Max


class OrderedModelManager(models.Manager):

    def __get_group_filter_dict(self, obj):
        group_filter_dict = {}
        group_field_name = getattr(obj, "group_field", None)

        if group_field_name is not None:
            group_field = getattr(obj, group_field_name, None)

            if group_field is not None:
                group_filter_dict.update({group_field_name: group_field})
        return group_filter_dict

    def __get_max_order(self, group_filter_dict):
        """
        group_filter_dict: {group_field_name: group_field}
        """
        results = self.filter(
            **group_filter_dict
        ).aggregate(
            Max("order")
        )
        max_order = results["order__max"]
        if max_order is None:
            max_order = 0
        return max_order

    def change_order(self, obj, new_order):
        """
        Move an object to a new order position.
        """

        group_filter_dict = self.__get_group_filter_dict(obj)

        if group_filter_dict:
            max_order = self.__get_max_order(group_filter_dict)
            qs = self.get_queryset()

            if new_order in range(1, max_order + 1):
                with transaction.atomic():
                    if obj.order > int(new_order):
                        group_filter_dict.update({
                            "order__lt": obj.order,
                            "order__gte": new_order
                        })
                        qs.filter(
                            **group_filter_dict
                        ).exclude(
                            pk=obj.pk
                        ).update(
                            order=F("order") + 1,
                        )
                    else:
                        group_filter_dict.update({
                            "order__lte": new_order,
                            "order__gt": obj.order
                        })
                        qs.filter(
                            **group_filter_dict
                        ).exclude(
                            pk=obj.pk,
                        ).update(
                            order=F("order") - 1,
                        )

                    obj.order = new_order
                    obj.save()

    def append_to_order(self, obj):
        """ Moves object to the last place in the order. """
        group_filter_dict = self.__get_group_filter_dict(obj)

        if group_filter_dict:
            with transaction.atomic():
                max_order = self.__get_max_order(group_filter_dict)
                value = max_order + 1
                obj.order = value
                obj.save()

    def close_order_gap(self, removed_obj):
        """
        Closes the gap made by an ordered element after being deleted from db.
        """
        group_filter_dict = self.__get_group_filter_dict(removed_obj)

        if group_filter_dict:
            exists_dict = dict(group_filter_dict)
            exists_dict.update({"order": removed_obj.order})

            qs = self.get_queryset()

            if not qs.filter(**exists_dict).exists():
                with transaction.atomic():
                    group_filter_dict.update({
                        "order__gt": removed_obj.order
                    })
                    qs.filter(
                        **group_filter_dict
                    ).update(
                        order=F("order") - 1,
                    )

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        if "order" not in kwargs:
            self.append_to_order(instance)
        else:
            instance.save()
        return instance


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

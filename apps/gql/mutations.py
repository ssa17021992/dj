import graphene
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from graphene.types.mutation import MutationOptions

from apps.gql.fields import File
from apps.gql.utils import node_from_global_id


class Mutation(graphene.Mutation):
    """Mutation."""

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, field_name=None, field_type=None, _meta=None, **options
    ):
        if not options.get("description"):
            raise ImproperlyConfigured("description is required.")
        if not field_name:
            raise ImproperlyConfigured("field_name is required.")
        if not field_type:
            raise ImproperlyConfigured("field_type is required.")
        _meta = _meta or MutationOptions(cls)
        _meta.field_name = field_name
        _meta.field_type = field_type
        super().__init_subclass_with_meta__(_meta=_meta, **options)
        cls._meta.fields.update({field_name: graphene.Field(field_type)})

    @classmethod
    def get_node(cls, info, id, field="id", only_type=None):
        node = node_from_global_id(info, id, only_type)
        if node is None:
            message = _('Could not resolve node "%(node)s".')
            raise ValidationError({field: message % {"node": id}})
        return node

    @classmethod
    def get_instance(cls, info, **kwargs):
        raise NotImplementedError

    @classmethod
    def clean_input(cls, info, input):
        raise NotImplementedError

    @classmethod
    def construct_instance(cls, instance, cleaned_input):
        raise NotImplementedError

    @classmethod
    def clean_instance(cls, instance):
        raise NotImplementedError

    @classmethod
    def save(cls, info, instance, cleaned_input):
        raise NotImplementedError

    @classmethod
    def success_response(cls, info, instance):
        return cls(**{cls._meta.field_name: instance})

    @classmethod
    def perform_mutation(cls, root, info, **kwargs):
        raise NotImplementedError

    @classmethod
    def mutate(cls, root, info, **kwargs):
        instance = cls.perform_mutation(root, info, **kwargs)
        return cls.success_response(info, instance)


class ModelMutation(Mutation):
    """Model mutation."""

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, model=None, exclude=None, _meta=None, **options
    ):
        if not model:
            raise ImproperlyConfigured("model is required.")
        _meta = _meta or MutationOptions(cls)
        _meta.model = model
        _meta.exclude = exclude
        super().__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def get_instance(cls, info, **kwargs):
        id = kwargs.get("id")
        if id:
            instance = cls.get_node(info, id, only_type=cls._meta.field_type)
        else:
            instance = cls._meta.model()
        return instance

    @classmethod
    def clean_input(cls, info, input, input_cls):
        def is_file_field(f):
            return issubclass(getattr(f.type, "of_type", f.type), File)

        cleaned_input = {}
        for f_name, f_value in input_cls._meta.fields.items():
            if f_name not in input:
                continue
            value = input[f_name]
            if is_file_field(f_value):
                cleaned_input[f_name] = info.context.FILES.get(value or f_name)
            else:
                cleaned_input[f_name] = value
        return cleaned_input

    @classmethod
    def construct_instance(cls, instance, cleaned_input):
        for f in instance._meta.fields:
            if (
                f.name not in cleaned_input
                or not f.editable
                or isinstance(f, models.AutoField)
            ):
                continue
            data = cleaned_input[f.name]
            if data is None:
                if isinstance(f, models.FileField):
                    data = False
                if not f.null:
                    data = f._get_default()
            f.save_form_data(instance, data)
        return instance

    @classmethod
    def clean_instance(cls, instance):
        instance.full_clean(exclude=cls._meta.exclude)

    @classmethod
    def save(cls, info, instance, cleaned_input):
        if instance._state.adding:
            instance.save()
        else:
            instance.save(update_fields=cleaned_input)

    @classmethod
    def perform_mutation(cls, root, info, **kwargs):
        if "id" in kwargs and not kwargs["id"]:
            raise ValidationError({"id": _("This field is required.")})
        instance = kwargs.get("instance") or cls.get_instance(info, **kwargs)
        input = kwargs.get("input")
        input_cls = kwargs.get("input_cls") or cls.Arguments.input
        cleaned_input = cls.clean_input(info, input, input_cls)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(instance)
        cls.save(info, instance, cleaned_input)
        return instance


class ModelDeleteMutation(ModelMutation):
    """Model delete mutation."""

    class Meta:
        abstract = True

    @classmethod
    def perform_mutation(cls, root, info, **kwargs):
        if not kwargs.get("id"):
            raise ValidationError({"id": _("This field is required.")})
        instance = cls.get_instance(info, **kwargs)
        id = instance.id
        instance.delete()
        instance.id = id
        return instance

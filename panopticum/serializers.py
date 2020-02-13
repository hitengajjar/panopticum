import rest_framework.authtoken.models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
import panopticum.models
from panopticum.models import *

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class HistoricalComponentVersionSerializer(serializers.HyperlinkedModelSerializer):
    """ Model for history of Component version changes. Check https://django-simple-history.readthedocs.io"""
    class Meta:
        model = getattr(panopticum.models, 'HistoricalComponentVersionModel')
        fields = '__all__'


class ComponentDataPrivacyClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentDataPrivacyClassModel
        fields = '__all__'


class ComponentRuntimeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentRuntimeTypeModel
        fields = '__all__'


class ComponentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentCategoryModel
        fields = '__all__'


class ComponentSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentSubcategoryModel
        fields = '__all__'


class ProductFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFamilyModel
        fields = '__all__'


class ProductVersionSerializer(serializers.ModelSerializer):
    family = ProductFamilySerializer(read_only=True)

    class Meta:
        model = ProductVersionModel
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('password', )

class SoftwareVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareVendorModel
        fields = '__all__'


class DeploymentLocationClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentLocationClassModel
        fields = '__all__'


class DeploymentEnvironmentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentEnvironmentModel
        fields = '__all__'


class ComponentDeploymentSerializer(serializers.ModelSerializer):
    product_version = ProductVersionSerializer(read_only=True)
    environment = DeploymentEnvironmentModelSerializer(read_only=True)
    location_class = DeploymentLocationClassSerializer(read_only=True)
    open_ports = serializers.SerializerMethodField()

    def get_open_ports(self, deployment):
        return ", ".join([str(p.port) for p in deployment.open_ports.all()])

    class Meta:
        model = ComponentDeploymentModel
        fields = '__all__'


class ComponentSerializerSimple(serializers.ModelSerializer):
    runtime_type = ComponentRuntimeTypeSerializer(read_only=True)
    data_privacy_class = ComponentDataPrivacyClassSerializer(read_only=True)
    category = ComponentCategorySerializer(read_only=True)
    subcategory = ComponentSubcategorySerializer(read_only=True)
    product = ProductVersionSerializer(read_only=True, many=True)
    vendor = SoftwareVendorSerializer(read_only=True)

    class Meta:
        model = ComponentModel
        fields = '__all__'


class ComponentDependencySerializerSimple(serializers.ModelSerializer):
    component = ComponentSerializerSimple(read_only=True)

    class Meta:
        model = ComponentDependencyModel
        fields = '__all__'


class RequirementSetSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequirementSet
        fields = ['id', 'name']


class RequirementSimpleSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):

    class Meta:
        model = Requirement
        fields = '__all__'


class RequirementSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    requirements = RequirementSetSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Requirement
        fields = '__all__'


class RequirementStatusEntrySerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    type = serializers.SlugRelatedField(
        read_only=True,
        slug_field='owner'
    )

    class Meta:
        model = RequirementStatusEntry
        fields = '__all__'


class RequirementSetSerializer(serializers.ModelSerializer):
    requirements = RequirementSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = RequirementSet
        fields = '__all__'


class ComponentVersionSerializerSimple(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    history = serializers.HyperlinkedRelatedField(view_name='historicalcomponentversionmodel-detail',
                                                  many=True, read_only=True,
                                                  )
    depends_on = ComponentDependencySerializerSimple(source='componentdependencymodel_set',
                                                     many=True, read_only=True)

    owner_maintainer = UserSerializer(read_only=True)
    owner_responsible_qa = UserSerializer(read_only=True)

    owner_product_manager = UserSerializer(read_only=True, many=True)
    owner_program_manager = UserSerializer(read_only=True, many=True)
    owner_escalation_list = UserSerializer(read_only=True, many=True)
    owner_expert = UserSerializer(read_only=True, many=True)
    owner_architect = UserSerializer(read_only=True, many=True)

    dev_languages = serializers.SerializerMethodField()
    dev_frameworks = serializers.SerializerMethodField()

    compliance = serializers.SerializerMethodField()
    operations = serializers.SerializerMethodField()
    maintenance = serializers.SerializerMethodField()
    quality_assurance = serializers.SerializerMethodField()

    deployments = serializers.SerializerMethodField()

    meta_locations = DeploymentLocationClassSerializer(read_only=True, many=True)
    meta_product_versions = ProductVersionSerializer(read_only=True, many=True)

    def get_dev_languages(self, component):
        objs = component.dev_language.get_queryset()
        return ", ".join([o.name for o in objs])

    def get_dev_frameworks(self, component):
        objs = component.dev_framework.get_queryset()
        return ", ".join([o.name for o in objs])

    def _serialize_fields(self, component, applicable, fields):
        ret = []
        for f in fields:
            signoff = getattr(component, f.replace('_status', '_signoff'))
            ret.append({'title': component._meta.get_field(f).verbose_name,
                        'field': f,
                        'status': getattr(component, f) if applicable else "n/a",
                        'notes': getattr(component, f.replace('_status', '_notes')) if applicable else "",
                        'signoff': signoff.email if signoff and applicable else ""})
        return ret

    def get_compliance(self, component):
        return self._serialize_fields(component, component.compliance_applicable, ComponentVersionModel.get_compliance_fields())

    def get_operations(self, component):
        return self._serialize_fields(component, component.op_applicable, ComponentVersionModel.get_operations_fields())

    def get_maintenance(self, component):
        return self._serialize_fields(component, component.mt_applicable, ComponentVersionModel.get_maintenance_fields())

    def get_quality_assurance(self, component):
        return self._serialize_fields(component, component.qa_applicable, ComponentVersionModel.get_quality_assurance_fields())

    def get_deployments(self, component):
        return ComponentDeploymentSerializer(ComponentDeploymentModel.objects.filter(component_version=component),
                                             read_only=True, many=True).data

    class Meta:
        model = ComponentVersionModel
        exclude = ComponentVersionModel.get_compliance_fields() + \
                  ComponentVersionModel.get_maintenance_fields() + \
                  ComponentVersionModel.get_operations_fields() + \
                  ComponentVersionModel.get_quality_assurance_fields()


class ComponentVersionSerializer(ComponentVersionSerializerSimple):
    component = ComponentSerializerSimple(read_only=True)


class TokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = rest_framework.authtoken.models.Token()
        fields = '__all__'

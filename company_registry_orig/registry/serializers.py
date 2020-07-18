from rest_framework import serializers


class CreateCompanyRequestSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=200)
    # TODO: Add validation here that the company name is not a single symbol (e.g., "."),
    #   but something more or less meaningful

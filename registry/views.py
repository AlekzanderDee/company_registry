from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from registry.registry_manager import Registry
from registry.serializers import CreateCompanyRequestSerializer


class AddCompanyView(APIView):

    def post(self, request):
        serializer = CreateCompanyRequestSerializer(data=request.data)
        if serializer.is_valid():
            company = Registry.add_company(serializer.validated_data['company_name'])
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'company_name': serializer.validated_data['company_name'],
            'duplicate': company is None
        })

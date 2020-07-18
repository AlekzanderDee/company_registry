from unittest import mock

from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from registry.models import Company
from registry.registry_manager import Registry


class APITestCase(TestCase):

    def test_adding_duplicate(self):
        """
        Test that if similarity score is greater than max value from settings,
        a new company name is not added to the registry
        """

        with mock.patch(
                'registry.registry_manager.Registry.get_similarity_score',
                return_value=settings.MAX_SIMILARITY_SCORE + 1
        ):
            # Add a company
            Company.objects.create(name='Unicorns Ltd.')
            initial_company_cnt = Company.objects.count()
            client = APIClient()
            response = client.post('/add-company/', {'company_name': 'Universal'})
            self.assertEqual(200, response.status_code)
            # Since both company names start with the same letter, their similarity will be scored
            # Since 'get_similarity_score` returns a value which is greater than MAX_SIMILARITY_SCORE,
            # a new company won't be added, so the total number of records should stay unchanged
            self.assertEqual(initial_company_cnt, Company.objects.count())

    def test_adding_unique_company_name(self):
        """
        Test that if similarity score is smaller pr equal to max value from settings,
        a new company name is added to the registry
        """
        with mock.patch(
                'registry.registry_manager.Registry.get_similarity_score',
                return_value=settings.MAX_SIMILARITY_SCORE
        ):
            # Add a company
            Company.objects.create(name='Unicorns Ltd.')
            initial_company_cnt = Company.objects.count()
            client = APIClient()

            response = client.post('/add-company/', {'company_name': 'Universal'})
            self.assertEqual(200, response.status_code)
            # Since both company names start with the same letter, their similarity will be scored
            # Since 'get_similarity_score` returns a value which is the same as MAX_SIMILARITY_SCORE,
            # a new company's name will be treated as unique and will be added
            self.assertEqual(initial_company_cnt + 1, Company.objects.count())

            response = client.post('/add-company/', {'company_name': 'Universal 2'})
            self.assertEqual(200, response.status_code)
            # Since both company names start with the same letter, their similarity will be scored
            # Since 'get_similarity_score` returns a value which is the same as MAX_SIMILARITY_SCORE,
            # a new company's name will be treated as unique and will be added
            self.assertEqual(initial_company_cnt + 2, Company.objects.count())

    def test_bad_request(self):
        client = APIClient()
        response = client.post('/add-company/', {'foo': 'bar'})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            {
                "company_name": [
                    "This field is required."
                ]
            },
            response.json()
        )

        response = client.post('/add-company/')
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            {
                "company_name": [
                    "This field is required."
                ]
            },
            response.json()
        )


class RegistryTestCase(TestCase):

    def test_company_name_normalization(self):

        self.assertEqual(
            'Normalized Name Ltd.',
            Registry.normalize_company_name('  normaliZed   NaMe    ltd.   ')
        )

        self.assertEqual(
            'Normalized Name Ltd.',
            Registry.normalize_company_name('  NORMALIZED   NAME    LTD.   ')
        )

        self.assertEqual(
            'Normalized Name Ltd.',
            Registry.normalize_company_name('  normalized   name    ltd.   ')
        )

    def test_clean_company_name(self):
        """
        Test that cleaning method removes all well-know prefixes from the normalized value
        """
        name_template = '{prefix} Normalized {prefix} name {prefix}'

        for prefix in settings.WELL_KNOWN_PREFIXES:
            # Each prefix ends with the same common suffix which is used in the regex pattern
            # Here we need to remove this suffix.
            # Also, if prefix starts with '\' escaping char, we need to remove it.
            prefix = prefix[:-9].strip('\\')
            with self.subTest(prefix=prefix):
                self.assertEqual(
                    'normalized name',
                    Registry.get_cleaned_company_name(name_template.format(prefix=prefix))
                )

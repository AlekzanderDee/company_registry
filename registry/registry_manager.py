import logging
import re
from typing import Optional

from django.conf import settings
from fuzzywuzzy import fuzz

from registry.models import Company

logger = logging.getLogger(__name__)


class Registry:
    """
    Class that decouples the presentation layer from the data layer (decouples view from the ORM)
    """

    @staticmethod
    def normalize_company_name(company_name: str) -> str:
        """
        Given a company name, returns its normalizes value without multiple consequent spaces
        """
        company_name = re.sub(r'\s+', ' ', company_name)
        return company_name.strip().title()

    @staticmethod
    def get_cleaned_company_name(company_name: str) -> str:
        """
        Given a normalized company name, returns its value omitting all well-known prefixes
        """
        return re.sub(r'\s+', ' ', settings.RE_PREFIXES_PATTERN.sub(' ', company_name.lower()).strip())

    @staticmethod
    def get_similarity_score(s1: str, s2: str) -> int:
        """
        Returns a similarity score for 2 provided strings
        """

        # Currently, there is only one mechanism used for scoring. For different lengths of strings
        # different algorithms should be used: 1-4 character strings require different
        # algorithm/approach than strings with 15 characters and so on.

        # If more algorithms get introduced based on the string lengths, this logic may be extracted to
        # its own manager (separate class/module).
        return fuzz.token_set_ratio(s1, s2)

    @classmethod
    def add_company(cls, company_name: str) -> Optional[Company]:
        """
        Checks if a given company name is unique, and adds it to the database
        """
        normalized_name = cls.normalize_company_name(company_name)
        name_token_str = cls.get_cleaned_company_name(normalized_name)

        # TODO: Here we need a more sophisticated algorithm for fetching 'similar' names. On one hand,
        #   we can't afford fetching ALL existing companies, and compare a value that gets added with them.
        #   On the other hand, in case of typo in the first letter, we miss all companies to compare.
        #   One possible solution would be to use ML in the background, and assign every company name to a cluster.
        #   Then we can fetch existing companies that belong to the same cluster, and compare this sub-set
        similar_companies = Company.objects.filter(name__istartswith=normalized_name[0])

        for company_candidate in similar_companies:
            score = cls.get_similarity_score(name_token_str, company_candidate.cleaned_name)
            # Here, based on the score, we may have additional handling.
            # Say, for one higher range of scores we may want to reject the operation, but for other lower range,
            # we may still add a new company name, but send a notification about 'possible' duplicate
            if score > settings.MAX_SIMILARITY_SCORE:
                logger.warning(f'Found duplicate with score {score}: '
                               f'{normalized_name}: {company_candidate.name}')
                return None

        return Company.objects.create(name=normalized_name, cleaned_name=name_token_str)




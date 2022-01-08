from enum import Enum


class SnykAPIRoots(Enum):
    """
    Enum for Snyk API Roots
    """

    SNYK_API_V1_ROOT = "https://snyk.io/api/v1"


class SnykAPIV1Resources(Enum):
    """
    Enum for Snyk API Resources
    """

    ORGANIZATIONS = "/orgs"
    ORGANIZATION_DEPENDENCIES = "/org/{}/dependencies?perPage=1000"

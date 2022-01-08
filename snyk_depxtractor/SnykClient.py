import logging

from typing import Tuple

import requests

from snyk_depxtractor.SnykConstants import (  # pylint: disable=import-error
    SnykAPIRoots,
    SnykAPIV1Resources,
)


class SnykClient:
    def __init__(self, token: str) -> None:
        self.auth = {"Authorization": f"token {token}"}
        self.logger = logging.getLogger("SnykClient")
        self.http_client = requests.Session()
        self.http_client.headers.update(self.auth)

    def get_organizations(self) -> list:
        url = f"{SnykAPIRoots.SNYK_API_V1_ROOT.value}{SnykAPIV1Resources.ORGANIZATIONS.value}"
        response = self._get_request(url)
        orgs = response.get("orgs", [])
        return orgs

    def get_organization_dependencies(
        self, org_id: str, org_slug: str, page: int = 1, total_pages="first_call"
    ) -> Tuple[list, int]:
        payload = {
            "orgId": org_id,
            "orgSlug": org_slug,
        }
        url = f"{SnykAPIRoots.SNYK_API_V1_ROOT.value}{SnykAPIV1Resources.ORGANIZATION_DEPENDENCIES.value.format(org_id)}&page={page}"
        response = self._post_request(url, payload)
        dependencies = response.get("results", [])
        total_dependencies = response.get("total", 0)
        return dependencies, total_dependencies

    def _get_request(self, url: str) -> dict:
        response = self.http_client.get(url, headers=self.auth)
        return self._process_response(response)

    def _post_request(self, url: str, data: dict) -> dict:
        response = self.http_client.post(url, json=data, headers=self.auth)
        return self._process_response(response)

    def _process_response(self, response: requests.Response) -> dict:
        if response.ok:
            return response.json()
        else:
            self.logger.error(f"Error: {response.status_code}")
            self.logger.error(f"Error: {response.text}")
            raise Exception(f"Error: {response.text}")

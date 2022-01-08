import os

from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm

from snyk_depxtractor.SnykClient import SnykClient  # pylint: disable=import-error


def core():
    snyk_token = os.getenv("SNYK_TOKEN", None)
    assert snyk_token is not None, "SNYK_TOKEN environment variable is not set"

    snyk_client = SnykClient(snyk_token)

    organizations = snyk_client.get_organizations()

    dependencies = process_orgs_multi_thread(snyk_client, organizations)
    flattened_dependencies = _filter_dependency_data(dependencies)

    return flattened_dependencies


def process_orgs_multi_thread(snyk_client: SnykClient, organizations: list) -> list:
    all_org_dependencies = []

    org_ids = [org["id"] for org in organizations]
    org_slugs = [org["slug"] for org in organizations]

    with ThreadPoolExecutor(max_workers=5) as executor:
        with tqdm(
            total=len(organizations), desc="Processed proejcts: ", unit="proj"
        ) as progress:
            futures = []

            for org_id, org_slug in zip(org_ids, org_slugs):
                future = executor.submit(
                    get_dependencies_multi_thread, snyk_client, org_id, org_slug
                )
                future.add_done_callback(lambda p: progress.update())
                futures.append(future)

            for future in futures:
                all_org_dependencies.extend(future.result())

    return all_org_dependencies


def get_dependencies_multi_thread(
    snyk_client: SnykClient, org_id: str, org_slug: str
) -> list:
    all_dependencies = []
    try:
        (
            dependencies,
            total_dependencies,
        ) = snyk_client.get_organization_dependencies(org_id=org_id, org_slug=org_slug)
    except Exception as e:
        print(f"Error: {e}")
        return []
    all_dependencies.extend(dependencies)

    total_pages = (total_dependencies // 1000) + 1
    # range() is exclusive of the upper bound so we add 1
    page_number_array = [i for i in range(2, total_pages + 1)]

    if total_pages > 1:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    snyk_client.get_organization_dependencies,
                    org_id,
                    org_slug,
                    page_number,
                    total_pages,
                )
                for page_number in page_number_array
            ]
            for future in futures:
                dependencies, _ = future.result()
                all_dependencies.extend(dependencies)

    return all_dependencies


def _filter_dependency_data(dependency_list: list) -> list:
    dependencies_duplicated_for_each_project = []

    # We only want to keep the keys we care about
    keys_to_keep = [
        "id",
        "name",
        "version",
        "type",
        "issuesCritical",
        "issuesHigh",
        "issuesMedium",
        "issuesLow",
    ]

    for dependency in dependency_list:

        filtered_dependency = {key: dependency[key] for key in keys_to_keep}

        # We duplicate the dependency data for each project in the dependency, for flattening out the data
        for project in dependency.get("projects", []):
            dependencies_duplicated_for_each_project.append(
                {
                    **filtered_dependency,
                    "projectId": project.get("id", ""),
                    "projectName": project.get("name", ""),
                }
            )

    return dependencies_duplicated_for_each_project


if __name__ == "__main__":
    core()

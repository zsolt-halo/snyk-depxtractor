from csv import DictWriter
from datetime import datetime

import click

from core import core  # pylint: disable=import-error

import snyk_depxtractor

context_settings = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=context_settings)
@click.version_option(snyk_depxtractor.__version__, "--version")
def cli():
    pass


@cli.command()
def dump_group_deps():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dependencies = core()
    _write_data_to_tsv(dependencies, f"dependencies-{timestamp}.tsv")


def _write_data_to_tsv(data: list, filename: str) -> None:
    with open(filename, "w") as f:
        fieldnames = data[0].keys()
        writer = DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for dependency in data:
            writer.writerow(dependency)


if __name__ == "__main__":
    cli()

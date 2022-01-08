import json

from csv import DictWriter
from datetime import datetime

import click
import pandas as pd

import snyk_depxtractor

from snyk_depxtractor.core import core  # pylint: disable=import-error

context_settings = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=context_settings)
@click.version_option(snyk_depxtractor.__version__, "--version")
def cli():
    pass


@click.argument(
    "output_format",
    type=click.Choice(["tsv", "parquet", "json"], case_sensitive=False),
)
@cli.command()
def dump_group_deps(output_format):
    dependencies = core()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"snyk_depxtractor_{timestamp}.{output_format}"

    match output_format:
        case "tsv":
            _write_data_to_tsv(dependencies, filename)
        case "parquet":
            _save_data_to_parquet(dependencies, filename)
        case "json":
            _save_data_to_json(dependencies, filename)

    click.echo(f"Dependencies written to {filename}")


def _write_data_to_tsv(data: list, filename: str) -> None:
    with open(filename, "w") as f:
        fieldnames = data[0].keys()
        writer = DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for dependency in data:
            writer.writerow(dependency)


def _save_data_to_parquet(data: list, filename: str) -> None:
    df = pd.DataFrame(data)
    df.to_parquet(filename)


def _save_data_to_json(data: list, filename: str) -> None:
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, default=str)


if __name__ == "__main__":
    cli()

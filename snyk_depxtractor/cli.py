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
    core()


if __name__ == "__main__":
    cli()

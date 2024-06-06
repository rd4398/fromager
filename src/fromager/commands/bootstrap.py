import logging

import click
from packaging.requirements import Requirement

from .. import sdist, server

logger = logging.getLogger(__name__)


def _get_requirements_from_args(toplevel, requirements_file):
    to_build = []
    to_build.extend(toplevel)
    for filename in requirements_file:
        with open(filename, 'r') as f:
            for line in f:
                useful, _, _ = line.partition('#')
                useful = useful.strip()
                logger.debug('line %r useful %r', line, useful)
                if not useful:
                    continue
                to_build.append(useful)
    return to_build


@click.command()
@click.option('--variant', default='cpu',
              help='the build variant name')
@click.option('-r', '--requirements-file', multiple=True,
              help='pip requirements file')
@click.argument('toplevel', nargs=-1)
@click.pass_obj
def bootstrap(wkctx, variant, requirements_file, toplevel):
    """Compute and build the dependencies of a set of requirements recursively

    TOPLEVEL is a requirements specification, including a package name
    and optional version constraints.

    """
    pre_built = wkctx.settings.pre_built(variant)
    if pre_built:
        logger.info('treating %s as pre-built wheels', list(sorted(pre_built)))

    server.start_wheel_server(wkctx)

    to_build = _get_requirements_from_args(toplevel, requirements_file)
    if not to_build:
        raise RuntimeError('Pass a requirement specificiation or use -r to pass a requirements file')
    logger.debug('bootstrapping %s', to_build)
    for toplevel in to_build:
        sdist.handle_requirement(wkctx, Requirement(toplevel))

    # If we put pre-built wheels in the downloads directory, we should
    # remove them so we can treat that directory as a source of wheels
    # to upload to an index.
    for prebuilt_wheel in wkctx.wheels_prebuilt.glob('*.whl'):
        filename = wkctx.wheels_downloads / prebuilt_wheel.name
        if filename.exists():
            logger.info(f'removing prebuilt wheel {prebuilt_wheel.name} from download cache')
            filename.unlink()

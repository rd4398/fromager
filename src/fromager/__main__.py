#!/usr/bin/env python3

import logging
import pathlib

import click

from . import commands, context, overrides, settings

logger = logging.getLogger(__name__)

TERSE_LOG_FMT = '%(message)s'
VERBOSE_LOG_FMT = '%(levelname)s:%(name)s:%(lineno)d: %(message)s'


@click.group()
@click.option('-v', '--verbose', default=False)
@click.option('--log-file', type=click.Path())
@click.option('-o', '--sdists-repo', default=pathlib.Path('sdists-repo'), type=click.Path())
@click.option('-w', '--wheels-repo', default=pathlib.Path('wheels-repo'), type=click.Path())
@click.option('-t', '--work-dir', default=pathlib.Path('work-dir'), type=click.Path())
@click.option('-p', '--patches-dir', default=pathlib.Path('overrides/patches'), type=click.Path())
@click.option('-e', '--envs-dir', default=pathlib.Path('overrides/envs'), type=click.Path())
@click.option('--settings-file', default=pathlib.Path('overrides/settings.yaml'), type=click.Path())
@click.option('--wheel-server-url', default='', type=str)
@click.option('--cleanup/--no-cleanup', default=True)
@click.pass_context
def main(ctx, verbose, log_file,
         sdists_repo, wheels_repo, work_dir, patches_dir, envs_dir,
         settings_file, wheel_server_url,
         cleanup,
         ):
    # Configure console and log output.
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    stream_formatter = logging.Formatter(VERBOSE_LOG_FMT if verbose else TERSE_LOG_FMT)
    stream_handler.setFormatter(stream_formatter)
    logging.getLogger().addHandler(stream_handler)
    if log_file:
        # Always log to the file at debug level
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(VERBOSE_LOG_FMT)
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)
    # We need to set the overall logger level to debug and allow the
    # handlers to filter messages at their own level.
    logging.getLogger().setLevel(logging.DEBUG)

    overrides.log_overrides()

    wkctx = context.WorkContext(
        settings=settings.load(settings_file),
        patches_dir=patches_dir,
        envs_dir=envs_dir,
        sdists_repo=sdists_repo,
        wheels_repo=wheels_repo,
        work_dir=work_dir,
        wheel_server_url=wheel_server_url,
        cleanup=cleanup,
    )
    wkctx.setup()
    ctx.obj = wkctx


for cmd in commands.commands:
    main.add_command(cmd)


if __name__ == '__main__':
    main(auto_envvar_prefix='FROMAGER')

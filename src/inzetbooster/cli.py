import os

import click
import httpx

from .inzetrooster import Inzetrooster


@click.group()
@click.option(
    "--org", default="rvliethorp", envvar="ORGANIZATION", help="Organization name"
)
@click.option("--user", prompt=True, envvar="USERNAME", help="Username")
@click.password_option(envvar="PASSWORD", confirmation_prompt=False)
@click.pass_context
def main(ctx: click.Context, org: str, user: str, password: str):
    """Add-on utilities for inzetrooster"""
    ctx.obj = {
        "user": user,
        "password": password,
        "org": org,
    }


@main.command()
@click.pass_obj
def export_shifts(obj: dict[str, str]):
    """Export shifts"""
    with httpx.Client(follow_redirects=True) as client:
        ir = Inzetrooster(client, obj["org"])
        ir.login(obj["user"], obj["password"])
        print(ir.export_shifts())


if __name__ == "__main__":
    main()

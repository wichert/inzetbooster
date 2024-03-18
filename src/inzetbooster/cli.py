import io
import sys

import click
import httpx
import structlog
from structlog.contextvars import bind_contextvars

from . import shifts
from .auditlog import AuditLog
from .inzetrooster import Inzetrooster


@click.group()
@click.option(
    "--org", default="rvliethorp", envvar="ORGANIZATION", help="Organization name"
)
@click.option("--user", prompt=True, envvar="USERNAME", help="Username")
@click.password_option(envvar="PASSWORD", confirmation_prompt=False)
@click.option("--auditlog", envvar="AUDITLOG", default="audit.db")
@click.pass_context
def main(ctx: click.Context, org: str, user: str, password: str, auditlog: str):
    """Add-on utilities for inzetrooster"""
    structlog.configure()
    if not sys.stdout.isatty():
        structlog.configure(
            processors=structlog.get_config()["processors"][:-1]
            + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ]
        )
    bind_contextvars(org=org)
    ctx.obj = {
        "user": user,
        "password": password,
        "org": org,
        "auditlog": auditlog,
    }


@main.command()
@click.pass_obj
def export_shifts(obj: dict[str, str]):
    """Export shifts"""
    with httpx.Client(follow_redirects=True) as client:
        ir = Inzetrooster(client, obj["org"])
        ir.login(obj["user"], obj["password"])
        print(ir.export_shifts())


@main.command()
@click.pass_obj
def send_shift_mails(obj: dict[str, str]) -> None:
    """Send a thank-you mail for new shift assignments"""
    auditlog = AuditLog(obj["auditlog"])
    try:
        with httpx.Client(follow_redirects=True) as client:
            ir = Inzetrooster(client, obj["org"])
            ir.login(obj["user"], obj["password"])
            all_shifts = shifts.parse_csv(ir.export_shifts())
            shifts.send_shift_mails(auditlog, all_shifts)
    finally:
        auditlog.close()


if __name__ == "__main__":
    main()

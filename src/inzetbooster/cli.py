import logging
import sys
from typing import BinaryIO

import click
import httpx
import structlog
from structlog.contextvars import bind_contextvars

from . import shifts, users
from .auditlog import AuditLog
from .inzetrooster import Inzetrooster
from .mailer import Mailer


@click.group()
@click.option(
    "--org", default="rvliethorp", envvar="ORGANIZATION", help="Organization name"
)
@click.option("--user", prompt=True, envvar="USERNAME", help="Username")
@click.password_option(envvar="PASSWORD", confirmation_prompt=False)
@click.option("--auditlog", envvar="AUDITLOG", default="audit.db")
@click.option("-v", "--verbose", count=True)
@click.pass_context
def main(
    ctx: click.Context, org: str, user: str, password: str, auditlog: str, verbose: int
):
    """Add-on utilities for inzetrooster"""
    log_level = logging.WARNING
    if verbose >= 2:
        log_level = logging.DEBUG
    elif verbose >= 1:
        log_level = logging.INFO
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )

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
@click.option("--smtp-server", envvar="SMTP_SERVER", help="SMTP server")
@click.option(
    "--smtp-port",
    envvar="SMTP_PORT",
    type=click.IntRange(min=1),
    help="SMTP port",
)
@click.option(
    "--smtp-use-ssl",
    envvar="SMTP_SSL",
    type=click.BOOL,
    default="Connect to SMTP server with SSL",
)
@click.option("--smtp-user", envvar="SMTP_USER", help="Username for SMTP server")
@click.option(
    "--smtp-password", envvar="SMTP_PASSWORD", help="Password for SMTP server"
)
@click.option(
    "--email-from-addr",
    envvar="EMAIL_FROM_ADDR",
    help="Email address to send mail from",
)
@click.option(
    "--email-from-name",
    envvar="EMAIL_FROM_NAME",
    default="Vrijwilligers coordinator",
    help="Name of person sending the email",
)
@click.pass_obj
def send_shift_mails(
    obj: dict[str, str],
    email_from_addr: str,
    email_from_name: str,
    smtp_server: str,
    smtp_use_ssl: bool,
    smtp_port: int = 0,
    smtp_user: str | None = None,
    smtp_password: str | None = None,
) -> None:
    """Send a thank-you mail for new shift assignments"""
    auditlog = AuditLog(obj["auditlog"])
    mailer = Mailer(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        smtp_use_ssl=smtp_use_ssl,
        from_address=email_from_addr,
        from_name=email_from_name,
    )
    try:
        with httpx.Client(follow_redirects=True) as client:
            ir = Inzetrooster(client, obj["org"])
            ir.login(obj["user"], obj["password"])
            all_shifts = shifts.parse_csv(ir.export_shifts())
            shifts.send_shift_mails(auditlog, mailer, all_shifts)
    finally:
        auditlog.close()


@main.command()
@click.argument("manegeplan_export", type=click.File("rb"))
@click.pass_obj
def sync_users_from_manegeplan(obj: dict[str, str], manegeplan_export: BinaryIO):
    """Sync users with an export from manegeplan"""
    logger = structlog.stdlib.get_logger(__name__)

    logger.debug("reading manegeplan data", path=manegeplan_export.name)
    people = []
    for person in users.read_manegeplan_export(manegeplan_export):
        if not person.is_valid():
            logger.warn(
                "skipping invalid person", email=person.email, user_id=person.id
            )
        else:
            people.append(person)
    logger.info("finished parsing manegeplan data", user_count=len(people))

    with httpx.Client(follow_redirects=True) as client:
        ir = Inzetrooster(client, obj["org"])
        ir.login(obj["user"], obj["password"])
        existing_people = list(users.parse_csv(ir.export_users()))
        for person in existing_people:
            if not person.is_manegeplan_user():
                # Adding inzetrooster-native people to our list of people to
                # import will reactive their account.
                logger.info(
                    "adding non-manegeplan user to import list", email=person.email
                )
                people.append(person)
        ir.make_all_users_inactive()
        user_csv = users.create_csv(people)
        with open("/tmp/users.csv", "wb") as output:
            output.write(user_csv.encode("utf-8"))
        ir.import_users(user_csv)


if __name__ == "__main__":
    main()

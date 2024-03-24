import csv
import datetime
import io
from dataclasses import dataclass
from typing import Iterable

import jinja2
import structlog.stdlib
from structlog.contextvars import bound_contextvars
from babel.dates import format_date
from mjml import mjml2html

from .auditlog import AuditLog
from .mailer import Mailer

logger = structlog.stdlib.get_logger(__name__)


@dataclass()
class Shift:
    id: int
    group_id: int
    group_name: str
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    comments: str
    user_id: str | None = None
    user_name: str | None = None
    user_email: str | None = None

    @classmethod
    def from_record(self, record: dict[str, str]):
        logger.debug("parsing CSV record", data=record)
        return Shift(
            id=int(record["Dienst_id"]),
            group_id=int(record["Groep_id"]),
            group_name=record["Groep_naam"],
            date=datetime.datetime.strptime(record["Datum"], "%d-%m-%Y").date(),
            start_time=datetime.datetime.strptime(record["Starttijd"], "%H:%M").time(),
            end_time=datetime.datetime.strptime(record["Eindtijd"], "%H:%M").time(),
            user_id=record["Gebruiker_id"] if record["Gebruiker_id"] else None,
            user_name=record["Naam"] if record["Naam"] else None,
            user_email=record["Email"] if record["Email"] else None,
            comments=record["Opmerkingen"],
        )

    @property
    def is_covered(self) -> bool:
        return self.user_id is not None


def parse_csv(f: str) -> Iterable[Shift]:
    reader = csv.DictReader(io.StringIO(f), dialect=csv.unix_dialect)
    return [Shift.from_record(row) for row in reader]


def send_shift_mails(auditlog: AuditLog, mailer: Mailer, shifts: Iterable[Shift]):
    env = create_jinja_environment()

    for shift in shifts:
        _send_shift_mail(env, auditlog, mailer, shift)


def create_jinja_environment(locale: str = "nl_NL") -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("inzetbooster"),
        autoescape=jinja2.select_autoescape(),
    )

    def filter_date_format(value: datetime.date):
        return format_date(value, "EEEE d MMMM", locale=locale)

    env.filters["format_date"] = filter_date_format
    return env


def _send_shift_mail(
    env: jinja2.Environment, auditlog: AuditLog, mailer: Mailer, shift: Shift
) -> None:
    with bound_contextvars(
        shift_id=shift.id,
        group_id=shift.group_id,
        group_name=shift.group_name,
        comments=shift.comments,
        user_email=shift.user_email,
        date=f"{shift.date.strftime("%Y-%m-%d")} {shift.start_time.strftime("%H:%M")}",
    ):
        if not shift.is_covered:
            logger.debug("shift is not covered, skipping")
            return
        mail_template_id = f"shift-{shift.group_id}.html"
        if auditlog.was_mail_send(shift.id, mail_template_id, shift.user_email):
            logger.debug("email already send for this shift")
            return
        logger.debug("generating email for shift")

        try:
            template = env.get_template(mail_template_id)
        except jinja2.TemplateNotFound:
            logger.error(
                "template was not found, can not send email", template=mail_template_id
            )
            return
        subject = f"Aanmelding dienst {shift.group_name}"
        mjml = template.render(
            {
                "subject": subject,
                "name": shift.user_name,
                "date": shift.date,
                "start_time": shift.start_time,
                "end_time": shift.end_time,
            }
        )
        html = mjml2html(mjml)
        msg_id = mailer.send(
            to_addr=shift.user_email,
            to_name=shift.user_name,
            subject=subject,
            html=html,
        )
        logger.info("shift email successfully sent")
        auditlog.log_mail(shift.id, mail_template_id, shift.user_email, msg_id)

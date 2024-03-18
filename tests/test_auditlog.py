from inzetbooster.auditlog import AuditLog


def test_mail_log() -> None:
    auditor = AuditLog(path=":memory:")
    assert not auditor.was_mail_send(145, "bar-shift", "alice@example.com")
    auditor.log_mail(145, "bar-shift", "alice@example.com", "msgid")
    assert auditor.was_mail_send(145, "bar-shift", "alice@example.com")
    assert not auditor.was_mail_send(146, "bar-shift", "alice@example.com")
    assert not auditor.was_mail_send(145, "shift-cancelled", "alice@example.com")

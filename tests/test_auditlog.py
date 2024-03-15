from inzetbooster.auditlog import AuditLog


def test_mail_log() -> None:
    auditor = AuditLog(path=":memory:")
    assert not auditor.was_mail_send("bar-shift", "alice@example.com")
    auditor.log_mail("bar-shift", "alice@example.com", "12345")
    assert auditor.was_mail_send("bar-shift", "alice@example.com")

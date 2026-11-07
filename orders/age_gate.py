import fcntl
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect


PUBLIC_PAGE = re.compile(r"^/(?:stores/[a-z0-9-]+/)?$")


def safe_public_path(value):
    return value if value and PUBLIC_PAGE.fullmatch(value) else "/"


def log_path():
    return Path(getattr(settings, "AGE_VERIFICATION_LOG_PATH", settings.BASE_DIR / "data" / "age_verification.jsonl"))


def append_age_log(request, birthdate, age, answer, allowed, page_path):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": request.META.get("REMOTE_ADDR", ""),
        "birthdate": birthdate,
        "age": age,
        "answer_21_or_older": answer,
        "allowed": allowed,
        "page": page_path,
    }
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_APPEND | os.O_RDWR, 0o600)
    os.fchmod(descriptor, 0o600)
    with os.fdopen(descriptor, "a+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        fcntl.flock(handle, fcntl.LOCK_UN)


def read_age_logs():
    path = log_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_SH)
        lines = handle.readlines()
        fcntl.flock(handle, fcntl.LOCK_UN)
    records = []
    for line in reversed(lines):
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def clear_age_logs():
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_APPEND | os.O_RDWR, 0o600)
    os.fchmod(descriptor, 0o600)
    with os.fdopen(descriptor, "a+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        handle.truncate()
        handle.flush()
        os.fsync(handle.fileno())
        fcntl.flock(handle, fcntl.LOCK_UN)


class PublicAgeGateMiddleware:
    """A home-page attestation covers the public site for the current session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET" and PUBLIC_PAGE.fullmatch(request.path):
            if not request.session.get("age_verified_via_home") and request.session.pop("age_gate_allowed_path", None) != request.path:
                return redirect(f"/age-check/?{urlencode({'next': request.path})}")
        return self.get_response(request)

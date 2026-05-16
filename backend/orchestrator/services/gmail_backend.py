from __future__ import annotations

import ssl
from pathlib import Path

import certifi
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.utils.functional import cached_property


class CertifiEmailBackend(EmailBackend):
    @cached_property
    def ssl_context(self):
        if getattr(settings, "EMAIL_ALLOW_INSECURE_TLS", False):
            return ssl._create_unverified_context()
        cafile = Path(certifi.__file__).resolve().parent / "cacert.pem"
        context = ssl.create_default_context(cafile=str(cafile))
        if self.ssl_certfile or self.ssl_keyfile:
            context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
        return context

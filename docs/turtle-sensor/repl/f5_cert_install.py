"""REPL helper to exercise a single F5Cert install.

Copy/paste this into a Python REPL (or run as a script) to perform one
certificate install against a target BIG-IP CSSL profile.
"""
import logging

from app.cert.model import F5Cert
from conftest import get_chain_pem, get_crt_pem, get_key_pem

CSSL_PROF = "/Common/enrolltest.opentext.cloud"
PROJECT_ID = "Common"  # partition; defaults from cssl_prof if omitted
CN = "enrolltest.opentext.cloud"


def lookup_device():
    from app.device.lookup import get_device
    device = get_device(name="lit-elb05-p001")
    return device


def build_cert_attachment(device):
    """Load PEMs, fingerprint the cert, and prepare the F5Cert attachment."""
    crt_pem = get_crt_pem()
    key_pem = get_key_pem()
    chain_pem = get_chain_pem()

    f5cert = F5Cert(
        device=device,
        # project_id=PROJECT_ID,
        cssl_prof=CSSL_PROF,
        certfile={
            "cn": CN,
            "crt_pem": crt_pem,
            "key_pem": key_pem,
            "chain_pem": chain_pem,
        },
    )
    f5cert.logger = logging.getLogger("repl-f5cert")
    return f5cert


def readiness_report(f5cert: F5Cert):
    """Return a dictionary of quick checks before running an install."""

    certfile = f5cert.certfile or {}

    def _get_cert_attr(name: str):
        """Return PEM attributes from either CertFile objects or plain dicts."""

        if isinstance(certfile, dict):
            return certfile.get(name)
        return getattr(certfile, name, None)
    return {
        "device_name": getattr(f5cert.device, "name", ""),
        "has_proxy": bool(getattr(f5cert.device, "proxy", None)),
        "has_credentials": bool(getattr(f5cert.device, "user", None))
        and bool(getattr(f5cert.device, "pwd", None)),
        "cssl_profile": f5cert.cssl_prof,
        "project_id": f5cert.project_id,
        "has_scope_key": bool(getattr(f5cert, "scope_key", None)),
        "has_cert_pem": bool(_get_cert_attr("crt_pem")),
        "has_chain_pem": bool(_get_cert_attr("chain_pem")),
        "has_key_pem": bool(_get_cert_attr("key_pem")),
    }


def log_readiness(f5cert: F5Cert):
    """Log the pre-install checks in a readable format for REPL use."""

    logger = getattr(f5cert, "logger", logging.getLogger("repl-f5cert"))
    report = readiness_report(f5cert)

    logger.info("Pre-install readiness checks:")
    for key, value in report.items():
        logger.info("  %s: %s", key, value)

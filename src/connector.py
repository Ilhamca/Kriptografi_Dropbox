"""Secure external-site connector helpers.

This module provides a thin wrapper around `requests.Session` that:
- enforces TLS certificate verification by default
- applies sensible timeouts and retries
- allows using a custom CA bundle or client certs when needed
- serializes/deserializes cookies to/from simple dicts for storing in a DB

Usage:
    from src.connector import make_session_from_cookie, secure_session_with_retries

    s = secure_session_with_retries(verify=True)
    r = s.get("https://example.com/protected", timeout=10)

    # To persist cookies returned by the site into DB, call cookies_to_dict(s.cookies)
    cookie_dict = cookies_to_dict(s.cookies)

    # Later, rebuild the session with stored cookies:
    s2 = make_session_from_cookie(cookie_dict, verify=True)

"""
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import logging

LOG = logging.getLogger(__name__)


def secure_session_with_retries(
    verify: bool = True,
    ca_bundle: Optional[str] = None,
    client_cert: Optional[str] = None,
    timeout: int = 10,
    max_retries: int = 3,
    backoff_factor: float = 0.3,
) -> requests.Session:
    """Create a requests.Session with secure defaults and retry behavior.

    Args:
        verify: whether to verify TLS certificates. If False, TLS verification is disabled (not recommended).
        ca_bundle: path to a CA bundle file to use for verification (overrides system CA bundle).
        client_cert: path to client cert file (or tuple (cert, key)) to use for mTLS.
        timeout: default timeout (in seconds) for use by callers; session does not itself enforce per-request timeout,
                 so callers should pass `timeout=` to session methods.
        max_retries: number of retries for idempotent requests.
        backoff_factor: backoff factor applied between retry attempts.

    Returns:
        Configured requests.Session
    """
    s = requests.Session()

    # Enforce TLS verification by default; allow custom CA bundle
    if ca_bundle:
        s.verify = ca_bundle
    else:
        s.verify = verify

    # Optionally set client certificate for mutual TLS
    if client_cert:
        s.cert = client_cert

    # Configure retries for idempotent methods
    retries = Retry(
        total=max_retries,
        read=max_retries,
        connect=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "OPTIONS", "PUT", "DELETE"),
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)

    # Good to have server-side default timeout value enforced by callers
    s.request_timeout = timeout  # informational only

    return s


def cookies_to_dict(cookiejar: requests.cookies.RequestsCookieJar) -> Dict[str, Dict[str, Any]]:
    """Serialize cookiejar to a simple dict suitable for JSON storage.

    Format: {cookie_name: {"value": ..., "domain": ..., "path": ..., "expires": ...}}
    """
    out: Dict[str, Dict[str, Any]] = {}
    for c in cookiejar:
        out[c.name] = {
            "value": c.value,
            "domain": c.domain,
            "path": c.path,
            "expires": c.expires,
            "secure": c.secure,
            "httponly": getattr(c, "rest", {}).get("HttpOnly", False),
        }
    return out


def make_session_from_cookie(cookie_dict: Dict[str, Dict[str, Any]], verify: bool = True, ca_bundle: Optional[str] = None) -> requests.Session:
    """Rebuild a requests.Session and populate its cookie jar from a stored cookie dict.

    Args:
        cookie_dict: cookie mapping previously returned by `cookies_to_dict`.
        verify: TLS verification setting for the session.
        ca_bundle: optional CA bundle path.
    """
    s = requests.Session()
    if ca_bundle:
        s.verify = ca_bundle
    else:
        s.verify = verify

    for name, info in cookie_dict.items():
        try:
            s.cookies.set(name, info["value"], domain=info.get("domain"), path=info.get("path", "/"))
        except Exception:
            LOG.exception("failed to set cookie %s", name)

    return s


def attach_cookie_to_session(s: requests.Session, name: str, value: str, domain: Optional[str] = None, path: str = "/") -> None:
    """Helper to attach a single cookie to a session's cookiejar."""
    s.cookies.set(name, value, domain=domain, path=path)


def example_login_and_save_cookies(login_url: str, payload: Dict[str, Any], ca_bundle: Optional[str] = None) -> Dict[str, Any]:
    """Example flow: log in to external site and return cookie dict and expiry.

    This is a convenience helper for demos. In production, handle errors, rate limits, and do not store raw passwords.
    """
    s = secure_session_with_retries(verify=True if not ca_bundle else ca_bundle, ca_bundle=ca_bundle)
    r = s.post(login_url, data=payload, timeout=15)
    r.raise_for_status()

    cookie_dict = cookies_to_dict(s.cookies)
    # Compute an approximate expiry (use the earliest cookie expiry or None)
    expires = None
    for info in cookie_dict.values():
        if info.get("expires"):
            if expires is None or (info["expires"] and info["expires"] < expires):
                expires = info["expires"]

    return {"cookies": cookie_dict, "expires": expires}

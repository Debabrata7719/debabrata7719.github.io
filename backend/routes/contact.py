"""
routes/contact.py - POST /contact endpoint with rate limiting and strict MX verification.

Validates the incoming payload, performs strict Mail Exchange (MX) DNS verification
to block fake/disposable domains, forwards legitimate messages to Resend, and returns
a structured response. Rate-limited to 5 requests per IP per 10 minutes.
"""

import logging
import dns.resolver
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.schemas.contact import ContactRequest, ContactResponse
from backend.services.email_service import send_contact_email

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Contact"])

# Common disposable / temporary email domains to reject instantly
DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "guerrillamail.com", "10minutemail.com",
    "sharklasers.com", "yopmail.com", "throwawaymail.com", "trashmail.com",
    "fucker.com", "dispostable.com", "getairmail.com", "temp-mail.org",
}


def verify_email_domain(email: str) -> bool:
    """Strictly verify that the domain has legitimate active Mail Exchange (MX) servers."""
    try:
        if "@" not in email:
            return False

        domain = email.split("@")[-1].strip().lower()

        # 1. Check basic domain structure
        if not domain or "." not in domain:
            return False

        # 2. Check known disposable / spam domains
        if domain in DISPOSABLE_DOMAINS:
            logger.info("Blocked known spam/disposable domain: %s", domain)
            return False

        # 3. Strict MX DNS query (must have genuine mail exchange records)
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3.0
        resolver.lifetime = 3.0

        try:
            mx_records = resolver.resolve(domain, "MX")
            valid_mx = [
                str(r.exchange).rstrip(".")
                for r in mx_records
                if str(r.exchange).strip() not in (".", "")
            ]
            if not valid_mx:
                logger.info("Domain %s has empty or null MX record", domain)
                return False
            return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            logger.info("Domain %s has no active MX records", domain)
            return False
        except dns.resolver.Timeout:
            logger.warning("DNS timeout querying MX for %s", domain)
            return False

    except Exception as exc:
        logger.error("Unexpected error verifying domain %s: %s", email, exc)
        return False


@router.post(
    "/contact",
    response_model=ContactResponse,
    summary="Submit contact form",
    description=(
        "Validates the payload, verifies valid MX mail records on the domain, "
        "sends an email via Resend, and returns a success response. "
        "Rate-limited to 5 requests per IP per 10 minutes."
    ),
)
@limiter.limit("5/10minute")
async def submit_contact(
    request: Request,
    payload: ContactRequest,
) -> ContactResponse:
    """Handle a contact form submission."""
    logger.info(
        "Contact form submission received from '%s' <%s>",
        payload.name,
        payload.email,
    )

    email_str = str(payload.email).strip()

    # Verify that the email domain actually has mail servers configured to receive emails
    if not verify_email_domain(email_str):
        logger.warning("Rejected fake/invalid email domain: %s", email_str)
        raise HTTPException(
            status_code=400,
            detail="The email domain does not have active mail servers. Please enter a valid, active email address.",
        )

    try:
        send_contact_email(
            name=payload.name,
            sender_email=email_str,
            subject=payload.subject,
            message=payload.message,
        )
    except RuntimeError as exc:
        logger.error("Email service error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to deliver your message. Please try again later.",
        ) from exc

    logger.info("Contact email delivered for '%s'", payload.name)
    return ContactResponse(
        success=True,
        message="Your message has been sent! I'll get back to you soon.",
    )

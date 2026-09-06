"""
routes/contact.py - POST /contact endpoint with rate limiting and DNS MX verification.

Validates the incoming payload, verifies the sender's email domain has active
mail servers (MX records), forwards it to the email service, and returns a
structured response. Rate-limited to 5 requests per IP per 10 minutes to prevent spam.
"""

import logging
import dns.resolver
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.schemas.contact import ContactRequest, ContactResponse
from backend.services.email_service import send_contact_email

logger = logging.getLogger(__name__)

# Limiter is configured globally in main.py; importing it here so
# the decorator below can reference it without circular imports.
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Contact"])


def verify_email_domain(email: str) -> bool:
    """Verify that the email's domain actually has active mail exchange (MX) servers."""
    try:
        domain = email.split("@")[-1].strip().lower()
        if not domain or "." not in domain:
            return False

        # Query DNS for MX records
        try:
            records = dns.resolver.resolve(domain, "MX", lifetime=3.0)
            if records:
                return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout):
            pass

        # Fallback: check A record (RFC 5321 permits direct A-record host routing if no MX exists)
        try:
            records = dns.resolver.resolve(domain, "A", lifetime=2.0)
            if records:
                return True
        except Exception:
            pass

        return False
    except Exception as e:
        logger.warning("DNS lookup failed for %s: %s", email, e)
        # In case of internal DNS timeout/error, allow request to proceed
        return True


@router.post(
    "/contact",
    response_model=ContactResponse,
    summary="Submit contact form",
    description=(
        "Validates the payload, checks for active MX records on the email domain, "
        "sends an email to the portfolio owner via Resend, and returns a success response. "
        "Rate-limited to 5 requests per IP per 10 minutes."
    ),
)
@limiter.limit("5/10minute")
async def submit_contact(
    request: Request,
    payload: ContactRequest,
) -> ContactResponse:
    """Handle a contact form submission.

    Args:
        request:  FastAPI Request object (required by slowapi).
        payload:  Validated ContactRequest body.

    Returns:
        ContactResponse with success=True on delivery, or raises
        HTTPException 400 on fake email domain or 500 on email failure.
    """
    logger.info(
        "Contact form submission received from '%s' <%s>",
        payload.name,
        payload.email,
    )

    # Validate that the email domain actually exists and accepts mail
    email_str = str(payload.email)
    if not verify_email_domain(email_str):
        logger.warning("Rejected contact form from invalid/non-existent domain: %s", email_str)
        raise HTTPException(
            status_code=400,
            detail="The email domain does not appear to be active or able to receive mail. Please use a real email address.",
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

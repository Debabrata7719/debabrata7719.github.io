"""
routes/contact.py — POST /contact endpoint with rate limiting.

Validates the incoming payload, forwards it to the email service,
and returns a structured response. Rate-limited to 5 requests per
IP per 10 minutes to prevent spam.
"""

import logging
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.schemas.contact import ContactRequest, ContactResponse
from backend.services.email_service import send_contact_email

logger = logging.getLogger(__name__)

# Limiter is configured globally in main.py; importing it here so
# the decorator below can reference it without circular imports.
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Contact"])


@router.post(
    "/contact",
    response_model=ContactResponse,
    summary="Submit contact form",
    description=(
        "Validates the payload, sends an email to the portfolio owner "
        "via Resend, and returns a success response. "
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
        HTTPException 500 on email failure.
    """
    logger.info(
        "Contact form submission received from '%s' <%s>",
        payload.name,
        payload.email,
    )

    try:
        send_contact_email(
            name=payload.name,
            sender_email=str(payload.email),
            subject=payload.subject,
            message=payload.message,
        )
    except RuntimeError as exc:
        logger.error("Email service error: %s", exc)
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="Failed to deliver your message. Please try again later.",
        ) from exc

    logger.info("Contact email delivered for '%s'", payload.name)
    return ContactResponse(
        success=True,
        message="Your message has been sent! I'll get back to you soon.",
    )

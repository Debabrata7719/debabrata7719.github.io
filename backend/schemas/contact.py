"""
schemas/contact.py — Pydantic models for the /contact endpoint.
"""

from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    """Incoming contact form payload."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Sender's full name",
        examples=["Debabrata Dey"],
    )
    email: EmailStr = Field(
        ...,
        description="Sender's email address",
        examples=["someone@example.com"],
    )
    subject: str = Field(
        default="New Contact Form Submission",
        max_length=200,
        description="Subject of the message",
        examples=["Project Inquiry"],
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Message body (10–2000 characters)",
        examples=["Hi! I'd love to collaborate on a project."],
    )


class ContactResponse(BaseModel):
    """Response returned after processing the contact form."""

    success: bool
    message: str

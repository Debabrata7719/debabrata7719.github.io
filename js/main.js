/**
 * main.js — Shared JavaScript for all portfolio pages.
 *
 * Features:
 * 1. Mobile navigation toggle
 * 2. Active nav-link highlighting
 * 3. Contact form submission with validation
 * 4. Scroll-triggered fade-in animations
 */

const API_BASE = "https://debabrata7719-github-io.onrender.com";

document.addEventListener("DOMContentLoaded", () => {

  // =========================================================
  // 1. Mobile Navigation
  // =========================================================

  const menuBtn = document.getElementById("menu-btn");
  const mobileNav = document.getElementById("mobile-nav");

  if (menuBtn && mobileNav) {
    menuBtn.addEventListener("click", () => {
      mobileNav.classList.toggle("open");

      const icon = menuBtn.querySelector(".material-symbols-outlined");

      if (icon) {
        icon.textContent = mobileNav.classList.contains("open")
          ? "close"
          : "menu";
      }
    });
  }

  // =========================================================
  // 2. Active Navigation Link
  // =========================================================

  const page =
    window.location.pathname.split("/").pop() || "index.html";

  document.querySelectorAll("[data-page]").forEach((link) => {
    if (link.dataset.page === page) {
      link.classList.add("active");
      link.style.opacity = "1";
      link.style.color = "var(--color-primary)";
    }
  });

  // =========================================================
  // 3. Contact Form
  // =========================================================

  const contactForm = document.getElementById("contact-form");

  if (contactForm) {
    contactForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const submitBtn = contactForm.querySelector(
        'button[type="submit"]'
      );

      const originalText = submitBtn.textContent;

      submitBtn.textContent = "Sending...";
      submitBtn.disabled = true;

      const subjectEl = contactForm.querySelector("#subject");

      const payload = {
        name: contactForm.querySelector("#name").value.trim(),
        email: contactForm.querySelector("#email").value.trim(),
        subject: subjectEl
          ? subjectEl.value.trim()
          : "New Contact Form Submission",
        message: contactForm.querySelector("#message").value.trim(),
      };

      // =====================================================
      // Client-side Validation
      // =====================================================

      if (payload.name.length < 2) {
        showToast(
          "Please enter your full name (minimum 2 characters).",
          "error"
        );
        resetButton();
        return;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!emailRegex.test(payload.email)) {
        showToast(
          "Please enter a valid email address.",
          "error"
        );
        resetButton();
        return;
      }

      if (payload.subject.length > 200) {
        showToast(
          "Subject cannot exceed 200 characters.",
          "error"
        );
        resetButton();
        return;
      }

      if (payload.message.length < 10) {
        showToast(
          "Message must be at least 10 characters long.",
          "error"
        );
        resetButton();
        return;
      }

      if (payload.message.length > 2000) {
        showToast(
          "Message cannot exceed 2000 characters.",
          "error"
        );
        resetButton();
        return;
      }

      // =====================================================
      // API Request
      // =====================================================

      try {

        const res = await fetch(`${API_BASE}/contact`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        // Rate limit

        if (res.status === 429) {
          showToast(
            "Too many requests. Please wait a few minutes before trying again.",
            "error"
          );
          return;
        }

        const data = await res.json();

        // Success

        if (res.ok && data.success) {
          showToast(
            data.message || "Message sent successfully!",
            "success"
          );

          contactForm.reset();
          return;
        }

        // =================================================
        // Backend Validation Errors
        // =================================================

        let errorMessage =
          "Something went wrong. Please try again.";

        if (Array.isArray(data.detail)) {

          const messages = [];

          data.detail.forEach((error) => {

            switch (error.loc[1]) {

              case "name":
                messages.push(
                  "• Please enter your full name (minimum 2 characters)."
                );
                break;

              case "email":
                messages.push(
                  "• Please enter a valid email address."
                );
                break;

              case "subject":
                messages.push(
                  "• Subject cannot exceed 200 characters."
                );
                break;

              case "message":
                messages.push(
                  "• Message must be at least 10 characters long."
                );
                break;

              default:
                messages.push(`• ${error.msg}`);
            }

          });

          errorMessage = messages.join("\n");

        } else if (typeof data.detail === "string") {

          errorMessage = data.detail;

        } else if (typeof data.message === "string") {

          errorMessage = data.message;

        }

        showToast(errorMessage, "error");

      } catch (err) {

        console.error(err);

        showToast(
          "Could not reach the server. Please try again later.",
          "error"
        );

      } finally {

        resetButton();

      }

      // =====================================================
      // Helper
      // =====================================================

      function resetButton() {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
      }

    });
  }

  // =========================================================
  // 4. Fade-in Animation
  // =========================================================

  const fadeEls = document.querySelectorAll(".fade-in");

  if (fadeEls.length > 0) {

    const observer = new IntersectionObserver(
      (entries) => {

        entries.forEach((entry) => {

          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }

        });

      },
      {
        threshold: 0.12,
      }
    );

    fadeEls.forEach((el) => observer.observe(el));

  }

});

// =========================================================
// Toast Helper
// =========================================================

function showToast(message, type = "success") {

  const existing = document.querySelector(".toast");

  if (existing) existing.remove();

  const toast = document.createElement("div");

  toast.className = `toast ${type}`;

  toast.textContent = message;

  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      toast.classList.add("show");
    });
  });

  setTimeout(() => {

    toast.classList.remove("show");

    setTimeout(() => toast.remove(), 400);

  }, 5000);

}
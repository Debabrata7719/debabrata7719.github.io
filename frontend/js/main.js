/**
 * main.js — Shared JavaScript for all portfolio pages.
 *
 * Features:
 *  1. Mobile navigation toggle
 *  2. Active nav-link highlighting per page
 *  3. Contact form → FastAPI /contact submission with toast feedback
 *  4. Scroll-triggered fade-in animations
 */

const API_BASE = 'http://localhost:8000';

// =========================================================
// 1. Mobile nav toggle
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.getElementById('menu-btn');
  const mobileNav = document.getElementById('mobile-nav');

  if (menuBtn && mobileNav) {
    menuBtn.addEventListener('click', () => {
      mobileNav.classList.toggle('open');
      const icon = menuBtn.querySelector('.material-symbols-outlined');
      if (icon) {
        icon.textContent = mobileNav.classList.contains('open') ? 'close' : 'menu';
      }
    });
  }

  // =========================================================
  // 2. Active nav-link highlighting
  // =========================================================
  const page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('[data-page]').forEach(link => {
    if (link.dataset.page === page) {
      link.classList.add('active');
      link.style.opacity = '1';
      link.style.color = 'var(--color-primary)';
    }
  });

  // =========================================================
  // 3. Contact form submission
  // =========================================================
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.textContent;

      // Loading state
      submitBtn.textContent = 'Sending…';
      submitBtn.disabled = true;

      const subjectEl = contactForm.querySelector('#subject');
      const payload = {
        name:    contactForm.querySelector('#name').value.trim(),
        email:   contactForm.querySelector('#email').value.trim(),
        subject: subjectEl ? subjectEl.value.trim() : 'New Contact Form Submission',
        message: contactForm.querySelector('#message').value.trim(),
      };

      try {
        const res = await fetch(`${API_BASE}/contact`, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(payload),
        });

        if (res.status === 429) {
          showToast('Too many requests — please wait a few minutes.', 'error');
          return;
        }

        const data = await res.json();

        if (res.ok && data.success) {
          showToast(data.message || 'Message sent! 🎉', 'success');
          contactForm.reset();
        } else {
          showToast(data.detail || 'Something went wrong. Please try again.', 'error');
        }
      } catch (err) {
        console.error('Contact form error:', err);
        showToast('Could not reach the server. Please try again later.', 'error');
      } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
      }
    });
  }

  // =========================================================
  // 4. Scroll-triggered fade-in
  // =========================================================
  const fadeEls = document.querySelectorAll('.fade-in');
  if (fadeEls.length > 0) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    fadeEls.forEach(el => observer.observe(el));
  }
});

// =========================================================
// Toast helper
// =========================================================
function showToast(message, type = 'success') {
  // Remove any existing toast
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  // Trigger CSS transition
  requestAnimationFrame(() => {
    requestAnimationFrame(() => toast.classList.add('show'));
  });

  // Auto-hide after 5 s
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 5000);
}

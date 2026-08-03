/* ============================================
   Clinical Neuroimaging Lab — interactivity
   Vanilla JS, no dependencies.
   ============================================ */

(function () {
  'use strict';

  /* ---------- Sticky header shadow on scroll ---------- */
  const header = document.querySelector('.site-header');
  if (header) {
    const onScroll = () => {
      if (window.scrollY > 8) header.classList.add('scrolled');
      else header.classList.remove('scrolled');
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Active nav link ----------
     The nav markup is shared across pages (see partials/header.html), so the
     active link is no longer hard-coded per page. We set aria-current="page"
     on whichever primary-nav link matches the current file; CSS styles it via
     .nav-links a[aria-current="page"]. */
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a[href]').forEach(link => {
    if (link.getAttribute('href') === currentPage) {
      link.setAttribute('aria-current', 'page');
    }
  });

  /* ---------- Mobile nav toggle ---------- */
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      navLinks.classList.toggle('open', !open);
      document.body.style.overflow = !open ? 'hidden' : '';
    });

    // Close menu on link click (mobile)
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (navLinks.classList.contains('open')) {
          toggle.setAttribute('aria-expanded', 'false');
          navLinks.classList.remove('open');
          document.body.style.overflow = '';
        }
      });
    });
  }

  /* ---------- Scroll-fade-in via IntersectionObserver ---------- */
  const fadeEls = document.querySelectorAll('.fade-in');
  if (fadeEls.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -50px 0px' });
    fadeEls.forEach(el => io.observe(el));
  } else {
    // Fallback: show everything
    fadeEls.forEach(el => el.classList.add('visible'));
  }

  /* ---------- Publications: year filter + search ---------- */
  const pubSearch = document.getElementById('pub-search');
  const yearChips = document.querySelectorAll('.year-chip');
  const pubItems = document.querySelectorAll('.pub-item');
  const noResults = document.querySelector('.no-results');

  if (pubItems.length) {
    let currentYear = 'all';
    let currentQuery = '';

    const apply = () => {
      let visible = 0;
      pubItems.forEach(item => {
        const year = item.dataset.year || '';
        const text = (item.textContent || '').toLowerCase();
        const yearMatch = currentYear === 'all' || year === currentYear;
        const queryMatch = !currentQuery || text.includes(currentQuery);
        const show = yearMatch && queryMatch;
        item.style.display = show ? '' : 'none';
        if (show) visible++;
      });
      if (noResults) noResults.style.display = visible === 0 ? 'block' : 'none';
    };

    yearChips.forEach(chip => {
      chip.addEventListener('click', () => {
        yearChips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentYear = chip.dataset.year;
        apply();
      });
    });

    if (pubSearch) {
      let timer;
      pubSearch.addEventListener('input', () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          currentQuery = pubSearch.value.trim().toLowerCase();
          apply();
        }, 120);
      });
    }
  }

  /* ---------- Photo lightbox ---------- */
  // Only tiles that actually hold an <img> are viewable. The gallery also renders
  // "coming soon" placeholder tiles which carry .photo-item for layout but have no
  // image inside, and opening one would dereference a null querySelector result.
  const photos = Array.from(document.querySelectorAll('.photo-item'))
    .filter(item => item.querySelector('img'));
  if (photos.length) {
    // Build lightbox
    const lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Photo viewer');
    lb.innerHTML = `
      <button class="lightbox-close" aria-label="Close">✕</button>
      <button class="lightbox-prev" aria-label="Previous photo">‹</button>
      <button class="lightbox-next" aria-label="Next photo">›</button>
      <img alt="" />
    `;
    document.body.appendChild(lb);
    const lbImg = lb.querySelector('img');
    const lbClose = lb.querySelector('.lightbox-close');
    const lbPrev = lb.querySelector('.lightbox-prev');
    const lbNext = lb.querySelector('.lightbox-next');

    let currentIndex = 0;
    const photoArr = photos;

    const open = (i) => {
      currentIndex = i;
      const img = photoArr[i].querySelector('img');
      lbImg.src = img.src;
      lbImg.alt = img.alt;
      lb.classList.add('open');
      document.body.style.overflow = 'hidden';
      lbClose.focus();
    };

    const close = () => {
      lb.classList.remove('open');
      document.body.style.overflow = '';
    };

    const nav = (delta) => {
      currentIndex = (currentIndex + delta + photoArr.length) % photoArr.length;
      const img = photoArr[currentIndex].querySelector('img');
      lbImg.src = img.src;
      lbImg.alt = img.alt;
    };

    photoArr.forEach((item, i) => {
      item.addEventListener('click', () => open(i));
      item.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          open(i);
        }
      });
      item.setAttribute('tabindex', '0');
      item.setAttribute('role', 'button');
      item.setAttribute('aria-label', 'View photo');
    });

    lbClose.addEventListener('click', close);
    lbPrev.addEventListener('click', () => nav(-1));
    lbNext.addEventListener('click', () => nav(1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });

    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') nav(-1);
      if (e.key === 'ArrowRight') nav(1);
    });
  }

  /* ---------- Set current year in footer ---------- */
  document.querySelectorAll('[data-current-year]').forEach(el => {
    el.textContent = new Date().getFullYear();
  });

})();

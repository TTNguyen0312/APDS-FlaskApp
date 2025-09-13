// static/js/product-detail.js
(function () {
  
  // 1) Thumbnail 
  const mainImg = document.querySelector('.product-detail__image-main img');
  const thumbsWrap = document.querySelector('.product-detail__thumbnails');

  if (thumbsWrap && mainImg) {
    thumbsWrap.addEventListener('click', (e) => {
      const btn = e.target.closest('.product-detail__thumbnail');
      if (!btn) return;

      const img = btn.querySelector('img');
      if (img && img.src) {
        mainImg.src = img.src;

        // active style
        thumbsWrap.querySelectorAll('.product-detail__thumbnail').forEach(b => {
          b.classList.remove('is-active');
          b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('is-active');
        btn.setAttribute('aria-selected', 'true');
      }
    });
  }

  // 2) Quantity +/- 
  const qtyWrap = document.querySelector('.product-detail__quantity-controls');
  if (qtyWrap) {
    const input = qtyWrap.querySelector('.product-detail__quantity-input');
    const min = parseInt(input?.getAttribute('min') || '1', 10);
    const maxAttr = input?.getAttribute('max');
    const max = maxAttr ? parseInt(maxAttr, 10) : Infinity;

    const clamp = (v) => Math.max(min, Math.min(max, v));

    qtyWrap.addEventListener('click', (e) => {
      const btn = e.target.closest('.product-detail__quantity-btn');
      if (!btn || !input) return;

      let v = parseInt(input.value || min, 10);
      if (isNaN(v)) v = min;

      if (btn.dataset.action === 'inc') v = clamp(v + 1);
      if (btn.dataset.action === 'dec') v = clamp(v - 1);

      input.value = v;
    });


    if (input) {
      input.addEventListener('input', () => {
        const digits = input.value.replace(/[^\d]/g, '');
        input.value = digits === '' ? '' : clamp(parseInt(digits, 10));
      });
      input.addEventListener('blur', () => {
        let v = parseInt(input.value || min, 10);
        if (isNaN(v)) v = min;
        input.value = clamp(v);
      });
    }
  }

   // ===== 3) REVIEWS  =====
  const root = document.querySelector('main.product-detail');
  const clothId = root?.dataset?.clothId ? String(root.dataset.clothId) : null;

  const form = document.getElementById('reviewForm');
  const titleInput = document.getElementById('reviewTitle');
  const textInput  = document.getElementById('reviewText');
  const errorEl    = document.getElementById('reviewError');
  const listEl     = document.getElementById('reviewsList');

  if (!clothId || !form || !titleInput || !textInput || !listEl) return;

  function escapeHTML(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function renderReviewItem(r) {
    const wrap = document.createElement('article');
    wrap.className = 'product-reviews__item';
    wrap.innerHTML = `
      <div class="product-reviews__item-avatar" aria-hidden="true"></div>
      <div class="product-reviews__item-body">
        <h4 class="product-reviews__item-title">${escapeHTML(r.reviewTitle)}</h4>
        <p class="product-reviews__item-text">${escapeHTML(r.reviewText)}</p>
      </div>
    `;
    return wrap;
  }

  async function loadReviews() {
    listEl.innerHTML = '';
    try {
      const res = await fetch(`/review/${clothId}`);
      const data = await res.json();
      const items = Array.isArray(data.review) ? data.review : [];
      if (!items.length) {
        listEl.innerHTML = `<p class="product-reviews__empty">No reviews yet. Be the first to review!</p>`;
        return;
      }
      const frag = document.createDocumentFragment();
      items.forEach(r => frag.appendChild(renderReviewItem(r)));
      listEl.appendChild(frag);
    } catch {
      listEl.innerHTML = `<p class="product-reviews__empty">Failed to load reviews.</p>`;
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorEl.hidden = true;

    const title = titleInput.value.trim();
    const text  = textInput.value.trim();

    if (!title || !text) {
      errorEl.textContent = 'Please fill in both title and review text.';
      errorEl.hidden = false;
      return;
    }

    try {
      const res = await fetch('/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clothId: String(clothId),
          reviewTitle: title,
          reviewText: text,
        }),
      });
      const data = await res.json();

      if (!res.ok) {
        errorEl.textContent = data?.message || 'Failed to create review.';
        errorEl.hidden = false;
        return;
      }

      const emptyMsg = listEl.querySelector('.product-reviews__empty');
      if (emptyMsg) emptyMsg.remove();


      const dom = renderReviewItem(data.review);
      const first = listEl.firstElementChild;
      if (first) listEl.insertBefore(dom, first); else listEl.appendChild(dom);

      titleInput.value = '';
      textInput.value  = '';

    } catch {
      errorEl.textContent = 'Network error. Please try again.';
      errorEl.hidden = false;
    }
  });
  async function loadProductFromAPI() {
  if (!clothId) return;
  try {
    //  API JSON: /item/{id}?format=json
    const res  = await fetch(`/item/${clothId}?format=json`, {
      headers: { Accept: 'application/json' }
    });
    const data = await res.json();
    const item = data?.items?.[0];
    if (!item) return;

    // title + description
    document.querySelector('.product-detail__title')?.replaceChildren(
      document.createTextNode(item.clothTitle ?? '')
    );
    document.querySelector('.product-detail__description')?.replaceChildren(
      document.createTextNode(item.clothDescription ?? '')
    );

    // price
    const priceEl = document.querySelector('.product-detail__price-value');
    if (priceEl && typeof item.price === 'number') {
      priceEl.textContent =
        new Intl.NumberFormat('vi-VN').format(item.price) + ' VND';
    }

    // images
    const imgs = Array.isArray(item.images) ? item.images : [];
    const mainImg = document.querySelector('.product-detail__image-main img');
    if (imgs[0] && mainImg) mainImg.src = imgs[0];

    const thumbsWrap = document.querySelector('.product-detail__thumbnails');
    if (thumbsWrap && imgs.length > 1) {
      thumbsWrap.innerHTML = imgs.slice(1).map((src, i) => `
        <button class="product-detail__thumbnail" aria-label="Thumbnail ${i+1}">
          <img src="${src}" alt="thumb ${i+1}" />
        </button>
      `).join('');
    }
  } catch {
   
  }
}

loadProductFromAPI();

  loadReviews();
})();
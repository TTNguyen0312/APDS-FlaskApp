document.addEventListener("DOMContentLoaded", () => {
  const reviewsPerPage = 5;
  const reviews = document.querySelectorAll(".product-reviews__item");
  const totalReviewPages = Math.ceil(reviews.length / reviewsPerPage);
  const paginationContainer = document.getElementById("reviews-pagination");
  let currentReviewPage = 1;

  function showReviewPage(page) {
    currentReviewPage = page;
    const start = (page - 1) * reviewsPerPage;
    const end = start + reviewsPerPage;

    reviews.forEach((review, index) => {
      review.style.display = index >= start && index < end ? "block" : "none";
    });

    renderReviewPagination();
  }

  function renderReviewPagination() {
    paginationContainer.innerHTML = "";

    if (currentReviewPage > 1) {
      const prev = document.createElement("li");
      prev.innerHTML = `<a href="#">«</a>`;
      prev.addEventListener("click", e => { e.preventDefault(); showReviewPage(currentReviewPage - 1); });
      paginationContainer.appendChild(prev);
    }

    const startPage = Math.max(1, currentReviewPage - 2);
    const endPage = Math.min(totalReviewPages, currentReviewPage + 2);

    if (startPage > 1) {
      const first = document.createElement("li");
      first.innerHTML = `<a href="#">1</a>`;
      first.addEventListener("click", e => { e.preventDefault(); showReviewPage(1); });
      paginationContainer.appendChild(first);

      if (startPage > 2) {
        const dots = document.createElement("li");
        dots.innerHTML = `<span>...</span>`;
        paginationContainer.appendChild(dots);
      }
    }

    for (let i = startPage; i <= endPage; i++) {
      const li = document.createElement("li");
      if (i === currentReviewPage) {
        li.innerHTML = `<span>${i}</span>`;
      } else {
        li.innerHTML = `<a href="#">${i}</a>`;
        li.addEventListener("click", e => { e.preventDefault(); showReviewPage(i); });
      }
      paginationContainer.appendChild(li);
    }

    if (endPage < totalReviewPages) {
      if (endPage < totalReviewPages - 1) {
        const dots = document.createElement("li");
        dots.innerHTML = `<span>...</span>`;
        paginationContainer.appendChild(dots);
      }

      const last = document.createElement("li");
      last.innerHTML = `<a href="#">${totalReviewPages}</a>`;
      last.addEventListener("click", e => { e.preventDefault(); showReviewPage(totalReviewPages); });
      paginationContainer.appendChild(last);
    }

    if (currentReviewPage < totalReviewPages) {
      const next = document.createElement("li");
      next.innerHTML = `<a href="#">»</a>`;
      next.addEventListener("click", e => { e.preventDefault(); showReviewPage(currentReviewPage + 1); });
      paginationContainer.appendChild(next);
    }
  }

  // Init reviews pagination
  if (reviews.length > 0) {
    showReviewPage(1);
  }

  // Handle form submission with fetch to /add-review
  const reviewForm = document.getElementById("reviewForm");
  if (reviewForm) {
    reviewForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const formData = new FormData(this);
      const data = Object.fromEntries(formData.entries());
      console.log(data);
      try {
        const res = await fetch("/add-review", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data)
        });

        if (!res.ok) throw new Error("Failed to submit review");

        // Reload page to see the new review
        window.location.reload();
      } catch (err) {
        document.getElementById("reviewError").innerText = err.message;
        document.getElementById("reviewError").hidden = false;
      }
    });
  }
});

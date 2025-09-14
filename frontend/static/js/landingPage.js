document.addEventListener("DOMContentLoaded", () => {
    const itemsPerPage = 12;
    const items = document.querySelectorAll(".product-item");
    const totalPages = Math.ceil(items.length / itemsPerPage);
    const paginationContainer = document.getElementById("pagination-controls");
    let currentPage = 1;

    function showPage(page) {
        currentPage = page;
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;

        items.forEach((item, index) => {
        item.style.display = index >= start && index < end ? "block" : "none";
        });

        renderPagination();
    }

    function renderPagination() {
        paginationContainer.innerHTML = "";

        if (currentPage > 1) {
        const prev = document.createElement("li");
        prev.innerHTML = `<a href="#">«</a>`;
        prev.addEventListener("click", e => { e.preventDefault(); showPage(currentPage - 1); });
        paginationContainer.appendChild(prev);
        }

        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        if (startPage > 1) {
        const li = document.createElement("li");
        li.innerHTML = `<a href="#">1</a>`;
        li.addEventListener("click", e => { e.preventDefault(); showPage(1); });
        paginationContainer.appendChild(li);

        if (startPage > 2) {
            const dots = document.createElement("li");
            dots.innerHTML = `<span>...</span>`;
            paginationContainer.appendChild(dots);
        }
        }

        for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement("li");
        if (i === currentPage) {
            li.innerHTML = `<span>${i}</span>`;
        } else {
            li.innerHTML = `<a href="#">${i}</a>`;
            li.addEventListener("click", e => { e.preventDefault(); showPage(i); });
        }
        paginationContainer.appendChild(li);
        }

        if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const dots = document.createElement("li");
            dots.innerHTML = `<span>...</span>`;
            paginationContainer.appendChild(dots);
        }

        const li = document.createElement("li");
        li.innerHTML = `<a href="#">${totalPages}</a>`;
        li.addEventListener("click", e => { e.preventDefault(); showPage(totalPages); });
        paginationContainer.appendChild(li);
        }

        if (currentPage < totalPages) {
        const next = document.createElement("li");
        next.innerHTML = `<a href="#">»</a>`;
        next.addEventListener("click", e => { e.preventDefault(); showPage(currentPage + 1); });
        paginationContainer.appendChild(next);
        }
    }

    showPage(1);
});

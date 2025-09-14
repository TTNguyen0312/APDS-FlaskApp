// static/js/search.js
const toggle = document.getElementById('searchToggle');
const bar = document.getElementById('searchBar');
const closeBtn = document.getElementById('searchClose');
const input = document.getElementById('q');

function openBar() {
  bar.classList.add('open');
  toggle.setAttribute('aria-expanded', 'true');
  setTimeout(() => input && input.focus(), 0);
}
function closeBar() {
  bar.classList.remove('open');
  toggle.setAttribute('aria-expanded', 'false');
}
toggle?.addEventListener('click', (e) => {
  e.stopPropagation();
  bar.classList.contains('open') ? closeBar() : openBar();
});
closeBtn?.addEventListener('click', closeBar);
document.addEventListener('keydown', (e) => e.key === 'Escape' && closeBar());
document.addEventListener('click', (e) => {
  if (bar.classList.contains('open') && !bar.contains(e.target) && e.target !== toggle) closeBar();
});
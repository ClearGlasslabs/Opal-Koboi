document.addEventListener('click', function (event) {
  var button = event.target.closest('.opal-btn');
  if (!button || button.disabled || button.getAttribute('aria-disabled') === 'true') return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var rect = button.getBoundingClientRect();
  var mark = document.createElement('span');
  var size = Math.max(rect.width, rect.height) / 8;

  mark.className = 'opal-ripple';
  mark.style.left = String(event.clientX - rect.left) + 'px';
  mark.style.top = String(event.clientY - rect.top) + 'px';
  mark.style.width = String(size) + 'px';
  mark.style.height = String(size) + 'px';

  button.appendChild(mark);
  window.setTimeout(function () {
    mark.remove();
  }, 560);
});

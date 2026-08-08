/* Progressive interaction layer: no navigation, form, or application handlers are replaced. */
(() => {
  "use strict";

  const selector = [
    "button", ".btn", ".cta", "[role='button']",
    "input[type='submit']", "input[type='button']", "a.button", "a.btn",
    ".btn-primary", ".btn-ghost", ".nav-cta", ".navlinks a",
    ".mobile-menu a", ".journey-step", ".nextBridge", ".context-link"
  ].join(",");
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = matchMedia("(hover: hover) and (pointer: fine)");
  const controls = new Set();

  const classify = (control) => {
    const names = control.classList;
    if (names.contains("primary") || names.contains("btn-primary") || names.contains("nav-cta")) {
      names.add("btn--primary-future");
      control.dataset.futureMagnetic = "true";
    } else if (names.contains("ghost") || names.contains("btn-ghost") || names.contains("context-link") || control.closest(".navlinks, .mobile-menu")) {
      names.add("btn--glass-ghost");
    } else {
      names.add("btn--glass-secondary");
    }
  };

  const observer = "IntersectionObserver" in window ? new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      target.classList.toggle("is-future-visible", isIntersecting);
      target.dataset.futureActive = String(isIntersecting);
    });
  }, { rootMargin: "160px", threshold: 0 }) : null;

  const enhance = (root = document) => {
    const candidates = [];
    if (root.nodeType === 1 && root.matches(selector)) candidates.push(root);
    root.querySelectorAll?.(selector).forEach((item) => candidates.push(item));
    candidates.forEach((control) => {
      if (controls.has(control)) return;
      controls.add(control);
      control.classList.add("future-glass");
      classify(control);
      control.style.setProperty("--future-delay", `${Math.floor(Math.random() * 5000)}ms`);
      observer?.observe(control);
      if (!observer) {
        control.classList.add("is-future-visible");
        control.dataset.futureActive = "true";
      }
    });
  };

  let frame = 0;
  let pending;
  const renderPointer = () => {
    frame = 0;
    if (!pending || reduceMotion.matches || !finePointer.matches) return;
    const { control, clientX, clientY } = pending;
    if (control.dataset.futureActive !== "true") return;
    const rect = control.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const y = Math.max(0, Math.min(1, (clientY - rect.top) / rect.height));
    const distance = Math.max(0, 1 - Math.hypot(x - .5, y - .5) / .708);
    control.style.setProperty("--pointer-x", `${(x * 100).toFixed(1)}%`);
    control.style.setProperty("--pointer-y", `${(y * 100).toFixed(1)}%`);
    control.style.setProperty("--pointer-distance", distance.toFixed(3));
    if (control.dataset.futureMagnetic === "true") {
      control.style.setProperty("--magnetic-x", `${((x - .5) * 8).toFixed(2)}px`);
      control.style.setProperty("--magnetic-y", `${((y - .5) * 6).toFixed(2)}px`);
    }
  };

  document.addEventListener("pointermove", (event) => {
    const control = event.target.closest?.(".future-glass");
    if (!control || control.dataset.futureActive !== "true") return;
    pending = { control, clientX: event.clientX, clientY: event.clientY };
    if (!frame) frame = requestAnimationFrame(renderPointer);
  }, { passive: true });

  document.addEventListener("pointerout", (event) => {
    const control = event.target.closest?.(".future-glass");
    if (!control || control.contains(event.relatedTarget)) return;
    control.style.removeProperty("--magnetic-x");
    control.style.removeProperty("--magnetic-y");
    control.style.setProperty("--pointer-distance", "0");
  }, { passive: true });

  document.addEventListener("click", (event) => {
    const control = event.target.closest?.(".future-glass[aria-busy='true']");
    if (control) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  }, true);

  enhance();
  new MutationObserver((records) => records.forEach((record) => record.addedNodes.forEach(enhance)))
    .observe(document.documentElement, { childList: true, subtree: true });
})();

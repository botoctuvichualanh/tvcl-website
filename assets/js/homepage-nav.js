(() => {
  const initialize = () => {
    document.querySelectorAll("nav.main-nav > details.nav-group").forEach((group) => {
      group.addEventListener("pointerenter", (event) => {
        if (event.pointerType === "touch") return;
        const nav = group.closest("nav.main-nav");
        nav.querySelectorAll(":scope > details.nav-group").forEach((sibling) => {
          if (sibling !== group) sibling.open = false;
        });
        group.open = true;
      });

      group.addEventListener("pointerleave", (event) => {
        if (event.pointerType === "touch") return;
        group.open = false;
      });

      group.addEventListener("focusout", (event) => {
        if (!group.contains(event.relatedTarget)) group.open = false;
      });
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();

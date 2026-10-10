/* Original MIT Docsify hooks. No learner state or third-party requests. */
(function () {
  function prepareScrollAreas() {
    const vi = document.documentElement.lang === 'vi';
    document.querySelectorAll('.markdown-section table, .markdown-section pre').forEach(node => {
      if (node.scrollWidth > node.clientWidth + 1) {
        node.tabIndex = 0;
        node.setAttribute('aria-label', vi
          ? 'Nội dung rộng, dùng phím mũi tên để cuộn ngang'
          : 'Wide content, use arrow keys to scroll horizontally');
      } else {
        node.removeAttribute('tabindex');
        node.removeAttribute('aria-label');
      }
    });
  }
  const reading = (hook, vm) => {
    hook.doneEach(() => {
      document.documentElement.lang = vm.route.path.startsWith('/vi/') ? 'vi' : 'en';
      const heading = document.querySelector('.markdown-section h1');
      if (heading) document.title = heading.textContent.trim();
      prepareScrollAreas();
    });
  };
  window.$docsify.plugins = [...(window.$docsify.plugins || []), reading];
  window.addEventListener('resize', prepareScrollAreas);
  document.addEventListener('toggle', prepareScrollAreas, true);
}());

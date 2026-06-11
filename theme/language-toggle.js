(function () {
  function counterpart(pathname) {
    if (pathname.includes('/en/')) {
      return pathname.replace('/en/', '/zh/');
    }
    if (pathname.includes('/zh/')) {
      return pathname.replace('/zh/', '/en/');
    }
    return null;
  }

  var target = counterpart(window.location.pathname);
  if (!target) {
    return;
  }

  var content = document.querySelector('main') || document.querySelector('.content');
  if (!content) {
    return;
  }

  var bar = document.createElement('div');
  bar.className = 'language-toggle';

  var current = document.createElement('span');
  current.textContent = window.location.pathname.includes('/zh/') ? '当前: 中文' : 'Current: English';

  var link = document.createElement('a');
  link.href = target + window.location.search + window.location.hash;
  link.textContent = window.location.pathname.includes('/zh/') ? 'English' : '中文';

  bar.appendChild(current);
  bar.appendChild(link);
  content.insertBefore(bar, content.firstChild);
})();

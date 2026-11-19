(() => {
  const button = document.getElementById('language-toggle');
  if (!button) {
    return;
  }
  function setLanguage(language) {
    const lang = language === 'en' ? 'en' : 'ar';
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.querySelectorAll('[data-ar][data-en]').forEach(el => { el.textContent = el.dataset[lang]; });
    button.textContent = lang === 'ar' ? 'EN' : 'عربي';
    button.setAttribute('aria-label', lang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية');
    document.title = lang === 'ar' ? 'ESAS PRIME | تقنية بلا حدود' : 'ESAS PRIME | Technology Without Boundaries';
    try { localStorage.setItem('esas-language', lang); } catch (_) {}
  }
  let saved = 'ar';
  try { saved = localStorage.getItem('esas-language') || 'ar'; } catch (_) {}
  setLanguage(saved);
  button.addEventListener('click', () => setLanguage(document.documentElement.lang === 'ar' ? 'en' : 'ar'));
})();

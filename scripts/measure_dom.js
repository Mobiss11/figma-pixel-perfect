// Численный аудит вёрстки против спеки Figma.
// Вставь в browser_evaluate / playwright page.evaluate как СТРОКУ
// (не TS-стрелку: tsx-обёртки ломаются в браузерном контексте).
//
// Использование: подставь свои селекторы в SELECTORS и сравни
// вывод с ожиданиями из get_metadata / get_design_context.
(() => {
  // селектор → короткое имя элемента из макета
  const SELECTORS = {
    // '.hero h1': 'Заголовок',
    // '.hero button': 'Кнопка CTA',
  };
  const props = [
    'fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing',
    'color', 'backgroundColor', 'borderRadius', 'boxShadow',
    'padding', 'margin', 'gap', 'display', 'alignItems', 'justifyContent',
  ];
  const out = { viewport: { w: innerWidth, h: innerHeight, dpr: devicePixelRatio }, elements: {}, counts: {} };
  for (const [sel, name] of Object.entries(SELECTORS)) {
    const el = document.querySelector(sel);
    if (!el) { out.elements[name] = 'NOT FOUND: ' + sel; continue; }
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const styles = {};
    for (const p of props) styles[p] = cs[p];
    out.elements[name] = {
      rect: { x: +r.x.toFixed(1), y: +r.y.toFixed(1), w: +r.width.toFixed(1), h: +r.height.toFixed(1) },
      styles,
      text: (el.textContent || '').trim().slice(0, 80),
    };
  }
  // Счётчики против числа скачанных ассетов — ловят выдуманные и задублированные иконки
  out.counts.svg = document.querySelectorAll('svg').length;
  out.counts.img = document.querySelectorAll('img').length;
  out.counts.bgImages = [...document.querySelectorAll('*')]
    .filter(e => getComputedStyle(e).backgroundImage !== 'none').length;
  return JSON.stringify(out, null, 2);
})();

import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT = path.resolve(import.meta.dirname, '..');
const PUBLIC_DIR = path.join(ROOT, 'public');

function readPublic(relPath) {
  return fs.readFileSync(path.join(PUBLIC_DIR, relPath), 'utf8');
}

function getPngDimensions(filePath) {
  const buf = fs.readFileSync(filePath);
  const PNG_SIG = '89504e470d0a1a0a';
  assert.equal(buf.subarray(0, 8).toString('hex'), PNG_SIG, `${filePath} must be a valid PNG`);
  return {
    width: buf.readUInt32BE(16),
    height: buf.readUInt32BE(20),
  };
}

test('Cloudflare Pages deployment structure and required files exist', () => {
  const required = [
    'wrangler.toml',
    'package.json',
    'tailwind.config.cjs',
    'src/styles.css',
    'public/index.html',
    'public/assets/site.css',
    'public/assets/app.js',
    'public/_headers',
    'public/_redirects',
    'public/robots.txt',
    'public/sitemap.xml',
    'public/site.webmanifest',
    'public/favicon.ico',
  ];
  for (const rel of required) {
    assert.ok(fs.existsSync(path.join(ROOT, rel)), `Missing required file: ${rel}`);
  }

  const wrangler = fs.readFileSync(path.join(ROOT, 'wrangler.toml'), 'utf8');
  assert.match(wrangler, /name\s*=\s*"esasprime-landing"/);
  assert.match(wrangler, /pages_build_output_dir\s*=\s*"public"/);

  const css = readPublic('assets/site.css');
  assert.ok(css.length > 500, 'Compiled site.css must not be empty');
  assert.match(css, /\.brand-logo/, 'site.css must contain .brand-logo rule');
  assert.match(css, /\.text-start/, 'site.css must contain logical .text-start utility');
  assert.match(css, /Plus Jakarta Sans,Cairo/, 'font-en must include Cairo fallback');
});

test('Identity 2.0 tokens, SVG integrity, PNG dimensions, and all HTML/manifest references match', () => {
  const tokens = JSON.parse(fs.readFileSync(path.join(ROOT, 'identity/v2/brand-tokens.json'), 'utf8'));
  const tokensCss = readPublic('brand/brand-tokens.css');
  for (const [key, hex] of Object.entries(tokens.colors)) {
    const expectedVar = key.replace(/_/g, '-');
    assert.ok(
      tokensCss.includes(`--esas-${expectedVar}: ${hex};`),
      `brand-tokens.css missing --esas-${expectedVar}: ${hex}`,
    );
  }

  const html = readPublic('index.html');
  const localRefs = [...html.matchAll(/(?:href|src)="(\/[^"]+)"/g)].map((m) => m[1]);
  assert.ok(localRefs.length >= 7, 'Expected local asset references in index.html');
  for (const ref of localRefs) {
    const clean = ref.split('?')[0].slice(1);
    if (clean === '') continue;
    assert.ok(fs.existsSync(path.join(PUBLIC_DIR, clean)), `Broken local ref in HTML: ${ref}`);
  }

  const ogImgMatch = html.match(/property="og:image"\s+content="https:\/\/esasprime\.com([^"]+)"/);
  assert.ok(ogImgMatch, 'og:image meta tag must point to https://esasprime.com/...');
  assert.ok(fs.existsSync(path.join(PUBLIC_DIR, ogImgMatch[1].slice(1))), 'og:image file missing');

  for (const manifestRel of ['site.webmanifest', 'brand/site.webmanifest']) {
    const manifest = JSON.parse(readPublic(manifestRel));
    assert.equal(manifest.name, 'ESAS PRIME');
    assert.equal(manifest.start_url, '/');
    for (const icon of manifest.icons) {
      assert.ok(icon.src.startsWith('/'), `Manifest icon src must be absolute path: ${icon.src}`);
      assert.ok(fs.existsSync(path.join(PUBLIC_DIR, icon.src.slice(1))), `Missing manifest icon: ${icon.src}`);
    }
  }

  const logoDark = readPublic('brand/logo-dark.svg');
  assert.match(logoDark, /^<svg\b[^>]*width="1271"[^>]*height="414"/, 'logo-dark.svg must be v2 1271x414');
  assert.match(html, /src="\/brand\/logo-dark\.svg\?v=2"\s+width="1271"\s+height="414"/);

  assert.deepEqual(getPngDimensions(path.join(PUBLIC_DIR, 'brand/social-preview.png')), { width: 1200, height: 630 });
  assert.deepEqual(getPngDimensions(path.join(PUBLIC_DIR, 'brand/app-icon-square_180.png')), { width: 180, height: 180 });
  assert.deepEqual(getPngDimensions(path.join(PUBLIC_DIR, 'brand/icon-any_192.png')), { width: 192, height: 192 });
  assert.deepEqual(getPngDimensions(path.join(PUBLIC_DIR, 'brand/icon-any_512.png')), { width: 512, height: 512 });
  assert.deepEqual(getPngDimensions(path.join(PUBLIC_DIR, 'brand/icon-maskable_512.png')), { width: 512, height: 512 });
});

test('Security headers, CSP compatibility, SEO metadata, and content hygiene pass', () => {
  const html = readPublic('index.html');
  const headers = readPublic('_headers');
  const robots = readPublic('robots.txt');
  const sitemap = readPublic('sitemap.xml');
  const redirects = readPublic('_redirects');

  assert.match(html, /<link href="https:\/\/esasprime\.com\/" rel="canonical"\/>/);
  assert.match(html, /<meta name="twitter:card" content="summary_large_image">/);
  assert.match(html, /mailto:contact@esasprime\.com/);
  assert.match(html, /mailto:dev@esasprime\.com/);
  assert.doesNotMatch(html, /cdn\.tailwindcss\.com/, 'Tailwind CDN must not be present');
  assert.doesNotMatch(html, /\/cdn-cgi\//, 'Cloudflare edge proxy paths must not be committed in source');
  assert.doesNotMatch(html, /<script(?![^>]*\bsrc=)/i, 'Inline <script> violates CSP script-src self');
  assert.doesNotMatch(html, /\son[a-z]+\s*=/i, 'Inline event handlers violate CSP script-src self');
  assert.doesNotMatch(html, /TODO|FIXME|PLACEHOLDER/i);

  assert.match(headers, /X-Content-Type-Options:\s*nosniff/);
  assert.match(headers, /X-Frame-Options:\s*DENY/);
  assert.match(headers, /Referrer-Policy:\s*strict-origin-when-cross-origin/);
  assert.match(headers, /Permissions-Policy:/);
  assert.match(headers, /Content-Security-Policy:\s*default-src 'self'; script-src 'self';/);
  assert.doesNotMatch(headers, /unsafe-inline|unsafe-eval/);

  assert.match(robots, /Sitemap:\s*https:\/\/esasprime\.com\/sitemap\.xml/);
  assert.match(sitemap, /<loc>https:\/\/esasprime\.com\/<\/loc>/);
  assert.match(redirects, /https:\/\/www\.esasprime\.com\/\*\s+https:\/\/esasprime\.com\/:splat\s+301/);

  const bilingualMatches = [...html.matchAll(/<([a-z0-9]+)\b[^>]*\bdata-ar="([^"]*)"[^>]*\bdata-en="([^"]*)"[^>]*>([\s\S]*?)<\/\1>/gi)];
  assert.equal(bilingualMatches.length, 16, 'Expected 16 bilingual data-ar/data-en elements');
  for (const [, tag, ar, en, inner] of bilingualMatches) {
    assert.ok(ar.trim().length > 0, `<${tag}> has empty data-ar`);
    assert.ok(en.trim().length > 0, `<${tag}> has empty data-en`);
    assert.doesNotMatch(inner, /<[a-z]/i, `<${tag}> contains child HTML that textContent would overwrite`);
  }
});

test('app.js syntax and bilingual RTL/LTR state transitions and persistence', () => {
  const appSource = readPublic('assets/app.js');
  const html = readPublic('index.html');
  new vm.Script(appSource, { filename: 'public/assets/app.js' });

  const bilingualElements = [...html.matchAll(/\bdata-ar="([^"]*)"[^>]*\bdata-en="([^"]*)"/g)].map((m) => ({
    dataset: { ar: m[1], en: m[2] },
    textContent: m[1],
  }));

  function runApp({ initialStored = null, throwStorage = false, hasButton = true } = {}) {
    const store = new Map();
    if (initialStored !== null) store.set('esas-language', initialStored);
    let clickHandler = null;
    const button = hasButton
      ? {
          textContent: 'EN',
          attrs: {},
          setAttribute(k, v) { this.attrs[k] = v; },
          addEventListener(ev, fn) { if (ev === 'click') clickHandler = fn; },
        }
      : null;

    const document = {
      documentElement: { lang: 'ar', dir: 'rtl' },
      title: '',
      getElementById(id) { return id === 'language-toggle' ? button : null; },
      querySelectorAll(sel) { return sel === '[data-ar][data-en]' ? bilingualElements : []; },
    };

    const localStorage = {
      getItem(k) { if (throwStorage) throw new Error('blocked'); return store.has(k) ? store.get(k) : null; },
      setItem(k, v) { if (throwStorage) throw new Error('blocked'); store.set(k, v); },
    };

    vm.runInNewContext(appSource, { document, localStorage });
    return { document, button, store, triggerClick: () => clickHandler && clickHandler() };
  }

  const def = runApp();
  assert.equal(def.document.documentElement.lang, 'ar');
  assert.equal(def.document.documentElement.dir, 'rtl');
  assert.equal(def.button.textContent, 'EN');
  assert.equal(def.button.attrs['aria-label'], 'Switch to English');
  assert.equal(def.document.title, 'ESAS PRIME | تقنية بلا حدود');

  def.triggerClick();
  assert.equal(def.document.documentElement.lang, 'en');
  assert.equal(def.document.documentElement.dir, 'ltr');
  assert.equal(def.button.textContent, 'عربي');
  assert.equal(def.button.attrs['aria-label'], 'التبديل إلى العربية');
  assert.equal(def.document.title, 'ESAS PRIME | Technology Without Boundaries');
  assert.equal(def.store.get('esas-language'), 'en');
  assert.equal(bilingualElements[1].textContent, 'Contact us');

  const reloaded = runApp({ initialStored: 'en' });
  assert.equal(reloaded.document.documentElement.lang, 'en');
  assert.equal(reloaded.document.documentElement.dir, 'ltr');

  const invalid = runApp({ initialStored: 'fr' });
  assert.equal(invalid.document.documentElement.lang, 'ar');
  assert.equal(invalid.document.documentElement.dir, 'rtl');

  assert.doesNotThrow(() => runApp({ throwStorage: true }));
  assert.doesNotThrow(() => runApp({ hasButton: false }));
});

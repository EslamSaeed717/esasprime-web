# ESAS PRIME — الموقع الرسمي

الموقع التعريفي على https://esasprime.com — واجهة عربية وإنجليزية، تدعم RTL والهاتف والحاسوب.

## الملفات

- `public/`: ملفات الموقع المنشورة فقط.
- `src/styles.css` و`tailwind.config.cjs`: مصدر التنسيق.
- `public/assets/app.js`: تبديل اللغة وحفظ الاختيار على الجهاز.
- `wrangler.toml`: إعداد Cloudflare Pages.

## التطوير والنشر

```bash
npm ci
npm run build
```

Cloudflare Pages مرتبط بمستودع `EslamSaeed717/esasprime-web`، فرع `main`، والمشروع `esasprime-landing`. مجلد النشر `public` وأمر البناء `npm run build`. نُشرت النسخة الحالية مباشرة من ملفات `public` لأن اتصال GitHub في ChatGPT لم يشمل هذا المستودع بعد. النشر التلقائي متوقف مؤقتًا حتى حفظ هذه الملفات في `main` ومنح المستودع الصلاحية اللازمة. بعد ذلك يُفعّل `production_deployments_enabled` في Cloudflare. يمكن الرجوع إلى نشر سابق من صفحة Deployments في Cloudflare.

للنشر اليدوي عند الحاجة، بعد تسجيل الدخول محليًا إلى Cloudflare:

```bash
npx wrangler pages deploy public --project-name esasprime-landing --branch main
```

النطاق الرئيسي `esasprime.com`، ويُحوّل `www.esasprime.com` إليه. يُفرض HTTPS على مستوى النطاق. لا ترفع مفاتيح API أو بيانات دخول إلى المستودع.

## البريد

عناوين `contact@esasprime.com` و`dev@esasprime.com` و`eslam@esasprime.com` مخصصة للاستقبال عبر Cloudflare Email Routing. التحويل إلى البريد الشخصي يُدار من Cloudflare، ولا تُخزّن بياناته في الموقع. هذه الخدمة لا تنشئ صندوق بريد أو خادم إرسال SMTP، ويحتاج الإرسال باسم النطاق إلى مزوّد بريد صادر يُجهّز على حدة.

## نطاق الموقع

هذه صفحة تعريفية بالخدمات ومعلومات الاتصال. تطبيقات العملاء والأنظمة المحاسبية تُنشر بصورة مستقلة، ولا توجد بيانات عملاء أو أنظمة إنتاج داخل هذا المستودع.

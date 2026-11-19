from pathlib import Path
import json,shutil,hashlib,zipfile,os
import cairosvg,fitz
R=Path(__file__).resolve().parent
ns={"__file__":str(R/"build_identity.py")};exec((R/'build_identity.py').read_text().split('PROFILE=')[0],ns)
base_text=ns['text']
def filtered_text(t,*args,**kw):
    lang=kw.get('lang',args[4] if len(args)>4 else 'en')
    if lang=='ar':
        cm=ns['FT']['ar'][4].getBestCmap();t=''.join(c for c in t if c.isspace() or ord(c) in cm)
    return base_text(t,*args,**kw)
ns['text']=filtered_text
O=ns['OUT'];svg=ns['svg'];text=ns['text'];group=ns['group'];layout=ns['layout'];COL=ns['COL'];rect=lambda x,y,w,h,c:f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>'

def art(kind,theme,x,y,width):
    w,h,b=layout(kind,*ns['PALETTES'][theme]);return group(b,x,y,width/w)
def title(s):return text(s,1200,60,40,COL['ink'],'ar','right')
def lines(items,y=165):return ''.join(text(s,1200,y+i*69,25,COL['ink'],'ar','right')for i,s in enumerate(items))

pages=[]
pages.append(svg(1280,720,art('horizontal','on-dark',100,155,1080)+text('ESAS PRIME',80,65,27,'#FFFFFF',tracking=3)+text('دليل الهوية والاستخدام',1200,575,35,'#FFFFFF','ar','right')+text('2.0  /  18.11.2026',80,625,20,'#A65BFF'),bg=COL['navy']))
pages.append(svg(1280,720,title('الاسم والنسخ الرسمية')+art('horizontal','on-light',55,160,610)+art('arabic','on-light',680,160,550)+text('ESAS PRIME Technologies',80,440,31,COL['royal'])+lines(['الاسم الأساسي كلمتان: لا تحذف برايم عند التعريف بالعلامة.','أساس برايم: الكتابة العربية المستخدمة في هذه الحزمة.','وصف النشاط اختياري في النسخة المؤسسية الممتدة.'],505),bg='#FFFFFF'))
pages.append(svg(1280,720,title('ترتيبات تتبع علامة واحدة')+art('horizontal','on-light',55,150,650)+art('stacked','on-light',820,130,330)+art('inline','black',45,480,1130)+text('أفقي — مكدس — سطر واحد — كتابة — رمز',1200,640,24,COL['ink'],'ar','right'),bg=COL['cloud']))
b=title('الألوان والخلفيات')
for i,k in enumerate(['navy','royal','signal','violet','violet_light']):
    x=80+i*228;b+=rect(x,170,205,170,COL[k])+text(COL[k],x,365,22,COL['ink'])
b+=lines(['الأزرق الملكي والبنفسجي على الخلفيات الفاتحة.','الأزرق الفاتح والبنفسجي الفاتح أو الأبيض على الداكنة.','لا تستخدم الأزرق الملكي فوق الكحلي؛ ولا تضف وهجًا إلى الأصل.','ملفات الطباعة ملونة؛ تحويل المطبعة يعتمد على الورق وملف اللون.'],445)
pages.append(svg(1280,780,b,bg='#FFFFFF'))
pages.append(svg(1280,720,title('المساحة والحجم والوضوح')+lines(['هوامش العزل موجودة داخل ملفات الشعار المرجعية.','احجز ربع ارتفاع الرمز عند وضع الأصل بجوار عناصر أخرى.','استخدم الرمز للمساحات الصغيرة والنسخة المبسطة عند المقاسات الدقيقة.','استخدم التوقيع الأفقي بعرض مريح، والرمز للمساحات الأصغر.','لا تمدد الرسم أو تعكس الاسم أو تعيد كتابة الحروف بخط بديل.','لا تستخدم الشعار الأفقي مصغرًا بدل أيقونة الهاتف.'],160),bg='#FFFFFF'))
pages.append(svg(1280,720,title('أيقونات لكل وسيط')+lines(['للويب: أيقونات عامة وقابلة للقص وأيقونات المتصفح.','الحسابات: صور مربعة ومستديرة مع مساحة أمان للقص الدائري.','لمتجر جوجل: ملف بخمسمئة واثني عشر بكسل بصيغة ملونة وملف لون مضمّن.','لأندرويد: طبقات أصلية ونسخة أحادية اللون وموارد التطبيق.','لآبل: أصل عالي الدقة ومجلد أيقونات للتطبيق الأصلي.','تجهيز الموارد منفصل عن بناء التطبيق وتجربته على جهاز.'],160),bg=COL['cloud']))
pages.append(svg(1280,720,title('اختيار الملف الصحيح')+lines(['الملف المتجه: للموقع والتعديل والتكبير دون فقدان الجودة.','الصور الشفافة: للبرامج التي لا تقبل الرسم المتجه.','الملف المحمول المتجه: للتسليم إلى المصمم أو المطبعة.','القوالب: ترويسة مستند وصورة مشاركة وتوقيع بريد.','المصدر الهندسي والخطوط المرخصة مرفقان لإعادة البناء.','الفحص القانوني للاسم وتجربة المستخدم والبروفة المادية مستقلة.'],160),bg='#FFFFFF'))
guide=fitz.open()
for i,p in enumerate(pages,1):
    target=O/'07_Guide'/f'page-{i:02}.svg';target.write_text(p)
    pdf=cairosvg.svg2pdf(bytestring=p.encode());doc=fitz.open(stream=pdf,filetype='pdf');guide.insert_pdf(doc)
guide.save(O/'07_Guide/ESAS_PRIME_Brand_Guide_AR.pdf')

# Individual clean images, without contact-sheet labels.
for theme,bg in [('on-light','#FFFFFF'),('on-dark',COL['navy'])]:
    source=(O/'01_Vector'/f'esas-prime_horizontal_{theme}.svg').read_text().replace('<title>',f'<rect width="1271" height="414" fill="{bg}"/><title>',1)
    target=O/f'ESAS_PRIME_Logo_{theme}_6000.png';ns['cairosvg'].svg2png(bytestring=source.encode(),write_to=str(target),output_width=6000)
    im=ns['Image'].open(target).convert('RGB');im.save(target,icc_profile=ns['ImageCms'].ImageCmsProfile(ns['ImageCms'].createProfile('sRGB')).tobytes())
shutil.copy2(O/'04_Icons/Social/profile-rounded_2048.png',O/'ESAS_PRIME_Icon_2048.png')
(O/'06_Templates/email-signature.html').write_text('''<table role="presentation" cellpadding="0" cellspacing="0" style="font:14px Arial,sans-serif;color:#111827"><tr><td style="padding-right:18px"><img src="https://esasprime.com/brand/logo-light.svg" width="220" alt="ESAS PRIME"></td><td><strong>ESAS PRIME</strong><br>Technologies<br><a href="https://esasprime.com/">esasprime.com</a><br><a href="mailto:contact@esasprime.com">contact@esasprime.com</a></td></tr></table>\n''')
(O/'07_Guide/README_AR.md').write_text('''# ESAS PRIME — حزمة التصميم 2.0

الشعار والرمز والحروف هنا أصول متجهة مصقولة، وليست تكبيرًا لصور. أزيلت الفواصل الرفيعة، وكبرت PRIME إلى 58.1% من ارتفاع ESAS، وضُبطت قمم الرمز وحرف A والمسافات. الاسم المستخدم بالعربية «أساس برايم»، والاسم المؤسسي الممتد ESAS PRIME Technologies.

## البداية السريعة

- `01_Vector`: 32 أصلًا: أفقي، كتابة، مكدس، سطر واحد، رمز، مؤسسي ممتد، عربي وثنائي اللغة؛ لكل منها فاتح وداكن وأسود وأبيض.
- `02_PNG_Transparent`: نسخ شفافة، الأفقي حتى عرض 6000 بكسل والرمز حتى 4096.
- `03_PDF_Vector_RGB`: ملفات متجهة RGB. المطبعة تضبط التحويل حسب الورق؛ لا ندعي مطابقة CMYK أو Pantone دون بروفة.
- `04_Icons`: أيقونات الويب والحسابات وملف Google Play وحزمة موارد Android وأصل Apple.
- `05_Web`: ملفات جاهزة للدمج؛ انسخ محتويات brand إلى public/brand، وملف manifest إلى public/site.webmanifest، واستخدم مقتطف HTML.
- `06_Templates`: ترويسة A4 وصورة مشاركة وتوقيع بريد. يدعم بعض عملاء البريد PNG فقط؛ استبدل رابط SVG بصورة PNG مستضافة عند الحاجة.
- `07_Guide`: دليل عربي PDF وخريطة الأصول وعرض الهوية.
- `08_Source`: البرنامج الهندسي وإحداثيات الرسم والخطوط المستخدمة مع ترخيصها. لا يحتاج عرض SVG/PDF إلى تثبيت الخطوط.
- `09_QA`: نتائج التحقق وحدوده.

الهوامش داخل الأصول المرجعية تحجز مساحة العزل؛ لا تقصها ثم تلصق الشعار بعناصر أخرى. استعمل on-light فوق الفاتح وon-dark فوق الداكن. لا تمدد الرسم، ولا تضف وهجًا أو حدودًا إلى الأصل. نسخة Micro تحذف التفصيل الداخلي عمدًا عند المقاسات الدقيقة.

## إعادة البناء

من 08_Source، ثبّت requirements.txt، وتأكد من وجود HarfBuzz في النظام، ثم شغّل build_identity.py. ينشئ أصول الرسم والأيقونات. شغّل finalize_identity.py لإنشاء الدليل والقوالب بعد ذلك. لا يلزم مفتاح خدمة أو حساب مدفوع.

## حدود الاعتماد

هذه نسخة تسليم تصميمية مكتملة للأصول المذكورة، وليست شهادة تسجيل علامة أو نتيجة اختبار مستخدمين. فحص الاسم القانوني في الأسواق المقصودة ما زال منفصلًا. قياس أمان PWA وفحص صيغة المتجر وملفات XML نجحت؛ لم ينفذ تركيب على هاتف أو تجميع APK/Xcode أو بروفة ورقية. لا تتضمن الحزمة ادعاء تسجيل أو رمز ®.

Figma: https://www.figma.com/design/HFOg4VXAoVZGmavDDY5vlw?node-id=5-193
''')
shutil.copy2(R/'finalize_identity.py',O/'08_Source/finalize_identity.py')
print(json.dumps({'guide_pages':len(pages),'output':str(O)},ensure_ascii=False))

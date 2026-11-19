"""ESAS PRIME v2: deterministic vector masters and derivative exports.

Run: PYTHONPATH=<CairoSVG/Pillow deps> python3 build_identity.py
HarfBuzz is used only to outline the licensed Arabic/descriptor typefaces.
"""
from pathlib import Path
import ctypes as C, ctypes.util, json, shutil, html, csv, math, hashlib
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageCms
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'ESAS_PRIME_Identity_v2_20261118'
for d in ['01_Vector','02_PNG_Transparent','03_PDF_Vector_RGB','04_Icons/Web','04_Icons/Social','04_Icons/GooglePlay','04_Icons/Android/res/drawable','04_Icons/Android/res/mipmap-anydpi-v26','04_Icons/Android/res/mipmap-anydpi-v33','04_Icons/Android/res/values','04_Icons/Apple/AppIcon.appiconset','05_Web/brand','06_Templates','07_Guide','08_Source/fonts','09_QA']:
    (OUT/d).mkdir(parents=True,exist_ok=True)
COL={'navy':'#040B2B','royal':'#0B2DAF','signal':'#276AFF','violet':'#891FF5','violet_light':'#A65BFF','white':'#FFFFFF','cloud':'#F4F6FC','ink':'#111827'}
MARK='M149 6 Q155 -3 161 6 L310 274 H267 Q248 274 239 257 L155 100 L71 257 Q62 274 43 274 H0 Z'
FACET='M155 148 L207 246 L120 212 Z'
E='M0 0 H154 L135 32 H36 V59 H138 L119 90 H36 V116 H154 L135 148 H0 Z'
S='M184 0 L164 32 H60 C43 32 35 35 35 43 C35 51 45 54 65 57 L118 66 C159 73 177 86 177 109 C177 134 156 148 121 148 H0 L20 116 H119 C132 116 141 112 141 105 C141 99 133 96 113 93 L58 84 C19 77 6 64 6 42 C6 18 26 0 59 0 Z'
A='M0 148 L96 9 Q104 -3 112 9 L210 148 H170 L104 45 L40 148 Z M69 148 L94 105 H115 L140 148 Z'
PRIME=[('P',0,'M0 40 V0 H17 Q30 0 30 13 Q30 26 17 26 H7 V40 Z M7 6 V20 H16 Q23 20 23 13 Q23 6 16 6 Z'),('R',52,'M0 40 V0 H17 Q30 0 30 13 Q30 23 21 25 L33 40 H24 L13 26 H7 V40 Z M7 6 V20 H16 Q23 20 23 13 Q23 6 16 6 Z'),('I',108,'M0 0 H7 V40 H0 Z'),('M',140,'M0 40 V0 H8 L18 22 L28 0 H36 V40 H29 V12 L20 31 H16 L7 12 V40 Z'),('E',202,'M0 40 V0 H27 V6 H7 V17 H24 V23 H7 V34 H27 V40 Z')]
PALETTES={'on-light':(COL['royal'],COL['violet'],COL['royal']),'on-dark':(COL['signal'],COL['violet_light'],COL['white']),'black':('#000000',)*3,'white':('#FFFFFF',)*3}

def path(d,f,extra=''):return f'<path d="{d}" fill="{f}" {extra}/>'
def group(body,x=0,y=0,s=1):return f'<g transform="translate({x:g} {y:g}) scale({s:g})">{body}</g>'
def mark(m,a,micro=False):return path(MARK,m)+(path(FACET,a) if not micro else '')
def esas(m):return path(E,m)+path(S,m,'transform="translate(160 0)"')+path(A,m,'transform="translate(349 0)"')+path(S,m,'transform="translate(565 0)"')

def prime(f,compact=False):
    pos=[0,37,77,96,140] if compact else [x for _,x,_ in PRIME]
    return ''.join(path(d,f,f'fill-rule="evenodd" transform="translate({x} 0)"') for x,(_,_,d) in zip(pos,PRIME))
def svg(w,h,body,title='ESAS PRIME',bg=None):
    b=f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>{b}{body}</svg>\n'

# HarfBuzz ABI: keep shaping and outlining independent of system text rendering.
hb=C.CDLL(ctypes.util.find_library('harfbuzz'))
def api(n,r,a):f=getattr(hb,n);f.restype=r;f.argtypes=a;return f
blob=api('hb_blob_create',C.c_void_p,[C.c_void_p,C.c_uint,C.c_int,C.c_void_p,C.c_void_p])
face=api('hb_face_create',C.c_void_p,[C.c_void_p,C.c_uint]);font=api('hb_font_create',C.c_void_p,[C.c_void_p])
ot=api('hb_ot_font_set_funcs',None,[C.c_void_p]);scale=api('hb_font_set_scale',None,[C.c_void_p,C.c_int,C.c_int])
bufnew=api('hb_buffer_create',C.c_void_p,[]);add=api('hb_buffer_add_utf8',None,[C.c_void_p,C.c_char_p,C.c_int,C.c_uint,C.c_int])
guess=api('hb_buffer_guess_segment_properties',None,[C.c_void_p]);shape=api('hb_shape',None,[C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint])
class Info(C.Structure):_fields_=[('codepoint',C.c_uint32),('mask',C.c_uint32),('cluster',C.c_uint32),('v1',C.c_uint32),('v2',C.c_uint32)]
class Pos(C.Structure):_fields_=[('x_advance',C.c_int32),('y_advance',C.c_int32),('x_offset',C.c_int32),('y_offset',C.c_int32),('v',C.c_uint32)]
infos=api('hb_buffer_get_glyph_infos',C.POINTER(Info),[C.c_void_p,C.POINTER(C.c_uint)])
poses=api('hb_buffer_get_glyph_positions',C.POINTER(Pos),[C.c_void_p,C.POINTER(C.c_uint)])
destroy=api('hb_buffer_destroy',None,[C.c_void_p])
FT={}
for key,name in [('ar','NotoKufiArabic-Bold.ttf'),('en','NotoSans-Regular.ttf')]:
    src=ROOT/'fonts'/name
    if not src.exists():src=Path('/usr/share/fonts/truetype/noto')/name
    data=src.read_bytes(); raw=C.create_string_buffer(data); bl=blob(raw,len(data),0,None,None); fa=face(bl,0); fo=font(fa);ot(fo)
    tt=TTFont(src);up=tt['head'].unitsPerEm;scale(fo,up,up)
    FT[key]=(raw,bl,fa,fo,tt,tt.getGlyphSet(),tt.getGlyphOrder(),up)
    shutil.copy2(src,OUT/'08_Source/fonts'/name)

def text_outline(text,size=30,color=None,lang='en',tracking=0):
    _,_,_,fo,tt,gs,order,up=FT[lang];buf=bufnew();data=text.encode();add(buf,data,len(data),0,len(data));guess(buf);shape(fo,buf,None,0)
    n=C.c_uint(); inf=infos(buf,C.byref(n));po=poses(buf,C.byref(n));s=size/up;xp=yp=0;paths=[];bounds=[]
    for i in range(n.value):
        g=gs[order[inf[i].codepoint]]; tr=(s,0,0,-s,(xp+po[i].x_offset)*s,-(yp+po[i].y_offset)*s)
        pen=SVGPathPen(gs);g.draw(TransformPen(pen,tr));d=pen.getCommands()
        if d:paths.append(path(d,color or COL['ink']))
        bp=BoundsPen(gs);g.draw(TransformPen(bp,tr))
        if bp.bounds:bounds.append(bp.bounds)
        xp+=po[i].x_advance+tracking/s;yp+=po[i].y_advance
    destroy(buf)
    if not bounds:return '',0,0
    x0=min(b[0] for b in bounds);y0=min(b[1] for b in bounds);x1=max(b[2] for b in bounds);y1=max(b[3] for b in bounds)
    return group(''.join(paths),-x0,-y0),x1-x0,y1-y0

def text(text,x,y,size=28,color=None,lang='en',align='left',tracking=0):
    b,w,h=text_outline(text,size,color,lang,tracking);xx=x-w if align=='right' else x-w/2 if align=='center' else x
    return group(b,xx,y)

def layout(kind,m,a,t):
    if kind=='horizontal':return 1271,414,group(mark(m,a),70,70)+group(esas(m),452,74)+group(prime(t),455,254,2.15)
    if kind=='wordmark':return 889,414,group(esas(m),70,74)+group(prime(t),73,254,2.15)
    if kind=='stacked':return 889,805,group(mark(m,a),289.5,70)+group(esas(m),70,437)+group(prime(t),198,617,2.15)
    if kind=='inline':return 1550,342,group(mark(m,a),70,70,.74)+group(esas(m),360,92,.85)+group(prime(t,True),1047,134,2.05)
    if kind=='symbol':return 450,414,group(mark(m,a),70,70)
    if kind=='extended':
        w,h,b=layout('horizontal',m,a,t)
        b+=text('TECHNOLOGIES',455,385,32,t,tracking=4)
        return w,484,b
    if kind=='arabic':
        ar,aw,ah=text_outline('أساس برايم',116,m,'ar');desc,dw,dh=text_outline('للتقنية',38,t,'ar')
        return 1180,414,group(mark(m,a),800,70)+group(ar,70+(650-aw)/2,99)+group(desc,70+(650-dw)/2,271)
    if kind=='bilingual':
        w,h,b=layout('horizontal',m,a,t); ar,aw,ah=text_outline('أساس برايم',63,t,'ar')
        return w,530,b+group(ar,452+(749-aw)/2,399)
    raise ValueError(kind)

PROFILE=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
ASSETS=[]
def raster(content,target,width,mode=None):
    cairosvg.svg2png(bytestring=content.encode(),write_to=str(target),output_width=width)
    im=Image.open(target)
    if mode:im=im.convert(mode)
    im.save(target,icc_profile=PROFILE)
def save(content,target):target.write_text(content);return target
MASTERS={}
for kind in ['horizontal','wordmark','stacked','inline','symbol','extended','arabic','bilingual']:
    for theme,colors in PALETTES.items():
        w,h,b=layout(kind,*colors);key=f'esas-prime_{kind}_{theme}';art=svg(w,h,b)
        save(art,OUT/'01_Vector'/f'{key}.svg');MASTERS[key]=art
        widths=[2400,6000] if kind=='horizontal' else [2048,4096] if kind=='symbol' else [3200]
        for width in widths:raster(art,OUT/'02_PNG_Transparent'/f'{key}_{width}px.png',width,'RGBA')
        cairosvg.svg2pdf(bytestring=art.encode(),write_to=str(OUT/'03_PDF_Vector_RGB'/f'{key}.pdf'))
        ASSETS.append([key,kind,theme,w,h,'SVG; transparent PNG; vector RGB PDF'])

def icon(rounded=False,mask=False,micro=False,mono=False,light=False):
    bg='#FFFFFF' if light else COL['navy'];m=COL['royal'] if light else ('#FFFFFF' if micro or mono else COL['signal']);a=COL['violet'] if light else COL['violet_light']
    b=f'<rect width="512" height="512" rx="{112 if rounded else 0}" fill="{bg}"/>'
    s=.92 if mask else 1.08; xx=(512-310*s)/2; yy=(512-274*s)/2+3
    return svg(512,512,b+group(mark(m,'#FFFFFF' if mono else a,micro),xx,yy,s),'ESAS PRIME icon')

for name,art,sizes in [('icon-any',icon(),[64,128,180,192,256,512,1024]),('icon-maskable',icon(mask=True),[192,512,1024]),('favicon',icon(micro=True),[16,24,32,48])]:
    save(art,OUT/'04_Icons/Web'/f'{name}.svg')
    for sz in sizes:raster(art,OUT/'04_Icons/Web'/f'{name}_{sz}.png',sz,'RGBA')
fav=Image.open(OUT/'04_Icons/Web/favicon_48.png');fav.save(OUT/'04_Icons/Web/favicon.ico',sizes=[(16,16),(32,32),(48,48)])
save(svg(450,414,group(mark('#000000','#000000'),70,70)),OUT/'04_Icons/Web/safari-pinned-tab.svg')
for name,art in [('profile-square',icon(mask=True)),('profile-rounded',icon(rounded=True,mask=True)),('profile-light',icon(light=True,mask=True))]:
    save(art,OUT/'04_Icons/Social'/f'{name}.svg')
    for sz in [512,2048]:raster(art,OUT/'04_Icons/Social'/f'{name}_{sz}.png',sz,'RGBA')
raster(icon(),OUT/'04_Icons/GooglePlay/google-play_512_rgba_srgb.png',512,'RGBA')
raster(icon(),OUT/'04_Icons/Apple/AppIcon.appiconset/AppIcon.png',1024,'RGB')
raster(icon(mono=True),OUT/'04_Icons/Apple/AppIcon-dark.png',1024,'RGB')
save(json.dumps({'images':[{'filename':'AppIcon.png','idiom':'universal','platform':'ios','size':'1024x1024'}],'info':{'author':'xcode','version':1}},indent=2),OUT/'04_Icons/Apple/AppIcon.appiconset/Contents.json')

ANDROID=OUT/'04_Icons/Android/res'
def android_vector(m,a):return f'''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108"><group android:scaleX="0.155" android:scaleY="0.155" android:translateX="29.975" android:translateY="33.515"><path android:fillColor="{m}" android:pathData="{MARK}"/><path android:fillColor="{a}" android:pathData="{FACET}"/></group></vector>\n'''
save(android_vector(COL['signal'],COL['violet_light']),ANDROID/'drawable/ic_esas_foreground.xml')
save(android_vector('#FFFFFF','#FFFFFF'),ANDROID/'drawable/ic_esas_monochrome.xml')
save(f'<resources><color name="esas_icon_background">{COL["navy"]}</color></resources>\n',ANDROID/'values/esas_colors.xml')
adaptive='<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"><background android:drawable="@color/esas_icon_background"/><foreground android:drawable="@drawable/ic_esas_foreground"/>{mono}</adaptive-icon>\n'
save(adaptive.format(mono=''),ANDROID/'mipmap-anydpi-v26/ic_launcher.xml')
save(adaptive.format(mono='<monochrome android:drawable="@drawable/ic_esas_monochrome"/>'),ANDROID/'mipmap-anydpi-v33/ic_launcher.xml')
for den,sz in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
    d=ANDROID/f'mipmap-{den}';d.mkdir(exist_ok=True);raster(icon(),d/'ic_launcher.png',sz,'RGBA');raster(icon(rounded=True),d/'ic_launcher_round.png',sz,'RGBA')

# Web paths are consistent with the drop-in brand/ directory.
for p in (OUT/'04_Icons/Web').iterdir():shutil.copy2(p,OUT/'05_Web/brand'/p.name)
for k in ['horizontal_on-light','horizontal_on-dark','inline_on-light','inline_on-dark','symbol_on-light','symbol_white']:
    shutil.copy2(OUT/'01_Vector'/f'esas-prime_{k}.svg',OUT/'05_Web/brand'/f'esas-prime_{k}.svg')
manifest={'id':'/','name':'ESAS PRIME','short_name':'ESAS PRIME','start_url':'/','scope':'/','display':'standalone','background_color':COL['navy'],'theme_color':COL['navy'],'icons':[{'src':f'/brand/icon-any_{n}.png','sizes':f'{n}x{n}','type':'image/png','purpose':'any'}for n in[192,512]]+[{'src':'/brand/icon-maskable_512.png','sizes':'512x512','type':'image/png','purpose':'maskable'}]}
save(json.dumps(manifest,indent=2),OUT/'05_Web/site.webmanifest')
tokens={'name':'ESAS PRIME','version':'2.0.0','arabic_display_name':'أساس برايم','descriptor':'Technologies','colors':COL,'logo_type':'custom outlined ESAS and PRIME','arabic_type':'Noto Kufi Arabic Bold outlined','embedded_clear_space':True,'clear_space':'At least 0.25 of symbol ink height; supplied master padding already reserves this','size_guidance':'Use symbol/micro for small slots; test contextual reading. Horizontal suggested >=280 CSS px; inline >=320; these are implementation guidance, not a human-study certification.'}
save(json.dumps(tokens,ensure_ascii=False,indent=2),OUT/'05_Web/brand-tokens.json')
save(':root{\n'+''.join(f' --esas-{k.replace("_","-")}: {v};\n'for k,v in COL.items())+'}\n',OUT/'05_Web/brand-tokens.css')
save('''<link rel="icon" href="/brand/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/brand/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/brand/icon-any_180.png">
<link rel="mask-icon" href="/brand/safari-pinned-tab.svg" color="#0B2DAF">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#040B2B">
''',OUT/'05_Web/head-snippet.html')

def inset_art(key,x,y,w):
    el=ET.fromstring(MASTERS[key]);ow=float(el.attrib['width']);inside=''.join(ET.tostring(c,encoding='unicode')for c in el)
    return group(inside,x,y,w/ow)
def rect(x,y,w,h,c,r=0):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c}"/>'

# Clean contact sheet: labels are confined to the guide, not individual exports.
b=rect(0,0,2000,1720,COL['cloud'])
b+=text('ESAS PRIME',85,62,35,COL['ink'],tracking=2)+text('REFINED IDENTITY  /  2.0',1910,73,18,COL['royal'],align='right',tracking=2)
b+=rect(65,150,1870,610,COL['navy'],26)+inset_art('esas-prime_horizontal_on-dark',220,220,1560)
b+=rect(65,800,1200,380,'#FFFFFF',26)+inset_art('esas-prime_horizontal_on-light',100,820,1130)
b+=rect(1305,800,630,380,'#FFFFFF',26)
el=ET.fromstring(icon(rounded=True,mask=True));b+=group(''.join(ET.tostring(c,encoding='unicode')for c in el),1455,840,300/512)
b+=rect(65,1220,900,260,'#FFFFFF',26)+inset_art('esas-prime_inline_black',85,1240,860)
b+=rect(1005,1220,930,260,COL['navy'],26)+inset_art('esas-prime_inline_white',1030,1240,880)
for i,k in enumerate(['navy','royal','signal','violet','violet_light']):
    x=65+i*382;b+=rect(x,1530,342,65,COL[k],10)+text(COL[k],x,1620,19,COL['ink'])
board=svg(2000,1720,b,'ESAS PRIME refined identity preview')
save(board,OUT/'ESAS_PRIME_Preview_v2.svg');raster(board,OUT/'ESAS_PRIME_Preview_v2.png',3000,'RGB');cairosvg.svg2pdf(bytestring=board.encode(),write_to=str(OUT/'ESAS_PRIME_Preview_v2.pdf'))

# Social preview and a useful editable stationery template.
social=svg(1200,630,inset_art('esas-prime_horizontal_on-dark',85,125,1030),'ESAS PRIME social preview',COL['navy'])
save(social,OUT/'06_Templates/social-preview_1200x630.svg');raster(social,OUT/'06_Templates/social-preview_1200x630.png',1200,'RGB')
station=inset_art('esas-prime_horizontal_on-light',55,40,400)+text('esasprime.com',1135,70,19,COL['royal'],align='right')+rect(70,260,1060,3,COL['royal'])+text('contact@esasprime.com',70,1560,19,COL['ink'])+text('ESAS PRIME  /  Technologies',1135,1560,17,COL['ink'],align='right')
station=svg(1200,1697,station,'ESAS PRIME letterhead template','#FFFFFF')
save(station,OUT/'06_Templates/letterhead_A4.svg');cairosvg.svg2pdf(bytestring=station.encode(),write_to=str(OUT/'06_Templates/letterhead_A4_RGB.pdf'),output_width=595.276,output_height=841.89)

with (OUT/'07_Guide/asset-index.csv').open('w',encoding='utf-8-sig',newline='')as f:
    wr=csv.writer(f);wr.writerow(['asset','layout','theme','canvas_width','canvas_height','formats']);wr.writerows(ASSETS)
shutil.copy2(Path(__file__),OUT/'08_Source/build_identity.py')
src_license=ROOT/'fonts/NOTO-LICENSE.txt'
if not src_license.exists():src_license=Path('/usr/share/doc/fonts-noto-core/copyright')
shutil.copy2(src_license,OUT/'08_Source/fonts/NOTO-LICENSE.txt')
save(json.dumps({'mark':MARK,'facet':FACET,'E':E,'S':S,'A':A,'PRIME':PRIME,'colors':COL},ensure_ascii=False,indent=2),OUT/'08_Source/geometry.json')
save('CairoSVG==2.9.1\nPillow==13.0.0\nfonttools>=4.0\n# System: libharfbuzz0b. Fonts are included alongside this script.\n',OUT/'08_Source/requirements.txt')

def lumin(c):
    vals=[int(c[i:i+2],16)/255 for i in[1,3,5]];vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals];return sum(v*w for v,w in zip(vals,[.2126,.7152,.0722]))
def contrast(a,b):x,y=sorted([lumin(a),lumin(b)]);return (y+.05)/(x+.05)
im=Image.open(OUT/'04_Icons/Web/icon-maskable_512.png').convert('RGB');maxr=0
for y in range(512):
    for x in range(512):
        if max(abs(a-b) for a,b in zip(im.getpixel((x,y)),(4,11,43)))>16:maxr=max(maxr,math.hypot(x+.5-256,y+.5-256))
qa={'release':'2.0.0','date':'2026-11-18','vector_masters':len(MASTERS),'prime_cap_ratio':86/148,'divider_or_rules':False,'maskable_512_foreground_radius_px':round(maxr,3),'maskable_safe_radius_px':204.8,'maskable_pass':maxr<=204.8,'google_play_mode':Image.open(OUT/'04_Icons/GooglePlay/google-play_512_rgba_srgb.png').mode,'google_play_icc':bool(Image.open(OUT/'04_Icons/GooglePlay/google-play_512_rgba_srgb.png').info.get('icc_profile')),'apple_icon_mode':Image.open(OUT/'04_Icons/Apple/AppIcon.appiconset/AppIcon.png').mode,'native_compile_or_install':'NOT_RUN','user_recognition_test':'NOT_RUN','physical_print_proof':'NOT_RUN','trademark_clearance':'NOT_COMPLETED','contrast_signal_navy':round(contrast(COL['signal'],COL['navy']),3)}
assert qa['maskable_pass'] and qa['google_play_mode']=='RGBA' and qa['google_play_icc']
for p in (OUT/'01_Vector').glob('*.svg'):
    root=ET.parse(p).getroot();assert all(e.tag.split('}')[-1]not in['text','image','script','foreignObject']for e in root.iter())
for p in (OUT/'04_Icons/Android').rglob('*.xml'):ET.parse(p)
save(json.dumps(qa,ensure_ascii=False,indent=2),OUT/'09_QA/validation.json')
print(json.dumps({'directory':str(OUT),'vector_masters':len(MASTERS),'maskable_pass':qa['maskable_pass'],'maskable_radius':qa['maskable_512_foreground_radius_px']},ensure_ascii=False))

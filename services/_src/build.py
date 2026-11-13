# Builds services/index.html for the Physio Art site.
import html, urllib.parse, pathlib

WA = "201113270387"
def wa(msg):
    return f"https://wa.me/{WA}?text=" + urllib.parse.quote(msg)

# ---------- icons (inline SVG symbols) ----------
ICONS = {
 "snow": '<path d="M12 2v20M4.9 6.5l14.2 11M19.1 6.5 4.9 17.5M9 3.5l3 2.5 3-2.5M9 20.5l3-2.5 3 2.5"/>',
 "wave": '<path d="M2 12c2-4 4-4 6 0s4 4 6 0 4-4 6 0M2 18c2-3 4-3 6 0s4 3 6 0 4-3 6 0M2 6c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/>',
 "radio": '<circle cx="12" cy="12" r="2.5"/><path d="M7.5 7.5a6.4 6.4 0 0 0 0 9M16.5 7.5a6.4 6.4 0 0 1 0 9M4.6 4.6a10.5 10.5 0 0 0 0 14.8M19.4 4.6a10.5 10.5 0 0 1 0 14.8"/>',
 "laser": '<path d="M4 4h16v5H4zM7 9l-2 11M12 9v11M17 9l2 11"/>',
 "focus": '<path d="M3 4h18M5 4l7 11 7-11M12 15v5"/><circle cx="12" cy="15" r="1.6"/>',
 "slender": '<rect x="3" y="6" width="7" height="12" rx="2"/><path d="M10 9h4M10 12h6M10 15h4M18 10l3 2-3 2"/>',
 "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
 "vibe": '<rect x="4" y="15" width="16" height="5" rx="1.5"/><path d="M8 15V9M16 15V9M8 9h8M7 5c1 1 1 2 0 3M17 5c-1 1-1 2 0 3"/>',
 "syringe": '<path d="m18 2 4 4M15 5l4 4M17 7 7.5 16.5M10 7l7 7M4 20l3.5-3.5M6 13l5 5"/>',
 "pen": '<path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11z"/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5"/>',
 "gas": '<circle cx="8" cy="9" r="3"/><circle cx="15.5" cy="7" r="2"/><circle cx="15" cy="15" r="4"/>',
 "drop": '<path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11z"/>',
 "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
 "dots": '<circle cx="7" cy="7" r="1.2"/><circle cx="12" cy="7" r="1.2"/><circle cx="17" cy="7" r="1.2"/><circle cx="7" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="17" cy="12" r="1.2"/><circle cx="7" cy="17" r="1.2"/><circle cx="12" cy="17" r="1.2"/><circle cx="17" cy="17" r="1.2"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 "scale": '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M8 9a5 5 0 0 1 8 0M12 9l1.5-2"/>',
 "wa": '<path d="M3.5 20.5 5 16a8.5 8.5 0 1 1 3 3z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-2.3-2.3l.8-1-1-2z"/>',
 "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
 "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
 "play": '<path d="M8 5v14l11-7z"/>',
}
def icon(n, cls=""):
    return f'<svg class="ic {cls}" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-{n}"/></svg>'
SYMBOLS = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())

# ---------- HIFU illustration ----------
HIFU_SVG = '''<svg class="hifu" viewBox="0 0 320 400" role="img" aria-label="رسم توضيحي لطريقة عمل الهايفو: موجات فوق صوتية مركزة بتتجمع في نقطة داخل طبقة الشد العميقة">
<defs><linearGradient id="hg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16224a"/><stop offset="1" stop-color="#0c1430"/></linearGradient>
<radialGradient id="hp"><stop offset="0" stop-color="#ffe08a"/><stop offset=".5" stop-color="#e0a93a" stop-opacity=".7"/><stop offset="1" stop-color="#e0a93a" stop-opacity="0"/></radialGradient></defs>
<rect width="320" height="400" fill="url(#hg)"/>
<rect x="105" y="40" width="110" height="78" rx="18" fill="#eef1fb"/><rect x="120" y="54" width="80" height="22" rx="6" fill="#1d4fc4"/>
<text x="160" y="70" text-anchor="middle" font-size="12" fill="#fff" font-family="sans-serif">HIFU</text>
<rect x="128" y="118" width="64" height="12" rx="3" fill="#b9c1dc"/>

<rect x="0" y="150" width="320" height="34" fill="#f2c9b3"/><text x="300" y="172" text-anchor="start" direction="rtl" font-size="13" fill="#5a3426" font-family="sans-serif">البشرة</text>
<rect x="0" y="184" width="320" height="56" fill="#e8a990"/><text x="300" y="216" text-anchor="start" direction="rtl" font-size="13" fill="#5a2a1a" font-family="sans-serif">الأدمة</text>
<rect x="0" y="240" width="320" height="76" fill="#c97e6a"/><text x="300" y="300" text-anchor="start" direction="rtl" font-size="13" fill="#fff" font-family="sans-serif">طبقة الشد</text>
<rect x="0" y="316" width="320" height="84" fill="#9b5a4c"/><text x="300" y="362" text-anchor="start" direction="rtl" font-size="13" fill="#fff" font-family="sans-serif">العضلة</text>
<g fill="none" stroke="#ffe08a" stroke-width="2" class="beams"><path d="M132 132 160 280"/><path d="M146 132 160 280"/><path d="M174 132 160 280"/><path d="M188 132 160 280"/>
<path d="M132 132 112 300" opacity=".35"/><path d="M188 132 208 300" opacity=".35"/></g>
<g class="pts"><circle cx="160" cy="280" r="22" fill="url(#hp)"/><circle cx="112" cy="300" r="14" fill="url(#hp)"/><circle cx="208" cy="300" r="14" fill="url(#hp)"/></g>
<circle cx="160" cy="280" r="4" fill="#fff"/></svg>'''

# ---------- data ----------
PACKAGES = [
 dict(name="باقة النحت الأساسية", price=100, old=200, tag="الأكثر طلبًا",
      items=["كرايو (تجميد الدهون)", "كافيتيشن", "راديو فريكونسي", "ليزر بارد"]),
 dict(name="النحت + الميزوثيرابي", price=150, old=300, tag="",
      items=["الأربع أجهزة بتوع الباقة الأساسية", "+ جلسة ميزوثيرابي (6 حقن)"]),
 dict(name="شد الترهلات بالهايفو", price=250, old=500, tag="",
      items=["جلسة هايفو لشد الترهلات", "+ جلسة راديو فريكونسي"]),
 dict(name="الشد الكامل + كاربوكسي", price=300, old=600, tag="أقوى نتيجة شد",
      items=["جلسة هايفو + راديو فريكونسي", "+ حقن كاربوكسي لشد الترهلات"]),
]

# media: (kind, src, poster)  kind = video | img | hifu | icon
SECTIONS = [
 ("sculpt", "النحت والتخسيس الموضعي", "أجهزة بتشتغل على الدهون العنيدة في مكانها: البطن والجنبين والأرداف والذراعين.", [
  dict(n="الكرايو – تجميد الدهون", ic="snow", m=("video","media/cryo-device.mp4","media/cryo-device.jpg"),
       d="تبريد مدروس لخلايا الدهون في المنطقة المستهدفة فتتكسّر وتتخلص منها الجسم طبيعيًا على مدار الأسابيع، من غير جراحة ولا فترة نقاهة.", pk="ضمن باقة الـ100"),
  dict(n="الكافيتيشن", ic="wave", m=("img","media/dev-cavitation.jpg"),
       d="موجات صوتية منخفضة التردد بتفتّت الدهون الموضعية وبتساعد في تنعيم شكل السيلوليت، وغالبًا بتتعمل مع الراديو فريكونسي لنتيجة أسرع.", pk="ضمن باقة الـ100"),
  dict(n="الراديو فريكونسي RF", ic="radio", m=("video","media/rf.mp4","media/rf.jpg"),
       d="حرارة عميقة بتنشّط الكولاجين وبتشد الجلد بعد نزول الوزن، وبتحسّن ملمس البشرة والسيلوليت.", pk="ضمن باقة الـ100"),
  dict(n="الليزر البارد", ic="laser", m=("video","media/lipolaser.mp4","media/lipolaser.jpg"),
       d="ألواح ليزر منخفض الطاقة بتحفّز خلايا الدهون تفرّغ محتواها، جلسة مريحة تمامًا ومن غير ألم.", pk="ضمن باقة الـ100"),
  dict(n="الميزوثيرابي – حقن التخسيس الموضعي", ic="syringe", m=("video","media/meso.mp4","media/meso.jpg"),
       d="حقن موضعية بتساعد على إذابة الدهون العنيدة وشد المنطقة. الجلسة 6 حقن، وبتتحدد المناطق بعد الكشف.", pk="ضمن باقة الـ150"),
  dict(n="أجهزة السليندر", ic="slender", m=("img","media/dev-slender.jpg"),
       d="تمارين سلبية بتشغّل العضلات وانت مستريح، مناسبة لشد القوام وتحسين الدورة الدموية في الجسم كله.", pk=""),
  dict(n="الـ EMS – تحفيز العضلات", ic="bolt", m=("img","media/dev-ems.jpg"),
       d="نبضات كهربية بتعمل انقباضات عضلية قوية، تقوّي عضلات البطن والأرداف وتساعد في النحت مع الحرق.", pk=""),
  dict(n="الكريزي فيت", ic="vibe", m=("video","../gym/videos/crazyfit.mp4",""),
       d="منصة اهتزاز بتنشّط الدورة الدموية والليمفاوية وبتقوّي العضلات وتزوّد الحرق في دقايق.", pk=""),
 ]),
 ("tight", "شد الترهلات", "بعد التخسيس أو الولادة: نرجّع للجلد شدّه ومرونته.", [
  dict(n="الهايفو HIFU", ic="focus", m=("img","media/dev-hifu.jpg"),
       d="موجات فوق صوتية مركّزة بتوصل لطبقة الشد العميقة (SMAS) وبتعمل نقاط حرارية دقيقة بتشد الأنسجة وتحفّز كولاجين جديد. نتيجته بتبان تدريجيًا خلال أسابيع.", pk="ضمن باقة الـ250"),
  dict(n="الراديو فريكونسي لشد الترهلات", ic="radio", m=("video","media/rf-body.mp4","media/rf-body.jpg"),
       d="جلسات حرارة عميقة مخصصة لترهلات البطن والذراعين والأفخاذ، وبتكمّل نتيجة الهايفو.", pk="ضمن باقة الـ250"),
  dict(n="الكاربوكسي ثيرابي", ic="gas", m=("img","media/dev-carboxy.jpg"),
       d="حقن ثاني أكسيد الكربون الطبي تحت الجلد بيحسّن تدفق الدم والأكسجين للمنطقة، فيشد الترهلات ويقلل السيلوليت وعلامات التمدد.", pk="ضمن باقة الـ300"),
  dict(n="حقن شد الجلد والترهلات", ic="syringe", m=("video","media/belly-inj.mp4","media/belly-inj.jpg"),
       d="كوكتيل حقن ميزو مخصص لشد الجلد وتحسين مرونته بعد نزول الوزن، وبيتحدد نوعه وعدد الجلسات بعد الكشف.", pk=""),
 ]),
 ("beauty", "البشرة والتجميل", "عناية بالوش والبشرة بأجهزة طبية.", [
  dict(n="الهيدروفيشيال", ic="drop", m=("video","media/hydra.mp4","media/hydra.jpg"),
       d="تنظيف عميق للبشرة بخطوات: تقشير وشفط للرؤوس السوداء وترطيب بسيرومات، فتطلع البشرة نضرة من أول جلسة.", pk=""),
  dict(n="البلازما", ic="spark", m=("icon",),
       d="حقن البلازما الغنية بالصفائح من دمك لتجديد البشرة وتحسين النضارة والهالات، وتستخدم كمان لتقوية الشعر.", pk=""),
  dict(n="ميزوثيرابي البشرة", ic="syringe", m=("video","media/face-meso.mp4","media/face-meso.jpg"),
       d="حقن ميزو للبشرة بتغذّي الجلد وتحسّن النضارة والملمس، بإبر دقيقة وتحت إشراف الطبيب.", pk=""),
  dict(n="الديرمابن", ic="dots", m=("ba",),
       d="إبر دقيقة بتحفّز الكولاجين وبتعالج آثار الحبوب والمسام الواسعة وعلامات التمدد، وبتساعد السيروم يوصل لعمق البشرة.", pk=""),
 ]),
 ("laser", "إزالة الشعر بالليزر", "جلسات ليزر لكل مناطق الجسم.", [
  dict(n="ليزر إزالة الشعر – جهاز سان شور", ic="sun", m=("img","media/dev-laser.jpg"),
       d="إزالة الشعر بجهاز ليزر سان شور، مع تبريد لراحتك أثناء الجلسة. عدد الجلسات بيتحدد حسب المنطقة ونوع الشعر والبشرة.", pk=""),
 ]),
]

RESULTS = [("ba1.jpg",41),("ba2.jpg",59),("ba3.jpg",34),("ba4.jpg",22),("ba5.jpg",19),("ba6.jpg",25)]

BRANCHES = [
 ("فرع حلوان – الكورنيش", "كورنيش منشية جمال عبد الناصر، بجوار كشري العملاق، مدخل شارع محل فلاش، أعلى محل كريم البطل للدواجن", "السبت – الاثنين – الأربعاء", "من 3 العصر", "https://maps.app.goo.gl/fUDvMPkbsZ3dZLNo8"),
 ("فرع التبين", "مدخل المساكن، أمام مونجيني", "الأحد – الخميس", "من 7 مساءً", "https://maps.app.goo.gl/EfSoLcqr4deZM1Mo9"),
 ("فرع المعصرة", "شارع كوبري 45، بجوار مسجد أبو بكر", "الثلاثاء – الجمعة", "من 6 مساءً", "https://www.google.com/maps/search/?api=1&query=29.8924623%2C31.2924481"),
]

e = html.escape

def media(m, name):
    k = m[0]
    if k == "video":
        poster = f' poster="{m[2]}"' if m[2] else ""
        return f'<div class="media"><video data-src="{m[1]}"{poster} muted loop playsinline preload="none" aria-label="فيديو {e(name)}"></video></div>'
    if k == "img":
        return f'<div class="media"><img src="{m[1]}" alt="جهاز {e(name)} في Physio Art" loading="lazy"></div>'
    if k == "ba":
        return '<div class="media ba"><img src="media/derm-before.jpg" alt="قبل جلسات الديرمابن" loading="lazy"><img src="media/derm-after.jpg" alt="بعد جلسات الديرمابن" loading="lazy"><span class="lb t">قبل</span><span class="lb b">بعد</span></div>'
    if k == "hifu":
        return f'<div class="media">{HIFU_SVG}<span class="note">رسم توضيحي</span></div>'
    return ""

def svc_card(s):
    has_media = s["m"][0] != "icon"
    pk = f'<span class="pk">{e(s["pk"])}</span>' if s["pk"] else '<span></span>'
    head = "" if has_media else f'<div class="icon-tile">{icon(s["ic"], "big")}</div>'
    return f'''<article class="svc{' has-media' if has_media else ''}">
{media(s["m"], s["n"])}{head}
<div class="svc-body"><h3>{e(s["n"])}</h3><p>{e(s["d"])}</p>
<div class="svc-foot">{pk}<a class="link-wa" href="{wa("مرحبًا، حابب أحجز / أستفسر عن: " + s["n"])}" target="_blank" rel="noopener">{icon("wa","sm")} احجز</a></div></div>
</article>'''


DERM_BLOCK = """<div class="derm"><div class="derm-text"><span class="num">نتيجة حقيقية من العيادة</span><h4>الديرمابن: قبل وبعد</h4>
<p>الإبر الدقيقة بتعمل ثقوب مجهرية بتحفّز الكولاجين وبتساعد في علاج آثار الحبوب والمسام الواسعة، فتبان البشرة أنعم وأصفى.</p>
<p class="fine">اسحب الخط للمقارنة بين قبل وبعد. النتائج بتختلف من شخص لآخر حسب الحالة وعدد الجلسات.</p>
<a class="btn btn-gold" href="WA_DERM" target="_blank" rel="noopener">احجز جلسة ديرمابن</a></div>
<div class="cmp" id="cmp" dir="ltr" style="--p:50%"><img class="after" id="cmp-after" src="media/derm-after.jpg" alt="بعد جلسات الديرمابن" loading="lazy"><img class="before" src="media/derm-before.jpg" alt="قبل جلسات الديرمابن" loading="lazy"><span class="lb l">قبل</span><span class="lb r" id="cmp-r">بعد</span><div class="bar-line"></div><input type="range" min="2" max="98" value="50" aria-label="مقارنة قبل وبعد" id="cmp-range"></div></div>""".replace("WA_DERM", wa("مرحبًا، حابب أحجز جلسة ديرمابن"))

sections_html = ""
tabs_html = '<button class="chip on" data-f="all">الكل</button>'
for sid, title, sub, items in SECTIONS:
    tabs_html += f'<button class="chip" data-f="{sid}">{e(title)}</button>'
    cards = "\n".join(svc_card(s) for s in items)
    sections_html += f'''<div class="cat" data-cat="{sid}" id="{sid}"><div class="cat-head"><h3 class="cat-title">{e(title)}</h3><p>{e(sub)}</p></div>
<div class="svc-grid">{cards}</div>{DERM_BLOCK if sid=="beauty" else ""}</div>'''

pk_html = ""
FEAT_MSG = 'مرحبًا، حابب أحجز عرض الـ15 جلسة بـ 450 جنيه + 10 حقن ميزوثيرابي هدية'
for p in PACKAGES:
    tag = f'<span class="ribbon">{e(p["tag"])}</span>' if p["tag"] else ""
    lis = "".join(f'<li>{icon("check","sm")}{e(i)}</li>' for i in p["items"])
    msg = f'مرحبًا، حابب أحجز عرض "{p["name"]}" بـ {p["price"]} جنيه'
    pk_html += f'''<article class="pkg">{tag}<h3>{e(p["name"])}</h3>
<div class="price"><b>{p["price"]}</b><span>جنيه / الجلسة</span><s>{p["old"]} ج</s></div>
<ul>{lis}</ul><a class="btn btn-gold" href="{wa(msg)}" target="_blank" rel="noopener">احجز العرض</a></article>'''

res_html = "".join(f'<figure><img src="media/{f}" alt="نتيجة قبل وبعد – خسارة {kg} كيلو" loading="lazy" width="432" height="443"><figcaption>خسارة <b>{kg}</b> كيلو</figcaption></figure>' for f, kg in RESULTS)

br_html = "".join(f'''<article class="branch"><h3>{icon("pin")} {e(n)}</h3><p>{e(a)}</p>
<p class="hours">{icon("clock","sm")} <b>{e(d)}</b> · {e(t)}</p>
<a class="btn btn-ghost-dark" href="{m}" target="_blank" rel="noopener">افتح الموقع على الخريطة</a></article>''' for n, a, d, t, m in BRANCHES)

svc_options = "".join(f'<option>{e(x)}</option>' for x in
  ["كشف دايت بالإنبادي (أول مرة – 100 ج)", "متابعة دايت (30 ج)"] + [f'{p["name"]} – {p["price"]} ج' for p in PACKAGES] +
  ["حقن المونجارو / بديل التكميم – 1000 ج"] + [s["n"] for _,_,_,its in SECTIONS for s in its])
br_options = "".join(f'<option>{e(b[0])}</option>' for b in BRANCHES)

tpl = pathlib.Path(__file__).with_name("template.html").read_text()
out = (tpl.replace("{{SYMBOLS}}", SYMBOLS).replace("{{PACKAGES}}", pk_html).replace("{{TABS}}", tabs_html)
          .replace("{{SECTIONS}}", sections_html).replace("{{RESULTS}}", res_html).replace("{{BRANCHES}}", br_html)
          .replace("{{SVC_OPTIONS}}", svc_options).replace("{{BR_OPTIONS}}", br_options)
          .replace("{{WA_FEAT}}", wa(FEAT_MSG)).replace("{{WA_DIET}}", wa("مرحبًا، حابب أحجز كشف دايت بجهاز الإنبادي"))
          .replace("{{WA_MOUNJARO}}", wa("مرحبًا، حابب أستفسر عن حقن المونجارو (بديل التكميم) – عرض 1000 جنيه"))
          .replace("{{WA_HI}}", wa("مرحبًا، حابب أستفسر عن خدمات النحت والتخسيس في Physio Art"))
          .replace("{{ICON_WA}}", icon("wa","sm")).replace("{{ICON_PHONE}}", icon("phone","sm"))
          .replace("{{ICON_CHECK}}", icon("check","sm")).replace("{{ICON_SCALE}}", icon("scale","big")))
assert "{{" not in out, out[out.index("{{"):out.index("{{")+40]
pathlib.Path(__file__).resolve().parent.parent.joinpath("index.html").write_text(out)
print("ok", len(out))

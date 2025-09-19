
import streamlit as st
from pathlib import Path
import re
import base64
import random
import datetime as dt

# =========================
# CONFIG & THEME
# =========================
st.set_page_config(
    page_title="50 ORAÇÕES SAGRADAS DE ARCANJO MIGUEL",
    page_icon="🛡️",
    layout="centered",
)

st.markdown(
    """
    <style>
      :root { --gold:#D4AF37; --purple:#5A2A82; --bg:#0e0b12; }
      .app-wrap { max-width:392px; margin:0 auto; }
      .title-center h1 { text-align:center !important; margin:.25rem 0 .1rem; line-height:1.2 }
      .subtitle { text-align:center; margin-bottom:.65rem; opacity:.9 }
      .sticky {
        position: sticky; top: 0; z-index: 999;
        background: linear-gradient(180deg, rgba(14,11,18,.97), rgba(14,11,18,.88));
        backdrop-filter: blur(6px);
        border-bottom: 1px solid rgba(212,175,55,.18);
        padding: .35rem .5rem .6rem;
      }
      .card { border:1px solid rgba(212,175,55,.35); border-radius:14px; padding:.75rem .9rem; margin:.5rem 0; background:rgba(90,42,130,.04); }
      .title { font-weight:800; }
      .muted { opacity:.8; font-size:.9rem }
      .vday {
        border:1px dashed rgba(212,175,55,.45);
        border-radius:12px; padding:.6rem .75rem; background:rgba(212,175,55,.06);
        margin:.4rem 0 .6rem 0;
      }
      .vtitle { font-weight:800; color:var(--purple); margin-bottom:.25rem }
      .vref { font-size:.85rem; opacity:.8 }
      audio { width: 100% !important; }
      .stButton>button {
        background: linear-gradient(90deg, #5A2A82, #7b3ab3);
        color: #fff; border:0; border-radius:12px; padding:.25rem .6rem; font-weight:800;
      }
      /* Footer CTA keeps content visible above it */
      .footer-spacer { height: 76px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================
MEDIA_DIR = Path(".")
PDF_NAME = "50 ORAÇÕES PODEROSAS DE ARCANJO MIGUEL DEIXADAS POR PADRE PIO (CONTEÚDO EXCLUSIVO).pdf"
BIBLE_TXT = "biblia-em-txt.txt"

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())

def find_file_anycase(*candidates: str) -> Path | None:
    for cand in candidates:
        p = MEDIA_DIR / cand
        if p.exists():
            return p
    targets = [_norm(c) for c in candidates]
    for path in MEDIA_DIR.glob("*"):
        if path.is_file():
            stem = _norm(path.stem)
            if stem in targets or any(_norm(path.name).startswith(t) for t in targets):
                return path
    return None

def get_audio_path(n: int) -> Path | None:
    base = f"ORAÇÃO{n}"
    variants = [
        f"{base}.mp3",
        f"ORACAO{n}.mp3",
        f"Oracao{n}.mp3",
        f"oração{n}.mp3",
    ]
    return find_file_anycase(*variants)

def video_candidates() -> Path | None:
    names = [
        "BOAS VINDAS.mp4", "Boas Vindas.mp4", "boas_vindas.mp4",
        "BOAS_VINDAS.mp4", "Boas-Vindas.mp4", "boas-vindas.mp4",
    ]
    return find_file_anycase(*names)

def clean_title_from_path(p: Path) -> str:
    title = p.stem.replace("_", " ").replace("-", " ")
    title = re.sub(r"^(ORA(C|Ç)AO|Oração|oração)\\s*\\d+\\s*", "", title, flags=re.IGNORECASE)
    m = re.search(r"(\\d+)", p.stem)
    if not title.strip() and m:
        return f"Oração {int(m.group(1))}"
    return title.strip() or p.stem

def collect_category_indices(exp_label: str):
    if exp_label == "💰 Orações de Riqueza (1–20)":
        return list(range(1, 21))
    elif exp_label == "🌾 Orações de Prosperidade (21–40)":
        return list(range(21, 41))
    elif exp_label == "🕊️ Orações de Cura (41–50)":
        return list(range(41, 51))
    else:
        return []

def ensure_state():
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    if "todays_date" not in st.session_state:
        st.session_state.todays_date = dt.date.today().isoformat()
    if "todays_three" not in st.session_state or st.session_state.get("todays_date") != dt.date.today().isoformat():
        st.session_state.todays_date = dt.date.today().isoformat()
        st.session_state.todays_three = []

def parse_verse_of_day():
    path = find_file_anycase(BIBLE_TXT, BIBLE_TXT.upper(), BIBLE_TXT.lower())
    if not path or not path.exists():
        return None
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        try:
            lines = path.read_text(encoding="latin-1", errors="ignore").splitlines()
        except Exception:
            return None

    verses = []
    book = None
    chapter = None
    header_re = re.compile(r"^\\s*([A-ZÁÂÃÀÉÊÍÓÔÕÚÇÜ ]+?)\\s+(\\d+)\\s*$")
    verse_re = re.compile(r"^\\s*(\\d{1,3})\\s+(.+)$")

    for line in lines:
        h = header_re.match(line)
        if h:
            book = h.group(1).strip().title()
            chapter = h.group(2)
            continue
        v = verse_re.match(line)
        if v and book and chapter:
            if book in ("Salmos", "Provérbios"):
                vnum = v.group(1)
                vtext = v.group(2).strip()
                verses.append((f"{book} {chapter}:{vnum}", vtext))

    if not verses:
        return None
    doy = dt.date.today().timetuple().tm_yday
    idx = (doy - 1) % len(verses)
    return verses[idx]

# =========================
# STATE
# =========================
ensure_state()

# =========================
# UI START
# =========================
st.markdown("<div class='app-wrap'>", unsafe_allow_html=True)

# Versículo do dia
v = parse_verse_of_day()
if v:
    vref, vtext = v
    st.markdown(
        f"<div class='vday'><div class='vtitle'>📜 Versículo do Dia</div>"
        f"<div>{vtext}</div><div class='vref muted'>{vref}</div></div>",
        unsafe_allow_html=True,
    )

# Header fixo com seletor (PDF por último)
st.markdown("<div class='sticky'>", unsafe_allow_html=True)
st.markdown("<div class='title-center'><h1>50 ORAÇÕES SAGRADAS DE ARCANJO MIGUEL</h1></div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Escolha sua experiência e siga com fé.</div>", unsafe_allow_html=True)

exp_options = [
    "🎬 Boas-vindas (vídeo)",
    "💰 Orações de Riqueza (1–20)",
    "🌾 Orações de Prosperidade (21–40)",
    "🕊️ Orações de Cura (41–50)",
    "⭐ Favoritos",
    "🎯 Minhas 3 orações do dia",
    "📖 PDF completo (texto das 50 orações)",
]
exp = st.selectbox("Escolha uma experiência", options=exp_options)
st.session_state.current_exp = exp
st.markdown("</div>", unsafe_allow_html=True)

def render_video():
    st.markdown("<div class='label slim'>Mensagem de Boas-vindas</div>", unsafe_allow_html=True)
    vid = video_candidates()
    if vid:
        try:
            st.video(str(vid))
        except Exception as e:
            st.warning("Não foi possível carregar o vídeo.")
            st.code(str(e))
    else:
        st.info("Arquivo 'BOAS VINDAS.mp4' não encontrado.")

def render_pdf():
    st.markdown("<div class='label slim'>PDF das 50 orações</div>", unsafe_allow_html=True)
    pdf = find_file_anycase(PDF_NAME, PDF_NAME.replace('.pdf',''))
    if pdf and pdf.exists():
        data = pdf.read_bytes()
        st.download_button("📥 Baixar PDF", data=data, file_name=pdf.name, mime="application/pdf")
        b64 = base64.b64encode(data).decode()
        st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="520"></iframe>', unsafe_allow_html=True)
    else:
        st.info("PDF não encontrado.")

def render_category(label: str):
    rng = collect_category_indices(label)
    for i in rng:
        ap = get_audio_path(i)
        title = f"Oração {i}"
        if ap and ap.exists():
            title = clean_title_from_path(ap) or title
        # Título + favorito compacto à direita
        c1, c2 = st.columns([6,1])
        with c1:
            st.markdown(f"<div class='title'>{title}</div>", unsafe_allow_html=True)
        with c2:
            is_fav = i in st.session_state.favorites
            fav_label = "⭐" if not is_fav else "💛"
            if st.button(fav_label, key=f"fav_{i}"):
                if is_fav:
                    st.session_state.favorites = [n for n in st.session_state.favorites if n != i]
                else:
                    st.session_state.favorites.append(i)
        if ap and ap.exists():
            st.audio(str(ap))
        else:
            st.caption("Áudio não encontrado.")
        st.markdown("---")

def render_favorites():
    st.markdown("<div class='label slim'>Minhas orações favoritas</div>", unsafe_allow_html=True)
    favs = sorted(set(st.session_state.favorites))
    if not favs:
        st.info("Nenhum favorito ainda.")
    for i in favs:
        ap = get_audio_path(i)
        c1, c2 = st.columns([6,1])
        with c1:
            st.markdown(f"<div class='title'>Oração {i}</div>", unsafe_allow_html=True)
        with c2:
            if st.button("💛", key=f"fav_remove_{i}"):
                st.session_state.favorites = [n for n in st.session_state.favorites if n != i]
        if ap and ap.exists():
            st.audio(str(ap))
        else:
            st.caption("Áudio não encontrado.")
        st.markdown("---")

def render_daily_three():
    st.markdown("<div class='label slim'>Sugestão diária</div>", unsafe_allow_html=True)
    if not st.session_state.get("todays_three"):
        pool = [n for n in range(1, 51) if get_audio_path(n)]
        random.shuffle(pool)
        st.session_state.todays_three = pool[:3] if len(pool) >= 3 else pool
    for i in st.session_state.todays_three:
        ap = get_audio_path(i)
        c1, c2 = st.columns([6,1])
        with c1:
            st.markdown(f"<div class='title'>Oração {i}</div>", unsafe_allow_html=True)
        with c2:
            is_fav = i in st.session_state.favorites
            fav_label = "⭐" if not is_fav else "💛"
            if st.button(fav_label, key=f"fav_daily_{i}"):
                if is_fav:
                    st.session_state.favorites = [n for n in st.session_state.favorites if n != i]
                else:
                    st.session_state.favorites.append(i)
        if ap and ap.exists():
            st.audio(str(ap))
        else:
            st.caption("Áudio não encontrado.")
        st.markdown("---")

# Router
if exp == "🎬 Boas-vindas (vídeo)":
    render_video()
elif exp in ["💰 Orações de Riqueza (1–20)", "🌾 Orações de Prosperidade (21–40)", "🕊️ Orações de Cura (41–50)"]:
    render_category(exp)
elif exp == "⭐ Favoritos":
    render_favorites()
elif exp == "🎯 Minhas 3 orações do dia":
    render_daily_three()
elif exp == "📖 PDF completo (texto das 50 orações)":
    render_pdf()

# Espaço para não cobrir conteúdo pelo footer
st.markdown("<div class='footer-spacer'></div>", unsafe_allow_html=True)

# =========================
# FOOTER PROMO LINK
# =========================
st.markdown(
    """
    <div style="
        position:fixed;
        bottom:0;
        left:0;
        width:100%;
        background:linear-gradient(90deg, #5A2A82, #7b3ab3);
        color:#fff;
        text-align:center;
        padding:.8rem;
        font-weight:700;
        font-size:1rem;
        box-shadow:0 -2px 12px rgba(0,0,0,.25);
        z-index:999;
    ">
      ⚜️ Descubra o <b>Truque Sagrado do Rei Salomão</b> — ative milagres financeiros e espirituais hoje mesmo →
      <a href="https://lastlink.com/p/C4EF58CA2/checkout-payment" target="_blank" style="color:#FFD700; text-decoration:none; font-weight:800;">
        Clique aqui
      </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)

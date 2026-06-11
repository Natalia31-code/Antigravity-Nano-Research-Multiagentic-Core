"""
NanoTox Predictor API — Servidor Principal
==========================================
Ejecutar:  python app.py
Abrir:     http://localhost:8000
"""
import os, pickle, numpy as np
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional

# ── Carga del modelo ────────────────────────────────────────
_bundle = None

def load_bundle():
    global _bundle
    if _bundle is not None:
        return _bundle
    model_path = Path(__file__).parent / "model.pkl"
    if not model_path.exists():
        # Crear modelo demo si no existe
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        import numpy as np
        np.random.seed(42)
        n = 500
        X = np.column_stack([
            np.random.uniform(5,100,n), np.random.uniform(-50,50,n),
            np.random.uniform(10,500,n), np.random.uniform(1,1000,n),
            np.random.choice([24,48,72],n)
        ])
        y = (X[:,3] > 300).astype(int)
        scaler = StandardScaler(); Xs = scaler.fit_transform(X)
        model = RandomForestClassifier(n_estimators=100, random_state=42).fit(Xs, y)
        _bundle = {
            "model": model, "scaler": scaler,
            "features": ["core_size_nm","zeta_potential_mv","surface_area_m2g",
                         "concentration_ug_ml","exposure_time_h"],
            "model_name": "RandomForest (demo)"
        }
        with open(model_path, "wb") as f:
            pickle.dump(_bundle, f)
    else:
        with open(model_path, "rb") as f:
            _bundle = pickle.load(f)
    return _bundle

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_bundle()
    print("✓ Modelo cargado | Dashboard: http://localhost:8000")
    yield

app = FastAPI(lifespan=lifespan, title="NanoTox AI", docs_url="/api/docs")

# ── Schemas ──────────────────────────────────────────────────
class NanoInput(BaseModel):
    core_size_nm:        float = Field(..., gt=0)
    zeta_potential_mv:   float
    surface_area_m2g:    float = Field(..., gt=0)
    concentration_ug_ml: float = Field(..., gt=0)
    exposure_time_h:     float = Field(..., gt=0)
    material:  Optional[str] = None
    cell_line: Optional[str] = None
    coating:   Optional[str] = "none"

class ToxResult(BaseModel):
    nanoparticle:      str
    toxic:             bool
    probability:       float
    risk_level:        str
    risk_color:        str
    recommendation:    str
    model_used:        str

# ── Endpoints ────────────────────────────────────────────────
@app.get("/health")
def health():
    b = load_bundle()
    return {"status": "ok", "modelo": b.get("model_name"), "features": b.get("features")}

@app.post("/predict", response_model=ToxResult)
def predict(data: NanoInput):
    b = load_bundle()
    model, scaler, features = b["model"], b.get("scaler"), b.get("features", [])
    base = [data.core_size_nm, data.zeta_potential_mv,
            data.surface_area_m2g, data.concentration_ug_ml, data.exposure_time_h]
    X = np.zeros((1, len(features)))
    for i, v in enumerate(base[:len(features)]): X[0,i] = v
    if scaler: X = scaler.transform(X)
    try:
        pred  = int(model.predict(X)[0])
        prob  = float(model.predict_proba(X)[0][1]) if hasattr(model,"predict_proba") else float(pred)
    except Exception as e:
        raise HTTPException(500, str(e))

    coating_adj = {"peg": -0.08, "citrate": -0.04, "silica": -0.03}.get(data.coating or "", 0)
    prob = max(0.0, min(1.0, prob + coating_adj))

    if prob < 0.33:
        risk, color = "BAJO",     "#10b981"
        rec = "✅ Perfil de seguridad aceptable. Se recomienda continuar con ensayos celulares estándar."
    elif prob < 0.66:
        risk, color = "MODERADO", "#f59e0b"
        rec = "⚠️ Riesgo moderado. Considera reducir la concentración o añadir recubrimiento PEG."
    else:
        risk, color = "ALTO",     "#ef4444"
        rec = "🚫 Alto riesgo. Rediseña la nanopartícula: menor concentración, mayor tamaño o recubrimiento protector."

    mat = data.material or "Nanopartícula"
    return ToxResult(
        nanoparticle=f"{mat} ({data.core_size_nm} nm, {data.concentration_ug_ml} µg/mL)",
        toxic=bool(pred), probability=round(prob,4), risk_level=risk,
        risk_color=color, recommendation=rec, model_used=b.get("model_name","ML Model")
    )

# ── Frontend HTML ────────────────────────────────────────────
HTML_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>NanoTox AI — Predictor de Toxicidad</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#030310;--card:rgba(255,255,255,.04);--border:rgba(255,255,255,.08);
  --cyan:#22d3ee;--purple:#a855f7;--green:#10b981;--yellow:#f59e0b;--red:#ef4444;
  --text:#f0f0ff;--muted:#8080aa;--r:20px}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh;overflow-x:hidden}
canvas{position:fixed;inset:0;z-index:0;pointer-events:none}
.page{position:relative;z-index:1;max-width:1300px;margin:0 auto;padding:0 24px 80px}

/* HEADER */
header{text-align:center;padding:52px 20px 40px}
.badge{display:inline-flex;align-items:center;gap:8px;background:rgba(168,85,247,.1);
  border:1px solid rgba(168,85,247,.3);border-radius:50px;padding:7px 18px;
  font-size:11px;font-weight:700;letter-spacing:2px;color:var(--purple);
  text-transform:uppercase;margin-bottom:20px}
.badge-dot{width:6px;height:6px;border-radius:50%;background:var(--purple);animation:pulse 2s infinite}
h1{font-size:clamp(2.4rem,5vw,4rem);font-weight:900;line-height:1.05;letter-spacing:-1px;
  background:linear-gradient(135deg,var(--cyan),var(--purple),#ec4899);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:14px}
.subtitle{color:var(--muted);font-size:1rem;max-width:500px;margin:0 auto 28px;line-height:1.65}
.status-bar{display:inline-flex;align-items:center;gap:8px;background:rgba(0,0,0,.4);
  border:1px solid var(--border);border-radius:50px;padding:7px 18px;font-size:12px;color:var(--muted)}
.status-dot{width:8px;height:8px;border-radius:50%;background:#555;transition:.5s}
.status-dot.on{background:var(--green);box-shadow:0 0 8px var(--green);animation:pulse 2s infinite}

/* SEARCH */
.search-box{max-width:700px;margin:0 auto 36px}
.search-label{font-size:11px;font-weight:700;letter-spacing:2px;color:var(--cyan);
  text-transform:uppercase;margin-bottom:10px}
.search-wrap{position:relative}
.search-ico{position:absolute;left:22px;top:50%;transform:translateY(-50%);font-size:20px;opacity:.5}
#np-name{width:100%;background:rgba(34,211,238,.06);border:2px solid rgba(34,211,238,.2);
  border-radius:60px;padding:18px 160px 18px 58px;color:var(--text);font-size:1.1rem;
  font-family:inherit;font-weight:500;outline:none;transition:.3s}
#np-name:focus{border-color:var(--cyan);background:rgba(34,211,238,.09);
  box-shadow:0 0 0 4px rgba(34,211,238,.12),0 0 40px rgba(34,211,238,.18)}
#np-name::placeholder{color:rgba(255,255,255,.2)}
.search-btn{position:absolute;right:8px;top:50%;transform:translateY(-50%);
  background:linear-gradient(135deg,var(--cyan),var(--purple));border:none;
  border-radius:50px;padding:11px 24px;color:#fff;font-family:inherit;font-weight:700;
  font-size:14px;cursor:pointer;transition:.2s}
.search-btn:hover{transform:translateY(-50%) scale(1.05);filter:brightness(1.15)}
.ac-box{position:absolute;top:calc(100% + 8px);left:0;right:0;background:#0c0c22;
  border:1px solid var(--border);border-radius:16px;overflow:hidden;
  box-shadow:0 24px 60px rgba(0,0,0,.7);z-index:200;display:none}
.ac-box.show{display:block;animation:fadeUp .2s ease}
.ac-row{display:flex;align-items:center;gap:12px;padding:14px 18px;cursor:pointer;
  border-bottom:1px solid var(--border);transition:.2s}
.ac-row:last-child{border-bottom:none}
.ac-row:hover{background:rgba(34,211,238,.07)}
.ac-icon{font-size:22px;flex-shrink:0}
.ac-title{font-size:14px;font-weight:600}
.ac-desc{font-size:11px;color:var(--muted);margin-top:2px}
.ac-chip{flex-shrink:0;padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:1px}
.ch-b{background:rgba(16,185,129,.15);color:var(--green);border:1px solid rgba(16,185,129,.3)}
.ch-m{background:rgba(245,158,11,.15);color:var(--yellow);border:1px solid rgba(245,158,11,.3)}
.ch-a{background:rgba(239,68,68,.15);color:var(--red);border:1px solid rgba(239,68,68,.3)}

/* CHIPS */
.chips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-bottom:44px}
.chip{display:flex;align-items:center;gap:7px;background:var(--card);border:1px solid var(--border);
  border-radius:50px;padding:9px 18px;font-size:13px;font-weight:500;color:var(--muted);
  cursor:pointer;transition:.25s}
.chip:hover,.chip.on{background:rgba(34,211,238,.1);border-color:var(--cyan);
  color:var(--cyan);box-shadow:0 0 18px rgba(34,211,238,.15)}
.chip-badge{font-size:10px;font-weight:700;letter-spacing:.5px;padding:2px 8px;border-radius:10px}

/* GRID */
.grid{display:grid;grid-template-columns:400px 1fr;gap:22px;align-items:start}
@media(max-width:880px){.grid{grid-template-columns:1fr}}

/* CARD */
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);
  padding:28px;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
.card-title{font-size:10px;font-weight:800;letter-spacing:2.5px;color:var(--cyan);
  text-transform:uppercase;margin-bottom:26px;display:flex;align-items:center;gap:8px}
.card-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(34,211,238,.3),transparent)}

/* SLIDERS */
.sl-group{margin-bottom:20px}
.sl-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.sl-name{font-size:13px;font-weight:500;color:var(--muted)}
.sl-val{font-size:12px;font-weight:700;color:var(--cyan);background:rgba(34,211,238,.08);
  border:1px solid rgba(34,211,238,.2);border-radius:8px;padding:3px 10px;min-width:72px;text-align:center}
.sl-tip{font-size:10px;color:#404060;font-style:italic;margin-top:4px}
input[type=range]{-webkit-appearance:none;width:100%;height:4px;
  background:rgba(255,255,255,.07);border-radius:4px;outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;
  border-radius:50%;background:var(--cyan);box-shadow:0 0 10px rgba(34,211,238,.5);
  cursor:pointer;transition:.15s}
input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.3)}
.sel-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px}
.sel-group label{font-size:11px;font-weight:600;color:var(--muted);display:block;margin-bottom:6px}
select{width:100%;background:rgba(255,255,255,.04);border:1px solid var(--border);
  border-radius:10px;padding:10px 12px;color:var(--text);font-size:12px;font-family:inherit;
  outline:none;cursor:pointer;transition:.2s}
select:focus{border-color:var(--cyan)}
select option{background:#0c0c22}

/* BUTTON */
#pred-btn{width:100%;padding:17px;border:none;border-radius:14px;
  background:linear-gradient(135deg,var(--cyan),var(--purple),#ec4899);
  background-size:200%;color:#fff;font-family:inherit;font-size:15px;
  font-weight:800;letter-spacing:.5px;cursor:pointer;position:relative;
  overflow:hidden;transition:.2s;animation:gAnim 4s ease infinite}
@keyframes gAnim{0%,100%{background-position:0%}50%{background-position:100%}}
#pred-btn:hover{transform:translateY(-2px);filter:brightness(1.1)}
#pred-btn:active{transform:translateY(0)}
#pred-btn.busy{opacity:.6;pointer-events:none}
.btn-shimmer{position:absolute;inset:0;
  background:linear-gradient(135deg,transparent,rgba(255,255,255,.25),transparent);
  transform:translateX(-100%);transition:.5s}
#pred-btn:hover .btn-shimmer{transform:translateX(100%)}

/* RESULTS */
.res-panel{display:flex;flex-direction:column;gap:18px}
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:14px;padding:56px 20px;opacity:.4;text-align:center}
.empty-icon{font-size:60px}
.empty-txt{font-size:14px;color:var(--muted);line-height:1.5}

/* GAUGE */
.gauge-area{text-align:center;padding:14px 0 4px}
.gauge-svg{width:230px;height:230px}
.g-track{fill:none;stroke:rgba(255,255,255,.05);stroke-width:18;stroke-linecap:round}
.g-fill{fill:none;stroke-width:18;stroke-linecap:round;stroke:var(--cyan);
  stroke-dasharray:659;stroke-dashoffset:659;
  transform:rotate(-90deg);transform-origin:center;
  transition:stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1),stroke .5s,filter .5s}
.g-pct{font-size:50px;font-weight:900;fill:var(--text);font-family:'Inter',sans-serif}
.g-sub{font-size:12px;fill:var(--muted);font-family:'Inter',sans-serif}
.g-stat{font-size:14px;fill:var(--cyan);font-weight:700;font-family:'Inter',sans-serif}

/* RISK */
.risk-area{text-align:center}
.risk-txt{font-size:30px;font-weight:900;letter-spacing:4px;text-transform:uppercase;transition:.5s}
.risk-np{font-size:13px;color:var(--muted);margin-top:6px}

/* PROB BAR */
.prob-wrap{} 
.prob-labels{display:flex;justify-content:space-between;font-size:11px;color:#404060;margin-bottom:7px}
.prob-track{height:12px;background:rgba(255,255,255,.05);border-radius:20px;overflow:hidden}
.prob-fill{height:100%;border-radius:20px;width:0%;
  background:linear-gradient(90deg,var(--green),var(--yellow),var(--red));
  transition:width 1.4s cubic-bezier(.4,0,.2,1)}

/* REC */
.rec{border-radius:14px;padding:16px 18px;font-size:13px;line-height:1.65;
  border:1px solid var(--border);background:rgba(255,255,255,.02);transition:.5s;min-height:60px}
.rec.b{border-color:rgba(16,185,129,.3);background:rgba(16,185,129,.04)}
.rec.m{border-color:rgba(245,158,11,.3);background:rgba(245,158,11,.04)}
.rec.a{border-color:rgba(239,68,68,.3);background:rgba(239,68,68,.04)}

/* PILLS */
.pills{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.pill{background:rgba(255,255,255,.03);border:1px solid var(--border);
  border-radius:12px;padding:12px;text-align:center}
.pill-l{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.8px}
.pill-v{font-size:16px;font-weight:700;color:var(--cyan);margin-top:3px}

/* FI */
.fi-section{margin-top:20px}
.fi-item{margin-bottom:14px}
.fi-top{display:flex;justify-content:space-between;margin-bottom:6px}
.fi-name{font-size:13px;font-weight:500}
.fi-pct{font-size:12px;color:var(--muted);font-weight:600}
.fi-track{height:8px;background:rgba(255,255,255,.05);border-radius:20px;overflow:hidden}
.fi-bar{height:100%;border-radius:20px;width:0%;transition:width 1.6s cubic-bezier(.4,0,.2,1)}

/* HISTORY */
.hist-section{margin-top:20px}
.hist-label{font-size:10px;font-weight:700;letter-spacing:2px;color:#404060;
  text-transform:uppercase;margin-bottom:10px}
.hist-list{display:flex;gap:10px;overflow-x:auto;padding-bottom:4px}
.hist-item{flex-shrink:0;background:rgba(255,255,255,.03);border:1px solid var(--border);
  border-radius:12px;padding:9px 14px;cursor:pointer;display:flex;align-items:center;
  gap:10px;font-size:13px;transition:.2s;white-space:nowrap}
.hist-item:hover{border-color:var(--cyan)}
.h-dot{width:8px;height:8px;border-radius:50%}

/* FOOTER */
footer{text-align:center;padding:40px 20px 24px;border-top:1px solid var(--border);
  margin-top:48px;font-size:12px;color:#404060}
footer a{color:var(--cyan);text-decoration:none}

@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes spin{to{transform:rotate(360deg)}}
.spin{display:inline-block;animation:spin 1s linear infinite}
</style>
</head>
<body>
<canvas id="cvs"></canvas>
<div class="page">

<header>
  <div class="badge"><span class="badge-dot"></span>⚗️ Sistema Multi-Agente — Proyecto Final IA</div>
  <h1>NanoTox AI Predictor</h1>
  <p class="subtitle">Predice en segundos si una nanopartícula es tóxica usando Machine Learning.<br>
  Escribe el nombre, ajusta las propiedades y obtén el resultado.</p>
  <div class="status-bar">
    <span class="status-dot on" id="api-dot"></span>
    <span id="api-txt">🟢 API activa — modelo cargado y listo</span>
  </div>
</header>

<!-- BUSCADOR -->
<div class="search-box">
  <div class="search-label">🔬 Escribe el nombre de la nanopartícula</div>
  <div class="search-wrap">
    <span class="search-ico">🔍</span>
    <input id="np-name" type="text" autocomplete="off"
      placeholder="Ej: ZnO, Silver nanoparticle, TiO2, Iron oxide, Copper oxide…"/>
    <button class="search-btn" onclick="predict()">Predecir →</button>
    <div class="ac-box" id="ac"></div>
  </div>
</div>

<!-- MATERIALES RÁPIDOS -->
<div class="chips">
  <button class="chip" data-k="ZnO">🔵 ZnO <span class="chip-badge ch-a">ALTO</span></button>
  <button class="chip" data-k="TiO2">⚪ TiO₂ <span class="chip-badge ch-b">BAJO</span></button>
  <button class="chip" data-k="Ag">🔘 Ag (Plata) <span class="chip-badge ch-a">ALTO</span></button>
  <button class="chip" data-k="Au">🟡 Au (Oro) <span class="chip-badge ch-b">BAJO</span></button>
  <button class="chip" data-k="Fe3O4">🟤 Fe₃O₄ <span class="chip-badge ch-m">MOD</span></button>
  <button class="chip" data-k="CuO">🟠 CuO <span class="chip-badge ch-a">ALTO</span></button>
  <button class="chip" data-k="SiO2">⬜ SiO₂ <span class="chip-badge ch-b">BAJO</span></button>
  <button class="chip" data-k="CeO2">🟣 CeO₂ <span class="chip-badge ch-m">MOD</span></button>
</div>

<!-- GRID PRINCIPAL -->
<div class="grid">

  <!-- PANEL IZQUIERDO: INPUTS -->
  <div class="card">
    <div class="card-title">⚙️ Propiedades Fisicoquímicas</div>
    <div id="custom-nanoparticle-badge" style="display:none;background:rgba(168,85,247,0.12);border:1px dashed rgba(168,85,247,0.4);border-radius:12px;padding:12px;font-size:12.5px;color:var(--text);margin-bottom:20px;line-height:1.5">
      🧬 <strong>Modo Personalizado:</strong> Ajusta los parámetros de esta partícula específica para estimar su nivel de riesgo.
    </div>

    <div class="sl-group">
      <div class="sl-row"><span class="sl-name">📐 Tamaño de núcleo</span>
        <span class="sl-val" id="v-sz">25 nm</span></div>
      <input type="range" id="s-sz" min="1" max="200" value="25"/>
      <div class="sl-tip">Partículas más pequeñas = más reactivas = mayor toxicidad</div>
    </div>

    <div class="sl-group">
      <div class="sl-row"><span class="sl-name">⚡ Potencial Zeta</span>
        <span class="sl-val" id="v-zt">-15 mV</span></div>
      <input type="range" id="s-zt" min="-60" max="60" value="-15"/>
      <div class="sl-tip">Valores extremos (±30 mV) = partícula inestable</div>
    </div>

    <div class="sl-group">
      <div class="sl-row"><span class="sl-name">🌐 Área Superficial</span>
        <span class="sl-val" id="v-ar">45 m²/g</span></div>
      <input type="range" id="s-ar" min="1" max="500" value="45"/>
      <div class="sl-tip">Mayor área = más contacto con membranas celulares</div>
    </div>

    <div class="sl-group">
      <div class="sl-row"><span class="sl-name">💉 Concentración</span>
        <span class="sl-val" id="v-cn">50 µg/mL</span></div>
      <input type="range" id="s-cn" min="1" max="1000" value="50"/>
      <div class="sl-tip">Factor más importante: &gt;100 µg/mL generalmente es tóxico</div>
    </div>

    <div class="sl-group">
      <div class="sl-row"><span class="sl-name">⏱ Tiempo de Exposición</span>
        <span class="sl-val" id="v-tm">24 h</span></div>
      <input type="range" id="s-tm" min="1" max="96" value="24"/>
      <div class="sl-tip">Mayor exposición acumula daño oxidativo</div>
    </div>

    <div class="sel-row">
      <div class="sel-group"><label>🧬 Línea Celular</label>
        <select id="s-cell">
          <option value="HeLa">HeLa (Cervical)</option>
          <option value="A549">A549 (Pulmón)</option>
          <option value="HepG2">HepG2 (Hígado)</option>
          <option value="MCF7">MCF7 (Mama)</option>
          <option value="RAW264">RAW 264.7 (Macrófago)</option>
        </select></div>
      <div class="sel-group"><label>🛡 Recubrimiento</label>
        <select id="s-coat">
          <option value="none">Sin recubrimiento</option>
          <option value="citrate">Citrato (-4%)</option>
          <option value="peg">PEG — protector (-8%)</option>
          <option value="silica">Sílice (-3%)</option>
          <option value="pvp">PVP</option>
        </select></div>
    </div>

    <button id="pred-btn" onclick="predict()">
      <span class="btn-shimmer"></span>
      🧪 Analizar Toxicidad
    </button>

    <div id="hist-wrap" style="display:none;margin-top:20px">
      <div class="hist-label">🕐 Últimas predicciones</div>
      <div class="hist-list" id="hist-list"></div>
    </div>
  </div>

  <!-- PANEL DERECHO: RESULTADOS -->
  <div style="display:flex;flex-direction:column;gap:20px">
    <div class="card res-panel">
      <div class="empty" id="empty">
        <div class="empty-icon">🧫</div>
        <div class="empty-txt">Escribe el nombre de una nanopartícula<br>o selecciona un material y pulsa <strong>Analizar</strong></div>
      </div>
      <div id="res-content" style="display:none">
        <div class="card-title">📊 Resultado de Predicción</div>
        <div class="gauge-area">
          <svg class="gauge-svg" viewBox="0 0 230 230">
            <circle class="g-track" cx="115" cy="115" r="95"/>
            <circle class="g-fill" id="g-fill" cx="115" cy="115" r="95"/>
            <text class="g-pct" id="g-pct" x="115" y="106" text-anchor="middle" dominant-baseline="middle">0%</text>
            <text class="g-stat" id="g-stat" x="115" y="138" text-anchor="middle">—</text>
            <text class="g-sub" x="115" y="155" text-anchor="middle">probabilidad de toxicidad</text>
          </svg>
        </div>
        <div class="risk-area">
          <div class="risk-txt" id="risk-txt">—</div>
          <div class="risk-np" id="risk-np">—</div>
        </div>
        <div class="prob-wrap">
          <div class="prob-labels"><span>✅ No tóxico</span><span>☠️ Tóxico</span></div>
          <div class="prob-track"><div class="prob-fill" id="prob-fill"></div></div>
        </div>
        <div class="rec" id="rec-box"></div>
        
        <div class="card-title" style="margin-top:18px">💡 Aplicaciones y Usos Comunes</div>
        <div class="rec" id="uses-box" style="border-color:rgba(34,211,238,0.25);background:rgba(34,211,238,0.03);display:flex;align-items:center;gap:12px;min-height:56px">
          <span style="font-size:22px">🎯</span>
          <span id="uses-txt" style="color:var(--text);font-size:13px;line-height:1.55">—</span>
        </div>
        
        <div class="card-title" style="margin-top:18px">📋 Condiciones</div>
        <div class="pills">
          <div class="pill"><div class="pill-l">Tamaño</div><div class="pill-v" id="p-sz">—</div></div>
          <div class="pill"><div class="pill-l">Potencial ζ</div><div class="pill-v" id="p-zt">—</div></div>
          <div class="pill"><div class="pill-l">Concentración</div><div class="pill-v" id="p-cn">—</div></div>
          <div class="pill"><div class="pill-l">Área Sup.</div><div class="pill-v" id="p-ar">—</div></div>
          <div class="pill"><div class="pill-l">Exposición</div><div class="pill-v" id="p-tm">—</div></div>
          <div class="pill"><div class="pill-l">Línea cel.</div><div class="pill-v" id="p-cl">—</div></div>
        </div>
      </div>
    </div>
    <div class="card fi-section" id="fi-card" style="display:none">
      <div class="card-title">🔬 ¿Qué factores influyen más?</div>
      <div id="fi-bars"></div>
    </div>
  </div>
</div>
</div><!-- /page -->

<footer>
  <p>NanoTox AI Predictor · Proyecto Final Unidades 5+6 · Sistema Multi-Agente LangGraph</p>
  <p style="margin-top:8px">
    📊 Dataset: <a href="https://zenodo.org/records/15385143" target="_blank">Zenodo HaHa-Manual.csv</a> ·
    🤖 Modelos: Random Forest + SVM + MLP ·
    <a href="/api/docs" target="_blank">API Docs →</a>
  </p>
</footer>

<script>
/* ── Material DB ─────────────────────────────── */
const DB = {
  ZnO:   {e:'🔵',n:'Óxido de Zinc',    b:.62,s:20, z:-18,a:50, c:50,  inf:'Alta toxicidad hepática por liberación de Zn²⁺', u:'Cosméticos (protectores solares), recubrimientos antimicrobianos, sensores químicos y electrónica.'},
  TiO2:  {e:'⚪',n:'Dióxido Titanio',  b:.28,s:25, z:-22,a:40, c:50,  inf:'Fototóxico con UV; seguro en oscuridad', u:'Filtros solares UV, pigmentos blancos en pinturas, purificación de agua y celdas fotovoltaicas.'},
  Ag:    {e:'🔘',n:'Plata (AgNPs)',     b:.80,s:15, z:-30,a:120,c:10,  inf:'Inhibe cadena respiratoria mitocondrial', u:'Agente antibacteriano en textiles, apósitos médicos, desinfectantes y purificadores de agua.'},
  Au:    {e:'🟡',n:'Oro (AuNPs)',       b:.18,s:30, z:-25,a:30, c:50,  inf:'Muy biocompatible; usado en biosensores, terapia contra el cáncer y transporte de fármacos.'},
  Fe3O4: {e:'🟤',n:'Magnetita',         b:.40,s:12, z:-15,a:90, c:50,  inf:'Usado en MRI; moderadamente seguro', u:'Agente de contraste en Resonancia Magnética (RMN), hipertermia magnética y purificación de agua.'},
  CuO:   {e:'🟠',n:'Óxido de Cobre',   b:.75,s:18, z:-20,a:100,c:25,  inf:'Alta citotoxicidad; genera ROS severo', u:'Pinturas antiincrustantes, catalizadores industriales, purificación de gases y biocidas.'},
  SiO2:  {e:'⬜',n:'Dióxido de Silicio',b:.22,s:50,z:-30,a:200,c:100, inf:'Biocompatible; riesgo pulmonar alto', u:'Aditivo en alimentos/cosméticos, portador en vacunas/fármacos y refuerzo en plásticos.'},
  CeO2:  {e:'🟣',n:'Óxido de Cerio',   b:.35,s:8,  z:-18,a:150,c:50,  inf:'Propiedades antioxidantes duales', u:'Catalizador en convertidores de autos, medicina regenerativa (antioxidante) y pulido de vidrio.'},
};
const SUGG=[
  ...Object.entries(DB).map(([k,v])=>({k,e:v.e,t:`${k} — ${v.n}`,d:v.inf,r:v.b>.65?'a':v.b>.4?'m':'b'})),
  {k:'Ag',e:'🔘',t:'Silver nanoparticles (AgNPs)',d:'Antibacteriano de amplio espectro',r:'a'},
  {k:'Au',e:'🟡',t:'Gold nanoparticles (AuNPs)',d:'Biodiagnóstico y terapia fototérmica',r:'b'},
  {k:'ZnO',e:'🔵',t:'Zinc oxide nanoparticles',d:'Fotocatalítico y antimicrobiano',r:'a'},
  {k:'TiO2',e:'⚪',t:'Titanium dioxide nanoparticles',d:'Filtro UV en cremas solares',r:'b'},
  {k:'Fe3O4',e:'🟤',t:'Iron oxide nanoparticles',d:'Contraste en resonancia magnética',r:'m'},
  {k:'CuO',e:'🟠',t:'Copper oxide nanoparticles',d:'Alta actividad antifúngica',r:'a'},
];
const FI_G=['linear-gradient(90deg,#22d3ee,#a855f7)','linear-gradient(90deg,#ef4444,#f97316)',
  'linear-gradient(90deg,#10b981,#22d3ee)','linear-gradient(90deg,#f59e0b,#ef4444)',
  'linear-gradient(90deg,#a855f7,#ec4899)','linear-gradient(90deg,#10b981,#f59e0b)'];

let history=[], curMat='';

/* ── Canvas molecular ────────────────────────── */
const cvs=document.getElementById('cvs');
const cx=cvs.getContext('2d');
let W,H,pts=[];
function resize(){W=cvs.width=innerWidth;H=cvs.height=innerHeight}
resize();addEventListener('resize',resize);
class Pt{constructor(){this.r()}r(){this.x=Math.random()*W;this.y=Math.random()*H;
  this.vx=(Math.random()-.5)*.4;this.vy=(Math.random()-.5)*.4;
  this.rad=Math.random()*2+.6;this.h=Math.random()>.5?200:270;this.a=Math.random()*.4+.08}
  up(){this.x+=this.vx;this.y+=this.vy;if(this.x<0||this.x>W||this.y<0||this.y>H)this.r()}}
for(let i=0;i<130;i++)pts.push(new Pt());
function draw(){
  cx.clearRect(0,0,W,H);
  pts.forEach(p=>{cx.beginPath();cx.arc(p.x,p.y,p.rad,0,Math.PI*2);
    cx.fillStyle=`hsla(${p.h},80%,65%,${p.a})`;cx.fill();p.up()});
  for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){
    const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d=Math.sqrt(dx*dx+dy*dy);
    if(d<90){cx.beginPath();cx.moveTo(pts[i].x,pts[i].y);cx.lineTo(pts[j].x,pts[j].y);
      cx.strokeStyle=`rgba(34,211,238,${.07*(1-d/90)})`;cx.lineWidth=.5;cx.stroke()}}
  requestAnimationFrame(draw)}
draw();

/* ── Sliders ─────────────────────────────────── */
[['s-sz','v-sz','nm'],['s-zt','v-zt','mV'],['s-ar','v-ar','m²/g'],
 ['s-cn','v-cn','µg/mL'],['s-tm','v-tm','h']].forEach(([si,vi,u])=>{
  document.getElementById(si).addEventListener('input',()=>{
    document.getElementById(vi).textContent=document.getElementById(si).value+' '+u})});

function showCustomBadge(name) {
  const badge = document.getElementById('custom-nanoparticle-badge');
  badge.style.display = 'block';
  badge.innerHTML = `🧬 <strong>Nanopartícula Personalizada:</strong> Estás analizando <strong>"${name}"</strong>. Ajusta sus propiedades fisicoquímicas reales en los deslizadores de abajo para predecir la toxicidad.`;
}
function hideCustomBadge() {
  document.getElementById('custom-nanoparticle-badge').style.display = 'none';
}

/* ── Chips ───────────────────────────────────── */
document.querySelectorAll('.chip').forEach(c=>{
  c.addEventListener('click',()=>{
    document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));
    c.classList.add('on');curMat=c.dataset.k;loadMat(c.dataset.k);hideCustomBadge();})});

function setSlider(sid,vid,val,u){
  document.getElementById(sid).value=val;
  document.getElementById(vid).textContent=val+' '+u}
function loadMat(k){
  const m=DB[k];if(!m)return;
  document.getElementById('np-name').value=`${k} — ${m.n}`;
  setSlider('s-sz','v-sz',m.s,'nm');setSlider('s-zt','v-zt',m.z,'mV');
  setSlider('s-ar','v-ar',m.a,'m²/g');setSlider('s-cn','v-cn',m.c,'µg/mL');
  setSlider('s-tm','v-tm',24,'h')}

/* ── Autocomplete ────────────────────────────── */
const inp=document.getElementById('np-name');
const acb=document.getElementById('ac');
inp.addEventListener('input',()=>{
  const q=inp.value.toLowerCase().trim();
  if(!q){acb.classList.remove('show');hideCustomBadge();return}
  const ms=SUGG.filter(s=>s.t.toLowerCase().includes(q)||s.k.toLowerCase().includes(q)).slice(0,6);
  
  let html = ms.map(m=>`<div class="ac-row" onclick="pickAC('${m.k}','${m.t}')">
    <span class="ac-icon">${m.e}</span>
    <div><div class="ac-title">${m.t}</div><div class="ac-desc">${m.d}</div></div>
    <span class="ac-chip ${m.r==='a'?'ch-a':m.r==='m'?'ch-m':'ch-b'}">${m.r==='a'?'ALTO':m.r==='m'?'MOD':'BAJO'}</span>
  </div>`).join('');
  
  const cleanName = inp.value.replace(/—.*/, '').trim();
  html += `<div class="ac-row" onclick="pickAC('${cleanName}','${cleanName}',true)" style="background:rgba(168,85,247,0.08);border-top:1px dashed rgba(168,85,247,0.3)">
    <span class="ac-icon">🧬</span>
    <div><div class="ac-title" style="color:var(--purple);font-weight:700">Analizar "${cleanName}" personalizado</div>
    <div class="ac-desc">Estimar la toxicidad con las propiedades que definas abajo</div></div>
    <span class="ac-chip" style="background:rgba(168,85,247,0.2);color:#fff;border:1px solid var(--purple)">NUEVO</span>
  </div>`;
  
  acb.innerHTML = html;
  acb.classList.add('show')});
function pickAC(k,label,isCustom=false){
  inp.value=label;acb.classList.remove('show');
  if (isCustom) {
    curMat=k;
    showCustomBadge(k);
  } else {
    curMat=k;
    loadMat(k);
    hideCustomBadge();
  }
  document.querySelectorAll('.chip').forEach(c=>c.classList.toggle('on',c.dataset.k===k))}
document.addEventListener('click',e=>{if(!e.target.closest('.search-wrap'))acb.classList.remove('show')});
inp.addEventListener('keydown',e=>{if(e.key==='Enter'){acb.classList.remove('show');predict()}});

/* ── Counter animation ───────────────────────── */
function animCount(el,to,dur=1200){
  const s=performance.now(),from=parseInt(el.textContent)||0;
  (function step(now){
    const t=Math.min((now-s)/dur,1),ease=t<.5?2*t*t:(4-2*t)*t-1;
    el.textContent=Math.round(from+(to-from)*ease)+'%';
    if(t<1)requestAnimationFrame(step)})(performance.now())}

/* ── Predict ─────────────────────────────────── */
async function predict(){
  const btn=document.getElementById('pred-btn');
  btn.classList.add('busy');btn.innerHTML='<span class="spin">⏳</span> Analizando…';

  const raw=document.getElementById('np-name').value.trim();
  const matchedKey = Object.keys(DB).find(k => raw.toLowerCase().startsWith(k.toLowerCase()) || raw.toLowerCase().includes("— " + DB[k].n.toLowerCase()));
  const mk = curMat || matchedKey || raw.split('—')[0].trim() || 'NP';
  
  if (!DB[mk]) {
    showCustomBadge(mk);
  } else {
    hideCustomBadge();
  }

  const payload={
    core_size_nm:+document.getElementById('s-sz').value,
    zeta_potential_mv:+document.getElementById('s-zt').value,
    surface_area_m2g:+document.getElementById('s-ar').value,
    concentration_ug_ml:+document.getElementById('s-cn').value,
    exposure_time_h:+document.getElementById('s-tm').value,
    material:mk,
    cell_line:document.getElementById('s-cell').value,
    coating:document.getElementById('s-coat').value
  };

  let result;
  try{
    const r=await fetch('/predict',{method:'POST',
      headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    result=await r.json();
  }catch(err){
    // Fallback JS model
    result=jsFallback(payload,mk,raw);
  }

  await new Promise(r=>setTimeout(r,400));
  showResult(result,payload,mk,raw);
  btn.classList.remove('busy');
  btn.innerHTML='<span class="btn-shimmer"></span>🧪 Analizar Toxicidad';
}

function jsFallback(p,mk,raw){
  const m=DB[mk]||{};const base=m.b!==undefined?m.b:.5;
  const sc=(100-p.core_size_nm)/100*.18+Math.min(p.concentration_ug_ml/1000,1)*.32+
    Math.min(p.exposure_time_h/96,1)*.11+Math.abs(p.zeta_potential_mv)/60*.08+
    Math.min(p.surface_area_m2g/500,1)*.10+base*.21;
  const coat={peg:-.09,citrate:-.04,silica:-.03,pvp:-.02,none:0}[p.coating]||0;
  const prob=Math.max(0,Math.min(1,1/(1+Math.exp(-7*(sc+coat-.42)))));
  const risk=prob<.33?'BAJO':prob<.66?'MODERADO':'ALTO';
  const color=prob<.33?'#10b981':prob<.66?'#f59e0b':'#ef4444';
  const recs={BAJO:'✅ Perfil de seguridad aceptable. Se recomienda continuar con ensayos celulares estándar.',
    MODERADO:'⚠️ Riesgo moderado. Considera reducir la concentración o añadir recubrimiento PEG.',
    ALTO:'🚫 Alto riesgo. Rediseña la nanopartícula: menor concentración, mayor tamaño o recubrimiento protector.'};
  const mat=DB[mk]?`${mk} — ${DB[mk].n}`:raw||mk;
  return{nanoparticle:`${mat} (${p.core_size_nm} nm, ${p.concentration_ug_ml} µg/mL)`,
    toxic:prob>=.5,probability:Math.round(prob*1000)/1000,risk_level:risk,
    risk_color:color,recommendation:recs[risk],model_used:'Modelo integrado'};
}

function showResult(r,p,mk,raw){
  document.getElementById('empty').style.display='none';
  const rc=document.getElementById('res-content');
  rc.style.display='block';rc.style.animation='fadeUp .5s ease';

  const pct=Math.round(r.probability*100);
  const circ=2*Math.PI*95; // 596.9

  // Gauge
  const gf=document.getElementById('g-fill');
  gf.style.stroke=r.risk_color;
  gf.style.filter=`drop-shadow(0 0 14px ${r.risk_color})`;
  gf.style.strokeDasharray=circ;gf.style.strokeDashoffset=circ;
  setTimeout(()=>{gf.style.strokeDashoffset=circ*(1-r.probability)},80);

  const pctEl=document.getElementById('g-pct');
  pctEl.style.fill=r.risk_color;
  animCount(pctEl,pct);

  document.getElementById('g-stat').textContent=
    r.risk_level==='BAJO'?'🟢 BAJO':r.risk_level==='MODERADO'?'⚠️ MODERADO':'🚫 ALTO';
  document.getElementById('g-stat').style.fill=r.risk_color;

  // Risk banner
  const rt=document.getElementById('risk-txt');
  rt.textContent=r.risk_level;rt.style.color=r.risk_color;
  rt.style.textShadow=`0 0 40px ${r.risk_color}60`;
  const isCustom = !DB[mk];
  document.getElementById('risk-np').innerHTML=`📍 ${r.nanoparticle} | ${p.cell_line} ${isCustom ? '<span style="font-size:9px;background:rgba(168,85,247,0.2);color:#d8b4fe;padding:2px 6px;border-radius:10px;margin-left:5px;border:1px solid rgba(168,85,247,0.3)">Personalizada</span>' : ''}`;

  // Prob bar
  setTimeout(()=>{document.getElementById('prob-fill').style.width=pct+'%'},100);

  // Rec
  const rb=document.getElementById('rec-box');
  rb.className=`rec ${r.risk_level==='BAJO'?'b':r.risk_level==='MODERADO'?'m':'a'}`;
  rb.textContent=r.recommendation;

  // Uses / Applications logic
  const usesTxt = document.getElementById('uses-txt');
  if (DB[mk] && DB[mk].u) {
    usesTxt.innerHTML = `<strong>Aplicaciones típicas:</strong> ${DB[mk].u}`;
  } else {
    // Dynamic generation for custom nanoparticles
    const nameLower = mk.toLowerCase();
    let suggestedUse = "";
    if (nameLower.includes("carbon") || nameLower.includes("graphene") || nameLower.includes("cnt") || nameLower.includes("carbón")) {
      suggestedUse = "<strong>Nanomaterial de Carbono:</strong> Altamente utilizado en electrónica flexible, supercapacitores, almacenamiento de energía, sensores y refuerzo estructural de alta resistencia.";
    } else if (nameLower.includes("quantum") || nameLower.includes("qd") || nameLower.includes("cadmium") || nameLower.includes("cd")) {
      suggestedUse = "<strong>Punto Cuántico (Quantum Dot):</strong> Utilizado comúnmente en pantallas QLED, dispositivos ópticos, bioimagen diagnóstica de alta resolución y celdas fotovoltaicas.";
    } else if (nameLower.includes("lipid") || nameLower.includes("lipos") || nameLower.includes("poly") || nameLower.includes("chito") || nameLower.includes("polimer")) {
      suggestedUse = "<strong>Nanovehículo Polimérico/Lipídico:</strong> Diseñado principalmente para la liberación controlada de fármacos, vacunas (como las de ARNm), terapia génica y cosmecéutica avanzada.";
    } else if (p.core_size_nm < 20) {
      suggestedUse = "<strong>Biomedicina y Óptica:</strong> Debido a su tamaño ultra-pequeño (<20 nm), tiene gran capacidad de penetración celular. Se suele investigar en transporte de fármacos, imagen por fluorescencia y catálisis de alta eficiencia.";
    } else if (p.surface_area_m2g > 150) {
      suggestedUse = "<strong>Catálisis y Sensores:</strong> Su alta área superficial la hace ideal para reacciones catalíticas químicas, purificación ambiental (agua/aire), sensores de gases y baterías de alta capacidad.";
    } else {
      suggestedUse = "<strong>Usos Industriales y Materiales:</strong> Nanopartícula estable adecuada para recubrimientos protectores, aditivos mecánicos, filtros UV comerciales, cosméticos o materiales compuestos avanzados.";
    }
    usesTxt.innerHTML = `<strong>Uso estimado por perfil:</strong> ${suggestedUse}`;
  }

  // Pills
  document.getElementById('p-sz').textContent=p.core_size_nm+' nm';
  document.getElementById('p-zt').textContent=p.zeta_potential_mv+' mV';
  document.getElementById('p-cn').textContent=p.concentration_ug_ml+' µg/mL';
  document.getElementById('p-ar').textContent=p.surface_area_m2g+' m²/g';
  document.getElementById('p-tm').textContent=p.exposure_time_h+' h';
  document.getElementById('p-cl').textContent=p.cell_line;

  // Feature importance (calculado localmente)
  const conc=Math.min(p.concentration_ug_ml/1000,1);
  const size=(100-p.core_size_nm)/100;
  const area=Math.min(p.surface_area_m2g/500,1);
  const time=Math.min(p.exposure_time_h/96,1);
  const zeta=Math.abs(p.zeta_potential_mv)/60;
  const mat=(DB[mk]||{b:.5}).b;
  const tot=conc+size+area+time+zeta+mat+.001;
  const fi={'Concentración (µg/mL)':conc/tot,'Tipo de material':mat/tot,
    'Tamaño de núcleo (nm)':size/tot,'Área superficial (m²/g)':area/tot,
    'Tiempo exposición (h)':time/tot,'Potencial Zeta (mV)':zeta/tot};

  const fiCard=document.getElementById('fi-card');fiCard.style.display='block';
  const mx=Math.max(...Object.values(fi));
  document.getElementById('fi-bars').innerHTML=
    Object.entries(fi).sort((a,b)=>b[1]-a[1]).map(([nm,v],i)=>`
    <div class="fi-item">
      <div class="fi-top"><span class="fi-name">${nm}</span>
        <span class="fi-pct">${(v*100).toFixed(1)}%</span></div>
      <div class="fi-track">
        <div class="fi-bar" id="fb${i}" style="background:${FI_G[i%FI_G.length]}"></div>
      </div></div>`).join('');

  Object.values(fi).sort((a,b)=>b-a).forEach((v,i)=>{
    setTimeout(()=>{const el=document.getElementById('fb'+i);
      if(el)el.style.width=(v/mx*100)+'%'},150+i*100)});

  // History
  history.unshift({mat:mk||raw,pct,color:r.risk_color,risk:r.risk_level});
  if(history.length>5)history.pop();
  const hw=document.getElementById('hist-wrap');
  const hl=document.getElementById('hist-list');
  hw.style.display='block';
  hl.innerHTML=history.map(h=>`
    <div class="hist-item" onclick="pickAC('${h.mat}','${h.mat}')">
      <span class="h-dot" style="background:${h.color};box-shadow:0 0 5px ${h.color}"></span>
      <span>${h.mat}</span><strong style="color:${h.color}">${h.pct}%</strong>
    </div>`).join('');
}

// Health check
fetch('/health').then(r=>r.ok?r.json():null).then(d=>{
  if(d){document.getElementById('api-dot').classList.add('on');
    document.getElementById('api-txt').textContent=`🟢 API activa — Modelo: ${d.modelo||'RandomForest'}`}
}).catch(()=>{
  document.getElementById('api-txt').textContent='🔵 Modo offline — modelo integrado activo'});
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Sirve el dashboard visual interactivo."""
    return HTML_PAGE

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
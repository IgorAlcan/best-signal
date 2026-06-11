/* ==========================================================================
   BestSignal — lógica da interface web.
   Consome a API FastAPI por HTTP (fetch) e renderiza tudo no cliente.
   Sem framework e sem build: JS puro.
   ========================================================================== */

"use strict";

const SPORT_LABELS = { todos: "Todos", tennis: "Tênis", football: "Futebol", basketball: "Basquete" };

const state = { all: [], sport: "todos", minEv: 3.0 };

// ---- Helpers ---------------------------------------------------------------
const $ = (sel) => document.querySelector(sel);
const pct = (x) => `${Number(x).toFixed(2)}%`;
const money = (x) => `R$ ${Number(x).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  return res.json();
}

// ---- Seleção de dados ------------------------------------------------------
function filteredEvents() {
  return state.sport === "todos" ? state.all : state.all.filter((e) => e.sport === state.sport);
}
function valueBets() {
  return filteredEvents()
    .filter((e) => e.ev_percent >= state.minEv)
    .sort((a, b) => b.ev_percent - a.ev_percent);
}

// ---- KPIs ------------------------------------------------------------------
function renderKPIs() {
  const events = filteredEvents();
  const vbs = valueBets();
  const best = events.length ? Math.max(...events.map((e) => e.ev_percent)) : 0;
  const rate = events.length ? (vbs.length / events.length) * 100 : 0;

  $("#kpi-events").textContent = events.length;
  $("#kpi-value").textContent = vbs.length;
  $("#kpi-rate").textContent = `${rate.toFixed(0)}% do recorte`;
  $("#kpi-best").textContent = best > 0 ? `+${best.toFixed(2)}%` : "—";

  // Esporte líder entre as value bets
  if (!vbs.length) {
    $("#kpi-leader").textContent = "—";
  } else {
    const counts = {};
    vbs.forEach((b) => (counts[b.sport] = (counts[b.sport] || 0) + 1));
    const [sport, n] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
    $("#kpi-leader").textContent = `${SPORT_LABELS[sport] || sport} (${n})`;
  }
}

// ---- Scatter SVG -----------------------------------------------------------
function renderScatter() {
  const host = $("#scatter");
  const events = filteredEvents();
  if (!events.length) {
    host.innerHTML = '<div class="empty">Sem eventos para os filtros atuais.</div>';
    return;
  }

  const W = 560, H = 320, padL = 46, padR = 16, padT = 14, padB = 36;
  const xs = events.map((e) => e.bookmaker_odds);
  const ys = events.map((e) => e.ev_percent);
  const xMin = Math.min(...xs) - 0.2, xMax = Math.max(...xs) + 0.2;
  const yMin = Math.min(0, ...ys) - 2, yMax = Math.max(state.minEv, ...ys) + 2;

  const sx = (v) => padL + ((v - xMin) / (xMax - xMin)) * (W - padL - padR);
  const sy = (v) => H - padB - ((v - yMin) / (yMax - yMin)) * (H - padT - padB);

  const parts = [];
  // Gridlines + ticks Y
  const yTicks = niceTicks(yMin, yMax, 5);
  yTicks.forEach((t) => {
    const y = sy(t);
    parts.push(`<line class="grid" x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" />`);
    parts.push(`<text class="tick" x="${padL - 6}" y="${y + 3}" text-anchor="end">${t}</text>`);
  });
  // Ticks X
  niceTicks(xMin, xMax, 5).forEach((t) => {
    const x = sx(t);
    parts.push(`<text class="tick" x="${x}" y="${H - padB + 16}" text-anchor="middle">${t.toFixed(1)}</text>`);
  });
  // Eixos
  parts.push(`<line class="axis" x1="${padL}" y1="${padT}" x2="${padL}" y2="${H - padB}" />`);
  parts.push(`<line class="axis" x1="${padL}" y1="${H - padB}" x2="${W - padR}" y2="${H - padB}" />`);
  // Linha zero
  if (yMin < 0) parts.push(`<line class="zero" x1="${padL}" y1="${sy(0)}" x2="${W - padR}" y2="${sy(0)}" />`);
  // Linha de corte (EV mínimo)
  if (state.minEv > 0 && state.minEv >= yMin && state.minEv <= yMax) {
    const yc = sy(state.minEv);
    parts.push(`<line class="cut" x1="${padL}" y1="${yc}" x2="${W - padR}" y2="${yc}" />`);
    parts.push(`<text class="cut-label" x="${W - padR}" y="${yc - 5}" text-anchor="end">corte ${state.minEv.toFixed(1)}%</text>`);
  }
  // Rótulos de eixo
  parts.push(`<text class="axis-label" x="${(W) / 2}" y="${H - 4}" text-anchor="middle">Odd da casa</text>`);
  parts.push(`<text class="axis-label" transform="translate(13 ${(H - padB + padT) / 2}) rotate(-90)" text-anchor="middle">EV (%)</text>`);

  // Pontos
  events.forEach((e, i) => {
    const isVal = e.ev_percent >= state.minEv;
    const r = Math.max(4, Math.min(12, 4 + Math.abs(e.ev_percent) * 0.45));
    parts.push(
      `<circle class="dot" cx="${sx(e.bookmaker_odds).toFixed(1)}" cy="${sy(e.ev_percent).toFixed(1)}" r="${r.toFixed(1)}" ` +
      `fill="${isVal ? "#2dd4a7" : "#5d6b80"}" data-i="${i}" />`
    );
  });

  host.innerHTML = `<svg class="scatter" viewBox="0 0 ${W} ${H}" role="img" aria-label="Dispersão de EV por odd">${parts.join("")}</svg>`;
  attachTooltip(events);
}

function niceTicks(min, max, count) {
  const span = max - min || 1;
  const step = Math.pow(10, Math.floor(Math.log10(span / count)));
  const err = (span / count) / step;
  const mult = err >= 7.5 ? 10 : err >= 3 ? 5 : err >= 1.5 ? 2 : 1;
  const s = step * mult;
  const ticks = [];
  for (let t = Math.ceil(min / s) * s; t <= max; t += s) ticks.push(Math.round(t * 100) / 100);
  return ticks;
}

function attachTooltip(events) {
  const svg = $("#scatter svg");
  const tip = $("#tooltip");
  const wrap = svg.closest(".scatter-wrap");
  if (!svg) return;

  svg.addEventListener("mousemove", (ev) => {
    const dot = ev.target.closest(".dot");
    if (!dot) { tip.style.opacity = "0"; return; }
    const e = events[Number(dot.dataset.i)];
    tip.innerHTML =
      `<div class="tt-title">${esc(e.event)}</div>` +
      `<div class="tt-row"><span>Seleção</span><span>${esc(e.selection)}</span></div>` +
      `<div class="tt-row"><span>Casa / sharp</span><span>${e.bookmaker_odds.toFixed(2)} / ${e.sharp_odds.toFixed(2)}</span></div>` +
      `<div class="tt-row"><span>EV</span><span class="tt-ev">${e.ev_percent >= 0 ? "+" : ""}${e.ev_percent.toFixed(2)}%</span></div>`;
    const rect = wrap.getBoundingClientRect();
    let x = ev.clientX - rect.left + 14;
    const y = ev.clientY - rect.top + 14;
    if (x + 190 > rect.width) x = ev.clientX - rect.left - 190;
    tip.style.left = `${x}px`;
    tip.style.top = `${y}px`;
    tip.style.opacity = "1";
  });
  svg.addEventListener("mouseleave", () => { tip.style.opacity = "0"; });
}

// ---- Maior oportunidade ----------------------------------------------------
function renderTopBet() {
  const el = $("#top-bet");
  const top = valueBets()[0];
  if (!top) {
    el.innerHTML = '<h3>Sem sinal EV+</h3><p class="muted">Os filtros atuais não encontram eventos acima do corte.</p>';
    return;
  }
  el.innerHTML =
    `<h3>Top sinal do recorte</h3>` +
    `<p><strong>${esc(top.selection)}</strong> · <span class="muted">${esc(top.event)}</span></p>` +
    `<div class="chips">` +
    `<span class="chip green">EV +${top.ev_percent.toFixed(2)}%</span>` +
    `<span class="chip">casa ${top.bookmaker_odds.toFixed(2)}</span>` +
    `<span class="chip">sharp ${top.sharp_odds.toFixed(2)}</span>` +
    `</div>`;
}

// ---- Tabela ----------------------------------------------------------------
function renderTable() {
  const body = $("#vb-body");
  const vbs = valueBets();
  $("#vb-count").textContent = `(${vbs.length})`;
  if (!vbs.length) {
    body.innerHTML = '<tr><td colspan="7" class="empty">Nenhuma oportunidade com os filtros atuais — baixe o EV mínimo.</td></tr>';
    return;
  }
  body.innerHTML = vbs
    .map((b) => {
      const w = Math.max(2, Math.min(100, (b.ev_percent / 15) * 100));
      return (
        `<tr>` +
        `<td><span class="sport-tag">${esc(SPORT_LABELS[b.sport] || b.sport)}</span></td>` +
        `<td>${esc(b.event)}</td>` +
        `<td>${esc(b.selection)}</td>` +
        `<td class="num">${b.bookmaker_odds.toFixed(2)}</td>` +
        `<td class="num">${b.sharp_odds.toFixed(2)}</td>` +
        `<td class="num">${b.implied_probability.toFixed(4)}</td>` +
        `<td><div class="ev-cell"><div class="ev-bar"><i style="width:${w}%"></i></div>` +
        `<span class="ev-num pos">+${b.ev_percent.toFixed(2)}%</span></div></td>` +
        `</tr>`
      );
    })
    .join("");
}

// ---- Alertas (GET /alerts) -------------------------------------------------
async function loadAlerts() {
  const box = $("#alert-box");
  try {
    const alerts = await fetchJSON(`/alerts?min_ev=${encodeURIComponent(state.minEv)}`);
    box.textContent = alerts.length ? alerts[0].message : "Nenhum alerta no corte atual.";
  } catch (e) {
    box.textContent = "Não foi possível carregar os alertas.";
  }
}

// ---- Gestão de banca (POST /suggest-stake) --------------------------------
let stakeTimer = null;
function updateStake() {
  clearTimeout(stakeTimer);
  stakeTimer = setTimeout(async () => {
    const bankroll = Number($("#bankroll").value);
    const risk = Number($("#risk").value);
    const out = $("#stake");
    try {
      const r = await fetchJSON("/suggest-stake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bankroll, risk_percent: risk }),
      });
      out.innerHTML = `${money(r.stake)}<small>STAKE SUGERIDA</small>`;
    } catch (e) {
      out.innerHTML = `R$ —<small>VALOR INVÁLIDO</small>`;
    }
  }, 250);
}

// ---- Render geral ----------------------------------------------------------
function render() {
  renderKPIs();
  renderScatter();
  renderTopBet();
  renderTable();
}

// ---- Init ------------------------------------------------------------------
async function init() {
  try {
    state.all = await fetchJSON("/odds");
  } catch (e) {
    $("#scatter").innerHTML = '<div class="empty">Erro ao carregar a API. A API está rodando?</div>';
    return;
  }
  $("#pill-events").textContent = state.all.length;
  render();
  loadAlerts();
  updateStake();

  // Filtro de esporte (segmented control)
  $("#sport-seg").addEventListener("click", (ev) => {
    const btn = ev.target.closest("button");
    if (!btn) return;
    state.sport = btn.dataset.sport;
    document.querySelectorAll("#sport-seg button").forEach((b) => b.classList.toggle("active", b === btn));
    render();
  });

  // Slider de EV mínimo
  $("#minev").addEventListener("input", (ev) => {
    state.minEv = Number(ev.target.value);
    $("#minev-out").textContent = `${state.minEv.toFixed(1)}%`;
    render();
    loadAlerts();
  });

  // Inputs de banca
  $("#bankroll").addEventListener("input", updateStake);
  $("#risk").addEventListener("input", updateStake);
}

document.addEventListener("DOMContentLoaded", init);

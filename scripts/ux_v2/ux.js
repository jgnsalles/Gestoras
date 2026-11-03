(() => {
  // ---------- base ----------
  const MES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  const L = d3.formatLocale({ decimal: ',', thousands: '.', grouping: [3], currency: ['R$ ', ''] });
  const fPct = L.format('+.1%'), fPct0 = L.format('.0%'), fPct1 = L.format('.1%'), fPP = L.format('+.1f'), fNum = L.format(',.0f');
  const ymLabel = (s) => (s ? MES[+s.slice(5, 7) - 1] + '/' + s.slice(2, 4) : '');
  const endDate = (ym) => new Date(Date.UTC(+ym.slice(0, 4), +ym.slice(5, 7), 1));
  const num = (x) => (x === '' || x == null ? NaN : +x);
  const D = (id) => dash.data(id).data || [];
  const ok = (ids) => ids.every((i) => dash.data(i).status === 'ok');
  const P = () => dash.params();
  const win = () => { const p = P(); let a = p.inicio || '2013-12', b = p.fim || '2018-12'; if (b < a) [a, b] = [b, a]; return [a, b]; };
  const comp = (ms, f) => { let g = 1, n = 0; ms.forEach((m) => { const x = f(m); if (Number.isFinite(x)) { g *= 1 + x; n++; } }); return n ? g - 1 : NaN; };
  const prevYm = (ym) => { let y = +ym.slice(0, 4), m = +ym.slice(5, 7) - 1; if (!m) { m = 12; y--; } return y + '-' + String(m).padStart(2, '0'); };
  const sc = (v) => (v > 0 ? 'rx-pos' : v < 0 ? 'rx-neg' : '');
  const C0 = dash.colors[0];

  const EVENTS = [['2014-03-17', 'Lava Jato'], ['2014-10-26', 'Reeleição de Dilma'], ['2015-07-29', 'Selic 14,25%'], ['2015-09-09', 'S&P tira o grau'], ['2016-05-12', 'Afastamento'], ['2016-08-31', 'Impeachment'], ['2016-12-15', 'PEC do teto'], ['2017-05-17', 'Joesley Day'], ['2018-05-21', 'Greve dos caminhoneiros'], ['2018-10-28', 'Eleição de Bolsonaro']]
    .map(([d, l]) => ({ d: new Date(d + 'T12:00:00Z'), ds: d, l }));
  const PHASES = [['Dilma 2', '2013-12', '2016-02', 'Dilma 2'], ['Impeachment', '2016-02', '2016-08', 'Impeach.'], ['Temer', '2016-08', '2018-04', 'Temer'], ['Greve e eleição', '2018-04', '2018-12', '2018']];
  const SHORT = { 'Financeiro': 'Financeiro', 'Consumo Cíclico': 'Cons. cíclico', 'Utilidade Pública': 'Util. pública', 'Bens Industriais': 'Bens indust.', 'Materiais Básicos': 'Materiais', 'Consumo não Cíclico': 'Cons. não cícl.', 'Saúde': 'Saúde', 'Petróleo, Gás e Biocombustíveis': 'Petróleo e gás', 'Tecnologia da Informação': 'Tecnologia', 'Comunicações': 'Comunicações' };
  const phasesIn = (ini, fim) => PHASES.map(([nm, a, z, sh]) => { const a2 = a < ini ? ini : a, z2 = z > fim ? fim : z; return a2 < z2 ? { nm, sh, a: a2, z: z2 } : null; }).filter(Boolean);

  const IDS = ['fundos', 'serie_mensal', 'posicoes_1', 'posicoes_2', 'precos', 'acoes', 'ibov'];
  let B = null;
  const base = () => {
    if (!ok(IDS)) return null; if (B) return B;
    const ibp = new Map(D('ibov').map((r) => [r.ym, num(r.pontos)]));
    const ser = D('serie_mensal').map((r) => ({ id: String(r.id), ym: r.ym, PL: num(r.PL_mi), rf: num(r.ret_fundo), rc: num(r.ret_acoes_contrib), ri: num(r.ret_ibov), el: num(r.exp_long), fl: num(r.fluxo_mi) }));
    const ibS = new Map(); ser.forEach((r) => { if (Number.isFinite(r.ri) && !ibS.has(r.ym)) ibS.set(r.ym, r.ri); });
    const ibr = (ym) => { if (ibS.has(ym)) return ibS.get(ym); const a = ibp.get(ym), b = ibp.get(prevYm(ym)); return a && b ? a / b - 1 : NaN; };
    const byM = d3.group(ser, (r) => r.ym);
    const months = [...byM.keys()].sort();
    const ret = new Map(); D('precos').forEach((r) => { const x = num(r.ret_total); if (!Number.isFinite(x)) return; let m = ret.get(r.tk); if (!m) { m = new Map(); ret.set(r.tk, m); } m.set(r.ym, x); });
    const nome = new Map(D('acoes').map((r) => [r.tk, r.empresa])), setor = new Map(D('acoes').map((r) => [r.tk, r.setor]));
    const cnt = new Map(), hold = new Map(), wsum = new Map(), rootMax = new Map();
    for (const r of [...D('posicoes_1'), ...D('posicoes_2')]) {
      const w = num(r.peso); if (!Number.isFinite(w)) continue; const rt = r.tk.slice(0, 4);
      cnt.set(r.tk, (cnt.get(r.tk) || 0) + 1); rootMax.set(rt, Math.max(rootMax.get(rt) || 0, w));
      let m = wsum.get(rt); if (!m) { m = new Map(); wsum.set(rt, m); } m.set(r.ym, (m.get(r.ym) || 0) + w);
      if (w >= 0.01) { let h = hold.get(rt); if (!h) { h = new Map(); hold.set(rt, h); } let s = h.get(r.ym); if (!s) { s = new Set(); h.set(r.ym, s); } s.add(String(r.id)); }
    }
    const rep = new Map(); [...cnt].sort((a, b) => b[1] - a[1]).forEach(([tk]) => { const rt = tk.slice(0, 4); if (!rep.has(rt) && ret.has(tk)) rep.set(rt, tk); });
    const nAct = new Map(months.map((m) => [m, (byM.get(m) || []).filter((r) => Number.isFinite(r.PL)).length]));
    const gross = new Map(); const gEl = document.getElementById('csv-captacao_bruta');
    if (gEl) d3.csvParse(gEl.textContent.trim()).forEach((r) => { const c = num(r.capt_mi), z = num(r.resg_mi); if (Number.isFinite(c) && Number.isFinite(z)) gross.set(String(r.id) + '|' + r.ym, { c, z }); });
    B = { gross, ibr, byM, months, ret, nome, setor, hold, wsum, rep, rootMax, nAct };
    return B;
  };
  const tkName = (b, tk) => tk + (b.nome.get(tk) ? ' · ' + b.nome.get(tk) : '');

  // ---------- helpers ----------
  const tipOf = (box) => { let t = box.querySelector(':scope > .rx-tip'); if (!t) { t = document.createElement('div'); t.className = 'rx-tip'; t.hidden = true; box.append(t); } return t; };
  const showTip = (box, t, x, y, head, lines) => {
    t.replaceChildren(); const d = document.createElement('div'); d.className = 'd'; d.textContent = head; t.append(d);
    lines.forEach(([c, n, v]) => { const r = document.createElement('div'); r.className = 'r'; if (c) { const s = document.createElement('span'); s.className = 's'; s.style.background = c; r.append(s); } const tx = document.createElement('span'); tx.textContent = n + (v != null ? ': ' + v : ''); r.append(tx); t.append(r); });
    t.hidden = false; const bw = box.clientWidth, tw = t.offsetWidth, th = t.offsetHeight;
    t.style.left = Math.max(0, Math.min(bw - tw, x + 12)) + 'px'; t.style.top = Math.max(0, y - th - 10) + 'px';
  };
  const axisClean = (g) => { g.attr('font-size', null).attr('font-family', null); g.selectAll('text').attr('fill', 'var(--color-fg-muted)').style('font-size', '11px'); g.selectAll('.domain').attr('stroke', 'var(--cds-chart-axis)'); g.selectAll('.tick line').attr('stroke', 'var(--cds-chart-grid)'); };
  const svgFor = (el, h) => { const w = Math.max(300, el.clientWidth); el.querySelectorAll(':scope > svg').forEach((s) => s.remove()); const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${w} ${h}`).attr('height', h); return { svg, w }; };
  const setH = (svg, w, h) => svg.attr('viewBox', `0 0 ${w} ${h}`).attr('height', h);
  const div = (v, cap) => (!Number.isFinite(v) ? 'none' : `color-mix(in srgb, var(${v >= 0 ? '--color-ok' : '--color-bad'}) ${Math.round(10 + 72 * Math.min(1, Math.abs(v) / cap))}%, var(--color-panel))`);
  const label = (svg, x, y, txt, anchor) => svg.append('text').attr('x', x).attr('y', y).attr('text-anchor', anchor || 'start').attr('fill', 'var(--color-fg-muted)').style('font-size', '11px').text(txt);
  const measure = (svg, txt, size) => { const t = svg.append('text').style('font-size', (size || 11) + 'px').text(txt); const v = t.node().getComputedTextLength() || txt.length * 6; t.remove(); return v; };
  const yearAxis = (svg, x, y, w) => svg.append('g').attr('transform', `translate(0,${y})`).call(d3.axisBottom(x).ticks(d3.utcYear.every(w < 420 ? 2 : 1)).tickFormat((d) => String(d.getUTCFullYear())).tickSizeOuter(0)).call(axisClean);
  const drawPhases = (svg, x, y0, y1, ini, fim, labelY) => {
    phasesIn(ini, fim).forEach((p, i) => {
      const x0 = x(endDate(p.a)), x1 = x(endDate(p.z));
      if (i % 2) svg.append('rect').attr('x', x0).attr('width', Math.max(0, x1 - x0)).attr('y', y0).attr('height', Math.max(0, y1 - y0)).style('fill', 'var(--cds-chart-grid)').style('opacity', 0.7);
      if (labelY != null) { const full = measure(svg, p.nm, 11) + 6 < x1 - x0; const t = full ? p.nm : p.sh; if (measure(svg, t, 11) + 4 < x1 - x0) svg.append('text').attr('x', (x0 + x1) / 2).attr('y', labelY).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg)').style('font-size', '11px').style('font-weight', 600).text(t); }
    });
  };
  const eventsIn = (d0, d1) => EVENTS.filter((e) => e.d >= d0 && e.d <= d1);
  const layoutEvents = (svg, x, d0, d1, xmax, numbered) => {
    const evs = eventsIn(d0, d1).map((e, i) => ({ ...e, l0: String(i + 1) })); const ends = [];
    evs.forEach((e) => {
      if (numbered) { e.full = e.l; }
      e.txt = numbered ? e.l0 : e.l; e.tw = measure(svg, e.txt, 11); e.px = x(e.d); const right = e.px + 4 + e.tw <= xmax;
      e.anchor = right ? 'start' : 'end'; e.x0 = right ? e.px : e.px - e.tw - 4; e.x1 = right ? e.px + e.tw + 4 : e.px;
      let r = ends.findIndex((end) => e.x0 > end + 6); if (r < 0) { if (ends.length < 4) { r = ends.length; ends.push(-1e9); } else r = ends.indexOf(Math.min(...ends)); }
      ends[r] = e.x1; e.row = r;
    });
    return { evs, nRows: Math.max(1, ends.length) };
  };
  const eventLines = (svg, x, d0, d1, y0, y1) => eventsIn(d0, d1).forEach((e) => svg.append('line').attr('x1', x(e.d)).attr('x2', x(e.d)).attr('y1', y0).attr('y2', y1).attr('stroke', 'var(--cds-chart-reference)').attr('stroke-dasharray', '2 3').attr('opacity', 0.55));
  const go = (id) => requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));

  // ---------- ciclo model ----------
  let CM = null;
  const cyc = () => {
    const b = base(); if (!b) return null; const [ini, fim] = win(); const k = ini + fim; if (CM && CM.k === k) return CM.m;
    const ms = b.months.filter((m) => m >= ini && m <= fim); const rm = ms.slice(1);
    let gi = 1, gf = 1;
    const rows = ms.map((ym, i) => {
      const rs = b.byM.get(ym) || [];
      if (i > 0) { const ri = b.ibr(ym); if (Number.isFinite(ri)) gi *= 1 + ri; const fr = rs.map((r) => r.rf).filter(Number.isFinite); if (fr.length) gf *= 1 + d3.mean(fr); }
      const el = rs.map((r) => r.el).filter(Number.isFinite).sort(d3.ascending); const fl = rs.map((r) => r.fl).filter(Number.isFinite);
      const gs = rs.filter((r) => Number.isFinite(r.PL)).map((r) => b.gross.get(r.id + '|' + ym)); const gk = gs.filter(Boolean);
      return { ym, d: endDate(ym), ib: gi - 1, fu: gf - 1, el: d3.mean(el), e25: d3.quantile(el, 0.25), e75: d3.quantile(el, 0.75), fl: i > 0 && fl.length ? d3.sum(fl) : NaN, nf: rs.filter((r) => Number.isFinite(r.rf)).length,
        cap: i > 0 && gk.length ? d3.sum(gk, (g) => g.c) : NaN, res: i > 0 && gk.length ? d3.sum(gk, (g) => g.z) : NaN, gMiss: gs.length - gk.length };
    });
    const GK = { T: [(m) => m.slice(0, 4) + ' T' + Math.ceil(+m.slice(5, 7) / 3), 3], S: [(m) => m.slice(0, 4) + ' S' + Math.ceil(+m.slice(5, 7) / 6), 6], A: [(m) => m.slice(0, 4), 12] };
    const uni = [...b.rep].filter(([rt]) => (b.rootMax.get(rt) || 0) >= 0.005).map(([rt, tk]) => ({ rt, tk, s: b.setor.get(tk) || '' }));
    const full = (tk, list) => { const m = b.ret.get(tk); return list.every((x) => Number.isFinite(m.get(x))) ? comp(list, (x) => m.get(x)) : NaN; };
    const secCache = {};
    const sectorsFor = (g) => { if (secCache[g]) return secCache[g]; const [kf, len] = GK[g];
      const per = d3.groups(rm, kf).map(([q, qm]) => ({ q, ms: qm, d0: endDate(prevYm(qm[0])), d1: endDate(qm[qm.length - 1]), ib: comp(qm, b.ibr), partial: qm.length < len }));
      return (secCache[g] = d3.groups(uni.filter((u) => SHORT[u.s]), (u) => u.s).map(([s, us]) => ({
        s, short: SHORT[s], n: us.length,
        cells: per.map((Q) => { const rs = us.map((u) => full(u.tk, Q.ms)).filter(Number.isFinite); const med = rs.length ? d3.median(rs) : NaN; return { Q, n: rs.length, med, ex: med - Q.ib }; }),
      })).sort((a, z) => z.n - a.n)); };
    const phases = phasesIn(ini, fim).map((p) => {
      const pm = rm.filter((m) => m > p.a && m <= p.z);
      const st = uni.map((u) => ({ ...u, r: full(u.tk, pm) })).filter((u) => Number.isFinite(u.r)).sort((x, y) => y.r - x.r);
      const rs = rows.filter((r) => r.ym > p.a && r.ym <= p.z); let gf = 1; rs.forEach((r) => { const fr = (b.byM.get(r.ym) || []).map((x) => x.rf).filter(Number.isFinite); if (fr.length) gf *= 1 + d3.mean(fr); });
      const ib = comp(pm, b.ibr);
      const sectors = d3.groups(uni.filter((u) => SHORT[u.s]), (u) => u.s).map(([sn, us]) => { const v = us.map((u) => full(u.tk, pm)).filter(Number.isFinite); return { s: sn, short: SHORT[sn], n: v.length, ex: v.length ? d3.median(v) - ib : NaN }; }).filter((x) => Number.isFinite(x.ex)).sort((x, y) => y.ex - x.ex);
      return { ...p, pm, ib, fu: gf - 1, cap: d3.sum(rs, (r) => r.cap || 0), res: d3.sum(rs, (r) => r.res || 0), sectors, best: st.slice(0, 20), worst: st.slice(-20).reverse(), n: st.length };
    });
    const m = { ms, rm, rows, sectorsFor, phases, ini, fim };
    CM = { k, m }; return m;
  };

  // ---------- ciclo: main chart (retorno + captação) ----------
  const mkLegend = (el, items) => { el.replaceChildren(); items.forEach(([bg, t]) => { const s = document.createElement('span'); const i = document.createElement('i'); i.style.background = bg; s.append(i, document.createTextNode(t)); el.append(s); }); };
  dash.draw('cy-legend', (el) => mkLegend(el, [[C0, 'Fundos (média)'], ['var(--cds-chart-muted)', 'Ibovespa'], ['var(--color-ok)', 'Captação bruta'], ['var(--color-bad)', 'Resgate bruto']]));
  const eventKey = (el, evs, narrow) => {
    el.querySelectorAll(':scope > .cy-key').forEach((k) => k.remove());
    if (!narrow || !evs.length) return; const key = document.createElement('div'); key.className = 'rx-legend cy-key';
    evs.forEach((e) => { const sp = document.createElement('span'); const b = document.createElement('b'); b.textContent = e.l0; sp.append(b, document.createTextNode(' ' + e.l + ' (' + e.ds.slice(8) + '/' + e.ds.slice(5, 7) + '/' + e.ds.slice(2, 4) + ')')); key.append(sp); }); el.append(key);
  };
  dash.draw('cy-main', (el) => {
    const m = cyc(); if (!m || m.rows.length < 2) return; const t = tipOf(el);
    const { svg, w } = svgFor(el, 10); const narrow = w < 560;
    const ml = narrow ? 44 : 52, mr = narrow ? 40 : 52;
    const d0 = m.rows[0].d, d1 = m.rows[m.rows.length - 1].d;
    const x = d3.scaleUtc([d0, d1], [ml, w - mr]);
    const { evs, nRows } = layoutEvents(svg, x, d0, d1, w - 2, narrow); eventKey(el, evs, narrow);
    const evTop = 22, evH = nRows * 13 + 4, pTop = evTop + evH + 14, pH = narrow ? 170 : 230;
    const fTop = pTop + pH + 34, fH = narrow ? 70 : 90, H = fTop + fH + 24; setH(svg, w, H);
    drawPhases(svg, x, evTop - 2, H - 24, m.ini, m.fim, 12);
    evs.forEach((e) => {
      const ly = evTop + 10 + e.row * 13;
      svg.append('line').attr('x1', e.px).attr('x2', e.px).attr('y1', ly + 3).attr('y2', H - 24).attr('stroke', 'var(--cds-chart-reference)').attr('stroke-dasharray', '2 3').attr('opacity', 0.5);
      svg.append('text').attr('x', e.anchor === 'start' ? e.px + 3 : e.px - 3).attr('y', ly).attr('text-anchor', e.anchor).attr('fill', 'var(--color-fg-muted)').style('font-size', '11px').style('font-weight', e.txt === e.l0 ? 600 : 400).text(e.txt);
    });
    const ext = d3.extent(m.rows.flatMap((r) => [r.ib, r.fu]));
    const yP = d3.scaleLinear([Math.min(0, ext[0]), Math.max(0, ext[1])], [pTop + pH, pTop]).nice();
    svg.append('g').attr('transform', `translate(${ml},0)`).call(d3.axisLeft(yP).ticks(4).tickFormat(L.format('.0%')).tickSize(-(w - ml - mr))).call(axisClean).call((g) => g.select('.domain').remove());
    svg.append('line').attr('x1', ml).attr('x2', w - mr).attr('y1', yP(0)).attr('y2', yP(0)).attr('stroke', 'var(--cds-chart-reference)');
    const ln = (k) => d3.line().x((r) => x(r.d)).y((r) => yP(r[k]));
    svg.append('path').datum(m.rows).attr('d', ln('ib')).attr('fill', 'none').attr('stroke', 'var(--cds-chart-muted)').attr('stroke-width', 2);
    svg.append('path').datum(m.rows).attr('d', ln('fu')).attr('fill', 'none').attr('stroke', C0).attr('stroke-width', 2.5);
    const last = m.rows[m.rows.length - 1]; let yf = yP(last.fu), yi = yP(last.ib); if (Math.abs(yf - yi) < 13) { const mid = (yf + yi) / 2; [yf, yi] = yf <= yi ? [mid - 7, mid + 7] : [mid + 7, mid - 7]; }
    svg.append('text').attr('x', w - mr + 5).attr('y', yf).attr('dy', '0.35em').attr('fill', C0).style('font-size', '12px').style('font-weight', 600).text(fPct0(last.fu));
    svg.append('text').attr('x', w - mr + 5).attr('y', yi).attr('dy', '0.35em').attr('fill', 'var(--color-fg-muted)').style('font-size', '12px').text(fPct0(last.ib));
    label(svg, ml, fTop - 8, 'Captação e resgate brutos (R$ mi)');
    const gr = m.rows.filter((r) => Number.isFinite(r.cap));
    const fmax = Math.max(1, d3.max(gr, (r) => Math.max(r.cap, r.res)) || 1);
    const yF = d3.scaleLinear([-fmax, fmax], [fTop + fH, fTop]).nice();
    svg.append('g').attr('transform', `translate(${ml},0)`).call(d3.axisLeft(yF).ticks(2).tickFormat((v) => L.format(',.0f')(Math.abs(v))).tickSize(-(w - ml - mr))).call(axisClean).call((g) => g.select('.domain').remove());
    const step = (w - ml - mr) / Math.max(1, m.rows.length - 1); const bx = (r) => x(r.d) - step * 0.85, bw = Math.max(1, step * 0.7);
    svg.append('g').selectAll('rect').data(gr).join('rect').attr('x', bx).attr('width', bw).attr('y', (r) => yF(r.cap)).attr('height', (r) => Math.max(0, yF(0) - yF(r.cap))).style('fill', 'var(--color-ok)').style('opacity', 0.75);
    svg.append('g').selectAll('rect').data(gr).join('rect').attr('x', bx).attr('width', bw).attr('y', yF(0)).attr('height', (r) => Math.max(0, yF(-r.res) - yF(0))).style('fill', 'var(--color-bad)').style('opacity', 0.75);
    yearAxis(svg, x, H - 24, w);
    const rule = svg.append('line').attr('y1', pTop).attr('y2', H - 24).attr('stroke', 'var(--color-fg-muted)').style('display', 'none');
    const bis = d3.bisector((r) => r.d).center;
    const move = (ev) => {
      const [px, py] = d3.pointer(ev, el); const sx = px * w / el.clientWidth; const r = m.rows[bis(m.rows, x.invert(sx))]; if (!r) return;
      rule.style('display', null).attr('x1', x(r.d)).attr('x2', x(r.d));
      const ev2 = EVENTS.filter((e) => Math.abs(x(e.d) - sx) < 6).map((e) => [null, e.l, e.ds.split('-').reverse().join('/')]);
      showTip(el, t, px, py, ymLabel(r.ym), [[C0, 'Fundos (média)', fPct(r.fu)], ['var(--cds-chart-muted)', 'Ibovespa', fPct(r.ib)], ['var(--color-ok)', 'Captação', Number.isFinite(r.cap) ? fNum(r.cap) + ' mi' : '—'], ['var(--color-bad)', 'Resgate', Number.isFinite(r.res) ? fNum(r.res) + ' mi' : '—'], ...(r.gMiss ? [[null, r.gMiss + ' fundo(s) sem dado no mês', null]] : []), ...ev2]);
    };
    svg.append('rect').attr('x', ml).attr('y', pTop - 10).attr('width', Math.max(0, w - ml - mr)).attr('height', H - 24 - pTop + 10).attr('fill', 'transparent')
      .on('pointermove', move).on('pointerdown', move).on('pointerleave', () => { rule.style('display', 'none'); t.hidden = true; });
  });

  // ---------- ciclo: resumo por fase ----------
  const curTk = (m, b) => { const p = P().cTk; return p && b.ret.has(p) ? p : null; };
  const pickTk = (tk) => { dash.setParams({ cTk: tk }); go('cy-acao-card'); };
  const fBi = (v) => (Number.isFinite(v) ? L.format(',.1f')(v / 1000) + ' bi' : '—');
  dash.draw('cy-strip', (el) => {
    el.replaceChildren(); const m = cyc(); if (!m) return; const b = base(); const sel = curTk(m, b);
    m.phases.forEach((p) => {
      const c = document.createElement('div'); c.className = 'rx-phase';
      const h = document.createElement('h3'); h.textContent = p.nm; const meta = document.createElement('div'); meta.className = 'meta'; meta.textContent = ymLabel(p.a) + ' → ' + ymLabel(p.z);
      const big = document.createElement('div'); big.className = 'rx-pbig';
      [['Ibovespa', p.ib], ['Fundos', p.fu]].forEach(([k, v]) => { const d = document.createElement('div'); const a = document.createElement('span'); a.textContent = k; const z = document.createElement('span'); z.className = sc(v); z.textContent = L.format('+.0%')(v); d.append(a, z); big.append(d); });
      const fl = document.createElement('div'); fl.className = 'meta'; fl.textContent = 'Aportes ' + fBi(p.cap) + ' · resgates ' + fBi(p.res);
      c.append(h, meta, big, fl);
      const sec = (title, list, fmt, click) => {
        const l = document.createElement('div'); l.className = 'lbl'; l.textContent = title; c.append(l);
        list.forEach((s) => { const bt = document.createElement(click ? 'button' : 'div'); if (click) { bt.type = 'button'; bt.onclick = () => pickTk(s.tk); bt.setAttribute('aria-pressed', String(s.tk === sel)); } bt.className = 'rx-stk' + (click ? '' : ' st');
          const a = document.createElement('span'); a.className = 'tk'; a.textContent = s.lab; const v = document.createElement('span'); v.className = sc(s.v); v.textContent = fmt(s.v); bt.append(a, v); c.append(bt); });
      };
      const ss = p.sectors.filter((s) => s.n >= 3);
      sec('Setores que mais ganharam do Ibov (p.p.)', ss.slice(0, 3).map((s) => ({ lab: s.short, v: s.ex })), (v) => fPP(v * 100), false);
      sec('Setores que mais perderam do Ibov (p.p.)', ss.slice(-3).reverse().map((s) => ({ lab: s.short, v: s.ex })), (v) => fPP(v * 100), false);
      sec('Ações que mais subiram', p.best.slice(0, 3).map((s) => ({ tk: s.tk, lab: s.tk, v: s.r })), fPct0, true);
      sec('Ações que mais caíram', p.worst.slice(0, 3).map((s) => ({ tk: s.tk, lab: s.tk, v: s.r })), fPct0, true);
      el.append(c);
    });
  });

  // ---------- ciclo: detalhes ----------
  const curG = (el) => { const g = P().cyG; return ['T', 'S', 'A'].includes(g) ? g : (Math.max(300, el?.clientWidth || 900) < 760 ? 'A' : 'T'); };
  dash.draw('cy-gran', (el) => {
    el.replaceChildren(); const g = curG(document.querySelector('[data-draw="cy-heat"]'));
    [['T', 'Trimestre'], ['S', 'Semestre'], ['A', 'Ano']].forEach(([k, t]) => { const bt = document.createElement('button'); bt.type = 'button'; bt.className = 'rx-chip'; bt.textContent = t; bt.setAttribute('aria-pressed', String(k === g)); bt.onclick = () => dash.setParams({ cyG: k }); el.append(bt); });
  });
  dash.draw('cy-heat', (el) => {
    const m0 = cyc(); if (!m0 || el.closest('details')?.open === false) return; const t = tipOf(el);
    const { svg, w } = svgFor(el, 10); const narrow = w < 560; const G = curG(el); const sectors = m0.sectorsFor(G);
    const ml = narrow ? 92 : 110, mr = 8, top = 22, hRow = narrow ? 20 : 22, H = top + sectors.length * hRow + 26; setH(svg, w, H);
    const x = d3.scaleUtc([m0.rows[0].d, m0.rows[m0.rows.length - 1].d], [ml, w - mr]);
    drawPhases(svg, x, top - 4, H - 24, m0.ini, m0.fim, 12);
    const pid = 'cyh' + Math.random().toString(36).slice(2, 8);
    svg.append('defs').append('pattern').attr('id', pid).attr('width', 4).attr('height', 4).attr('patternUnits', 'userSpaceOnUse').attr('patternTransform', 'rotate(45)').append('line').attr('x1', 0).attr('y1', 0).attr('x2', 0).attr('y2', 4).style('stroke', 'var(--color-fg)').style('stroke-width', 1).style('opacity', 0.45);
    const cap = G === 'T' ? 0.15 : G === 'S' ? 0.2 : 0.3;
    sectors.forEach((s, i) => {
      const y = top + i * hRow;
      svg.append('text').attr('x', ml - 6).attr('y', y + hRow / 2).attr('dy', '0.35em').attr('text-anchor', 'end').attr('fill', 'var(--color-fg)').style('font-size', '11px').text(s.short);
      s.cells.forEach((c) => {
        const cx = x(c.Q.d0) + 0.5, cw = Math.max(1, x(c.Q.d1) - x(c.Q.d0) - 1);
        const g = svg.append('g');
        g.append('rect').attr('x', cx).attr('y', y).attr('width', cw).attr('height', hRow - 2).attr('rx', 1.5).style('fill', Number.isFinite(c.ex) ? div(c.ex, cap) : 'none').style('stroke', Number.isFinite(c.ex) ? 'none' : 'var(--color-border-line)');
        if (c.n > 0 && c.n < 3) g.append('rect').attr('x', cx).attr('y', y).attr('width', cw).attr('height', hRow - 2).attr('fill', `url(#${pid})`);
        if (Number.isFinite(c.ex) && cw >= 20) g.append('text').attr('x', cx + cw / 2).attr('y', y + (hRow - 2) / 2).attr('dy', '0.35em').attr('text-anchor', 'middle').attr('fill', 'var(--color-fg)').style('font-size', cw < 30 ? '9.5px' : '11px').style('pointer-events', 'none').text(L.format('+.0f')(c.ex * 100).replace(/^[+−]0$/, '0'));
        const tp = (ev) => { const [px, py] = d3.pointer(ev, el); showTip(el, t, px, py, s.s + ' · ' + c.Q.q + (c.Q.partial ? ' (parcial)' : ''), [[null, 'Mediana do setor', Number.isFinite(c.med) ? fPct(c.med) : 'sem dado'], [null, 'Ibovespa', fPct(c.Q.ib)], [null, 'Ações na conta', String(c.n) + (c.n < 3 ? ' (amostra pequena)' : '')]]); };
        g.on('pointermove', tp).on('pointerdown', tp).on('pointerleave', () => { t.hidden = true; });
      });
    });
    yearAxis(svg, x, H - 24, w);
  });
  dash.draw('cy-exp', (el) => {
    const m = cyc(); if (!m || el.closest('details')?.open === false) return; const t = tipOf(el);
    const { svg, w } = svgFor(el, 10); const ml = 44, mr = 8, top = 22, eH = 120, H = top + eH + 26; setH(svg, w, H);
    const x = d3.scaleUtc([m.rows[0].d, m.rows[m.rows.length - 1].d], [ml, w - mr]);
    drawPhases(svg, x, top - 4, H - 24, m.ini, m.fim, 12);
    const yE = d3.scaleLinear([0, 1], [top + eH, top]);
    svg.append('g').attr('transform', `translate(${ml},0)`).call(d3.axisLeft(yE).ticks(4).tickFormat(L.format('.0%')).tickSize(-(w - ml - mr))).call(axisClean).call((g) => g.select('.domain').remove());
    const er = m.rows.filter((r) => Number.isFinite(r.el));
    svg.append('path').datum(er).attr('d', d3.area().x((r) => x(r.d)).y0((r) => yE(r.e25)).y1((r) => yE(r.e75))).style('fill', C0).style('opacity', 0.16);
    svg.append('path').datum(er).attr('d', d3.line().x((r) => x(r.d)).y((r) => yE(r.el))).attr('fill', 'none').attr('stroke', C0).attr('stroke-width', 2);
    yearAxis(svg, x, H - 24, w);
    const bis = d3.bisector((r) => r.d).center;
    const mv = (ev) => { const [px, py] = d3.pointer(ev, el); const r = er[bis(er, x.invert(px * w / el.clientWidth))]; if (r) showTip(el, t, px, py, ymLabel(r.ym), [[C0, 'Média', fPct0(r.el)], [null, 'Faixa 25–75%', fPct0(r.e25) + ' a ' + fPct0(r.e75)]]); };
    svg.append('rect').attr('x', ml).attr('y', 0).attr('width', w - ml - mr).attr('height', H).attr('fill', 'transparent').on('pointermove', mv).on('pointerdown', mv).on('pointerleave', () => { t.hidden = true; });
  });
  dash.draw('cy-phases', (el) => {
    el.replaceChildren(); const m = cyc(); if (!m) return; const b = base(); const sel = curTk(m, b);
    const grid = document.createElement('div'); grid.className = 'rx-phases'; el.append(grid); const N = P().cyN === 20 ? 20 : 10;
    m.phases.forEach((p) => {
      const c = document.createElement('div'); c.className = 'rx-phase'; const h = document.createElement('h3'); h.textContent = p.nm; c.append(h);
      [['Subiram mais', p.best.slice(0, N)], ['Caíram mais', p.worst.slice(0, N)]].forEach(([tt, list]) => {
        const l = document.createElement('div'); l.className = 'lbl'; l.textContent = tt; c.append(l);
        list.forEach((s) => { const bt = document.createElement('button'); bt.type = 'button'; bt.className = 'rx-stk'; bt.setAttribute('aria-pressed', String(s.tk === sel));
          const a = document.createElement('span'); a.className = 'tk'; a.textContent = s.tk; const n = document.createElement('span'); n.className = 'nm'; n.textContent = b.nome.get(s.tk) || ''; const v = document.createElement('span'); v.className = sc(s.r); v.textContent = fPct0(s.r);
          bt.append(a, n, v); bt.onclick = () => pickTk(s.tk); c.append(bt); });
      });
      grid.append(c);
    });
    const more = document.createElement('button'); more.type = 'button'; more.className = 'rx-btn'; more.style.marginTop = '12px'; const big = N === 20;
    more.textContent = big ? 'Mostrar 10 por lista' : 'Mostrar 20 por lista'; more.onclick = () => dash.setParams({ cyN: big ? 10 : 20 }); el.append(more);
  });
  document.addEventListener('toggle', (ev) => { const d = ev.target; if (d.matches?.('details.rx-more')) d.querySelectorAll('[data-draw]').forEach((n) => dash.draw(n.dataset.draw)); }, true);

  // ---------- ciclo: stock detail ----------
  dash.draw('cy-acao-t', (el) => { const m = cyc(); if (!m) return; const b = base(); const tk = curTk(m, b); el.textContent = tk ? tkName(b, tk) + (b.setor.get(tk) ? ' · ' + b.setor.get(tk) : '') : '—'; });
  dash.draw('cy-acao-lg', (el) => {
    el.replaceChildren();
    [[C0, 'Ação (retorno total, base 100)'], ['var(--cds-chart-muted)', 'Ibovespa'], ['color-mix(in srgb, var(--cds-chart-muted) 60%, transparent)', 'nº de fundos com ≥1% do PL']].forEach(([bg, t]) => { const s = document.createElement('span'); const i = document.createElement('i'); i.style.background = bg; s.append(i, document.createTextNode(t)); el.append(s); });
  });
  dash.draw('cy-acao-k', (el) => {
    el.replaceChildren(); const m = cyc(); if (!m) return; const b = base(); const tk = curTk(m, b); if (!tk) return; const rr = b.ret.get(tk);
    m.phases.forEach((p) => {
      const have = p.pm.filter((x) => Number.isFinite(rr.get(x))).length; const v = have === p.pm.length ? comp(p.pm, (x) => rr.get(x)) : NaN;
      const k = document.createElement('div'); k.className = 'rx-kv'; const a = document.createElement('span'); a.textContent = p.nm + ' (Ibov ' + fPct(p.ib) + ')';
      const c = document.createElement('span'); c.textContent = Number.isFinite(v) ? fPct(v) : 'sem dado completo'; c.className = sc(v); k.append(a, c); el.append(k);
    });
  });
  dash.draw('cy-acao', (el) => {
    const m = cyc(); if (!m) return; const b = base(); const tk = curTk(m, b); const t = tipOf(el); const { svg, w } = svgFor(el, 10); if (!tk) return;
    const rr = b.ret.get(tk); const h = b.hold.get(tk.slice(0, 4));
    let ix = 100, ii = 100, alive = true;
    const rows = m.ms.map((ym, k) => {
      if (k > 0) { const x = rr.get(ym); if (Number.isFinite(x)) ix *= 1 + x; else alive = false; const y = b.ibr(ym); if (Number.isFinite(y)) ii *= 1 + y; }
      return { ym, d: endDate(ym), ix: k === 0 || Number.isFinite(rr.get(ym)) ? ix : NaN, ii, n: h?.get(ym)?.size || 0 };
    });
    const ml = 44, mr = 12, top = 22, pH = 220, gap = 26, nH = 60, H = top + pH + gap + nH + 24; setH(svg, w, H);
    const x = d3.scaleUtc([rows[0].d, rows[rows.length - 1].d], [ml, w - mr]);
    drawPhases(svg, x, top - 4, H - 24, m.ini, m.fim, 12);
    eventLines(svg, x, rows[0].d, rows[rows.length - 1].d, top, H - 24);
    const vals = rows.flatMap((r) => [r.ix, r.ii]).filter(Number.isFinite);
    const y = d3.scaleLog([Math.max(1, d3.min(vals) * 0.95), d3.max(vals) * 1.05], [top + pH, top]);
    const ticks = y.ticks(5).filter((v, i, a) => a.length < 8 || [1, 2, 5].includes(+String(v)[0]));
    svg.append('g').attr('transform', `translate(${ml},0)`).call(d3.axisLeft(y).tickValues(ticks).tickFormat(L.format(',.0f')).tickSize(-(w - ml - mr))).call(axisClean).call((g) => g.select('.domain').remove());
    svg.append('line').attr('x1', ml).attr('x2', w - mr).attr('y1', y(100)).attr('y2', y(100)).attr('stroke', 'var(--cds-chart-reference)');
    svg.append('path').datum(rows).attr('d', d3.line().x((r) => x(r.d)).y((r) => y(r.ii))).attr('fill', 'none').attr('stroke', 'var(--cds-chart-muted)').attr('stroke-width', 2);
    svg.append('path').datum(rows).attr('d', d3.line().defined((r) => Number.isFinite(r.ix)).x((r) => x(r.d)).y((r) => y(r.ix))).attr('fill', 'none').attr('stroke', C0).attr('stroke-width', 2.25);
    const y0 = top + pH + gap; const yN = d3.scaleLinear([0, Math.max(3, d3.max(rows, (r) => r.n))], [y0 + nH, y0]).nice();
    label(svg, ml, y0 - 6, 'Fundos com ≥1% do PL na ação');
    svg.append('g').attr('transform', `translate(${ml},0)`).call(d3.axisLeft(yN).ticks(2).tickFormat(L.format('d')).tickSize(-(w - ml - mr))).call(axisClean).call((g) => g.select('.domain').remove());
    const step = (w - ml - mr) / Math.max(1, rows.length - 1);
    svg.append('g').selectAll('rect').data(rows.filter((r) => r.n > 0)).join('rect').attr('x', (r) => x(r.d) - step * 0.85).attr('width', Math.max(1, step * 0.7)).attr('y', (r) => yN(r.n)).attr('height', (r) => yN(0) - yN(r.n)).style('fill', 'var(--cds-chart-muted)').style('opacity', 0.8);
    yearAxis(svg, x, H - 24, w);
    const rule = svg.append('line').attr('y1', top).attr('y2', H - 24).attr('stroke', 'var(--color-fg-muted)').style('display', 'none');
    const bis = d3.bisector((r) => r.d).center;
    const move = (ev) => {
      const [px, py] = d3.pointer(ev, el); const r = rows[bis(rows, x.invert(px * w / el.clientWidth))]; if (!r) return; rule.style('display', null).attr('x1', x(r.d)).attr('x2', x(r.d));
      const ev2 = EVENTS.filter((e) => Math.abs(x(e.d) - x(r.d)) < step).map((e) => [null, e.l, e.ds.split('-').reverse().join('/')]);
      showTip(el, t, px, py, tk + ' · ' + ymLabel(r.ym), [[C0, 'Ação', Number.isFinite(r.ix) ? L.format(',.0f')(r.ix) : 'sem preço'], ['var(--cds-chart-muted)', 'Ibovespa', L.format(',.0f')(r.ii)], [null, 'Fundos com ≥1%', String(r.n)], ...ev2]);
    };
    svg.append('rect').attr('x', ml).attr('y', 0).attr('width', Math.max(0, w - ml - mr)).attr('height', H).attr('fill', 'transparent').on('pointermove', move).on('pointerdown', move).on('pointerleave', () => { rule.style('display', 'none'); t.hidden = true; });
    if (!alive) label(svg, w - mr, top + 10, 'linha some quando falta preço', 'end');
  });

  // ---------- resumo: heatmap ----------
  const sumModel = () => {
    const b = base(); if (!b) return null; const [ini, fim] = win();
    const rm = b.months.filter((m) => m > ini && m <= fim); const years = [...new Set(rm.map((m) => m.slice(0, 4)))];
    const ser = d3.group(D('serie_mensal'), (r) => String(r.id));
    const rows = D('fundos').map((f) => {
      const by = new Map((ser.get(String(f.id)) || []).map((r) => [r.ym, r]));
      const fr = (m) => { const r = by.get(m); if (!r) return NaN; const a = num(r.ret_fundo); return Number.isFinite(a) ? a : num(r.ret_acoes_contrib); };
      const cell = (msy) => { const mm = msy.filter((m) => Number.isFinite(fr(m))); const v = comp(mm, fr), ib = comp(mm, b.ibr); return { v, ib, d: v - ib, full: mm.length === msy.length, n: mm.length }; };
      return { id: String(f.id), fundo: f.fundo, gestora: f.gestora, cells: years.map((y) => cell(rm.filter((m) => m.startsWith(y)))), tot: cell(rm) };
    }).sort((a, z) => (Number.isFinite(z.tot.d) ? z.tot.d : -9) - (Number.isFinite(a.tot.d) ? a.tot.d : -9));
    return { years, rows, ibY: years.map((y) => comp(rm.filter((m) => m.startsWith(y)), b.ibr)), ibT: comp(rm, b.ibr), partial: years.map((y) => rm.filter((m) => m.startsWith(y)).length < 12) };
  };
  dash.draw('hm-sum', (el) => {
    const m = sumModel(); if (!m) return; const t = tipOf(el); const { svg, w } = svgFor(el, 10); const narrow = w < 560;
    const nameW = narrow ? 118 : 230, totW = narrow ? 54 : 74, rh = 22, head = 22, gapIb = 8;
    const cw = (w - nameW - totW - 6) / Math.max(1, m.years.length); const showNum = cw >= 26; const nf = cw < 44 ? '9.5px' : '11px';
    const H = head + m.rows.length * rh + gapIb + rh + 4; setH(svg, w, H);
    const maxC = narrow ? 17 : 34; const cut = (s) => (s.length > maxC ? s.slice(0, maxC - 1) + '…' : s);
    m.years.forEach((y, j) => svg.append('text').attr('x', nameW + j * cw + cw / 2).attr('y', 14).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg-muted)').style('font-size', '11px').text((cw >= 44 ? y : "'" + y.slice(2)) + (m.partial[j] ? '*' : '')));
    svg.append('text').attr('x', w - totW / 2).attr('y', 14).attr('text-anchor', 'middle').attr('fill', 'var(--color-fg-muted)').style('font-size', '11px').style('font-weight', 600).text('Total');
    const cellTip = (ev, f, yLab, c) => { const [px, py] = d3.pointer(ev, el); showTip(el, t, px, py, f.fundo + ' · ' + yLab, [[null, 'Fundo', Number.isFinite(c.v) ? fPct(c.v) : 'sem cota'], [null, 'Ibovespa', fPct(c.ib)], [Number.isFinite(c.d) ? (c.d >= 0 ? 'var(--color-ok)' : 'var(--color-bad)') : null, 'Diferença', Number.isFinite(c.d) ? fPP(c.d * 100) + ' p.p.' : '—'], ...(c.full ? [] : [[null, 'Só ' + c.n + ' meses com cota', null]])]); };
    m.rows.forEach((f, i) => {
      const y = head + i * rh;
      const nm = svg.append('text').attr('x', 0).attr('y', y + rh / 2).attr('dy', '0.35em').attr('fill', 'var(--color-fg)').style('font-size', '12px').style('cursor', 'pointer').style('text-decoration', 'underline').style('text-decoration-color', 'var(--color-border-line)').text(cut(f.fundo));
      nm.append('title').text(f.fundo + ' — ' + f.gestora + ' (abrir fundo)');
      nm.on('click', () => { dash.setParams({ fundo: f.id, acao: null, pg: 'fundo' }); go('topo'); });
      const cells = [...f.cells.map((c, j) => ({ c, x: nameW + j * cw, wd: cw, cap: 0.3, lab: m.years[j] })), { c: f.tot, x: w - totW, wd: totW, cap: 1, lab: 'período', tot: true }];
      cells.forEach((o) => {
        const g = svg.append('g').style('cursor', 'default');
        g.append('rect').attr('x', o.x + 1).attr('y', y + 1).attr('width', Math.max(1, o.wd - 2)).attr('height', rh - 2).attr('rx', 2).style('fill', Number.isFinite(o.c.v) ? div(o.c.d, o.cap) : 'none').style('stroke', Number.isFinite(o.c.v) ? 'none' : 'var(--color-border-line)');
        if (Number.isFinite(o.c.v) && (showNum || o.tot)) g.append('text').attr('x', o.x + o.wd / 2).attr('y', y + rh / 2).attr('dy', '0.35em').attr('text-anchor', 'middle').attr('fill', 'var(--color-fg)').style('font-size', o.tot ? '11px' : nf).style('font-weight', o.tot ? 600 : 400).text(fPct0(o.c.v) + (o.c.full ? '' : '¹'));
        g.on('pointermove', (ev) => cellTip(ev, f, o.lab, o.c)).on('pointerdown', (ev) => cellTip(ev, f, o.lab, o.c)).on('pointerleave', () => { t.hidden = true; });
      });
    });
    const yI = head + m.rows.length * rh + gapIb;
    svg.append('line').attr('x1', 0).attr('x2', w).attr('y1', yI - gapIb / 2).attr('y2', yI - gapIb / 2).attr('stroke', 'var(--color-fg-muted)');
    svg.append('text').attr('x', 0).attr('y', yI + rh / 2).attr('dy', '0.35em').attr('fill', 'var(--color-fg)').style('font-size', '12px').style('font-weight', 600).text('Ibovespa');
    [...m.ibY.map((v, j) => ({ v, x: nameW + j * cw, wd: cw })), { v: m.ibT, x: w - totW, wd: totW, tot: true }].forEach((o) => {
      if (showNum || o.tot) svg.append('text').attr('x', o.x + o.wd / 2).attr('y', yI + rh / 2).attr('dy', '0.35em').attr('text-anchor', 'middle').attr('class', sc(o.v)).style('fill', o.v >= 0 ? 'var(--color-ok)' : 'var(--color-bad)').style('font-size', o.tot ? '11px' : nf).style('font-weight', 600).text(fPct0(o.v));
      else svg.append('rect').attr('x', o.x + 1).attr('y', yI + 1).attr('width', o.wd - 2).attr('height', rh - 2).attr('rx', 2).style('fill', 'transparent').on('pointerdown', (ev) => { const [px, py] = d3.pointer(ev, el); showTip(el, t, px, py, 'Ibovespa', [[null, 'Retorno', fPct(o.v)]]); });
    });
  });

  // ---------- empresas: bubbles ----------
  const empYears = () => { const b = base(); if (!b) return []; const [ini, fim] = win(); return [...new Set(b.months.filter((m) => m > ini && m <= fim).map((m) => m.slice(0, 4)))]; };
  const empYear = () => { const ys = empYears(); const y = P().anoEmp; return ys.includes(y) ? y : ys[0]; };
  const bubModel = (y) => {
    const b = base(); const [ini, fim] = win(); const rm = b.months.filter((m) => m > ini && m <= fim && m.startsWith(y)); const out = [];
    b.rep.forEach((tk, rt) => {
      const ws = b.wsum.get(rt); if (!ws) return; const cons = d3.mean(rm, (m) => (ws.get(m) || 0) / (b.nAct.get(m) || 1)); if (!(cons >= 0.001)) return;
      const rr = b.ret.get(tk); if (!rm.every((m) => Number.isFinite(rr.get(m)))) return;
      const hs = new Set(); const h = b.hold.get(rt); rm.forEach((m) => h?.get(m)?.forEach((f) => hs.add(f)));
      out.push({ tk, nome: b.nome.get(tk) || '', cons, r: comp(rm, (m) => rr.get(m)), n: hs.size });
    });
    return { rows: out, ib: comp(rm, b.ibr), nf: D('fundos').length };
  };
  dash.draw('bub-anos', (el) => {
    el.replaceChildren(); const ys = empYears(); const y0 = empYear();
    ys.forEach((y) => { const bt = document.createElement('button'); bt.type = 'button'; bt.className = 'rx-chip'; bt.textContent = y; bt.setAttribute('aria-pressed', String(y === y0)); bt.onclick = () => dash.setParams({ anoEmp: y }); el.append(bt); });
  });
  dash.draw('emp-bub', (el) => {
    const b = base(); if (!b) return; const y = empYear(); if (!y) return; const m = bubModel(y); const t = tipOf(el);
    const { svg, w } = svgFor(el, 10); const narrow = w < 560; const H = narrow ? 360 : 440; setH(svg, w, H);
    const ml = 48, mr = 16, top = 14, mb = 40;
    const rows = m.rows.slice().sort((a, z) => z.n - a.n);
    const x = d3.scaleSqrt([0, d3.max(rows, (r) => r.cons) * 1.05], [ml, w - mr]);
    const lo = Math.max(-0.9, d3.min(rows, (r) => r.r)), hi = Math.min(2.5, d3.max(rows, (r) => r.r));
    const yS = d3.scaleLinear([Math.min(lo, m.ib, 0), Math.max(hi, m.ib, 0)], [H - mb, top]).nice();
    const rS = d3.scaleSqrt([0, m.nf], [2.5, narrow ? 12 : 16]);
    const cl = (v) => Math.max(yS.domain()[0], Math.min(yS.domain()[1], v));
    svg.append('g').attr('transform', `translate(0,${H - mb})`).call(d3.axisBottom(x).ticks(narrow ? 4 : 6).tickFormat(L.format('.1%')).tickSizeOuter(0)).call(axisClean);
    svg.append('g').attr('transform', `translate(${ml},0)`).call(d3.axisLeft(yS).ticks(6).tickFormat(L.format('.0%')).tickSize(-(w - ml - mr))).call(axisClean).call((g) => g.select('.domain').remove());
    label(svg, w - mr, H - 6, 'Peso médio nos fundos no ano (consenso) →', 'end');
    svg.append('line').attr('x1', ml).attr('x2', w - mr).attr('y1', yS(m.ib)).attr('y2', yS(m.ib)).attr('stroke', 'var(--color-fg-muted)').attr('stroke-dasharray', '5 4');
    label(svg, w - mr, yS(m.ib) - 5, 'Ibovespa ' + fPct(m.ib), 'end');
    const sel = P().cTk;
    const g = svg.append('g').selectAll('circle').data(rows).join('circle').attr('cx', (r) => x(r.cons)).attr('cy', (r) => yS(cl(r.r))).attr('r', (r) => rS(r.n))
      .style('fill', (r) => (r.r > m.ib ? 'var(--color-ok)' : 'var(--color-bad)')).style('fill-opacity', 0.45).style('stroke', (r) => (r.tk === sel ? 'var(--color-fg)' : r.r > m.ib ? 'var(--color-ok)' : 'var(--color-bad)')).style('stroke-width', (r) => (r.tk === sel ? 2 : 1)).style('cursor', 'pointer');
    const lab = new Set([...rows].sort((a, z) => z.cons - a.cons).slice(0, narrow ? 6 : 10).map((r) => r.tk));
    [...rows].sort((a, z) => z.r - a.r).slice(0, 3).forEach((r) => lab.add(r.tk)); [...rows].sort((a, z) => a.r - z.r).slice(0, 3).forEach((r) => lab.add(r.tk));
    svg.append('g').selectAll('text').data(rows.filter((r) => lab.has(r.tk))).join('text').attr('x', (r) => x(r.cons) + rS(r.n) + 3).attr('y', (r) => yS(cl(r.r))).attr('dy', '0.35em').attr('fill', 'var(--color-fg)').style('font-size', '11px').style('pointer-events', 'none').text((r) => r.tk + (r.r > hi || r.r < lo ? ' (' + fPct0(r.r) + ')' : ''));
    const tipF = (ev, r) => { const [px, py] = d3.pointer(ev, el); showTip(el, t, px, py, tkName(b, r.tk), [[null, 'Retorno ' + y, fPct(r.r)], [null, 'Ibovespa', fPct(m.ib)], [null, 'Peso de consenso', fPct1(r.cons)], [null, 'Fundos com ≥1%', r.n + ' de ' + m.nf], [null, 'Toque para ver no Ciclo', null]]); };
    g.on('pointermove', tipF).on('pointerenter', tipF).on('pointerleave', () => { t.hidden = true; }).on('click', (ev, r) => { dash.setParams({ pg: 'ciclo', cTk: r.tk }); go('cy-acao-card'); });
  });

  // ---------- cartas: timeline ----------
  let TM = null;
  const inv = (pos) => ['vendida', 'saída', 'reduziu', 'cautela'].includes(pos);
  const fwd = (b0, n, rf, back) => {
    const out = []; const y = +b0.slice(0, 4), mo = +b0.slice(5, 7);
    const st = (k) => { let mm = mo + k, yy = y; while (mm > 12) { mm -= 12; yy++; } while (mm < 1) { mm += 12; yy--; } return yy + '-' + String(mm).padStart(2, '0'); };
    if (back) { for (let k = -n + 1; k <= 0; k++) out.push(st(k)); } else { for (let k = 1; k <= n; k++) out.push(st(k)); }
    let g = 1, c = 0; out.forEach((ym) => { const x = rf(ym); if (Number.isFinite(x)) { g *= 1 + x; c++; } }); return c >= n * 0.75 ? g - 1 : NaN;
  };
  const teses = () => {
    const b = base(); if (!b || !ok(['cartas_teses'])) return null; if (TM) return TM;
    TM = D('cartas_teses').map((t) => {
      const rr = b.ret.get(t.tk) || new Map(); const rf = (ym) => rr.get(ym); const back = t.janela === 'antes';
      const res = (back ? [12] : [12, 24, 36]).map((n) => { const a = fwd(t.base, n, rf, back), bb = fwd(t.base, n, b.ibr, back); return { n, a, b: bb, d: a - bb }; });
      const key = back ? res[0] : (Number.isFinite(res[1].d) ? res[1] : res[0]); const mkt = t.posicao === 'mercado';
      const s = mkt ? key.a : inv(t.posicao) ? -key.d : key.d;
      let v = 'Neutro', vc = ''; if (Number.isFinite(s)) { if (s > 0.05) { v = 'Acertou'; vc = 'ok'; } else if (s < -0.05) { v = 'Errou'; vc = 'bad'; } } else v = 'Sem dado';
      if (back && key.d < -0.05) { v = 'Erro reconhecido'; vc = 'bad'; }
      return { ...t, id: String(t.id), back, mkt, res, key, s, v, vc, d: endDate(t.base), short: inv(t.posicao) };
    });
    return TM;
  };
  dash.draw('ct-legend', (el) => {
    el.replaceChildren();
    const add = (svgStr, txt) => { const s = document.createElement('span'); s.innerHTML = svgStr; s.append(document.createTextNode(txt)); el.append(s); };
    add('<svg width="12" height="12"><circle cx="6" cy="6" r="4.5" fill="var(--color-ok)" fill-opacity=".6" stroke="var(--color-ok)"/></svg>', 'long (comprou/recomendou)');
    add('<svg width="12" height="12"><path d="M6 1 L11 6 L6 11 L1 6Z" fill="var(--color-ok)" fill-opacity=".6" stroke="var(--color-ok)"/></svg>', 'short (vendeu/saiu/reduziu/cautela)');
    add('<svg width="12" height="12"><rect x="1.5" y="1.5" width="9" height="9" fill="var(--cds-chart-muted)" stroke="var(--cds-chart-muted)"/></svg>', 'visão sobre a bolsa');
    add('<svg width="12" height="12"><circle cx="6" cy="6" r="4.5" fill="none" stroke="var(--color-bad)" stroke-width="1.5"/></svg>', 'olhando para trás (erro admitido)');
  });
  dash.draw('ct-time', (el) => {
    const T = teses(); if (!T) return; const t = tipOf(el); const b = base();
    const { svg, w } = svgFor(el, 10); const narrow = w < 560; const H = narrow ? 300 : 340; setH(svg, w, H);
    const ml = 48, mr = 14, top = 22, mb = 26;
    const d0 = d3.min(T, (r) => r.d), d1 = d3.max(T, (r) => r.d);
    const x = d3.scaleUtc([d3.utcMonth.offset(d0, -3), d3.utcMonth.offset(d1, 3)], [ml, w - mr]);
    const vals = T.map((r) => r.s).filter(Number.isFinite);
    const cap = 1.5; const y = d3.scaleLinear([Math.max(-cap, Math.min(-0.2, d3.min(vals))), Math.min(cap, Math.max(0.2, d3.max(vals)))], [H - mb, top]).nice();
    const [ini, fim] = [d3.utcFormat('%Y-%m')(d3.utcMonth.offset(x.domain()[0], -1)), d3.utcFormat('%Y-%m')(d3.utcMonth.offset(x.domain()[1], -1))];
    drawPhases(svg, x, top - 4, H - mb, ini < '2013-12' ? '2013-12' : ini, fim, 12);
    eventLines(svg, x, x.domain()[0], x.domain()[1], top, H - mb);
    svg.append('rect').attr('x', ml).attr('width', w - ml - mr).attr('y', y(0.05)).attr('height', y(-0.05) - y(0.05)).style('fill', 'var(--cds-chart-grid)');
    svg.append('g').attr('transform', `translate(${ml},0)`).call(d3.axisLeft(y).ticks(6).tickFormat((v) => L.format('+.0f')(v * 100)).tickSize(-(w - ml - mr))).call(axisClean).call((g) => g.select('.domain').remove());
    svg.append('line').attr('x1', ml).attr('x2', w - mr).attr('y1', y(0)).attr('y2', y(0)).attr('stroke', 'var(--cds-chart-reference)');
    label(svg, ml + 4, top + 8, '↑ acertou (p.p. vs Ibovespa)'); label(svg, ml + 4, H - mb - 6, '↓ errou');
    svg.append('g').attr('transform', `translate(0,${H - mb})`).call(d3.axisBottom(x).ticks(d3.utcYear.every(1)).tickFormat((d) => String(d.getUTCFullYear())).tickSizeOuter(0)).call(axisClean);
    // jitter same month
    const seen = new Map(); const pts = T.filter((r) => Number.isFinite(r.s)).map((r) => { const k = r.base; const n = seen.get(k) || 0; seen.set(k, n + 1); return { r, jx: (n % 2 ? 1 : -1) * Math.ceil(n / 2) * 5 }; });
    const sel = P().cTese; const col = (r) => (r.vc === 'ok' ? 'var(--color-ok)' : r.vc === 'bad' ? 'var(--color-bad)' : 'var(--cds-chart-muted)');
    const sym = d3.symbol().size(narrow ? 60 : 80);
    const g = svg.append('g').selectAll('path').data(pts).join('path')
      .attr('transform', (p) => `translate(${x(p.r.d) + p.jx},${y(Math.max(y.domain()[0], Math.min(y.domain()[1], p.r.s)))})`)
      .attr('d', (p) => sym.type(p.r.mkt ? d3.symbolSquare : p.r.short ? d3.symbolDiamond : d3.symbolCircle)())
      .style('fill', (p) => (p.r.back ? 'none' : col(p.r))).style('fill-opacity', 0.6).style('stroke', (p) => (p.r.id === sel ? 'var(--color-fg)' : col(p.r))).style('stroke-width', (p) => (p.r.id === sel ? 2.5 : 1.5)).style('cursor', 'pointer');
    const tipF = (ev, p) => { const r = p.r; const [px, py] = d3.pointer(ev, el); showTip(el, t, px, py, r.gestora + ' · ' + (r.mkt ? 'Ibovespa' : r.tk) + ' · ' + ymLabel(r.base), [[null, r.posicao, null], ...(Math.abs(r.s) > y.domain()[1] ? [[null, 'fora da escala do gráfico', null]] : []), [col(r), r.v, Number.isFinite(r.s) ? fPP(r.s * 100) + ' p.p.' : null], [null, 'Toque para abrir', null]]); };
    g.on('pointermove', tipF).on('pointerenter', tipF).on('pointerleave', () => { t.hidden = true; }).on('click', (ev, p) => { dash.setParams({ cTese: p.r.id, gestora: p.r.gestora }); go('ct-det'); });
    const nNo = T.length - pts.length; if (nNo) label(svg, w - mr, H - 4, nNo + ' teses sem dado de retorno não aparecem', 'end');
  });
  dash.draw('ct-det', (el) => {
    el.replaceChildren(); const T = teses(); if (!T) return; const b = base(); const r = T.find((x) => x.id === P().cTese);
    if (!r) { const p = document.createElement('p'); p.className = 'rx-ct-empty'; p.textContent = 'Toque num ponto para ver a tese.'; el.append(p); return; }
    const card = document.createElement('div'); card.className = 'rx-tese';
    const head = document.createElement('div'); head.className = 'rx-tese-head';
    const tt = document.createElement('div'); const t1 = document.createElement('div'); t1.className = 'rx-tese-title'; t1.textContent = r.gestora + ' · ' + (r.mkt ? 'Ibovespa' : tkName(b, r.tk));
    const t2 = document.createElement('div'); t2.className = 'rx-tese-meta'; t2.append(document.createTextNode(ymLabel(r.base) + ' · ' + r.posicao + ' · '));
    if (/^https:\/\//.test(r.url || '')) { const a = document.createElement('a'); a.href = r.url; a.target = '_blank'; a.rel = 'noopener'; a.textContent = r.carta; t2.append(a); } else t2.append(document.createTextNode(r.carta));
    tt.append(t1, t2); const pill = document.createElement('span'); pill.className = 'rx-pill ' + r.vc; pill.textContent = r.v; head.append(tt, pill); card.append(head);
    [['O que pensava: ', r.visao], ['O que fez: ', r.acao], ['O que aconteceu: ', r.nota]].forEach(([k, v]) => { if (!v) return; const p = document.createElement('p'); const bb = document.createElement('b'); bb.textContent = k; p.append(bb, document.createTextNode(v)); card.append(p); });
    const rr = document.createElement('div'); rr.className = 'rx-res';
    r.res.forEach((x) => { const d = document.createElement('div'); const a = document.createElement('span'); a.textContent = r.back ? '12 meses antes da carta' : x.n / 12 + (x.n === 12 ? ' ano depois' : ' anos depois'); const s = document.createElement('span'); s.textContent = !Number.isFinite(x.a) ? 'sem dado' : r.mkt ? 'Ibovespa ' + fPct(x.a) : fPct(x.a) + ' vs Ibov ' + fPct(x.b) + ' (' + fPP(x.d * 100) + ' p.p.)'; if (Number.isFinite(x.d)) s.className = sc(r.mkt ? x.a : r.short ? -x.d : x.d); d.append(a, s); rr.append(d); });
    card.append(rr);
    const bt = document.createElement('button'); bt.type = 'button'; bt.className = 'rx-btn'; bt.textContent = 'Todas as teses da ' + r.gestora; bt.style.justifySelf = 'start';
    bt.onclick = () => { dash.setParams({ gestora: r.gestora }); go('cartas-detalhe'); }; card.append(bt);
    el.append(card);
  });

  // ---------- hooks ----------
  document.getElementById('cy-close')?.addEventListener('click', () => dash.setParams({ cTk: null }));
  dash.onData(() => { const c = document.getElementById('cy-acao-card'); if (c) c.hidden = !P().cTk; });
  dash.onData(() => { if (P().aba === 'pl') document.querySelectorAll('#resumo-tabela details.rx-more').forEach((d) => { d.open = true; }); });
  // tables -> cards on phones
  const cardify = () => {
    document.querySelectorAll('#dash-root table.rx-table:not(.rx-heat)').forEach((tb) => {
      tb.classList.add('rx-cardify');
      const hr = tb.tHead?.rows[tb.tHead.rows.length - 1]; if (!hr) return;
      const labs = [...hr.cells].map((c) => c.textContent.replace(/[↑↓]/g, '').trim());
      [...tb.tBodies, ...(tb.tFoot ? [tb.tFoot] : [])].forEach((sec) => [...sec.rows].forEach((row) => [...row.cells].forEach((c, i) => { const l = labs[i] || ''; if (c.dataset.label !== l) c.dataset.label = l; })));
    });
  };
  let raf = 0; new MutationObserver(() => { cancelAnimationFrame(raf); raf = requestAnimationFrame(cardify); }).observe(document.getElementById('dash-root'), { childList: true, subtree: true });
})();

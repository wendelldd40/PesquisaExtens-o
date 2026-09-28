#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os dois questionários (rua e clínica) a partir de um template único.

O fluxo é montado a partir da lista PASSOS de cada tema, então adicionar,
remover ou reordenar perguntas é só editar esse arquivo e rodar de novo.
"""

import json
import pathlib

TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=1">
<meta name="theme-color" content="__THEME_COLOR__">
<meta name="robots" content="noindex">
<title>__TITULO__</title>
<style>
:root{
  --g1:__G1__; --g2:__G2__; --g3:__G3__;
  --acento:__ACENTO__;
  --acento-escuro:__ACENTO_ESCURO__;
  --tinta:__TINTA__;
  --tinta-suave:__TINTA_SUAVE__;
  --campo:__CAMPO__;
  --borda:__BORDA__;
  --erro:#d64545;
}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  background:var(--g1);color:var(--tinta);overflow:hidden;-webkit-font-smoothing:antialiased;
}
#fundo{
  position:fixed;inset:0;z-index:0;
  background:linear-gradient(160deg,var(--g1) 0%,var(--g2) 48%,var(--g3) 100%);
  background-size:180% 180%;animation:respira 18s ease-in-out infinite;
}
@keyframes respira{0%,100%{background-position:0% 30%}50%{background-position:100% 70%}}
#fundo::after{
  content:"";position:absolute;inset:0;
  background:
    radial-gradient(60% 40% at 15% 8%,rgba(255,255,255,.28),transparent 70%),
    radial-gradient(50% 35% at 90% 95%,rgba(255,255,255,.18),transparent 70%);
}
@media (prefers-reduced-motion:reduce){#fundo{animation:none}}

.app{
  position:relative;z-index:1;height:100dvh;height:100vh;
  display:flex;flex-direction:column;
  padding:calc(env(safe-area-inset-top) + 14px) 16px calc(env(safe-area-inset-bottom) + 14px);
  max-width:540px;margin:0 auto;
}

/* ---------- topo ---------- */
.topo{display:flex;align-items:center;gap:12px;min-height:34px;flex-shrink:0}
.voltar{
  width:34px;height:34px;border:0;border-radius:50%;
  background:rgba(255,255,255,.22);color:#fff;
  display:none;align-items:center;justify-content:center;cursor:pointer;flex-shrink:0;
  transition:background .2s,transform .15s;
}
.voltar:active{transform:scale(.92)}
.voltar.on{display:flex}
.trilho{flex:1;height:4px;background:rgba(255,255,255,.28);border-radius:99px;overflow:hidden;opacity:0;transition:opacity .3s}
.trilho.on{opacity:1}
.barra{height:100%;width:0%;background:#fff;border-radius:99px;transition:width .45s cubic-bezier(.4,0,.2,1)}
.passo{font-size:12px;font-weight:600;color:rgba(255,255,255,.85);letter-spacing:.03em;opacity:0;transition:opacity .3s;flex-shrink:0}
.passo.on{opacity:1}

/* ---------- palco ---------- */
.palco{flex:1;display:flex;flex-direction:column;position:relative;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:10px 0;scrollbar-width:none}
.palco::-webkit-scrollbar{display:none}
.tela{display:none;flex-direction:column;margin:auto 0;animation:entra .42s cubic-bezier(.16,1,.3,1)}
.tela.ativa{display:flex}
@keyframes entra{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
@keyframes entraSuave{from{opacity:0}to{opacity:1}}

.selo{
  align-self:flex-start;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:rgba(255,255,255,.9);background:rgba(255,255,255,.18);
  padding:7px 13px;border-radius:99px;margin-bottom:18px;border:1px solid rgba(255,255,255,.25);
}
.selo.mini{margin-bottom:12px;letter-spacing:.1em;padding:6px 11px;font-size:10.5px}
h1{font-size:clamp(28px,8.2vw,38px);line-height:1.12;font-weight:800;color:#fff;letter-spacing:-.02em;margin-bottom:14px}
h2{font-size:clamp(21px,5.6vw,26px);line-height:1.25;font-weight:800;color:#fff;letter-spacing:-.02em;margin-bottom:8px}
h2.curta{font-size:clamp(24px,6.8vw,31px);line-height:1.2}
.apoio{font-size:16px;line-height:1.55;color:rgba(255,255,255,.88)}
.apoio.menor{font-size:14px;line-height:1.5}

/* ---------- campos ---------- */
.campo-area{margin-top:24px}
.campo{
  width:100%;border:2px solid transparent;outline:0;background:var(--campo);border-radius:16px;
  padding:18px;font-size:17px;font-family:inherit;color:var(--tinta);font-weight:500;
  transition:border-color .2s,background .2s,box-shadow .2s;
}
.campo.area{min-height:128px;resize:none;line-height:1.5;font-weight:400;font-size:16px}
.campo::placeholder{color:var(--tinta-suave);font-weight:400}
.campo:focus{border-color:#fff;background:#fff;box-shadow:0 8px 26px rgba(0,0,0,.14)}
.campo.ruim{border-color:var(--erro)}
.dica-campo{font-size:13px;color:rgba(255,255,255,.8);margin-top:10px;line-height:1.45;padding-left:2px}
.aviso{
  font-size:13.5px;color:#fff;margin-top:12px;font-weight:600;
  display:none;align-items:center;gap:7px;
  background:rgba(214,69,69,.92);padding:10px 13px;border-radius:12px;animation:entraSuave .25s;
}
.aviso.on{display:flex}

/* ---------- alternativas ---------- */
.opcoes{display:flex;flex-direction:column;gap:10px;margin-top:22px}
.opcao{
  width:100%;text-align:left;cursor:pointer;background:var(--campo);
  border:2px solid transparent;border-radius:16px;padding:15px 16px;
  display:flex;align-items:center;gap:13px;font-family:inherit;
  transition:transform .16s,border-color .2s,background .2s,box-shadow .2s;
}
.opcao:active{transform:scale(.985)}
.opcao.sel{border-color:#fff;background:#fff;box-shadow:0 10px 28px rgba(0,0,0,.16)}
.marca{
  width:23px;height:23px;border-radius:50%;border:2px solid var(--borda);flex-shrink:0;
  display:flex;align-items:center;justify-content:center;transition:all .2s;
}
.opcao.sel .marca{border-color:var(--acento);background:var(--acento)}
.marca svg{opacity:0;transform:scale(.5);transition:all .2s}
.opcao.sel .marca svg{opacity:1;transform:none}
.opcao-txt{display:flex;flex-direction:column;gap:3px;min-width:0}
.opcao-tit{font-size:15px;font-weight:600;color:var(--tinta);line-height:1.35}
.opcao.destaque .opcao-tit{font-size:16.5px;font-weight:700}
.opcao-sub{font-size:13.5px;color:var(--tinta-suave);line-height:1.4}

/* ---------- consentimento ---------- */
.termo{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);border-radius:16px;padding:16px;margin-top:20px}
.termo p{font-size:13.5px;line-height:1.6;color:rgba(255,255,255,.92)}
.aceite{
  display:flex;align-items:flex-start;gap:12px;margin-top:12px;cursor:pointer;
  background:var(--campo);border:2px solid transparent;border-radius:16px;padding:16px;
  transition:border-color .2s,background .2s;
}
.aceite.sel{border-color:#fff;background:#fff}
.caixa{
  width:23px;height:23px;border-radius:7px;border:2px solid var(--borda);flex-shrink:0;margin-top:1px;
  display:flex;align-items:center;justify-content:center;transition:all .2s;
}
.aceite.sel .caixa{border-color:var(--acento);background:var(--acento)}
.caixa svg{opacity:0;transform:scale(.5);transition:all .2s}
.aceite.sel .caixa svg{opacity:1;transform:none}
.aceite span{font-size:14.5px;line-height:1.45;color:var(--tinta);font-weight:600}

/* ---------- rodape ---------- */
.rodape{flex-shrink:0;padding-top:12px}
.btn{
  width:100%;border:0;border-radius:16px;padding:18px;cursor:pointer;font-family:inherit;
  font-size:17px;font-weight:700;letter-spacing:-.01em;background:#fff;color:var(--acento-escuro);
  display:flex;align-items:center;justify-content:center;gap:9px;
  box-shadow:0 10px 30px rgba(0,0,0,.18);transition:transform .16s,opacity .2s;
}
.btn:active{transform:scale(.985)}
.btn[disabled]{opacity:.45;cursor:not-allowed}
.btn.fantasma{background:rgba(255,255,255,.16);color:#fff;box-shadow:none;border:1px solid rgba(255,255,255,.3);margin-top:10px;font-size:15px;padding:15px}
[hidden]{display:none !important}
.rodape-nota{text-align:center;font-size:12px;color:rgba(255,255,255,.72);margin-top:12px;line-height:1.45}
.girando{width:19px;height:19px;border:2.5px solid rgba(0,0,0,.18);border-top-color:var(--acento-escuro);border-radius:50%;animation:gira .7s linear infinite}
@keyframes gira{to{transform:rotate(360deg)}}

/* ---------- final e gabarito ---------- */
.selo-ok{
  width:74px;height:74px;border-radius:50%;background:rgba(255,255,255,.2);
  border:2px solid rgba(255,255,255,.4);display:flex;align-items:center;justify-content:center;
  margin-bottom:22px;animation:pulsa .6s cubic-bezier(.16,1,.3,1);
}
@keyframes pulsa{0%{transform:scale(.4);opacity:0}60%{transform:scale(1.08)}100%{transform:scale(1);opacity:1}}
.cartao-info{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);border-radius:16px;padding:16px;margin-top:20px}
.cartao-info p{font-size:14px;line-height:1.6;color:rgba(255,255,255,.92)}
.gabarito{margin-top:18px;display:flex;flex-direction:column;gap:12px}
.item-gab{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.2);border-radius:16px;padding:15px;animation:entraSuave .35s}
.item-gab .tema{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.75);margin-bottom:7px;display:flex;align-items:center;gap:7px}
.pastilha{width:16px;height:16px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0}
.pastilha.certo{background:rgba(255,255,255,.95)}
.pastilha.errado{background:rgba(0,0,0,.22);border:1px solid rgba(255,255,255,.45)}
.item-gab .resposta{font-size:14.5px;font-weight:700;color:#fff;line-height:1.4;margin-bottom:6px}
.item-gab .porque{font-size:13.5px;line-height:1.6;color:rgba(255,255,255,.9)}

@media (max-height:680px){
  h1{font-size:26px}h2{font-size:20px}h2.curta{font-size:23px}
  .campo-area,.opcoes{margin-top:16px}
  .selo{margin-bottom:12px}
  .campo{padding:15px}.opcao{padding:13px 14px}
  .btn{padding:16px}
}
</style>
</head>
<body>
<div id="fundo"></div>

<div class="app">

  <header class="topo">
    <button class="voltar" id="btnVoltar" type="button" aria-label="Voltar">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
    </button>
    <div class="trilho" id="trilho"><div class="barra" id="barra"></div></div>
    <div class="passo" id="passo"></div>
  </header>

  <main class="palco" id="palco">

    <!-- abertura -->
    <section class="tela ativa" id="telaInicio">
      <div class="selo">__SELO__</div>
      <h1>__TITULO_H1__</h1>
      <p class="apoio">__ABERTURA__</p>
      <div class="cartao-info"><p>__INFO_ABERTURA__</p></div>
    </section>

    <!-- perguntas geradas dinamicamente -->

    <!-- final -->
    <section class="tela" id="telaFim">
      <div class="selo-ok">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
      </div>
      <h1 id="tituloFim">Registrado.</h1>
      <p class="apoio" id="textoFim">__FECHAMENTO__</p>
      <div class="cartao-info"><p id="notaFim">__NOTA_FIM__</p></div>
      <div class="gabarito" id="gabarito" hidden></div>
      <div class="gabarito" id="notasFinais">__NOTAS_FINAIS__</div>
    </section>

  </main>

  <footer class="rodape">
    <button class="btn" id="btnAvancar" type="button">
      <span id="txtBtn">__CTA_INICIAL__</span>
      <svg id="setaBtn" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
    </button>
    <button class="btn fantasma" id="btnGabarito" type="button" hidden>Ver o que a ciência diz</button>
    <div class="rodape-nota" id="notaRodape">__NOTA_RODAPE__</div>
  </footer>

</div>

<script>
/* =========================================================================
   CONFIGURAÇÃO - preencha com os dados do seu projeto Supabase
   Settings > API  ->  Project URL e anon public key
   ========================================================================= */
const CONFIG = {
  SUPABASE_URL:  "https://xplulvkgumomxjpctdah.supabase.co",
  SUPABASE_ANON: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhwbHVsdmtndW1vbXhqcGN0ZGFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA1NzkyNDQsImV4cCI6MjEwNjE1NTI0NH0.rB7cmw8SSUd04yt4O6jO1CVzFsJVW7UnieOZF00lsuE",
  TABELA:        "__TABELA__",
  TABELA_EVENTOS:"pesquisa_eventos",
  CANAL:         "__CANAL__",
  CAMPO_ORIGEM:  "__CAMPO_ORIGEM__",   // coluna que recebe o código do local/ponto
  PARAM_ORIGEM:  "__PARAM_ORIGEM__",   // parâmetro da URL: ?__PARAM_ORIGEM__=codigo
  FILA_KEY:      "fila_pesquisa___CANAL__"
};

/* Roteiro do questionário - gerado por build.py */
const PASSOS = __PASSOS_JSON__;

/* ===================== estado ===================== */
const params    = new URLSearchParams(location.search);
const origem    = (params.get(CONFIG.PARAM_ORIGEM) || "").trim().toLowerCase() || null;
const aplicador = (params.get("por") || "").trim() || null;

const estado = {
  i: -1,                      // -1 = abertura ; PASSOS.length = tela final
  resp: {},
  sessao: (crypto.randomUUID ? crypto.randomUUID() : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,c=>{const r=Math.random()*16|0;return (c==="x"?r:(r&0x3|0x8)).toString(16)})),
  inicio: Date.now(),
  enviando: false
};

const palco    = document.getElementById("palco");
const telaFim  = document.getElementById("telaFim");
const btn      = document.getElementById("btnAvancar");
const txtBtn   = document.getElementById("txtBtn");
const setaBtn  = document.getElementById("setaBtn");
const btnVolta = document.getElementById("btnVoltar");
const btnGab   = document.getElementById("btnGabarito");
const trilho   = document.getElementById("trilho");
const barra    = document.getElementById("barra");
const passoTxt = document.getElementById("passo");
const notaRod  = document.getElementById("notaRodape");

/* ===================== montagem das telas ===================== */
function esc(t){ const d = document.createElement("div"); d.textContent = t; return d.innerHTML; }
const CHECK = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>';

PASSOS.forEach((p, i) => {
  const sec = document.createElement("section");
  sec.className = "tela";
  sec.dataset.i = i;
  let html = "";

  if (p.selo)   html += '<div class="selo mini">' + esc(p.selo) + '</div>';
  html += '<h2' + (p.curta ? ' class="curta"' : '') + '>' + esc(p.titulo) + '</h2>';
  if (p.apoio)  html += '<p class="apoio menor">' + esc(p.apoio) + '</p>';

  if (p.tipo === "texto" || p.tipo === "tel"){
    html += '<div class="campo-area">'
         +  '<input class="campo" id="campo-' + i + '" type="' + (p.tipo === "tel" ? "tel" : "text") + '"'
         +  ' inputmode="' + (p.tipo === "tel" ? "numeric" : "text") + '"'
         +  ' autocomplete="' + (p.tipo === "tel" ? "tel" : "given-name") + '"'
         +  ' placeholder="' + esc(p.placeholder || "") + '" enterkeyhint="next"'
         +  (p.tipo === "tel" ? ' maxlength="16"' : ' maxlength="80" autocapitalize="words"') + '>'
         +  (p.dica ? '<div class="dica-campo">' + esc(p.dica) + '</div>' : '')
         +  '<div class="aviso" id="aviso-' + i + '"></div>'
         +  '</div>';
  }

  if (p.tipo === "longo"){
    html += '<div class="campo-area">'
         +  '<textarea class="campo area" id="campo-' + i + '" maxlength="600" rows="4"'
         +  ' placeholder="' + esc(p.placeholder || "") + '"></textarea>'
         +  (p.dica ? '<div class="dica-campo">' + esc(p.dica) + '</div>' : '')
         +  '<div class="aviso" id="aviso-' + i + '"></div>'
         +  '</div>';
  }

  if (p.tipo === "escolha"){
    html += '<div class="opcoes">';
    p.opcoes.forEach(o => {
      html += '<button class="opcao' + (o.sub ? ' destaque' : '') + '" type="button" data-v="' + esc(String(o.v)) + '">'
           +  '<span class="marca">' + CHECK + '</span>'
           +  '<span class="opcao-txt"><span class="opcao-tit">' + esc(o.t) + '</span>'
           +  (o.sub ? '<span class="opcao-sub">' + esc(o.sub) + '</span>' : '')
           +  '</span></button>';
    });
    html += '</div><div class="aviso" id="aviso-' + i + '"></div>';
  }

  if (p.tipo === "consent"){
    html += '<div class="termo"><p>' + esc(p.termo) + '</p></div>'
         +  '<label class="aceite" id="aceite-' + i + '">'
         +  '<span class="caixa">' + CHECK + '</span><span>' + esc(p.rotulo) + '</span></label>'
         +  '<div class="aviso" id="aviso-' + i + '"></div>';
  }

  sec.innerHTML = html;
  palco.insertBefore(sec, telaFim);
});

const telas = PASSOS.map((p,i) => palco.querySelector('.tela[data-i="' + i + '"]'));
const telaInicio = document.getElementById("telaInicio");

/* ===================== utilidades ===================== */
function tipoDispositivo(){
  const l = Math.min(screen.width, screen.height);
  return l < 600 ? "mobile" : (l < 1024 ? "tablet" : "desktop");
}
function vibra(ms){ if (navigator.vibrate){ try{ navigator.vibrate(ms); }catch(e){} } }
function alertar(i, msg){
  const el = document.getElementById("aviso-" + i);
  if (!el) return;
  el.textContent = msg; el.classList.add("on"); vibra(35);
  setTimeout(()=>el.classList.remove("on"), 4200);
}
function soDigitos(v){ return (v||"").replace(/\D/g,""); }
function formatarTelefone(v){
  const d = soDigitos(v).slice(0,11);
  if (d.length <= 2)  return d.length ? "(" + d : "";
  if (d.length <= 6)  return "(" + d.slice(0,2) + ") " + d.slice(2);
  if (d.length <= 10) return "(" + d.slice(0,2) + ") " + d.slice(2,6) + "-" + d.slice(6);
  return "(" + d.slice(0,2) + ") " + d.slice(2,7) + "-" + d.slice(7);
}
function telefoneValido(v){
  const d = soDigitos(v);
  if (d.length < 10 || d.length > 11) return false;
  if (/^(\d)\1+$/.test(d)) return false;
  const ddd = parseInt(d.slice(0,2),10);
  if (ddd < 11 || ddd > 99) return false;
  if (d.length === 11 && d[2] !== "9") return false;
  return true;
}

/* ===================== navegação ===================== */
/* Um passo com "exigeCampo" só aparece se aquele campo tiver sido preenchido.
   É o que faz a tela de dicas sumir para quem não deixou WhatsApp. */
function visivel(i){
  const p = PASSOS[i];
  if (!p) return false;
  if (p.exigeCampo){
    const v = estado.resp[p.exigeCampo];
    if (v === undefined || v === null || v === "") return false;
  }
  return true;
}
function totalVisiveis(){ return PASSOS.reduce((n,_,i)=> n + (visivel(i) ? 1 : 0), 0); }
function posicaoVisivel(i){ let n = 0; for (let k = 0; k <= i; k++) if (visivel(k)) n++; return n; }
function proximo(i){ let k = i + 1; while (k < PASSOS.length && !visivel(k)) k++; return k; }
function anterior(i){ let k = i - 1; while (k >= 0 && !visivel(k)) k--; return k; }
function ehUltimo(i){ return proximo(i) >= PASSOS.length; }

function vazio(i){
  const p = PASSOS[i];
  if (!p) return false;
  if (p.tipo === "texto" || p.tipo === "tel" || p.tipo === "longo"){
    const c = document.getElementById("campo-" + i);
    return !c || !c.value.trim();
  }
  return false;
}
function rotuloBotao(){
  if (estado.i === -1) return "__CTA_INICIAL__";
  const p = PASSOS[estado.i];
  if (p && p.opcional && vazio(estado.i)) return p.rotuloPular || "Pular esta pergunta";
  return ehUltimo(estado.i) ? "Enviar respostas" : "Continuar";
}
function atualizarBotao(){
  txtBtn.textContent = rotuloBotao();
  const seta = estado.i === -1 || !ehUltimo(estado.i);
  setaBtn.style.display = seta ? "" : "none";
}

function pintar(){
  telaInicio.classList.toggle("ativa", estado.i === -1);
  telaFim.classList.toggle("ativa", estado.i === PASSOS.length);
  telas.forEach((t,i)=> t.classList.toggle("ativa", i === estado.i));

  const emPerguntas = estado.i >= 0 && estado.i < PASSOS.length;
  trilho.classList.toggle("on", emPerguntas);
  passoTxt.classList.toggle("on", emPerguntas);
  btnVolta.classList.toggle("on", emPerguntas);
  if (emPerguntas){
    const total = totalVisiveis(), pos = posicaoVisivel(estado.i);
    barra.style.width = (pos / total * 100) + "%";
    passoTxt.textContent = pos + "/" + total;
  }

  atualizarBotao();
  btn.style.display = (estado.i === PASSOS.length) ? "none" : "";
  notaRod.style.display = (estado.i === -1 || estado.i === PASSOS.length) ? "" : "none";
  btn.disabled = false;
  palco.scrollTop = 0;

  const p = PASSOS[estado.i];
  if (p && (p.tipo === "texto" || p.tipo === "tel" || p.tipo === "longo")){
    setTimeout(()=>{ const c = document.getElementById("campo-" + estado.i); if (c) c.focus(); }, 340);
  }
}
function ir(n){
  estado.i = n;
  pintar();
  const p = PASSOS[n];
  if (p) registrarEvento(p.campo || ("passo" + n), n + 1);
}
function validar(){
  const i = estado.i, p = PASSOS[i];
  if (!p) return true;

  // campo opcional deixado em branco: segue em frente gravando vazio
  if (p.opcional && vazio(i)){ estado.resp[p.campo] = null; return true; }

  if (p.tipo === "texto" || p.tipo === "longo"){
    const c = document.getElementById("campo-" + i);
    const v = c.value.trim().replace(/[ \t]+/g," ");
    if (v.length < (p.minimo || 2)){ alertar(i, p.erro || "Preencha para continuar."); c.classList.add("ruim"); return false; }
    c.classList.remove("ruim"); estado.resp[p.campo] = v; return true;
  }
  if (p.tipo === "tel"){
    const c = document.getElementById("campo-" + i);
    if (!telefoneValido(c.value)){ alertar(i, p.erro || "Confira o número digitado."); c.classList.add("ruim"); return false; }
    c.classList.remove("ruim"); estado.resp[p.campo] = c.value.trim(); return true;
  }
  if (p.tipo === "escolha"){
    if (estado.resp[p.campo] === undefined){ alertar(i, p.erro || "Escolha uma das opções."); return false; }
    return true;
  }
  if (p.tipo === "consent"){
    if (!estado.resp[p.campo]){ alertar(i, p.erro || "Marque a autorização para enviar."); return false; }
    return true;
  }
  return true;
}
function avancar(){
  if (estado.i === -1){ ir(proximo(-1)); return; }
  if (!validar()) return;
  if (ehUltimo(estado.i)){ enviar(); return; }
  ir(proximo(estado.i));
}
function voltar(){ if (estado.i >= 0) ir(anterior(estado.i)); }

btn.addEventListener("click", avancar);
btnVolta.addEventListener("click", voltar);
document.addEventListener("keydown", e => { if (e.key === "Escape") voltar(); });

/* ---- delegação de eventos das telas geradas ---- */
palco.addEventListener("click", e => {
  const op = e.target.closest(".opcao");
  if (op){
    const sec = op.closest(".tela"); const i = +sec.dataset.i; const p = PASSOS[i];
    sec.querySelectorAll(".opcao").forEach(o => o.classList.remove("sel"));
    op.classList.add("sel");
    let v = op.dataset.v;
    if (v === "true" || v === "false") v = (v === "true");
    estado.resp[p.campo] = v;
    vibra(12);
    if (p.auto !== false) setTimeout(()=>{ if (estado.i === i) avancar(); }, 320);
    return;
  }
  const ac = e.target.closest(".aceite");
  if (ac){
    e.preventDefault();
    const i = +ac.closest(".tela").dataset.i; const p = PASSOS[i];
    estado.resp[p.campo] = !estado.resp[p.campo];
    ac.classList.toggle("sel", !!estado.resp[p.campo]);
    vibra(12);
  }
});
palco.addEventListener("input", e => {
  const c = e.target.closest(".campo");
  if (!c) return;
  const i = +c.closest(".tela").dataset.i;
  c.classList.remove("ruim");
  if (PASSOS[i].tipo === "tel"){
    const fim = c.selectionStart === c.value.length;
    c.value = formatarTelefone(c.value);
    if (fim) c.setSelectionRange(c.value.length, c.value.length);
  }
  atualizarBotao();      // "Pular esta pergunta" vira "Continuar" ao digitar
});
palco.addEventListener("keydown", e => {
  // Enter avança nos campos de uma linha; no texto longo ele quebra linha normalmente
  if (e.key === "Enter" && e.target.matches("input.campo")){ e.preventDefault(); avancar(); }
});

/* ===================== supabase ===================== */
function configurado(){
  return CONFIG.SUPABASE_URL.indexOf("supabase.co") !== -1 && CONFIG.SUPABASE_ANON.length > 40;
}
function cabecalhos(){
  return {
    "apikey": CONFIG.SUPABASE_ANON,
    "Authorization": "Bearer " + CONFIG.SUPABASE_ANON,
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
  };
}
async function postar(tabela, corpo){
  const r = await fetch(CONFIG.SUPABASE_URL + "/rest/v1/" + tabela, {
    method: "POST", headers: cabecalhos(), body: JSON.stringify(corpo)
  });
  if (!r.ok){
    const txt = await r.text();
    const err = new Error(txt || ("HTTP " + r.status));
    err.status = r.status; err.corpo = txt;
    throw err;
  }
  return true;
}
function registrarEvento(etapa, ordem){
  if (!configurado() || !etapa) return;
  try{
    fetch(CONFIG.SUPABASE_URL + "/rest/v1/" + CONFIG.TABELA_EVENTOS, {
      method:"POST", headers: cabecalhos(), keepalive: true,
      body: JSON.stringify({
        canal: CONFIG.CANAL, sessao_id: estado.sessao, etapa: etapa,
        ordem: ordem, local_codigo: origem, dispositivo: tipoDispositivo()
      })
    }).catch(()=>{});
  }catch(e){}
}

function montarRegistro(){
  const reg = {
    sessao_id: estado.sessao,
    duracao_seg: Math.max(1, Math.round((Date.now() - estado.inicio)/1000)),
    dispositivo: tipoDispositivo(),
    user_agent: navigator.userAgent.slice(0,400),
    referer: document.referrer ? document.referrer.slice(0,300) : null
  };
  PASSOS.forEach(p => { if (p.campo) reg[p.campo] = estado.resp[p.campo] ?? null; });
  reg[CONFIG.CAMPO_ORIGEM] = origem;
  if (CONFIG.CANAL === "rua") reg.entrevistador = aplicador;
  return reg;
}

/* fila local para quando o sinal cai (coleta de rua) */
function guardarNaFila(reg){
  try{
    const fila = JSON.parse(localStorage.getItem(CONFIG.FILA_KEY) || "[]");
    fila.push(reg);
    localStorage.setItem(CONFIG.FILA_KEY, JSON.stringify(fila));
  }catch(e){}
}
async function enviarFila(){
  if (!configurado()) return;
  let fila = [];
  try{ fila = JSON.parse(localStorage.getItem(CONFIG.FILA_KEY) || "[]"); }catch(e){ return; }
  if (!fila.length) return;
  const restantes = [];
  for (const reg of fila){
    try{ await postar(CONFIG.TABELA, reg); }
    catch(err){ if (err.status !== 409) restantes.push(reg); }
  }
  try{ localStorage.setItem(CONFIG.FILA_KEY, JSON.stringify(restantes)); }catch(e){}
}

async function enviar(){
  if (estado.enviando) return;
  estado.enviando = true;
  btn.disabled = true;
  txtBtn.textContent = "Enviando";
  setaBtn.style.display = "none";
  const load = document.createElement("span");
  load.className = "girando"; btn.appendChild(load);

  const reg = montarRegistro();

  if (!configurado()){            // modo demonstração
    guardarNaFila(reg);
    load.remove(); estado.enviando = false;
    concluir("demo"); return;
  }
  try{
    await postar(CONFIG.TABELA, reg);
    load.remove(); estado.enviando = false;
    enviarFila();
    concluir("ok");
  }catch(err){
    load.remove(); estado.enviando = false;
    if (err.status === 409){ concluir("repetido"); return; }
    guardarNaFila(reg);
    concluir("fila");
  }
}

/* ===================== conclusão e gabarito ===================== */
function montarGabarito(){
  const quiz = PASSOS.filter(p => p.correta);
  if (!quiz.length) return;
  const cx = document.getElementById("gabarito");
  cx.innerHTML = quiz.map(p => {
    const marcou  = estado.resp[p.campo];
    const acertou = marcou === p.correta;
    const certa   = p.opcoes.find(o => o.v === p.correta);
    return '<div class="item-gab">'
      + '<div class="tema"><span class="pastilha ' + (acertou ? 'certo' : 'errado') + '">'
      + (acertou ? '<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="' + getComputedStyle(document.documentElement).getPropertyValue("--acento") + '" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>' : '')
      + '</span>' + esc(p.tema || p.selo || "") + '</div>'
      + '<div class="resposta">' + esc(certa ? certa.t : "") + '</div>'
      + '<div class="porque">' + esc(p.explicacao || "") + '</div>'
      + '</div>';
  }).join("");
  const acertos = quiz.filter(p => estado.resp[p.campo] === p.correta).length;
  btnGab.hidden = false;
  btnGab.textContent = "Ver o que a ciência diz (" + acertos + " de " + quiz.length + ")";
  btnGab.onclick = () => {
    const aberto = !cx.hidden;
    cx.hidden = aberto;
    btnGab.textContent = aberto
      ? "Ver o que a ciência diz (" + acertos + " de " + quiz.length + ")"
      : "Ocultar explicações";
    if (!aberto) setTimeout(()=>{ palco.scrollTop = palco.scrollHeight; }, 60);
  };
}

function concluir(modo){
  const nomeCampo = (PASSOS.find(p => p.tipo === "texto") || {}).campo;
  const primeiro = ((estado.resp[nomeCampo] || "").split(" ")[0]) || "";
  const ola = primeiro ? "Obrigado, " + primeiro + ". " : "Obrigado. ";
  const t = document.getElementById("tituloFim");
  const x = document.getElementById("textoFim");
  const n = document.getElementById("notaFim");

  if (modo === "repetido"){
    t.textContent = "Você já participou";
    x.textContent = "Esse contato já consta na pesquisa" + (primeiro ? ", " + primeiro : "") + ". Não precisa responder de novo.";
    n.textContent = "Obrigado por colaborar com o projeto.";
  } else if (modo === "fila"){
    t.textContent = "Resposta salva";
    x.textContent = ola + "A conexão oscilou, mas sua resposta ficou guardada no aparelho e sobe automaticamente quando a internet voltar.";
    n.textContent = "Não feche esta página antes de recuperar o sinal.";
    montarGabarito();
  } else {
    t.textContent = "__TITULO_FIM__";
    x.textContent = ola + "__FECHAMENTO_DINAMICO__";
    n.textContent = estado.resp.aceita_dicas ? "__NOTA_FIM_SIM__" : "__NOTA_FIM_NAO__";
    montarGabarito();
  }
  registrarEvento("concluiu", PASSOS.length + 1);
  estado.i = PASSOS.length;
  pintar();
  vibra([18,60,18]);
}

/* ===================== inicialização ===================== */
window.addEventListener("online", enviarFila);
registrarEvento("abriu", 0);
enviarFila();
pintar();
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Passos comuns aos dois questionários (identificação e consentimento)
# ---------------------------------------------------------------------------
TERMO = ("Os dados informados serão utilizados exclusivamente para fins desta pesquisa de "
         "extensão universitária e para o envio do conteúdo, caso você tenha aceitado. Não "
         "serão repassados a terceiros e podem ser excluídos a qualquer momento mediante "
         "solicitação, conforme a Lei Geral de Proteção de Dados (Lei 13.709/2018).")


def identificacao(apoio_contato, contato_opcional=False):
    """Blocos finais: quem respondeu, contato e autorização.

    Com contato_opcional=True o WhatsApp pode ficar em branco e, nesse caso, a
    tela de opt-in some sozinha (exigeCampo) — não faz sentido perguntar se quer
    receber conteúdo de quem não deixou por onde enviar.
    """
    contato = {
        "tipo": "tel", "campo": "contato", "curta": True,
        "titulo": "Qual o seu WhatsApp?",
        "apoio": apoio_contato,
        "placeholder": "(79) 90000-0000",
        "dica": "Usado apenas para os fins descritos nesta pesquisa.",
        "erro": "Confira o número: DDD + 8 ou 9 dígitos.",
    }
    if contato_opcional:
        contato["opcional"] = True
        contato["rotuloPular"] = "Prefiro não informar"
        contato["dica"] = "Opcional. Se preferir não informar, é só seguir."

    dicas = {
        "tipo": "escolha", "campo": "aceita_dicas", "curta": True,
        "titulo": "Quer receber dicas de cuidado para o seu pet?",
        "apoio": "Conteúdo curto, sem custo, e você pode pedir para sair quando quiser.",
        "opcoes": [
            {"v": True,  "t": "Sim, quero receber", "sub": "Dicas de saúde, alimentação e bem-estar animal"},
            {"v": False, "t": "Não, obrigado",      "sub": "Participo da pesquisa sem receber conteúdo"},
        ],
        "erro": "Escolha uma das duas opções.",
    }
    if contato_opcional:
        dicas["exigeCampo"] = "contato"

    return [
        {
            "tipo": "texto", "campo": "nome", "curta": True,
            "titulo": "Como podemos te chamar?",
            "apoio": "Pode ser só o primeiro nome.",
            "placeholder": "Seu nome",
            "erro": "Escreva seu nome para continuar.",
        },
        contato,
        dicas,
        {
            "tipo": "consent", "campo": "consentimento", "curta": True,
            "titulo": "Autorização de uso dos dados",
            "termo": TERMO,
            "rotulo": "Li e autorizo o uso dos meus dados nos termos acima.",
            "erro": "Marque a autorização para enviar.",
        },
    ]


# ---------------------------------------------------------------------------
# Situações de segurança de alimentos (canal rua)
# ---------------------------------------------------------------------------
QUIZ_RUA = [
    {
        "tipo": "escolha", "campo": "q1_ovos", "selo": "Situação 1", "tema": "Ovos",
        "titulo": "Você chegou em casa após comprar ovos. O que faria antes de guardá-los?",
        "opcoes": [
            {"v": "a", "t": "Lavaria todos os ovos e depois os colocaria na geladeira"},
            {"v": "b", "t": "Guardaria sem lavar e higienizaria somente antes do uso, quando necessário"},
            {"v": "c", "t": "Deixaria os ovos fora da geladeira até o momento do consumo"},
            {"v": "d", "t": "Não sei qual é a forma mais adequada"},
        ],
        "correta": "b",
        "explicacao": ("A casca tem uma película natural, a cutícula, que barra a entrada de "
                       "microrganismos. Lavar antes de guardar remove essa proteção e a umidade "
                       "ainda ajuda a levar bactérias para dentro dos poros. O certo é guardar "
                       "seco e higienizar só na hora de usar."),
        "erro": "Escolha uma das alternativas.",
    },
    {
        "tipo": "escolha", "campo": "q2_carne", "selo": "Situação 2", "tema": "Carne",
        "titulo": "Você comprou carne para o almoço. Antes de temperá-la, o que faria?",
        "opcoes": [
            {"v": "a", "t": "Lavaria a carne em água corrente para retirar possíveis microrganismos"},
            {"v": "b", "t": "Lavaria com água e vinagre para garantir maior segurança"},
            {"v": "c", "t": "Não lavaria a carne"},
            {"v": "d", "t": "Não sei qual procedimento é recomendado"},
        ],
        "correta": "c",
        "explicacao": ("Lavar carne crua não elimina os microrganismos e ainda espalha respingos "
                       "contaminados pela pia, bancada e utensílios ao redor. Quem garante a "
                       "segurança é o cozimento adequado."),
        "erro": "Escolha uma das alternativas.",
    },
    {
        "tipo": "escolha", "campo": "q3_leite_uht", "selo": "Situação 3", "tema": "Leite UHT",
        "titulo": "“Não compro leite de caixinha porque ele tem conservantes para durar tanto tempo.” O que você acha dessa afirmação?",
        "opcoes": [
            {"v": "a", "t": "É verdadeira: o leite UHT precisa de conservantes para ter maior validade"},
            {"v": "b", "t": "É verdadeira apenas para algumas marcas"},
            {"v": "c", "t": "É falsa: a longa validade vem de um procedimento industrial"},
            {"v": "d", "t": "Não sei"},
        ],
        "correta": "c",
        "explicacao": ("A validade longa vem do tratamento UHT, em que o leite é aquecido a cerca "
                       "de 130 a 150 °C por poucos segundos e envasado em embalagem asséptica. A "
                       "legislação brasileira não permite conservantes no leite UHT."),
        "erro": "Escolha uma das alternativas.",
    },
    {
        "tipo": "escolha", "campo": "q4_queijo_coalho", "selo": "Situação 4", "tema": "Queijo coalho",
        "titulo": "Entre dois queijos coalho, um com pequenos furinhos na massa e outro uniforme, qual você escolheria?",
        "opcoes": [
            {"v": "a", "t": "O com furinhos, porque indica que é mais fresco ou artesanal"},
            {"v": "b", "t": "O sem furinhos, porque parece mais seguro"},
            {"v": "c", "t": "Qualquer um: os furinhos sozinhos não dizem se o queijo está próprio para consumo"},
            {"v": "d", "t": "Não sei o que a presença ou ausência de furinhos significa"},
        ],
        "correta": "c",
        "explicacao": ("Os furinhos, ou olhaduras, podem vir do próprio processo de fabricação ou "
                       "de gases produzidos por bactérias indesejadas. Sozinhos não indicam "
                       "qualidade: o que importa é a procedência, o selo do serviço de inspeção e "
                       "a conservação do produto."),
        "erro": "Escolha uma das alternativas.",
    },
]

# ---------------------------------------------------------------------------
# Bloco de nutrição (canal clínica / petshop)
#
# Cada pergunta foi escolhida para render duas leituras: um dado de prática
# alimentar para o relatório da extensão e uma informação acionável para o
# gestor da clínica que cede o espaço do QR Code.
# ---------------------------------------------------------------------------
QUIZ_CLINICA = [
    {
        # extensão: peso da orientação técnica | gestor: o quanto a indicação do vet decide a compra
        "tipo": "escolha", "campo": "q1_escolha_racao", "selo": "Alimentação 1",
        "titulo": "Na hora de escolher a ração do seu pet, o que mais pesa na decisão?",
        "apoio": "Escolha o principal.",
        "opcoes": [
            {"v": "a", "t": "O preço"},
            {"v": "b", "t": "A indicação do veterinário"},
            {"v": "c", "t": "A indicação do petshop ou de quem vende"},
            {"v": "d", "t": "A marca que já conheço ou que ele aceita bem"},
            {"v": "e", "t": "O que vejo na internet e nas redes sociais"},
        ],
        "erro": "Escolha uma das alternativas.",
    },
    {
        # extensão: risco de super/subalimentação | gestor: abre conversa de consulta nutricional
        "tipo": "escolha", "campo": "q2_medida_racao", "selo": "Alimentação 2",
        "titulo": "Como você mede a quantidade de ração que oferece por dia?",
        "opcoes": [
            {"v": "a", "t": "Uso a medida da embalagem ou a indicada pelo veterinário"},
            {"v": "b", "t": "Peso a porção em balança"},
            {"v": "c", "t": "Encho o pote no olho, quando vejo que acabou"},
            {"v": "d", "t": "Deixo comida à vontade o dia inteiro"},
            {"v": "e", "t": "Não sou eu quem cuida disso"},
        ],
        "erro": "Escolha uma das alternativas.",
    },
    {
        # extensão: prevalência de dieta caseira e petiscos | gestor: risco nutricional da clientela
        "tipo": "escolha", "campo": "q3_complemento", "selo": "Alimentação 3",
        "titulo": "Além da ração, o que seu pet costuma comer?",
        "opcoes": [
            {"v": "a", "t": "Só ração"},
            {"v": "b", "t": "Ração e petiscos industrializados"},
            {"v": "c", "t": "Ração e comida da nossa mesa"},
            {"v": "d", "t": "Alimentação natural preparada para ele"},
            {"v": "e", "t": "Ração e suplementos"},
        ],
        "erro": "Escolha uma das alternativas.",
    },
    {
        # extensão: barreira real ao cuidado | gestor: a objeção que trava a venda e o serviço
        "tipo": "escolha", "campo": "q4_barreira", "selo": "Alimentação 4",
        "titulo": "O que mais te atrapalha hoje a dar a melhor alimentação possível para ele?",
        "opcoes": [
            {"v": "a", "t": "O preço da ração de boa qualidade"},
            {"v": "b", "t": "Não sei qual é a mais adequada para ele"},
            {"v": "c", "t": "Ele é enjoado e recusa"},
            {"v": "d", "t": "Falta de tempo para organizar a alimentação"},
            {"v": "e", "t": "Nada, estou satisfeito com o que ofereço"},
        ],
        "erro": "Escolha uma das alternativas.",
    },
    {
        # extensão: nuvem de dúvidas reais | gestor: pauta de conteúdo e de serviço, nas palavras do tutor
        "tipo": "longo", "campo": "q5_duvida", "selo": "Alimentação 5",
        "titulo": "Se um veterinário pudesse responder uma dúvida sua agora, qual seria?",
        "apoio": "Pode ser sobre alimentação ou qualquer outro cuidado. Escreva do seu jeito.",
        "placeholder": "Escreva aqui a sua dúvida",
        "dica": "Opcional, mas é a resposta que mais ajuda o projeto.",
        "opcional": True,
        "rotuloPular": "Não tenho dúvidas agora",
        "minimo": 3,
    },
]

NOTAS_CLINICA = [
    {
        "tema": "Sobre a quantidade",
        "titulo": "A tabela da embalagem é ponto de partida, não regra fixa",
        "texto": ("A quantidade indicada considera um animal adulto, castrado ou não, com "
                  "atividade média. Porte, idade, castração e rotina mudam a necessidade — "
                  "por isso o ajuste fino é feito pelo veterinário, acompanhando o peso."),
    },
    {
        "tema": "Sobre petiscos",
        "titulo": "Petiscos e sobras contam como calorias do dia",
        "texto": ("A recomendação usual é que petiscos não passem de cerca de 10% das calorias "
                  "diárias. Acima disso, além do excesso de peso, a dieta perde o equilíbrio de "
                  "nutrientes que a ração fornece."),
    },
    {
        "tema": "Sobre comida caseira",
        "titulo": "Alimentação natural precisa de formulação",
        "texto": ("Comida caseira pode ser uma boa opção, mas montada no olho ela costuma faltar "
                  "cálcio e outros nutrientes. Quando bem formulada por um profissional, é "
                  "completa como qualquer outra dieta."),
    },
]

# ---------------------------------------------------------------------------
# Temas
# ---------------------------------------------------------------------------
TEMAS = {
    "rua": {
        "textos": {
            "__TITULO__": "Pesquisa sobre alimentos de origem animal",
            "__THEME_COLOR__": "#e8590c",
            "__G1__": "#ff9a3c", "__G2__": "#f2622e", "__G3__": "#d63e2f",
            "__ACENTO__": "#f2622e", "__ACENTO_ESCURO__": "#b8341f",
            "__TINTA__": "#3d1a0d", "__TINTA_SUAVE__": "#9a6a55",
            "__CAMPO__": "rgba(255,255,255,.9)", "__BORDA__": "#e3c4b6",
            "__SELO__": "Pesquisa de extensão universitária",
            "__TITULO_H1__": "Quatro situações do dia a dia na cozinha",
            "__ABERTURA__": ("Estudantes de Medicina Veterinária estão pesquisando o que as pessoas "
                             "sabem sobre alimentos de origem animal. São quatro situações rápidas — "
                             "no final você vê o que a ciência diz sobre cada uma."),
            "__INFO_ABERTURA__": ("Não existe pegadinha e ninguém é identificado no relatório. "
                                  "Responder leva cerca de dois minutos."),
            "__CTA_INICIAL__": "Começar",
            "__NOTA_RODAPE__": "Participação voluntária. Leva cerca de 2 minutos.",
            "__FECHAMENTO__": "Sua participação foi registrada.",
            "__NOTA_FIM__": "Obrigado por colaborar com o projeto.",
            "__TITULO_FIM__": "Tudo certo.",
            "__FECHAMENTO_DINAMICO__": "Sua participação foi registrada na pesquisa.",
            "__NOTA_FIM_SIM__": "Em breve você recebe as primeiras dicas no WhatsApp informado.",
            "__NOTA_FIM_NAO__": "Seus dados entram apenas na apuração da pesquisa, sem envio de conteúdo.",
            "__TABELA__": "pesquisa_respostas_rua",
            "__CANAL__": "rua",
            "__CAMPO_ORIGEM__": "ponto_codigo",
            "__PARAM_ORIGEM__": "ponto",
        },
        "passos": QUIZ_RUA + identificacao("É por onde a gente retorna, se precisar."),
    },
    "clinica": {
        "textos": {
            "__TITULO__": "Pesquisa com tutores — parceria clínica",
            "__THEME_COLOR__": "#0f6b78",
            "__G1__": "#1f7f8c", "__G2__": "#17a3a0", "__G3__": "#46c4a8",
            "__ACENTO__": "#0f7d84", "__ACENTO_ESCURO__": "#0a5b63",
            "__TINTA__": "#0b2f33", "__TINTA_SUAVE__": "#5d8288",
            "__CAMPO__": "rgba(255,255,255,.9)", "__BORDA__": "#c2dcdd",
            "__SELO__": "Pesquisa de extensão universitária",
            "__TITULO_H1__": "Enquanto você espera, participa da pesquisa?",
            "__ABERTURA__": ("Estudantes de Medicina Veterinária estão mapeando como os tutores "
                             "alimentam seus animais. São cinco perguntas rápidas sobre a "
                             "alimentação do seu pet."),
            "__INFO_ABERTURA__": ("Esta pesquisa é acadêmica e independente do atendimento que você "
                                  "recebe aqui. Participar ou não, não altera em nada o seu "
                                  "atendimento, e o WhatsApp é opcional."),
            "__CTA_INICIAL__": "Participar",
            "__NOTA_RODAPE__": "Participação voluntária e anônima no relatório final.",
            "__FECHAMENTO__": "Sua participação foi registrada.",
            "__NOTA_FIM__": "Obrigado por colaborar com o projeto.",
            "__TITULO_FIM__": "Participação registrada.",
            "__FECHAMENTO_DINAMICO__": ("Sua resposta entra na apuração da pesquisa. Abaixo, três "
                                        "pontos sobre alimentação que costumam gerar dúvida."),
            "__NOTA_FIM_SIM__": "Em breve você recebe as primeiras dicas no WhatsApp informado.",
            "__NOTA_FIM_NAO__": "Seus dados entram apenas na apuração da pesquisa, sem envio de conteúdo.",
            "__TABELA__": "pesquisa_respostas_clinica",
            "__CANAL__": "clinica",
            "__CAMPO_ORIGEM__": "local_codigo",
            "__PARAM_ORIGEM__": "local",
        },
        "passos": QUIZ_CLINICA + identificacao(
            "É por onde a gente retorna, se precisar.", contato_opcional=True),
        "notas_finais": NOTAS_CLINICA,
    },
}

SAIDA = {"rua": "questionario-rua.html", "clinica": "questionario-clinica.html"}


def sql_dicionario(temas):
    """Gera o SQL do dicionário de perguntas e alternativas a partir dos PASSOS.

    Assim os rótulos dos gráficos saem do banco e nunca divergem do formulário.
    """
    def txt(s):
        return "'" + s.replace("'", "''") + "'"

    perguntas, opcoes = [], []
    for canal, tema in temas.items():
        ordem = 0
        for p in tema["passos"]:
            if p["tipo"] not in ("escolha", "longo") or not p.get("campo"):
                continue
            if p["campo"] in ("aceita_dicas", "consentimento"):
                continue
            ordem += 1
            perguntas.append(
                f"  ({txt(canal)}, {txt(p['campo'])}, {ordem}, {txt(p['tipo'])}, "
                f"{txt(p.get('selo') or p.get('tema') or '')}, {txt(p['titulo'])}, "
                f"{txt(p.get('correta') or '') if p.get('correta') else 'null'})"
            )
            for k, o in enumerate(p.get("opcoes", []), start=1):
                opcoes.append(
                    f"  ({txt(canal)}, {txt(p['campo'])}, {txt(str(o['v']))}, {k}, {txt(o['t'])})"
                )

    bloco_perguntas = ",\n".join(perguntas)
    bloco_opcoes = ",\n".join(opcoes)

    return f"""-- ============================================================================
-- DICIONARIO DE PERGUNTAS E ALTERNATIVAS
-- ARQUIVO GERADO AUTOMATICAMENTE POR build.py - NAO EDITE A MAO.
-- Altere as perguntas em build.py e rode "python3 build.py" de novo.
--
-- Serve para rotular os graficos: em vez de "b" no eixo, sai o texto da
-- alternativa exatamente como o participante leu na tela.
-- ============================================================================

create table if not exists public.pesquisa_questoes (
  canal     text    not null,
  questao   text    not null,
  ordem     smallint not null,
  tipo      text    not null,
  rotulo    text,
  enunciado text    not null,
  correta   char(1),
  primary key (canal, questao)
);

create table if not exists public.pesquisa_opcoes (
  canal       text     not null,
  questao     text     not null,
  alternativa text     not null,
  ordem       smallint not null,
  rotulo      text     not null,
  primary key (canal, questao, alternativa)
);

insert into public.pesquisa_questoes (canal, questao, ordem, tipo, rotulo, enunciado, correta) values
{bloco_perguntas}
on conflict (canal, questao) do update
  set ordem = excluded.ordem, tipo = excluded.tipo, rotulo = excluded.rotulo,
      enunciado = excluded.enunciado, correta = excluded.correta;

insert into public.pesquisa_opcoes (canal, questao, alternativa, ordem, rotulo) values
{bloco_opcoes}
on conflict (canal, questao, alternativa) do update
  set ordem = excluded.ordem, rotulo = excluded.rotulo;

alter table public.pesquisa_questoes enable row level security;
alter table public.pesquisa_opcoes   enable row level security;
drop policy if exists "anon le questoes" on public.pesquisa_questoes;
drop policy if exists "anon le opcoes"   on public.pesquisa_opcoes;
create policy "anon le questoes" on public.pesquisa_questoes for select to anon using (true);
create policy "anon le opcoes"   on public.pesquisa_opcoes   for select to anon using (true);
"""


def html_notas(notas):
    """Blocos informativos exibidos na tela final (valor devolvido a quem respondeu)."""
    if not notas:
        return ""
    itens = []
    for n in notas:
        itens.append(
            '<div class="item-gab">'
            f'<div class="tema">{n["tema"]}</div>'
            f'<div class="resposta">{n["titulo"]}</div>'
            f'<div class="porque">{n["texto"]}</div>'
            '</div>'
        )
    return "".join(itens)

if __name__ == "__main__":
    base = pathlib.Path(__file__).parent
    for chave, tema in TEMAS.items():
        html = TEMPLATE.replace("__PASSOS_JSON__",
                                json.dumps(tema["passos"], ensure_ascii=False, indent=2))
        html = html.replace("__NOTAS_FINAIS__", html_notas(tema.get("notas_finais")))
        for token, valor in tema["textos"].items():
            html = html.replace(token, valor)
        destino = base / SAIDA[chave]
        destino.write_text(html, encoding="utf-8")
        print(f"gerado: {destino.name}  ({len(tema['passos'])} passos)")

    dic = base / "sql" / "05_dicionario.sql"
    dic.write_text(sql_dicionario(TEMAS), encoding="utf-8")
    print(f"gerado: sql/{dic.name}")

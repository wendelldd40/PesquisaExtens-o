#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Percorre o fluxo dos dois questionarios em viewport mobile e salva screenshots."""

import pathlib
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(__file__).parent
SHOTS = BASE / "screenshots"
SHOTS.mkdir(exist_ok=True)

ARQUIVOS = [
    ("rua", "questionario-rua.html?ponto=orla&por=wendell"),
    ("clinica", "questionario-clinica.html?local=chamego"),
]

erros = []
n = 0


def tira(pg, nome, rotulo):
    global n
    n += 1
    pg.screenshot(path=SHOTS / f"{nome}-{n:02d}-{rotulo}.png")


with sync_playwright() as p:
    nav = p.chromium.launch()
    for nome, arq in ARQUIVOS:
        n = 0
        ctx = nav.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2, is_mobile=True, has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
        )
        pg = ctx.new_page()
        pg.on("pageerror", lambda e, nm=nome: erros.append(f"{nm}: {e}"))
        pg.goto("file://" + str(BASE / arq))
        pg.wait_for_timeout(600)

        passos = pg.evaluate("PASSOS")
        tira(pg, nome, "abertura")
        pg.click("#btnAvancar")
        pg.wait_for_timeout(500)

        for i, passo in enumerate(passos):
            tipo = passo["tipo"]
            atual = pg.evaluate("estado.i")
            if atual != i:
                erros.append(f"{nome}: esperava passo {i}, estava em {atual}")
                break
            if passo.get("exigeCampo") and not pg.evaluate(f"visivel({i})"):
                erros.append(f"{nome}: passo condicional {i} deveria estar visivel aqui")

            if tipo == "escolha":
                # valida o bloqueio na primeira tela de escolha
                if i == 0:
                    pg.click("#btnAvancar")
                    pg.wait_for_timeout(350)
                    if not pg.is_visible(f"#aviso-{i}.on"):
                        erros.append(f"{nome}: avancou sem responder o passo {i}")
                tira(pg, nome, passo["campo"])
                alvo = passo.get("correta") or str(passo["opcoes"][0]["v"]).lower()
                pg.click(f'.tela[data-i="{i}"] .opcao[data-v="{alvo}"]')
                pg.wait_for_timeout(700)          # auto-avanca
                continue

            if tipo in ("texto", "longo"):
                if tipo == "longo":
                    if pg.inner_text("#txtBtn") != passo.get("rotuloPular", ""):
                        erros.append(f"{nome}: botao nao ofereceu pular no passo opcional {i}")
                    tira(pg, nome, passo["campo"] + "-vazio")
                    pg.fill(f"#campo-{i}", "Posso dar osso de frango cozido para o meu cachorro?")
                    pg.wait_for_timeout(250)
                    if pg.inner_text("#txtBtn") == passo.get("rotuloPular", ""):
                        erros.append(f"{nome}: botao continuou como pular apos digitar no passo {i}")
                else:
                    pg.fill(f"#campo-{i}", "Wendell")
                pg.wait_for_timeout(200)
                tira(pg, nome, passo["campo"])

            if tipo == "tel":
                pg.type(f"#campo-{i}", "79998877665", delay=10)
                pg.wait_for_timeout(250)
                tel = pg.input_value(f"#campo-{i}")
                if tel != "(79) 99887-7665":
                    erros.append(f"{nome}: mascara de telefone gerou '{tel}'")
                tira(pg, nome, passo["campo"])

            if tipo == "consent":
                pg.click("#btnAvancar")          # tenta enviar sem aceitar
                pg.wait_for_timeout(400)
                if not pg.is_visible(f"#aviso-{i}.on"):
                    erros.append(f"{nome}: envio sem consentimento nao foi bloqueado")
                tira(pg, nome, "consentimento-bloqueado")
                pg.click(f"#aceite-{i}")
                pg.wait_for_timeout(300)
                tira(pg, nome, "consentimento")

            pg.click("#btnAvancar")
            pg.wait_for_timeout(600)

        pg.wait_for_timeout(700)
        if not pg.is_visible("#telaFim"):
            erros.append(f"{nome}: tela final nao apareceu")
        tira(pg, nome, "final")

        tem_quiz = any(p.get("correta") for p in passos)
        if tem_quiz:
            if pg.is_hidden("#btnGabarito"):
                erros.append(f"{nome}: botao do gabarito nao apareceu")
            else:
                rotulo = pg.inner_text("#btnGabarito")
                if "4 de 4" not in rotulo:
                    erros.append(f"{nome}: contagem de acertos errada -> '{rotulo}'")
                pg.click("#btnGabarito")
                pg.wait_for_timeout(500)
                tira(pg, nome, "gabarito")
                itens = pg.locator(".item-gab").count()
                if itens != 4:
                    erros.append(f"{nome}: gabarito com {itens} itens, esperado 4")
        elif not pg.is_hidden("#btnGabarito"):
            erros.append(f"{nome}: gabarito apareceu num questionario sem quiz")

        # sem rede no teste local, o envio cai na fila offline — que e justamente
        # o caminho que precisa continuar mostrando o gabarito
        fila = pg.evaluate("localStorage.getItem('fila_pesquisa_' + CONFIG.CANAL)")
        if not fila or "Wendell" not in fila:
            erros.append(f"{nome}: fila local nao guardou a resposta (modo demo)")
        else:
            import json
            reg = json.loads(fila)[0]
            faltando = [p["campo"] for p in passos if p.get("campo") and p["campo"] not in reg]
            if faltando:
                erros.append(f"{nome}: registro sem os campos {faltando}")

        # --- caminho alternativo: quem nao deixa WhatsApp pula o opt-in ---
        if any(p.get("opcional") and p["tipo"] == "tel" for p in passos):
            pg2 = ctx.new_page()
            pg2.on("pageerror", lambda e, nm=nome: erros.append(f"{nm} (sem contato): {e}"))
            pg2.goto("file://" + str(BASE / arq))
            pg2.wait_for_timeout(500)
            pg2.click("#btnAvancar")
            pg2.wait_for_timeout(400)
            for i, passo in enumerate(passos):
                if not pg2.evaluate(f"visivel({i})"):
                    if pg2.evaluate("estado.i") == i:
                        erros.append(f"{nome}: parou num passo que deveria ter sido pulado ({i})")
                    continue
                t = passo["tipo"]
                if t == "escolha":
                    pg2.click(f'.tela[data-i="{i}"] .opcao:first-child')
                    pg2.wait_for_timeout(600)
                    continue
                if t == "texto":
                    pg2.fill(f"#campo-{i}", "Maria")
                if t == "consent":
                    pg2.click(f"#aceite-{i}")
                    pg2.wait_for_timeout(200)
                # tel e longo ficam em branco de proposito
                if t == "tel":
                    tira(pg2, nome, "whatsapp-opcional")
                pg2.click("#btnAvancar")
                pg2.wait_for_timeout(500)
            pg2.wait_for_timeout(600)
            if not pg2.is_visible("#telaFim"):
                erros.append(f"{nome}: fluxo sem contato nao chegou ao final")
            tira(pg2, nome, "final-sem-contato")
            import json as _j
            fila2 = _j.loads(pg2.evaluate("localStorage.getItem('fila_pesquisa_' + CONFIG.CANAL)"))
            reg2 = fila2[-1]
            if reg2.get("contato") is not None:
                erros.append(f"{nome}: contato deveria ser nulo, veio {reg2.get('contato')!r}")
            if reg2.get("aceita_dicas") is not None:
                erros.append(f"{nome}: aceita_dicas deveria ser nulo sem contato")
            if reg2.get("q5_duvida") is not None:
                erros.append(f"{nome}: pergunta aberta pulada deveria gravar nulo")
            pg2.close()

        ctx.close()
    nav.close()

print("ERROS:" if erros else "Tudo ok - fluxo, validacoes, gabarito e gravacao conferidos.")
for e in erros:
    print(" -", e)

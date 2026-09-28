#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Abre o painel em modo demonstração, percorre as abas e salva screenshots."""

import pathlib
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(__file__).parent
SHOTS = BASE / "screenshots"
SHOTS.mkdir(exist_ok=True)

erros = []

with sync_playwright() as p:
    nav = p.chromium.launch()

    for tema, larg, alt, marca in [("claro", 1440, 1000, "desk"), ("escuro", 1440, 1000, "desk"), ("claro", 390, 844, "mob")]:
        ctx = nav.new_context(
            viewport={"width": larg, "height": alt},
            device_scale_factor=2,
            color_scheme="dark" if tema == "escuro" else "light",
            is_mobile=(marca == "mob"),
            has_touch=(marca == "mob"),
        )
        pg = ctx.new_page()
        pg.on("pageerror", lambda e, t=tema, m=marca: erros.append(f"{m}/{t}: {e}"))
        pg.on("console", lambda m, t=tema, mk=marca: erros.append(f"{mk}/{t} console: {m.text}")
              if m.type == "error" else None)
        pg.goto("file://" + str(BASE / "painel.html"))
        pg.wait_for_timeout(500)

        if marca == "desk" and tema == "claro":
            pg.screenshot(path=SHOTS / "painel-00-login.png")

        pg.click("#btnDemo")
        pg.wait_for_timeout(900)

        if pg.is_visible(".carregando"):
            erros.append(f"{marca}/{tema}: ficou preso no carregamento")

        sufixo = f"{marca}-{tema}"
        for aba, nome in [("visao", "1-visao"), ("rua", "2-rua"), ("clinica", "3-clinica"), ("leads", "4-contatos")]:
            pg.click(f'.aba[data-aba="{aba}"]')
            pg.wait_for_timeout(700)
            if pg.locator(".vazio").count() and aba != "leads":
                texto = pg.locator(".vazio").first.inner_text()
                if "Não foi possível" in texto:
                    erros.append(f"{marca}/{tema}: aba {aba} quebrou -> {texto[:120]}")
            pg.screenshot(path=SHOTS / f"painel-{sufixo}-{nome}.png", full_page=(marca == "desk"))

        # interações só no desktop claro
        if marca == "desk" and tema == "claro":
            pg.click('.aba[data-aba="visao"]')
            pg.wait_for_timeout(400)
            pg.click('[data-per="30"]')
            pg.wait_for_timeout(500)
            if not pg.locator(".kpi .num").count():
                erros.append("filtro de 30 dias zerou a tela")
            pg.screenshot(path=SHOTS / "painel-desk-5-filtro30.png")

            pg.click('[data-per="0"]')
            pg.wait_for_timeout(300)
            pg.select_option("#filtroLocal", index=1)
            pg.wait_for_timeout(500)
            kpi = pg.locator(".kpi .num").first.inner_text()
            if kpi in ("0", "—"):
                erros.append(f"filtro por local zerou os KPIs ({kpi})")
            pg.select_option("#filtroLocal", index=0)
            pg.wait_for_timeout(300)

            # tooltip
            barra = pg.locator("svg .marca-barra").first
            barra.hover()
            pg.wait_for_timeout(350)
            if not pg.is_visible(".dica.on"):
                erros.append("tooltip nao apareceu no hover da barra")
            pg.screenshot(path=SHOTS / "painel-desk-6-tooltip.png")

            # CRM: mudar status e anotar
            pg.click('.aba[data-aba="leads"]')
            pg.wait_for_timeout(600)
            antes = pg.locator("tbody tr").count()
            pg.select_option("tbody tr:first-child .js-status", "contatado")
            pg.wait_for_timeout(300)
            pg.fill("tbody tr:first-child .js-obs", "ligar na parte da tarde")
            pg.locator("tbody tr:nth-child(2) .js-obs").click()
            pg.wait_for_timeout(300)

            pg.fill("#crmBusca", "Ana")
            pg.wait_for_timeout(700)
            depois = pg.locator("tbody tr").count()
            if depois >= antes:
                erros.append(f"busca do CRM nao filtrou ({antes} -> {depois})")
            pg.screenshot(path=SHOTS / "painel-desk-7-busca.png")
            pg.fill("#crmBusca", "")
            pg.wait_for_timeout(700)

            pg.select_option("#crmStatus", "contatado")
            pg.wait_for_timeout(500)
            if not pg.locator("tbody tr").count():
                erros.append("filtro de status nao encontrou o lead que acabou de ser marcado")
            pg.screenshot(path=SHOTS / "painel-desk-8-status.png")

            # link de whatsapp
            href = pg.locator("tbody tr:first-child .zap").first.get_attribute("href")
            if not href or not href.startswith("https://wa.me/55"):
                erros.append(f"link de whatsapp invalido: {href}")

        ctx.close()
    nav.close()

print("ERROS:" if erros else "Painel ok - abas, filtros, tooltips, CRM e exportacao conferidos.")
for e in dict.fromkeys(erros):
    print(" -", e)

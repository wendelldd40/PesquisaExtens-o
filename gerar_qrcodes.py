#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera os QR Codes dos locais parceiros e dos pontos de coleta.

Uso:  python3 gerar_qrcodes.py https://seu-dominio
Requer: pip install qrcode pillow
"""

import sys
import pathlib

try:
    import qrcode
except ImportError:
    sys.exit("Instale a dependência primeiro:  pip install qrcode pillow")

# Edite estas listas com os códigos que você cadastrou no Supabase (03_seed_exemplo.sql)
LOCAIS = ["chamego", "petshop01", "clinica02"]
PONTOS = ["campus", "feira-centro", "orla"]

base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://SEU-DOMINIO"
saida = pathlib.Path(__file__).parent / "qrcodes"
saida.mkdir(exist_ok=True)


def gerar(url, nome):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=14, border=3)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    destino = saida / f"{nome}.png"
    img.save(destino)
    print(f"{destino.name:28s} -> {url}")


for codigo in LOCAIS:
    gerar(f"{base}/questionario-clinica.html?local={codigo}", f"clinica-{codigo}")

for codigo in PONTOS:
    gerar(f"{base}/questionario-rua.html?ponto={codigo}", f"rua-{codigo}")

print(f"\n{len(LOCAIS) + len(PONTOS)} QR Codes em {saida}")

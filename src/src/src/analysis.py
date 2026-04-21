"""
analysis.py
Análise Exploratória + Visualizações
Projeto: Pré-diagnóstico de Eficiência Energética – Indústria de Laticínios
Autor: Alexsander Silva | github.com/alexsandersilva
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sqlite3
import os

DB_PATH   = "data/processed/energia_laticinio.db"
OUT_PATH  = "outputs/"
os.makedirs(OUT_PATH, exist_ok=True)

AZUL     = "#1F4E79"
VERMELHO = "#C00000"
CINZA    = "#7F7F7F"
AMARELO  = "#FFC000"
VERDE    = "#375623"

def load_db():
    conn = sqlite3.connect(DB_PATH)
    fato  = pd.read_sql("SELECT * FROM fato_mensal",      conn)
    prod  = pd.read_sql("SELECT * FROM producao_produto", conn)
    mot   = pd.read_sql("SELECT * FROM resumo_motores",   conn)
    ar    = pd.read_sql("SELECT * FROM ar_comprimido",    conn)
    conn.close()
    return fato, prod, mot, ar

# ──────────────────────────────────────────────────────
# GRÁFICO 1 — Consumo de Energia vs Produção vs Temperatura
# ──────────────────────────────────────────────────────
def plot_energia_producao_temp(fato):
    fig, ax1 = plt.subplots(figsize=(13, 5))
    x = range(len(fato))

    ax1.plot(x, fato["consumo_kwh"] / 1e6, color=VERMELHO, lw=2.5, marker="o", ms=5, label="Consumo energia (GWh)")
    ax1.set_ylabel("Consumo (GWh)", color=VERMELHO, fontsize=10)
    ax1.tick_params(axis="y", labelcolor=VERMELHO)

    ax2 = ax1.twinx()
    ax2.bar(x, fato["producao_total_kg"] / 1e6, alpha=0.25, color=AZUL, label="Produção (mil t)")
    ax2.set_ylabel("Produção (mil toneladas)", color=AZUL, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=AZUL)

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(x, fato["temp_media_c"], color=CINZA, lw=1.5, ls="--", marker="s", ms=4, label="Temp. média (°C)")
    ax3.set_ylabel("Temperatura (°C)", color=CINZA, fontsize=10)
    ax3.tick_params(axis="y", labelcolor=CINZA)

    # Anotação da anomalia
    ax1.axvline(x=3, color=AMARELO, lw=2, ls="--", alpha=0.8)
    ax1.annotate("⚠ Anomalia\n+23% consumo", xy=(3, fato["consumo_kwh"].max()/1e6 * 0.85),
                 fontsize=8, color=AMARELO,
                 bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.6))

    ax1.set_xticks(x)
    ax1.set_xticklabels(fato["mes_label"], rotation=45, ha="right", fontsize=8)
    ax1.set_title("Consumo de Energia × Produção × Temperatura Regional\n(Linha de base: Jul/2020 – Jun/2021)",
                  fontsize=11, fontweight="bold", pad=12)

    patches = [
        mpatches.Patch(color=VERMELHO, label="Consumo energia (GWh)"),
        mpatches.Patch(color=AZUL,     label="Produção (mil t)"),
        mpatches.Patch(color=CINZA,    label="Temp. média (°C)"),
    ]
    ax1.legend(handles=patches, loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}01_energia_producao_temperatura.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 1 salvo")

# ──────────────────────────────────────────────────────
# GRÁFICO 2 — W/kg: padrão ideal vs consumo real
# ──────────────────────────────────────────────────────
def plot_watt_por_kg(fato):
    fig, ax = plt.subplots(figsize=(13, 5))
    x  = range(len(fato))
    wk = fato["watt_por_kg"].values

    # Linha real
    ax.plot(x, wk, color=VERMELHO, lw=2.5, marker="D", ms=6, label="W/kg real")

    # Linha ideal (427 W/kg)
    ax.axhline(y=427, color=VERDE, lw=2, ls="--", label="Padrão ideal: 427 W/kg")

    # Zona de alerta
    ax.fill_between(x, 427, wk, where=[w > 427 for w in wk],
                    alpha=0.15, color=VERMELHO, label="Excedente energético")

    # R²
    from numpy.polynomial import polynomial as P
    coef = P.polyfit(list(x), wk, 1)
    tendencia = [coef[0] + coef[1]*xi for xi in x]
    ax.plot(x, tendencia, color=CINZA, lw=1.5, ls=":", label=f"Tendência (R²={fato['r2_global'].iloc[0]})")

    ax.set_xticks(x)
    ax.set_xticklabels(fato["mes_label"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Watts por kg produzido", fontsize=10)
    ax.set_title("Eficiência Energética: W/kg Produzido\nR² global abaixo de 0,75 → sem padrão de consumo identificado",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    economia_potencial = sum([(w - 427) if w > 427 else 0 for w in wk])
    ax.annotate(f"Diferença acumulada:\n~27% de excedente energético",
                xy=(8, max(wk) * 0.92), fontsize=8.5,
                bbox=dict(boxstyle="round", fc=AMARELO, alpha=0.8))

    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}02_watt_por_kg_produzido.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 2 salvo")

# ──────────────────────────────────────────────────────
# GRÁFICO 3 — Mix de produção por produto
# ──────────────────────────────────────────────────────
def plot_mix_producao(prod):
    total_produto = prod.groupby("produto")["volume_kg"].sum()
    pct = (total_produto / total_produto.sum() * 100).sort_values(ascending=False)

    cores = [AZUL, VERMELHO, CINZA, AMARELO, VERDE, "#9E4E7B"]
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        pct.values, labels=pct.index, autopct="%1.1f%%",
        colors=cores, startangle=140,
        textprops={"fontsize": 9}
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")

    ax.set_title("Mix de Produção por Produto\n(Jul/2020 – Jun/2021)",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}03_mix_producao.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 3 salvo")

# ──────────────────────────────────────────────────────
# GRÁFICO 4 — Inventário de motores por sistema
# ──────────────────────────────────────────────────────
def plot_motores(mot):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Quantidade por faixa
    pivot_qtd = mot.pivot_table(index="sistema", columns="faixa_potencia", values="qtd_motores", fill_value=0)
    pivot_qtd.plot(kind="bar", ax=axes[0], color=[CINZA, AZUL, VERMELHO], edgecolor="white")
    axes[0].set_title("Quantidade de Motores por Sistema e Faixa", fontsize=10, fontweight="bold")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Qtd motores")
    axes[0].tick_params(axis="x", rotation=20)
    axes[0].legend(title="Faixa CV", fontsize=8)

    # Potência instalada por sistema
    pot_sistema = mot.groupby("sistema")["potencia_total_kw"].sum()
    axes[1].barh(pot_sistema.index, pot_sistema.values, color=[AZUL, VERMELHO, VERDE])
    for i, v in enumerate(pot_sistema.values):
        axes[1].text(v + 20, i, f"{v:.0f} kW", va="center", fontsize=9)
    axes[1].set_title("Potência Instalada Total por Sistema (kW)", fontsize=10, fontweight="bold")
    axes[1].set_xlabel("kW")

    plt.suptitle("Inventário: 112 Motores — Sistemas de Bombeamento Industrial",
                 fontsize=11, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}04_inventario_motores.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 4 salvo")

# ──────────────────────────────────────────────────────
# GRÁFICO 5 — Fator de potência e multas acumuladas
# ──────────────────────────────────────────────────────
def plot_fator_potencia(fato):
    fig, ax1 = plt.subplots(figsize=(13, 5))
    x = range(len(fato))

    ax1.bar(x, fato["multa_energia_reativa_r$"], color=VERMELHO, alpha=0.6, label="Multa mensal (R$)")
    ax1.set_ylabel("Multa mensal (R$)", color=VERMELHO, fontsize=10)
    ax1.tick_params(axis="y", labelcolor=VERMELHO)

    ax2 = ax1.twinx()
    ax2.plot(x, fato["fator_potencia"], color=AZUL, lw=2.5, marker="o", ms=5, label="Fator de potência")
    ax2.axhline(y=0.92, color=VERDE, lw=2, ls="--", label="Limite sem multa: 0,92")
    ax2.set_ylabel("Fator de Potência", color=AZUL, fontsize=10)
    ax2.set_ylim(0.75, 1.0)
    ax2.tick_params(axis="y", labelcolor=AZUL)

    total_multas = fato["multa_energia_reativa_r$"].sum()
    ax1.annotate(f"Total de multas:\nR$ {total_multas:,.2f}",
                 xy=(5, fato["multa_energia_reativa_r$"].max() * 0.85),
                 fontsize=9, bbox=dict(boxstyle="round", fc=AMARELO, alpha=0.9))

    ax1.set_xticks(x)
    ax1.set_xticklabels(fato["mes_label"], rotation=45, ha="right", fontsize=8)
    ax1.set_title("Fator de Potência e Multas por Energia Reativa\n(Média fp=0,83 — limite sem multa: 0,92)",
                  fontsize=11, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}05_fator_potencia_multas.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 5 salvo")

# ──────────────────────────────────────────────────────
# GRÁFICO 6 — Ar comprimido: desperdício
# ──────────────────────────────────────────────────────
def plot_ar_comprimido(ar):
    por_mes = ar.groupby("mes").agg(
        pressao_media=("pressao_kgf_cm2","mean"),
        pct_iogurte_ativo=("setor_iogurte_ativo","mean")
    ).reset_index()
    por_mes["pct_desperdicio"] = (1 - por_mes["pct_iogurte_ativo"]) * 100

    fig, ax1 = plt.subplots(figsize=(13, 4))
    x = range(len(por_mes))
    ax1.bar(x, por_mes["pct_desperdicio"], color=AMARELO, alpha=0.7, label="% tempo sem consumo")
    ax1.set_ylabel("% tempo pressão mantida sem demanda", fontsize=9)
    ax1.set_ylim(0, 80)

    ax2 = ax1.twinx()
    ax2.plot(x, por_mes["pressao_media"], color=AZUL, lw=2, marker="o", ms=5, label="Pressão média (kgf/cm²)")
    ax2.set_ylabel("Pressão (kgf/cm²)", color=AZUL, fontsize=9)
    ax2.set_ylim(8, 10)
    ax2.tick_params(axis="y", labelcolor=AZUL)

    rotulos = pd.to_datetime(por_mes["mes"]).dt.strftime("%b/%y")
    ax1.set_xticks(x)
    ax1.set_xticklabels(rotulos, rotation=45, ha="right", fontsize=8)
    ax1.set_title("Ar Comprimido: Pressão Mantida vs Demanda Real do Setor de Iogurte\n"
                  "(Razão elétrica/pneumática ≈ 7:1 — desperdício operacional identificado)",
                  fontsize=10, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}06_ar_comprimido_desperdicio.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 6 salvo")

# ──────────────────────────────────────────────────────
# RESUMO EXECUTIVO — KPIs
# ──────────────────────────────────────────────────────
def print_kpis(fato):
    print("\n" + "═"*55)
    print("  RESUMO EXECUTIVO — KPIs DO PROJETO")
    print("═"*55)
    print(f"  Consumo médio total (linha de base): {fato['consumo_kwh'].mean()/1e3:.1f} GWh/mês")
    print(f"  Média W/kg produzido (período):      {fato['watt_por_kg'].mean():.0f} W/kg")
    print(f"  Padrão ideal identificado:           427 W/kg")
    print(f"  Excedente energético estimado:       27%")
    print(f"  Economia potencial (conservadora):   7%")
    print(f"  Multas energia reativa (período):    R$ {fato['multa_energia_reativa_r$'].sum():,.2f}")
    print(f"  Perda financeira total estimada:     R$ 370.084,01")
    print(f"  R² global Energia × Produção:        {fato['r2_global'].iloc[0]} (ref. mín. 0,75)")
    print("═"*55)

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    fato, prod, mot, ar = load_db()
    plot_energia_producao_temp(fato)
    plot_watt_por_kg(fato)
    plot_mix_producao(prod)
    plot_motores(mot)
    plot_fator_potencia(fato)
    plot_ar_comprimido(ar)
    print_kpis(fato)
    print(f"\n✅ Todos os gráficos salvos em: {OUT_PATH}")

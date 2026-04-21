"""
etl_pipeline.py
Pipeline ETL: Extração → Transformação → Carga
Projeto: Pré-diagnóstico de Eficiência Energética – Indústria de Laticínios
Autor: Alexsander Silva | github.com/alexsandersilva
"""

import pandas as pd
import numpy as np
import os
import sqlite3
from datetime import datetime

DB_PATH = "data/processed/energia_laticinio.db"

# ══════════════════════════════════════════
# EXTRACT
# ══════════════════════════════════════════
def extract():
    print("🔵 [EXTRACT] Carregando arquivos CSV...")
    dfs = {
        "temperatura":  pd.read_csv("data/raw/temperaturas_regionais.csv",    parse_dates=["mes"]),
        "producao":     pd.read_csv("data/raw/producao_mensal.csv",           parse_dates=["mes"]),
        "energia":      pd.read_csv("data/raw/consumo_energia.csv",           parse_dates=["mes"]),
        "motores":      pd.read_csv("data/raw/inventario_motores.csv"),
        "fator_pot":    pd.read_csv("data/raw/fator_potencia.csv",            parse_dates=["mes"]),
        "ar_comprimido":pd.read_csv("data/raw/pressao_ar_comprimido.csv",     parse_dates=["mes"]),
    }
    for nome, df in dfs.items():
        print(f"   ✅ {nome}: {len(df)} registros")
    return dfs

# ══════════════════════════════════════════
# TRANSFORM
# ══════════════════════════════════════════
def transform(dfs):
    print("\n🟡 [TRANSFORM] Aplicando regras de negócio e Data Quality...")

    # ── Produção total mensal
    prod_total = (
        dfs["producao"]
        .groupby("mes")["volume_kg"]
        .sum()
        .reset_index()
        .rename(columns={"volume_kg": "producao_total_kg"})
    )

    # ── Tabela fato principal: energia + produção + temperatura
    fato = (
        dfs["energia"]
        .merge(prod_total, on="mes")
        .merge(dfs["temperatura"], on="mes")
        .merge(dfs["fator_pot"], on="mes")
    )

    # ── KPIs calculados
    fato["watt_por_kg"]          = round(fato["consumo_kwh"] * 1000 / fato["producao_total_kg"], 4)
    fato["mwh_por_grau_c"]       = round(fato["consumo_kwh"] / 1000 / fato["temp_media_c"], 4)
    fato["anomalia_consumo"]     = fato["watt_por_kg"] > 500  # flag: acima do padrão ideal 427 W/kg
    fato["multa_acumulada_r$"]   = fato["multa_energia_reativa_r$"].cumsum().round(2)
    fato["mes_label"]            = fato["mes"].dt.strftime("%b/%y")

    # ── Regressão linear simples para R²
    from numpy.polynomial import polynomial as P
    x = np.arange(len(fato))
    y = fato["watt_por_kg"].values
    _, stats = P.polyfit(x, y, 1, full=True)
    ss_res = stats[0][0] if len(stats[0]) > 0 else np.var(y) * len(y)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2_global = round(1 - ss_res / ss_tot, 4)
    fato["r2_global"] = r2_global
    print(f"   📊 R² global Energia x Produção: {r2_global} (mínimo aceitável: 0.75)")

    # ── Data Quality: verificar nulos
    nulos = fato.isnull().sum().sum()
    print(f"   🔍 Data Quality — valores nulos: {nulos}")

    # ── Produção por produto
    prod_produto = dfs["producao"].copy()
    prod_produto["mes_label"] = prod_produto["mes"].dt.strftime("%b/%y")

    # ── Motores: potência total por sistema
    motores = dfs["motores"].copy()
    motores["potencia_total_kw"] = motores["potencia_kw"]
    resumo_motores = (
        motores.groupby(["sistema", "faixa_potencia"])
        .agg(qtd_motores=("motor_id","count"), potencia_total_kw=("potencia_kw","sum"))
        .reset_index()
    )
    pot_total = motores["potencia_kw"].sum()
    print(f"   ⚙️  Potência instalada total: {pot_total:.1f} kW ({len(motores)} motores)")

    # ── Ar comprimido: % do tempo com setor iogurte inativo mas pressão mantida
    ar = dfs["ar_comprimido"].copy()
    pct_desperdicio = round((~ar["setor_iogurte_ativo"]).mean() * 100, 1)
    print(f"   💨 Ar comprimido: pressão mantida sem consumo em {pct_desperdicio}% do tempo")

    return {
        "fato_mensal":      fato,
        "producao_produto": prod_produto,
        "motores":          motores,
        "resumo_motores":   resumo_motores,
        "ar_comprimido":    ar,
    }

# ══════════════════════════════════════════
# LOAD → SQLite
# ══════════════════════════════════════════
def load(tabelas):
    print(f"\n🟢 [LOAD] Carregando dados em SQLite: {DB_PATH}")
    os.makedirs("data/processed", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    mapa = {
        "fato_mensal":       tabelas["fato_mensal"],
        "producao_produto":  tabelas["producao_produto"],
        "motores":           tabelas["motores"],
        "resumo_motores":    tabelas["resumo_motores"],
        "ar_comprimido":     tabelas["ar_comprimido"],
    }

    for nome, df in mapa.items():
        df_save = df.copy()
        for col in df_save.select_dtypes(include=["datetime64[ns]"]).columns:
            df_save[col] = df_save[col].astype(str)
        df_save.to_sql(nome, conn, if_exists="replace", index=False)
        print(f"   ✅ Tabela '{nome}' — {len(df_save)} registros gravados")

    conn.close()
    print(f"\n✅ Pipeline concluído: {DB_PATH}")

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 55)
    print("  ETL Pipeline — Eficiência Energética Laticínios")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    raw   = extract()
    trans = transform(raw)
    load(trans)

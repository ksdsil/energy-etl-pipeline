"""
generate_data.py
Geração de dados sintéticos baseados em prédiagnóstico de eficiência energética
realizado em indústria de laticínios (dados anonimizados).
Autor: Alexsander Silva | github.com/alexsandersilva
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ─────────────────────────────────────────────
# 1. TEMPERATURAS REGIONAIS (INMET – simuladas)
# ─────────────────────────────────────────────
meses = pd.date_range(start="2020-07-01", periods=12, freq="MS")

temperaturas = [18.2, 18.8, 20.5, 22.1, 24.3, 26.7,
                27.9, 27.4, 26.1, 23.8, 21.2, 19.5]

df_temp = pd.DataFrame({
    "mes": meses,
    "temp_media_c": temperaturas
})
df_temp.to_csv("data/raw/temperaturas_regionais.csv", index=False)
print("✅ temperaturas_regionais.csv gerado")

# ─────────────────────────────────────────────
# 2. VOLUME DE PRODUÇÃO (Jul/2020 – Jun/2021)
# ─────────────────────────────────────────────
# Padrão real do relatório: queda após set/2020, com 10 categorias de produto
producao_total_kg = [
    9200000, 9500000, 10450000, 9800000,   # jul–out/20
    8900000, 8600000, 8400000, 8200000,    # nov/20–fev/21
    8700000, 9100000, 9300000, 9600000     # mar–jun/21
]

# Distribuição por produto (baseada nos % do relatório):
# Leite UHT 34%, Chanty mix 30%, Bebida láctea 25%,
# Bebida láctea sabores 6%, Iogurte grego 4%, outros 1%
dist_produtos = {
    "Leite_UHT":         0.34,
    "Chanty_Mix":        0.30,
    "Bebida_Lactea":     0.25,
    "Bebida_Lactea_Sab": 0.06,
    "Iogurte_Grego":     0.04,
    "Outros":            0.01,
}

rows = []
for i, mes in enumerate(meses):
    total = producao_total_kg[i]
    for produto, pct in dist_produtos.items():
        vol = round(total * pct * np.random.uniform(0.97, 1.03))
        rows.append({"mes": mes, "produto": produto, "volume_kg": vol})

df_prod = pd.DataFrame(rows)
df_prod.to_csv("data/raw/producao_mensal.csv", index=False)
print("✅ producao_mensal.csv gerado")

# ─────────────────────────────────────────────
# 3. CONSUMO DE ENERGIA (kWh/mês)
# ─────────────────────────────────────────────
# Padrão real: média 612 W/kg total; aumento abrupto +23% a partir de set/2020
# Período normal: ~427 W/kg; após anomalia: ~612 W/kg
consumo_kwh = []
for i, total_kg in enumerate(producao_total_kg):
    if i < 3:   # jul–set/20: padrão normal ~427 W/kg
        base_w_por_kg = 427
    else:       # out/20–jun/21: anomalia ~612 W/kg
        base_w_por_kg = 612
    kwh = round((total_kg * base_w_por_kg / 1000) * np.random.uniform(0.98, 1.02))
    consumo_kwh.append(kwh)

df_energia = pd.DataFrame({
    "mes": meses,
    "consumo_kwh": consumo_kwh
})
df_energia.to_csv("data/raw/consumo_energia.csv", index=False)
print("✅ consumo_energia.csv gerado")

# ─────────────────────────────────────────────
# 4. SISTEMAS DE BOMBEAMENTO (112 motores)
# ─────────────────────────────────────────────
sistemas = {
    "Beneficiamento_Estocagem": {"ate_5cv": 9,  "5_a_10cv": 8,  "acima_10cv": 22},
    "Utilidades":               {"ate_5cv": 5,  "5_a_10cv": 16, "acima_10cv": 25},
    "Estocagem_Iogurte":        {"ate_5cv": 5,  "5_a_10cv": 9,  "acima_10cv": 17},
}

motor_rows = []
mid = 1
for sistema, faixas in sistemas.items():
    for faixa, qtd in faixas.items():
        for _ in range(qtd):
            if faixa == "ate_5cv":
                pot_cv = round(np.random.uniform(1.5, 5.0), 1)
            elif faixa == "5_a_10cv":
                pot_cv = round(np.random.uniform(5.1, 10.0), 1)
            else:
                pot_cv = round(np.random.uniform(10.1, 75.0), 1)
            pot_kw = round(pot_cv * 0.7355, 2)
            motor_rows.append({
                "motor_id": f"MTR-{mid:03d}",
                "sistema": sistema,
                "faixa_potencia": faixa,
                "potencia_cv": pot_cv,
                "potencia_kw": pot_kw,
                "uso_continuo": True
            })
            mid += 1

df_motores = pd.DataFrame(motor_rows)
df_motores.to_csv("data/raw/inventario_motores.csv", index=False)
print(f"✅ inventario_motores.csv gerado — {len(df_motores)} motores")

# ─────────────────────────────────────────────
# 5. FATOR DE POTÊNCIA E MULTAS
# ─────────────────────────────────────────────
# Média fp=0.83 (multa abaixo de 0.92) → R$90.966,87 no período
fp_mensal = [0.81, 0.82, 0.83, 0.84, 0.83, 0.82,
             0.83, 0.84, 0.85, 0.83, 0.82, 0.92]  # correção em jun/21

multas = []
for fp in fp_mensal:
    multa = round(90966.87 / 11 * np.random.uniform(0.85, 1.15), 2) if fp < 0.92 else 0.0
    multas.append(multa)

df_fp = pd.DataFrame({
    "mes": meses,
    "fator_potencia": fp_mensal,
    "multa_energia_reativa_r$": multas
})
df_fp.to_csv("data/raw/fator_potencia.csv", index=False)
print("✅ fator_potencia.csv gerado")

# ─────────────────────────────────────────────
# 6. AR COMPRIMIDO – PRESSÃO DO VASO PRINCIPAL
# ─────────────────────────────────────────────
# Pressão mantida entre 8.5 e 9.0 kgf/cm² (mesmo sem consumo no setor de iogurte)
pressao_rows = []
for mes in meses:
    for hora in range(0, 24, 2):
        pressao_rows.append({
            "mes": mes,
            "hora": hora,
            "pressao_kgf_cm2": round(np.random.uniform(8.5, 9.0), 2),
            "setor_iogurte_ativo": bool(np.random.choice([True, False], p=[0.6, 0.4]))
        })

df_pressao = pd.DataFrame(pressao_rows)
df_pressao.to_csv("data/raw/pressao_ar_comprimido.csv", index=False)
print("✅ pressao_ar_comprimido.csv gerado")

print("\n✅ Todos os datasets gerados em data/raw/")

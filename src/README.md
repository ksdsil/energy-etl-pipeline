# ⚡ Energy Efficiency ETL Pipeline
### Pré-diagnóstico de Eficiência Energética — Indústria de Laticínios

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-ETL-green?logo=pandas)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Viz-orange)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

---

## 📌 Sobre o Projeto

Este projeto converte um **laudo técnico analógico de eficiência energética** — originalmente coletado em campo com prancheta e medições manuais — em um **pipeline de dados completo**, com dataset estruturado, banco de dados relacional, análises estatísticas e visualizações profissionais.

O estudo foi conduzido em uma **indústria de laticínios de grande porte** (dados anonimizados) durante uma semana de incursão técnica, seguindo o protocolo **IPMVP** *(International Performance Measurement and Verification Protocol)* — norma internacional de medição e verificação em eficiência energética.

> **Contexto real:** O relatório original identificou um excedente de consumo energético de **27%** sem justificativa produtiva, e uma perda financeira estimada de **R$ 370.084,01** no período analisado.

---

## 🎯 Objetivos Técnicos

- Estruturar dados de campo em datasets tabulares e banco relacional
- Implementar pipeline ETL com validação de **Data Quality**
- Calcular KPIs de eficiência energética (W/kg, R², fator de potência)
- Identificar anomalias de consumo via análise estatística
- Gerar visualizações que apoiem tomada de decisão gerencial

---

## 🗂️ Estrutura do Repositório

```
energy-etl-pipeline/
│
├── data/
│   ├── raw/                         # Datasets sintéticos (baseados em dados reais anonimizados)
│   │   ├── temperaturas_regionais.csv
│   │   ├── producao_mensal.csv
│   │   ├── consumo_energia.csv
│   │   ├── inventario_motores.csv
│   │   ├── fator_potencia.csv
│   │   └── pressao_ar_comprimido.csv
│   └── processed/
│       └── energia_laticinio.db     # SQLite com 5 tabelas carregadas pelo ETL
│
├── src/
│   ├── generate_data.py             # Geração dos datasets sintéticos
│   ├── etl_pipeline.py              # Pipeline ETL completo (Extract → Transform → Load)
│   └── analysis.py                  # Análise exploratória + 6 visualizações
│
├── outputs/                         # Gráficos gerados automaticamente
│   ├── 01_energia_producao_temperatura.png
│   ├── 02_watt_por_kg_produzido.png
│   ├── 03_mix_producao.png
│   ├── 04_inventario_motores.png
│   ├── 05_fator_potencia_multas.png
│   └── 06_ar_comprimido_desperdicio.png
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Manipulação de dados | Pandas, NumPy |
| Banco de dados | SQLite (via Python sqlite3) |
| Visualização | Matplotlib |
| Estatística | Regressão linear, R², análise de padrões |
| Protocolo de referência | IPMVP / ISO 50001 |
| Versionamento | Git + GitHub |

---

## 📊 KPIs do Projeto (Resultados Reais)

| Indicador | Valor |
|---|---|
| Consumo médio mensal (linha de base) | ~5.100 GWh/mês |
| Média W/kg produzido (período total) | 566 W/kg |
| Padrão ideal identificado (período normal) | **427 W/kg** |
| Excedente energético detectado | **27%** |
| Economia potencial conservadora | **7%** |
| R² global Energia × Produção | 0,54 *(abaixo do mínimo 0,75)* |
| Multas por energia reativa no período | R$ ~90.966,87 |
| **Perda financeira total estimada** | **R$ 370.084,01** |
| Total de motores inventariados | 112 motores / 2.295 kW instalados |

---

## 📈 Visualizações Geradas

### 1. Consumo × Produção × Temperatura
Identifica o **ponto de anomalia** (set/2020) onde o consumo sobe 23% sem aumento de produção correspondente.

### 2. W/kg Produzido — Padrão Ideal vs Real
Demonstra o desvio do padrão de consumo eficiente (427 W/kg) e o R² abaixo do aceitável.

### 3. Mix de Produção por Produto
Leite UHT (34%), Chanty Mix (30%) e Bebida Láctea (25%) respondem por 89% da produção.

### 4. Inventário de Motores
112 motores distribuídos em 3 sistemas — 64 deles com potência acima de 10 CV (candidatos a retrofit).

### 5. Fator de Potência e Multas
Média de 0,83 (limite sem multa: 0,92) gerando R$ ~90.966,87 em penalidades evitáveis.

### 6. Ar Comprimido — Desperdício Operacional
Pressão mantida entre 8,5–9,0 kgf/cm² em ~41% do tempo sem demanda ativa do setor consumidor.

---

## 🚀 Como Executar

```bash
# 1. Clone o repositório
git clone https://github.com/alexsandersilva/energy-etl-pipeline.git
cd energy-etl-pipeline

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Gere os dados sintéticos
python src/generate_data.py

# 4. Execute o pipeline ETL
python src/etl_pipeline.py

# 5. Gere as análises e visualizações
python src/analysis.py
```

---

## 💡 Principais Aprendizados Técnicos

- **Estruturação de dados industriais**: como converter registros de campo em datasets relacionais
- **Data Quality em pipelines reais**: validação de nulos, consistência e regras de negócio
- **Análise de regressão aplicada**: uso de R² como métrica de aderência ao protocolo IPMVP
- **Detecção de anomalias sem ML**: identificação de padrões de consumo atípico por análise estatística descritiva
- **ETL com carga em banco relacional**: modelagem de 5 tabelas a partir de 6 fontes distintas

---

## 🔍 Contexto do Projeto Original

O estudo técnico original foi conduzido seguindo as diretrizes da norma **ABNT NBR ISO 50001** e do protocolo **IPMVP (EVO — Efficiency Valuation Organization)**, envolvendo:

- Análise de 12 meses de linha de base (jul/2020 – jun/2021)
- Inventário de 112 motores elétricos industriais
- Análise de 3 sistemas energéticos: refrigeração, bombeamento e ar comprimido
- Correlação estatística entre consumo de energia, produção e temperaturas regionais (INMET)
- Identificação de R$ 370.084,01 em perdas financeiras evitáveis

> ⚠️ *Os dados deste repositório são sintéticos, gerados com base na estrutura e proporções do estudo real. Nomes de empresas, locais e valores exatos foram anonimizados por questões de confidencialidade.*

---

## 👤 Autor

**Alexsander Silva**
Analista de Dados | ETL | Python | SQL | Power BI | Databricks

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Alexsander_Silva-blue?logo=linkedin)](https://linkedin.com/in/alexsandersilva)
[![GitHub](https://img.shields.io/badge/GitHub-alexsandersilva-black?logo=github)](https://github.com/alexsandersilva)

---

*Key skills demonstrated: Data Analysis | ETL Pipeline | Data Quality | SQLite | Python | Pandas | Industrial IoT | Energy Efficiency | Statistical Analysis | IPMVP Protocol*

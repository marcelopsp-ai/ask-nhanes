#!/usr/bin/env python3
"""
NHANES Knowledge Base Builder
Gera documentos a partir de: Wikipedia + Papers + CSV + Conceitos

Uso:
    python3 build_nhanes_knowledge_base.py
"""

import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path


class NHANESKnowledgeBaseBuilder:
    """Builder para Knowledge Base sobre NHANES e Estatística"""
    
    def __init__(self, output_dir="data/knowledge_base", csv_path="data/raw/nhanes_2015_2016.csv"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = csv_path
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Research Bot)'
        })
    
    # =========================================================================
    # WIKIPEDIA SCRAPING
    # =========================================================================
    
    def scrape_wikipedia(self, topic, output_name):
        """Scrape artigo da Wikipedia"""
        url = f"https://en.wikipedia.org/wiki/{topic}"
        try:
            print(f"  📄 Wikipedia: {topic}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for tag in soup(['script', 'style', 'sup', 'table', 'img']):
                tag.decompose()
            
            content = soup.find('div', {'id': 'mw-content-text'})
            if not content:
                return False
            
            paragraphs = content.find_all('p')
            text = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            if len(text) > 500:
                output_path = self.output_dir / "wikipedia" / f"{output_name}.txt"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"Source: {url}\n")
                    f.write(f"Topic: {topic.replace('_', ' ')}\n\n")
                    f.write(text[:15000])
                
                print(f"  ✅ Saved: {output_name}.txt ({len(text)} chars)")
                return True
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def scrape_all_wikipedia(self):
        """Scrape todos os artigos relevantes da Wikipedia"""
        print("\n📚 WIKIPEDIA ARTICLES")
        print("=" * 50)
        
        articles = {
            "National_Health_and_Nutrition_Examination_Survey": "nhanes_overview",
            "Body_mass_index": "body_mass_index",
            "Obesity": "obesity",
            "Overweight": "overweight",
            "Linear_regression": "linear_regression",
            "Ordinary_least_squares": "ols_regression",
            "Coefficient_of_determination": "r_squared",
            "Normal_distribution": "normal_distribution",
            "Statistical_hypothesis_testing": "hypothesis_testing",
            "Epidemiology": "epidemiology",
            "Public_health": "public_health",
        }
        
        success = 0
        for topic, name in articles.items():
            if self.scrape_wikipedia(topic, name):
                success += 1
            time.sleep(2)
        
        print(f"\n✅ Wikipedia: {success}/{len(articles)} articles scraped")
        return success
    
    # =========================================================================
    # PAPERS / ACADEMIC SOURCES
    # =========================================================================
    
    def create_paper_summaries(self):
        """Criar resumos de papers acadêmicos sobre NHANES"""
        print("\n📄 ACADEMIC PAPERS")
        print("=" * 50)
        
        papers_dir = self.output_dir / "papers"
        papers_dir.mkdir(parents=True, exist_ok=True)
        
        papers = {
            "nhanes_methodology.txt": """# NHANES Methodology and Design

Source: CDC/NCHS Documentation

## Survey Design

The National Health and Nutrition Examination Survey (NHANES) is a program of studies 
designed to assess the health and nutritional status of adults and children in the 
United States.

### Key Features:
- Cross-sectional survey design
- Nationally representative sample
- Combines interviews and physical examinations
- Conducted by NCHS (National Center for Health Statistics)
- Part of CDC (Centers for Disease Control and Prevention)

## Sampling Strategy

NHANES uses a complex, multistage probability sampling design:

1. **Primary Sampling Units (PSUs)**: Counties or groups of counties
2. **Segments**: Census blocks or combinations
3. **Households**: Dwelling units within segments
4. **Individuals**: Persons within households

### Oversampling
Certain subgroups are oversampled to increase precision:
- Hispanic persons
- Non-Hispanic Black persons
- Non-Hispanic Asian persons
- Older adults (60+ years)
- Low-income white persons

## Data Collection

### Interview Component
- Demographic information
- Socioeconomic status
- Dietary intake (24-hour recall)
- Health-related questions

### Examination Component
- Body measurements (height, weight, waist circumference)
- Blood pressure
- Dental examination
- Laboratory tests (blood, urine)

## Survey Weights

NHANES provides sample weights to:
- Account for unequal probability of selection
- Adjust for nonresponse
- Post-stratify to population totals

**Important**: Always use sample weights for nationally representative estimates!
""",

            "obesity_prevalence_usa.txt": """# Obesity Prevalence in the United States

Source: CDC NCHS Data Briefs + Academic Literature

## Current Statistics (NHANES Data)

### Adult Obesity (Age 20+)
- Overall prevalence: ~42.4%
- Severe obesity (BMI ≥40): ~9.2%
- Trend: Increasing since 1999-2000

### By Sex
- Men: ~43.0%
- Women: ~41.9%

### By Age Group
- 20-39 years: ~40.0%
- 40-59 years: ~44.8% (highest)
- 60+ years: ~42.8%

### By Race/Ethnicity
- Non-Hispanic Black: ~49.6%
- Hispanic: ~44.8%
- Non-Hispanic White: ~42.2%
- Non-Hispanic Asian: ~17.4%

## BMI Classification (WHO)

| Category | BMI Range |
|----------|-----------|
| Underweight | < 18.5 |
| Normal | 18.5 - 24.9 |
| Overweight | 25.0 - 29.9 |
| Obesity Class I | 30.0 - 34.9 |
| Obesity Class II | 35.0 - 39.9 |
| Obesity Class III | ≥ 40.0 |

## Health Consequences

Obesity increases risk for:
- Type 2 diabetes
- Cardiovascular disease
- Hypertension
- Certain cancers
- Sleep apnea
- Osteoarthritis
""",

            "regression_health_studies.txt": """# Regression Analysis in Health Studies

Source: Biostatistics and Epidemiology Literature

## Why Regression in Health Research?

Regression analysis allows researchers to:
- Identify risk factors for diseases
- Quantify relationships between variables
- Control for confounding variables
- Make predictions about health outcomes

## Linear Regression in NHANES

### Common Applications

1. **BMI Prediction**
   - Predictors: Age, sex, diet, physical activity
   - Model: BMI = β₀ + β₁(Age) + β₂(Sex) + ...

2. **Blood Pressure Studies**
   - Predictors: BMI, sodium intake, age, smoking
   - Outcome: Systolic/Diastolic BP

### Key Assumptions

1. **Linearity**: Relationship between X and Y is linear
2. **Independence**: Observations are independent
3. **Normality**: Residuals are normally distributed
4. **Homoscedasticity**: Constant variance of residuals

### Interpreting Results

- R² = Proportion of variance explained
- β = Change in Y for 1-unit change in X
- p < 0.05 = Statistically significant
""",

            "statistical_tests_health.txt": """# Statistical Tests in Health Research

Source: Biostatistics Textbooks

## Choosing the Right Test

### For Comparing Groups

| Comparison | Parametric | Non-Parametric |
|------------|------------|----------------|
| 2 groups (independent) | t-test | Mann-Whitney U |
| 2 groups (paired) | Paired t-test | Wilcoxon signed-rank |
| 3+ groups | ANOVA | Kruskal-Wallis |

### For Relationships

| Variables | Test |
|-----------|------|
| 2 continuous | Pearson correlation |
| 2 continuous (non-normal) | Spearman correlation |
| Continuous + Categorical | t-test / ANOVA |
| 2 categorical | Chi-square |

## Tests Used in NHANES Analysis

### 1. Shapiro-Wilk (Normality)
- H₀: Data is normally distributed
- p > 0.05 → Assume normality

### 2. Independent t-test
- Compares means of 2 groups
- Example: Weight by Sex

### 3. Mann-Whitney U
- Non-parametric alternative to t-test
- Uses ranks instead of raw values

### 4. ANOVA
- Compares means of 3+ groups
- F-statistic = Between/Within variance

### 5. Pearson Correlation
- Measures linear relationship
- r = -1 to +1

### 6. Breusch-Pagan
- Tests homoscedasticity
- p > 0.05 = Constant variance
"""
        }
        
        for filename, content in papers.items():
            filepath = papers_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  ✅ Created: {filename}")
        
        print(f"\n✅ Papers: {len(papers)} documents created")
        return len(papers)
    
    # =========================================================================
    # CONCEITOS ESTATÍSTICOS
    # =========================================================================
    
    def create_concept_docs(self):
        """Criar documentos sobre conceitos estatísticos"""
        print("\n📝 STATISTICAL CONCEPTS")
        print("=" * 50)
        
        concepts_dir = self.output_dir / "conceitos"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        
        concepts = {
            "medidas_tendencia_central.txt": """# Medidas de Tendência Central

Source: Estatística Descritiva

## Definição
Medidas que indicam o "centro" ou valor típico de um conjunto de dados.

## Tipos de Média

### 1. Média Aritmética
- Soma de todos os valores dividida pela quantidade
- Fórmula: x̄ = Σxᵢ / n
- Sensível a outliers

### 2. Média Geométrica
- Raiz n-ésima do produto de n valores
- Sempre menor que aritmética
- Uso: Taxas de crescimento

### 3. Média Harmônica
- Inverso da média dos inversos
- Sempre a menor das três médias
- Uso: Velocidades, taxas

## Mediana
- Valor central quando dados ordenados
- Não afetada por outliers

## Moda
- Valor mais frequente
- Pode não existir ou haver múltiplas

## Comparação Média vs Mediana

| Distribuição | Relação |
|--------------|---------|
| Simétrica | Média ≈ Mediana |
| Assimétrica direita | Média > Mediana |
| Assimétrica esquerda | Média < Mediana |
""",

            "medidas_dispersao.txt": """# Medidas de Dispersão

Source: Estatística Descritiva

## Definição
Medidas que indicam o quanto os dados estão "espalhados".

## Principais Medidas

### 1. Amplitude
- Diferença entre máximo e mínimo
- Muito sensível a outliers

### 2. Variância (σ²)
- Média dos desvios quadráticos
- Amostral: s² = Σ(xᵢ - x̄)² / (n-1)

### 3. Desvio Padrão (σ ou s)
- Raiz quadrada da variância
- Mesma unidade dos dados
- ~68% dentro de ±1σ (normal)
- ~95% dentro de ±2σ (normal)

### 4. Coeficiente de Variação (CV)
- CV = (s / x̄) × 100%
- CV < 15%: Baixa variabilidade
- CV > 30%: Alta variabilidade

### 5. Intervalo Interquartil (IQR)
- IQR = Q3 - Q1
- Contém 50% dos dados centrais
- Robusto a outliers

## Identificação de Outliers

Regra do IQR:
- Limite inferior: Q1 - 1.5 × IQR
- Limite superior: Q3 + 1.5 × IQR
""",

            "pressupostos_regressao.txt": """# Pressupostos da Regressão Linear

Source: Econometria e Bioestatística

## Os 5 Pressupostos

### 1. Linearidade
- Relação entre X e Y é linear
- Verificar: Gráfico de dispersão

### 2. Independência
- Observações são independentes
- Verificar: Durbin-Watson (ideal ≈ 2.0)

### 3. Normalidade
- Resíduos seguem distribuição normal
- Verificar: Shapiro-Wilk, Q-Q Plot

### 4. Homoscedasticidade
- Variância constante dos resíduos
- Verificar: Breusch-Pagan

### 5. Ausência de Multicolinearidade
- Variáveis independentes não correlacionadas
- Verificar: VIF < 5

## Testes Diagnósticos

| Pressuposto | Teste | Bom resultado |
|-------------|-------|---------------|
| Independência | Durbin-Watson | DW ≈ 2.0 |
| Normalidade | Shapiro-Wilk | p > 0.05 |
| Homoscedasticidade | Breusch-Pagan | p > 0.05 |
| Multicolinearidade | VIF | VIF < 5 |
""",

            "interpretacao_regressao.txt": """# Interpretação de Resultados de Regressão

Source: Análise de Dados

## Bloco 1: Performance Geral

### R² (R-squared)
- Proporção da variância explicada
- 0 a 1 (0% a 100%)

### R² Ajustado
- Penaliza adição de variáveis
- Se R² ≈ R² ajustado: OK

### F-statistic
- Testa utilidade do modelo
- p < 0.05: Modelo é útil

## Bloco 2: Coeficientes

### Intercepto (β₀)
- Valor de Y quando todos X = 0

### Coeficientes (βᵢ)
- Mudança em Y para cada 1 unidade em Xᵢ

### P-valor
- p < 0.05: Significativo
- p < 0.001: Altamente significativo

## Bloco 3: Diagnóstico

### Durbin-Watson
- Ideal: ≈ 2.0
- < 1.5 ou > 2.5: Problema

### Omnibus / Jarque-Bera
- p > 0.05: Resíduos normais

### Skew / Kurtosis
- Skew = 0: Simétrico
- Kurtosis = 3: Normal
"""
        }
        
        for filename, content in concepts.items():
            filepath = concepts_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  ✅ Created: {filename}")
        
        print(f"\n✅ Concepts: {len(concepts)} documents created")
        return len(concepts)
    
    # =========================================================================
    # ESTATÍSTICAS DO CSV
    # =========================================================================
    
    def generate_csv_stats(self):
        """Gerar documentos de estatísticas a partir do CSV NHANES"""
        print("\n📊 CSV STATISTICS")
        print("=" * 50)
        
        if not os.path.exists(self.csv_path):
            print(f"  ⚠️  CSV não encontrado: {self.csv_path}")
            print("  ℹ️  Coloque o arquivo nhanes_2015_2016.csv em data/raw/")
            return 0
        
        stats_dir = self.output_dir / "estatisticas"
        stats_dir.mkdir(parents=True, exist_ok=True)
        
        df = pd.read_csv(self.csv_path)
        df = df[df['Idade'] >= 18].copy()
        
        print(f"  📂 Loaded: {len(df):,} records")
        
        docs_created = 0
        
        # 1. Resumo Geral
        resumo = f"""# NHANES 2015-2016 - Resumo do Dataset

Source: data/raw/nhanes_2015_2016.csv

## Informações Gerais
- Total de registros (adultos): {len(df):,}
- Variáveis disponíveis: {len(df.columns)}

## Estatísticas Descritivas

### IMC (Índice de Massa Corporal)
- N: {df['IMC'].notna().sum():,}
- Média: {df['IMC'].mean():.2f}
- Mediana: {df['IMC'].median():.2f}
- Desvio Padrão: {df['IMC'].std():.2f}
- Mínimo: {df['IMC'].min():.2f}
- Máximo: {df['IMC'].max():.2f}

### Peso (kg)
- Média: {df['Peso_kg'].mean():.2f}
- Mediana: {df['Peso_kg'].median():.2f}
- Desvio Padrão: {df['Peso_kg'].std():.2f}

### Altura (cm)
- Média: {df['Altura_cm'].mean():.2f}
- Mediana: {df['Altura_cm'].median():.2f}
- Desvio Padrão: {df['Altura_cm'].std():.2f}
"""
        
        with open(stats_dir / "resumo_geral.txt", 'w', encoding='utf-8') as f:
            f.write(resumo)
        print("  ✅ Created: resumo_geral.txt")
        docs_created += 1
        
        # 2. IMC por Faixa Etária
        df['FaixaEtaria'] = pd.cut(df['Idade'], 
                                    bins=[18, 29, 44, 59, 120],
                                    labels=['18-29', '30-44', '45-59', '60+'])
        
        imc_idade = df.groupby('FaixaEtaria')['IMC'].agg(['count', 'mean', 'median', 'std']).round(2)
        
        imc_doc = f"""# IMC por Faixa Etária - NHANES 2015-2016

Source: data/raw/nhanes_2015_2016.csv

## Estatísticas por Grupo

| Faixa Etária | N | Média | Mediana | DP |
|--------------|---|-------|---------|-----|
"""
        for idx, row in imc_idade.iterrows():
            imc_doc += f"| {idx} | {int(row['count']):,} | {row['mean']:.2f} | {row['median']:.2f} | {row['std']:.2f} |\n"
        
        imc_doc += f"""
## Interpretação

A faixa etária **45-59 anos** apresenta o maior IMC médio, 
classificado como **obesidade** segundo a OMS (IMC ≥ 30).

### Classificação OMS do IMC
- < 18.5: Baixo peso
- 18.5 - 24.9: Normal
- 25.0 - 29.9: Sobrepeso
- ≥ 30.0: Obesidade
"""
        
        with open(stats_dir / "imc_por_idade.txt", 'w', encoding='utf-8') as f:
            f.write(imc_doc)
        print("  ✅ Created: imc_por_idade.txt")
        docs_created += 1
        
        # 3. Peso por Sexo
        sexo_map = {1: 'Masculino', 2: 'Feminino'}
        df['SexoNome'] = df['Sexo'].map(sexo_map)
        peso_sexo = df.groupby('SexoNome')['Peso_kg'].agg(['count', 'mean', 'median', 'std']).round(2)
        
        peso_doc = f"""# Peso por Sexo - NHANES 2015-2016

Source: data/raw/nhanes_2015_2016.csv

## Estatísticas por Sexo

| Sexo | N | Média (kg) | Mediana (kg) | DP |
|------|---|------------|--------------|-----|
"""
        for idx, row in peso_sexo.iterrows():
            peso_doc += f"| {idx} | {int(row['count']):,} | {row['mean']:.2f} | {row['median']:.2f} | {row['std']:.2f} |\n"
        
        with open(stats_dir / "peso_por_sexo.txt", 'w', encoding='utf-8') as f:
            f.write(peso_doc)
        print("  ✅ Created: peso_por_sexo.txt")
        docs_created += 1
        
        # 4. Correlações
        corr_vars = ['Idade', 'Altura_cm', 'Peso_kg', 'IMC']
        corr_matrix = df[corr_vars].corr().round(3)
        
        corr_doc = f"""# Matriz de Correlação - NHANES 2015-2016

Source: data/raw/nhanes_2015_2016.csv

## Correlações de Pearson

|  | Idade | Altura | Peso | IMC |
|--|-------|--------|------|-----|
| Idade | 1.000 | {corr_matrix.loc['Idade', 'Altura_cm']:.3f} | {corr_matrix.loc['Idade', 'Peso_kg']:.3f} | {corr_matrix.loc['Idade', 'IMC']:.3f} |
| Altura | {corr_matrix.loc['Altura_cm', 'Idade']:.3f} | 1.000 | {corr_matrix.loc['Altura_cm', 'Peso_kg']:.3f} | {corr_matrix.loc['Altura_cm', 'IMC']:.3f} |
| Peso | {corr_matrix.loc['Peso_kg', 'Idade']:.3f} | {corr_matrix.loc['Peso_kg', 'Altura_cm']:.3f} | 1.000 | {corr_matrix.loc['Peso_kg', 'IMC']:.3f} |
| IMC | {corr_matrix.loc['IMC', 'Idade']:.3f} | {corr_matrix.loc['IMC', 'Altura_cm']:.3f} | {corr_matrix.loc['IMC', 'Peso_kg']:.3f} | 1.000 |

## Interpretação

### Correlações Fortes (|r| > 0.5)
- **Peso × IMC**: Muito forte (esperado)
- **Altura × Peso**: Moderada a forte

### Classificação de Cohen
- |r| < 0.1: Desprezível
- |r| 0.1 - 0.3: Fraca
- |r| 0.3 - 0.5: Moderada
- |r| > 0.5: Forte
"""
        
        with open(stats_dir / "correlacoes.txt", 'w', encoding='utf-8') as f:
            f.write(corr_doc)
        print("  ✅ Created: correlacoes.txt")
        docs_created += 1
        
        print(f"\n✅ CSV Stats: {docs_created} documents created")
        return docs_created
    
    # =========================================================================
    # RUN ALL
    # =========================================================================
    
    def run_all(self):
        """Executar todo o build da Knowledge Base"""
        print("\n" + "=" * 60)
        print("🚀 BUILDING NHANES KNOWLEDGE BASE")
        print("=" * 60)
        
        total = 0
        
        total += self.scrape_all_wikipedia()
        total += self.create_paper_summaries()
        total += self.create_concept_docs()
        total += self.generate_csv_stats()
        
        print("\n" + "=" * 60)
        print("✅ KNOWLEDGE BASE BUILD COMPLETE!")
        print("=" * 60)
        
        total_files = sum(1 for _ in self.output_dir.rglob('*.txt'))
        
        print(f"📊 Total documents: {total_files}")
        print(f"📁 Location: {self.output_dir}")
        
        print("\n📂 Breakdown:")
        for subdir in self.output_dir.iterdir():
            if subdir.is_dir():
                count = sum(1 for _ in subdir.rglob('*.txt'))
                if count > 0:
                    print(f"   {subdir.name}/: {count} files")
        
        print("=" * 60)
        return total_files


if __name__ == "__main__":
    builder = NHANESKnowledgeBaseBuilder()
    builder.run_all()
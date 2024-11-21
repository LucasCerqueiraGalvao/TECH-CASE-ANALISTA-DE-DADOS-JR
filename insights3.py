import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar os datasets
results = pd.read_csv('datasets\\results.csv')
shootouts = pd.read_csv('datasets\\shootouts.csv')

# 2. Filtrar as partidas em que o Brasil participou (como mandante ou visitante)
df_brasil = results[(results['home_team'] == 'Brazil') | (results['away_team'] == 'Brazil')].copy()

# 3. Ajustar os resultados para disputas de pênaltis
# 3.1 Mesclar o dataset de resultados com o de shootouts
df_merged = pd.merge(df_brasil, shootouts, on=['date', 'home_team', 'away_team'], how='left')

# 3.2 Criar uma função para determinar o resultado final da partida
def get_match_result(row):
    # Verificar se houve disputa de pênaltis
    if pd.notna(row['winner']):
        if row['winner'] == 'Brazil':
            return 'Vitória'
        else:
            return 'Derrota'
    else:
        # Determinar o resultado pelo placar
        if row['home_team'] == 'Brazil':
            if row['home_score'] > row['away_score']:
                return 'Vitória'
            elif row['home_score'] < row['away_score']:
                return 'Derrota'
            else:
                return 'Empate'
        else:
            if row['away_score'] > row['home_score']:
                return 'Vitória'
            elif row['away_score'] < row['home_score']:
                return 'Derrota'
            else:
                return 'Empate'

# 3.3 Aplicar a função para obter o resultado final
df_merged['Resultado'] = df_merged.apply(get_match_result, axis=1)

# 4. Perguntar ao usuário se deseja incluir amistosos
incluir_amistosos = input("Deseja incluir amistosos na análise? (S/N): ").strip().upper()

# 5. Filtrar as partidas com base na escolha do usuário
if incluir_amistosos == 'N':
    df_final = df_merged[df_merged['tournament'] != 'Friendly'].copy()
elif incluir_amistosos == 'S':
    df_final = df_merged.copy()
else:
    print("Opção inválida. Considerando apenas partidas não amistosas por padrão.")
    df_final = df_merged[df_merged['tournament'] != 'Friendly'].copy()

# 6. Perguntar ao usuário se deseja organizar por número absoluto de vitórias ou índice de vitórias
print("\nEscolha o critério para determinar a década mais vitoriosa do Brasil:")
print("1 - Maior número absoluto de vitórias")
print("2 - Maior índice de vitórias")
while True:
    criterio = input("Digite 1 ou 2: ").strip()
    if criterio == '1' or criterio == '2':
        break
    else:
        print("Opção inválida. Por favor, digite 1 ou 2.")

# 7. Converter a coluna 'date' para datetime
df_final['date'] = pd.to_datetime(df_final['date'])

# 8. Criar uma função para formatar a década
def format_decade(year):
    decade_start = (year // 10) * 10
    decade_end = decade_start + 9
    return f"{decade_start} - {decade_end}"

# 9. Aplicar a função para criar a coluna 'Década'
df_final['Década'] = df_final['date'].dt.year.apply(format_decade)

# 10. Agrupar os dados por década
grupos_decadas = df_final.groupby('Década')

# 11. Calcular as estatísticas por década
estatisticas_decadas = grupos_decadas.agg(
    Jogos=('Resultado', 'count'),
    Vitórias=('Resultado', lambda x: (x == 'Vitória').sum())
).reset_index()

# 12. Calcular o índice de vitórias
estatisticas_decadas['Índice de Vitórias'] = estatisticas_decadas['Vitórias'] / estatisticas_decadas['Jogos']

# 13. Organizar os dados de acordo com o critério escolhido
if criterio == '1':
    # Ordenar pelo número absoluto de vitórias
    estatisticas_decadas = estatisticas_decadas.sort_values(by='Vitórias', ascending=False)
else:
    # Ordenar pelo índice de vitórias
    estatisticas_decadas = estatisticas_decadas.sort_values(by='Índice de Vitórias', ascending=False)

# 14. Formatar a coluna 'Índice de Vitórias' como porcentagem
estatisticas_decadas['Índice de Vitórias (%)'] = (estatisticas_decadas['Índice de Vitórias'] * 100).round(1)
# Remover a coluna antiga
estatisticas_decadas = estatisticas_decadas.drop(columns='Índice de Vitórias')

# 15. Exibir os resultados
print("\nDécada mais vitoriosa do Brasil:")
print(estatisticas_decadas.to_string(index=False))

# 16. Exibir o gráfico de barras para ambos os critérios
plt.figure(figsize=(10,6))

if criterio == '1':
    # Gráfico para número absoluto de vitórias
    plt.bar(estatisticas_decadas['Década'], estatisticas_decadas['Vitórias'], color='blue')
    plt.ylabel('Número de Vitórias')
    plt.title('Número Absoluto de Vitórias do Brasil por Década')
else:
    # Gráfico para índice de vitórias
    plt.bar(estatisticas_decadas['Década'], estatisticas_decadas['Índice de Vitórias (%)'], color='green')
    plt.ylabel('Índice de Vitórias (%)')
    plt.title('Índice de Vitórias do Brasil por Década')

plt.xlabel('Década')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
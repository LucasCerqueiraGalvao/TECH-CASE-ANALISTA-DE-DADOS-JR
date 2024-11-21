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

# 3.2 Criar uma função para determinar o resultado final do ponto de vista do Brasil
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

# 6. Perguntar ao usuário se deseja organizar por número absoluto de derrotas ou índice de derrotas
print("\nEscolha o critério para determinar os times que mais venceram o Brasil:")
print("1 - Maior número absoluto de vitórias sobre o Brasil")
print("2 - Maior índice de vitórias sobre o Brasil")
while True:
    criterio = input("Digite 1 ou 2: ").strip()
    if criterio == '1' or criterio == '2':
        break
    else:
        print("Opção inválida. Por favor, digite 1 ou 2.")

# 7. Se o usuário escolher o índice, perguntar o número mínimo de jogos
if criterio == '2':
    while True:
        try:
            numero_minimo_jogos = int(input("Digite o número mínimo de jogos para considerar na análise: "))
            break
        except ValueError:
            print("Por favor, insira um número inteiro válido.")

# 8. Identificar os adversários e calcular as estatísticas
# 8.1 Criar uma lista para armazenar os resultados
estatisticas_adversarios = []

# 8.2 Obter todos os adversários do Brasil
df_final['Adversário'] = df_final.apply(lambda row: row['away_team'] if row['home_team'] == 'Brazil' else row['home_team'], axis=1)

# Agrupar as partidas por adversário
grupos_adversarios = df_final.groupby('Adversário')

for adversario, grupo in grupos_adversarios:
    jogos = len(grupo)
    derrotas_brasil = (grupo['Resultado'] == 'Derrota').sum()
    vitorias_brasil = (grupo['Resultado'] == 'Vitória').sum()
    empates = (grupo['Resultado'] == 'Empate').sum()
    indice_derrotas = derrotas_brasil / jogos if jogos > 0 else 0

    # Se o critério for índice, aplicar o filtro de número mínimo de jogos
    if criterio == '2' and jogos < numero_minimo_jogos:
        continue  # Pula para o próximo adversário

    estatisticas_adversarios.append({
        'Adversário': adversario,
        'Jogos': jogos,
        'Derrotas do Brasil': derrotas_brasil,
        'Vitórias do Brasil': vitorias_brasil,
        'Empates': empates,
        'Índice de Derrotas': indice_derrotas
    })

# 9. Criar DataFrame com as estatísticas
df_estatisticas = pd.DataFrame(estatisticas_adversarios)

# 10. Organizar os dados de acordo com o critério escolhido
if criterio == '1':
    # Ordenar pelo número absoluto de derrotas
    df_estatisticas = df_estatisticas.sort_values(by=['Derrotas do Brasil', 'Jogos'], ascending=[False, False])
else:
    # Ordenar pelo índice de derrotas
    df_estatisticas = df_estatisticas.sort_values(by=['Índice de Derrotas', 'Jogos'], ascending=[False, False])

# 11. Formatar a coluna 'Índice de Derrotas' como porcentagem
df_estatisticas['Índice de Derrotas (%)'] = (df_estatisticas['Índice de Derrotas'] * 100).round(1)
# Remover a coluna antiga
df_estatisticas = df_estatisticas.drop(columns='Índice de Derrotas')

# 12. Criar um DataFrame para os top 5 adversários (para o gráfico)
df_top5 = df_estatisticas.head(5)

# 13. Exibir os resultados completos
print("\nTimes que mais venceram o Brasil:")
print(df_estatisticas.to_string(index=False))

# 14. Exibir gráfico de barras com os top 5
plt.figure(figsize=(10,6))

if criterio == '1':
    # Gráfico para número absoluto de derrotas
    plt.bar(df_top5['Adversário'], df_top5['Derrotas do Brasil'], color='red')
    plt.ylabel('Número de Vitórias sobre o Brasil')
    plt.title('Top 5 Times que Mais Venceram o Brasil')
else:
    # Gráfico para índice de derrotas
    plt.bar(df_top5['Adversário'], df_top5['Índice de Derrotas (%)'], color='orange')
    plt.ylabel('Índice de Derrotas (%)')
    plt.title('Top 5 Índice de Vitórias sobre o Brasil por Adversário')

plt.xlabel('Adversário')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

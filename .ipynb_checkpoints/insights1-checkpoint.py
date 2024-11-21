import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar o dataset de resultados
df = pd.read_csv('datasets\\results.csv')

# 2. Filtrar as partidas em que o Brasil participou (como mandante ou visitante)
df_brasil = df[(df['home_team'] == 'Brazil') | (df['away_team'] == 'Brazil')].copy()

# 3. Criar uma função para determinar o resultado da partida do ponto de vista do Brasil
def get_result(row):
    # Se o Brasil foi o time mandante (home_team)
    if row['home_team'] == 'Brazil':
        if row['home_score'] > row['away_score']:
            return 'Vitória'       # Brasil venceu
        elif row['home_score'] < row['away_score']:
            return 'Derrota'       # Brasil perdeu
        else:
            return 'Empate'        # Partida empatada
    # Se o Brasil foi o time visitante (away_team)
    else:
        if row['away_score'] > row['home_score']:
            return 'Vitória'       # Brasil venceu
        elif row['away_score'] < row['home_score']:
            return 'Derrota'       # Brasil perdeu
        else:
            return 'Empate'        # Partida empatada

# 4. Aplicar a função para determinar o resultado de cada partida do Brasil
df_brasil['Resultado'] = df_brasil.apply(get_result, axis=1)

# 5. Carregar o dataset de disputas de pênaltis
df_shootouts = pd.read_csv('datasets\\shootouts.csv')

# 6. Mesclar os datasets para identificar partidas decididas nos pênaltis
df_merged = pd.merge(df_brasil, df_shootouts, on=['date', 'home_team', 'away_team'], how='left')

# 7. Criar uma função para ajustar o resultado em caso de disputa de pênaltis
def adjust_for_shootouts(row):
    # Verifica se o resultado foi empate e se houve disputa de pênaltis
    if row['Resultado'] == 'Empate' and pd.notna(row['winner']):
        if row['winner'] == 'Brazil':
            return 'Vitória'       # Brasil venceu nos pênaltis
        else:
            return 'Derrota'       # Brasil perdeu nos pênaltis
    else:
        return row['Resultado']    # Mantém o resultado original

# 8. Aplicar a função para ajustar os resultados com base nas disputas de pênaltis
df_merged['Resultado_Final'] = df_merged.apply(adjust_for_shootouts, axis=1)

# 9. Perguntar ao usuário se deseja considerar os amistosos
considerar_amistosos = input("Deseja considerar os amistosos na análise? (S/N): ").strip().upper()

# 10. Filtrar as partidas com base na escolha do usuário
if considerar_amistosos == 'N':
    # Excluir partidas amistosas para focar em competições internacionais oficiais
    df_final = df_merged[df_merged['tournament'] != 'Friendly']
elif considerar_amistosos == 'S':
    # Incluir todas as partidas, incluindo amistosos
    df_final = df_merged.copy()
else:
    print("Opção inválida. Considerando apenas partidas não amistosas por padrão.")
    df_final = df_merged[df_merged['tournament'] != 'Friendly']

# 11. Perguntar ao usuário se deseja a resposta em números absolutos ou por índice
print("\nDeseja que a análise seja baseada em:")
print("1 - Números absolutos (total de vitórias)")
print("2 - Índice (percentual de vitórias)")
while True:
    opcao_analise = input("Digite 1 ou 2: ").strip()
    if opcao_analise in ['1', '2']:
        break
    else:
        print("Opção inválida. Por favor, digite 1 ou 2.")

# 12. Agrupar os dados por torneio e calcular o total de jogos, vitórias, derrotas e empates
torneios = df_final.groupby('tournament').agg(
    Jogos=('Resultado_Final', 'count'),
    Vitórias=('Resultado_Final', lambda x: (x == 'Vitória').sum()),
    Derrotas=('Resultado_Final', lambda x: (x == 'Derrota').sum()),
    Empates=('Resultado_Final', lambda x: (x == 'Empate').sum())
).reset_index()

# 13. Se a análise for por índice, calcular o percentual de vitórias
if opcao_analise == '2':
    # Calcular o índice de vitórias
    torneios['Índice de Vitórias'] = (torneios['Vitórias'] / torneios['Jogos']) * 100
    # Arredondar para uma casa decimal e adicionar o símbolo '%'
    torneios['Índice de Vitórias'] = torneios['Índice de Vitórias'].round(1).astype(str) + '%'
    # Perguntar ao usuário o número mínimo de jogos para a análise
    while True:
        try:
            numero_minimo_jogos = int(input("Digite o número mínimo de jogos para considerar na análise: "))
            break
        except ValueError:
            print("Por favor, insira um número inteiro válido.")
    # Filtrar torneios com o número mínimo de jogos
    torneios_ordenado = torneios[torneios['Jogos'] >= numero_minimo_jogos]
    # Ordenar pelo índice de vitórias (removendo o símbolo '%' para ordenação correta)
    torneios_ordenado['Índice_Num'] = torneios_ordenado['Índice de Vitórias'].str.rstrip('%').astype(float)
    torneios_ordenado = torneios_ordenado.sort_values(by='Índice_Num', ascending=False)
    # Remover a coluna auxiliar
    torneios_ordenado.drop(columns='Índice_Num', inplace=True)
    # Responder diretamente à pergunta
    print("\nOs torneios com maior índice de vitórias do Brasil são:")
    print(torneios_ordenado[['tournament', 'Jogos', 'Vitórias', 'Índice de Vitórias']].head(5).to_string(index=False))
else:
    # Ordenar pelo número absoluto de vitórias
    torneios_ordenado = torneios.sort_values(by='Vitórias', ascending=False)
    # Responder diretamente à pergunta
    print("\nOs torneios com mais vitórias do Brasil são:")
    print(torneios_ordenado[['tournament', 'Jogos', 'Vitórias']].head(5).to_string(index=False))

# 14. Exibir o gráfico de barras com o top 5
plt.figure(figsize=(10,6))
if opcao_analise == '2':
    top5 = torneios_ordenado.head(5).copy()
    # Remover o símbolo '%' para plotar
    top5['Índice_Num'] = top5['Índice de Vitórias'].str.rstrip('%').astype(float)
    plt.bar(top5['tournament'], top5['Índice_Num'], color='blue')
    plt.ylabel('Índice de Vitórias (%)')
    plt.title('Top 5 Torneios por Índice de Vitórias do Brasil')
    # Adicionar os valores acima das barras
    for i, v in enumerate(top5['Índice_Num']):
        plt.text(i, v + 1, f"{v:.1f}%", ha='center')
else:
    top5 = torneios_ordenado.head(5)
    plt.bar(top5['tournament'], top5['Vitórias'], color='green')
    plt.ylabel('Número de Vitórias')
    plt.title('Top 5 Torneios com Mais Vitórias do Brasil')
    # Adicionar os valores acima das barras
    for i, v in enumerate(top5['Vitórias']):
        plt.text(i, v + 0.5, str(v), ha='center')
plt.xlabel('Torneio')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 15. Exibir os resultados finais completos
print("\nResultados completos:")
if opcao_analise == '2':
    print(torneios_ordenado[['tournament', 'Jogos', 'Vitórias', 'Derrotas', 'Empates', 'Índice de Vitórias']].to_string(index=False))
else:
    print(torneios_ordenado[['tournament', 'Jogos', 'Vitórias', 'Derrotas', 'Empates']].to_string(index=False))

import pandas as pd

# 1. Carregar os datasets
results = pd.read_csv('datasets\\results.csv')
shootouts = pd.read_csv('datasets\\shootouts.csv')

# 2. Carregar todas as partidas, incluindo amistosos
df = results.copy()

# 3. Ajustar resultados para disputas de pênaltis
# 3.1 Mesclar o dataset de resultados com o de shootouts
df_merged = pd.merge(df, shootouts, on=['date', 'home_team', 'away_team'], how='left')

# 3.2 Criar uma função para determinar o resultado final da partida
def get_match_result(row):
    # Verificar se houve disputa de pênaltis
    if pd.notna(row['winner']):
        if row['winner'] == row['home_team']:
            return row['home_team']
        else:
            return row['away_team']
    else:
        # Se não houve pênaltis, determinar o vencedor pelo placar
        if row['home_score'] > row['away_score']:
            return row['home_team']
        elif row['home_score'] < row['away_score']:
            return row['away_team']
        else:
            return 'Empate'

# 3.3 Aplicar a função para obter o resultado final
df_merged['vencedor'] = df_merged.apply(get_match_result, axis=1)

# 4. Perguntar ao usuário se deseja o maior número absoluto de vitórias ou o maior índice de vitórias
print("Escolha o critério para determinar o time mais vitorioso em cada competição:")
print("1 - Maior número absoluto de vitórias")
print("2 - Maior índice de vitórias")
while True:
    criterio = input("Digite 1 ou 2: ").strip()
    if criterio == '1' or criterio == '2':
        break
    else:
        print("Opção inválida. Por favor, digite 1 ou 2.")

# 5. Se o usuário escolheu o maior índice de vitórias, perguntar o número mínimo de jogos
if criterio == '2':
    while True:
        try:
            numero_minimo_jogos = int(input("Digite o número mínimo de jogos para considerar na análise: "))
            break
        except ValueError:
            print("Por favor, insira um número inteiro válido.")

# 6. Analisar cada torneio
torneios = df_merged['tournament'].unique()

# 6.1 Criar uma lista para armazenar os resultados
resultados = []

for torneio in torneios:
    # Filtrar partidas do torneio atual
    partidas_torneio = df_merged[df_merged['tournament'] == torneio]
    
    # Obter todos os times que participaram
    times = pd.unique(partidas_torneio[['home_team', 'away_team']].values.ravel('K'))
    
    # Criar uma lista para estatísticas dos times
    estatisticas_times = []

    for time in times:
        # Filtrar partidas do time no torneio
        partidas_time = partidas_torneio[
            (partidas_torneio['home_team'] == time) | (partidas_torneio['away_team'] == time)
        ]

        # Contar o número de jogos
        jogos = len(partidas_time)
        
        # Contar o número de vitórias
        vitorias = partidas_time['vencedor'].value_counts().get(time, 0)
        
        # Calcular o índice de vitórias
        indice_vitorias = vitorias / jogos if jogos > 0 else 0
        
        # Se o critério for índice de vitórias, aplicar o filtro do número mínimo de jogos
        if criterio == '2' and jogos < numero_minimo_jogos:
            continue  # Pula para o próximo time
        
        # Adicionar ao DataFrame de estatísticas
        estatisticas_times.append({
            'time': time,
            'jogos': jogos,
            'vitórias': vitorias,
            'índice de vitórias': indice_vitorias
        })
    
    # Verificar se há dados para o torneio
    if estatisticas_times:
        # Criar DataFrame de estatísticas
        df_estatisticas = pd.DataFrame(estatisticas_times)
        
        if criterio == '1':
            # Ordenar pelo número absoluto de vitórias em ordem decrescente
            df_estatisticas = df_estatisticas.sort_values(
                by=['vitórias', 'jogos'], ascending=[False, False]
            )
        else:
            # Ordenar pelo índice de vitórias em ordem decrescente
            df_estatisticas = df_estatisticas.sort_values(
                by=['índice de vitórias', 'jogos'], ascending=[False, False]
            )
        
        # Selecionar o time com maior valor de acordo com o critério
        time_mais_vitorioso = df_estatisticas.iloc[0]
        
        # Adicionar aos resultados
        resultados.append({
            'torneio': torneio,
            'time': time_mais_vitorioso['time'],
            'jogos': int(time_mais_vitorioso['jogos']),
            'vitórias': int(time_mais_vitorioso['vitórias']),
            'índice de vitórias': f"{(time_mais_vitorioso['índice de vitórias'] * 100):.1f}%"
        })

# 7. Criar DataFrame dos resultados e exibir
df_resultados = pd.DataFrame(resultados)

# Ordenar por ordem alfabética dos torneios
df_resultados = df_resultados.sort_values(by='torneio')

# 8. Exibir os resultados
print("\nTime mais vitorioso em cada competição internacional:")
print(df_resultados.to_string(index=False))

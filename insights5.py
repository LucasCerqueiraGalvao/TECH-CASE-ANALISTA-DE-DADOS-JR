import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar o dataset
goalscorers = pd.read_csv('datasets\\goalscorers.csv')

# 2. Filtrar os gols marcados por jogadores brasileiros
gols_brasileiros = goalscorers[goalscorers['team'] == 'Brazil'].copy()

# 3. Tratar as colunas 'penalty' e 'own_goal'
# Converter as colunas 'penalty' e 'own_goal' para booleano
gols_brasileiros['penalty'] = gols_brasileiros['penalty'].astype(bool)
gols_brasileiros['own_goal'] = gols_brasileiros['own_goal'].astype(bool)

# Remover gols contra (own goals) marcados a favor do Brasil
gols_brasileiros = gols_brasileiros[~gols_brasileiros['own_goal']]

# 4. Perguntar ao usuário qual estatística deseja visualizar
print("Escolha a categoria de gols que deseja analisar:")
print("1 - Jogador com mais gols totais")
print("2 - Jogador com mais gols de pênalti")
print("3 - Jogador com mais gols de não pênalti")
while True:
    escolha = input("Digite 1, 2 ou 3: ").strip()
    if escolha in ['1', '2', '3']:
        break
    else:
        print("Opção inválida. Por favor, digite 1, 2 ou 3.")

# 5. Calcular as estatísticas de gols por jogador
# 5.1 Total de gols por jogador
total_gols = gols_brasileiros.groupby('scorer').size().reset_index(name='Total de Gols')

# 5.2 Total de gols de pênalti por jogador
gols_penalti = gols_brasileiros[gols_brasileiros['penalty']]
total_gols_penalti = gols_penalti.groupby('scorer').size().reset_index(name='Gols de Pênalti')

# 5.3 Total de gols de não pênalti por jogador
gols_nao_penalti = gols_brasileiros[~gols_brasileiros['penalty']]
total_gols_nao_penalti = gols_nao_penalti.groupby('scorer').size().reset_index(name='Gols de Não Pênalti')

# 6. Combinar as estatísticas em um único DataFrame
estatisticas = total_gols.merge(total_gols_penalti, on='scorer', how='left')
estatisticas = estatisticas.merge(total_gols_nao_penalti, on='scorer', how='left')

# Preencher valores NaN com zero
estatisticas.fillna(0, inplace=True)

# Converter colunas de contagem para inteiros
estatisticas['Gols de Pênalti'] = estatisticas['Gols de Pênalti'].astype(int)
estatisticas['Gols de Não Pênalti'] = estatisticas['Gols de Não Pênalti'].astype(int)

# 7. Ordenar o DataFrame de acordo com o critério escolhido e critérios secundários
if escolha == '1':
    # Jogador com mais gols totais
    estatisticas = estatisticas.sort_values(
        by=['Total de Gols', 'Gols de Pênalti', 'Gols de Não Pênalti'],
        ascending=[False, False, False]
    )
    criterio_principal = 'Total de Gols'
elif escolha == '2':
    # Jogador com mais gols de pênalti
    estatisticas = estatisticas.sort_values(
        by=['Gols de Pênalti', 'Total de Gols', 'Gols de Não Pênalti'],
        ascending=[False, False, False]
    )
    criterio_principal = 'Gols de Pênalti'
else:
    # Jogador com mais gols de não pênalti
    estatisticas = estatisticas.sort_values(
        by=['Gols de Não Pênalti', 'Total de Gols', 'Gols de Pênalti'],
        ascending=[False, False, False]
    )
    criterio_principal = 'Gols de Não Pênalti'

# 8. Exibir o jogador com o maior número de gols na categoria escolhida
top_jogador = estatisticas.iloc[0]
print(f"\nJogador brasileiro com mais {criterio_principal.lower()}:")
print(f"{top_jogador['scorer']} - {top_jogador[criterio_principal]} {criterio_principal.lower()}")

# 9. Exibir o DataFrame completo com todos os jogadores
print("\nEstatísticas de todos os jogadores:")
print(estatisticas.to_string(index=False))

# 10. Plotar o gráfico de barras com o top 5 jogadores da categoria escolhida
top5 = estatisticas.head(5)

plt.figure(figsize=(10,6))
plt.bar(top5['scorer'], top5[criterio_principal], color='blue')
plt.xlabel('Jogador')
plt.ylabel(criterio_principal)
plt.title(f"Top 5 jogadores brasileiros - {criterio_principal}")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar o dataset
results = pd.read_csv('datasets\\results.csv')

# 2. Filtrar as partidas em que o Brasil participou (como mandante ou visitante)
df_brasil = results[(results['home_team'] == 'Brazil') | (results['away_team'] == 'Brazil')].copy()

# 3. Perguntar ao usuário se deseja incluir amistosos
incluir_amistosos = input("Deseja incluir amistosos na análise? (S/N): ").strip().upper()

# 4. Filtrar as partidas com base na escolha do usuário
if incluir_amistosos == 'N':
    df_brasil = df_brasil[df_brasil['tournament'] != 'Friendly']
elif incluir_amistosos == 'S':
    pass  # Não precisa filtrar, pois já inclui todos os jogos
else:
    print("Opção inválida. Considerando apenas partidas não amistosas por padrão.")
    df_brasil = df_brasil[df_brasil['tournament'] != 'Friendly']

# 5. Perguntar ao usuário qual opção deseja analisar
print("\nEscolha a categoria para análise dos gols:")
print("1 - Times que mais tomaram gols do Brasil (total)")
print("2 - Times que mais tomaram gols do Brasil quando o Brasil era mandante")
print("3 - Times que mais tomaram gols do Brasil quando o Brasil era visitante")
while True:
    opcao = input("Digite 1, 2 ou 3: ").strip()
    if opcao in ['1', '2', '3']:
        break
    else:
        print("Opção inválida. Por favor, digite 1, 2 ou 3.")

# 6. Perguntar ao usuário se deseja gols absolutos ou relativos ao número de jogos
print("\nDeseja que os gols sejam:")
print("1 - Gols absolutos")
print("2 - Gols por jogo (média de gols por partida)")
while True:
    opcao_gols = input("Digite 1 ou 2: ").strip()
    if opcao_gols in ['1', '2']:
        break
    else:
        print("Opção inválida. Por favor, digite 1 ou 2.")

# 7. Criar colunas auxiliares para os gols marcados pelo Brasil em cada partida
df_brasil['gols_brasil'] = df_brasil.apply(
    lambda row: row['home_score'] if row['home_team'] == 'Brazil' else row['away_score'], axis=1)
df_brasil['adversario'] = df_brasil.apply(
    lambda row: row['away_team'] if row['home_team'] == 'Brazil' else row['home_team'], axis=1)
df_brasil['mandante'] = df_brasil['home_team'] == 'Brazil'
df_brasil['visitante'] = df_brasil['away_team'] == 'Brazil'

# 8. Selecionar os dados conforme a opção escolhida
if opcao == '1':
    # Todas as partidas
    df_selecionado = df_brasil.copy()
    criterio = 'Total de gols sofridos contra o Brasil'
elif opcao == '2':
    # Partidas com o Brasil como mandante
    df_selecionado = df_brasil[df_brasil['mandante']].copy()
    criterio = 'Gols sofridos do Brasil como mandante'
else:
    # Partidas com o Brasil como visitante
    df_selecionado = df_brasil[df_brasil['visitante']].copy()
    criterio = 'Gols sofridos do Brasil como visitante'

# 9. Calcular os gols e o número de jogos por adversário
gols_por_adversario = df_selecionado.groupby('adversario').agg(
    gols_brasil=('gols_brasil', 'sum'),
    jogos=('adversario', 'count')
).reset_index()

# 10. Calcular gols por jogo se o usuário escolheu a opção 2
if opcao_gols == '2':
    gols_por_adversario['gols_por_jogo'] = gols_por_adversario['gols_brasil'] / gols_por_adversario['jogos']
    # Arredondar para uma casa decimal
    gols_por_adversario['gols_por_jogo'] = gols_por_adversario['gols_por_jogo'].round(1)
    # Ordenar pelos gols por jogo
    gols_por_adversario = gols_por_adversario.sort_values(by='gols_por_jogo', ascending=False)
    coluna_grafico = 'gols_por_jogo'
    ylabel = 'Gols por Jogo'
    titulo_grafico = f"Top 5 times que mais tomaram gols por jogo do Brasil\n({criterio})"
else:
    # Ordenar pelos gols absolutos
    gols_por_adversario = gols_por_adversario.sort_values(by='gols_brasil', ascending=False)
    coluna_grafico = 'gols_brasil'
    ylabel = 'Gols Sofridos'
    titulo_grafico = f"Top 5 times que mais tomaram gols do Brasil\n({criterio})"

# 11. Selecionar os top 5 adversários
top5 = gols_por_adversario.head(5)

# 12. Mostrar a resposta direta para a pergunta
print(f"\nOs times que mais tomaram gols do Brasil ({criterio}):")
if opcao_gols == '2':
    for index, row in top5.iterrows():
        print(f"{row['adversario']}: {row['gols_por_jogo']:.1f} gols por jogo em {row['jogos']} jogos")
else:
    for index, row in top5.iterrows():
        print(f"{row['adversario']}: {row['gols_brasil']} gols em {row['jogos']} jogos")

# 13. Mostrar o dataset com as estatísticas calculadas
print("\nEstatísticas completas:")
if opcao_gols == '2':
    # Ordenar para exibir todo o dataset corretamente
    gols_por_adversario = gols_por_adversario.sort_values(by='gols_por_jogo', ascending=False)
    print(gols_por_adversario[['adversario', 'jogos', 'gols_brasil', 'gols_por_jogo']].to_string(index=False))
else:
    gols_por_adversario = gols_por_adversario.sort_values(by='gols_brasil', ascending=False)
    print(gols_por_adversario[['adversario', 'jogos', 'gols_brasil']].to_string(index=False))

# 14. Exibir o gráfico de barras pertinente à opção escolhida
plt.figure(figsize=(10,6))
if opcao_gols == '2':
    plt.bar(top5['adversario'], top5[coluna_grafico], color='green')
    plt.ylabel(ylabel)
    # Adicionar os valores acima das barras com uma casa decimal
    for i, v in enumerate(top5[coluna_grafico]):
        plt.text(i, v + 0.05, f"{v:.1f}", ha='center')
else:
    plt.bar(top5['adversario'], top5[coluna_grafico], color='green')
    plt.ylabel(ylabel)
    # Adicionar os valores acima das barras
    for i, v in enumerate(top5[coluna_grafico]):
        plt.text(i, v + 0.5, str(int(v)), ha='center')
plt.xlabel('Adversário')
plt.title(titulo_grafico)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

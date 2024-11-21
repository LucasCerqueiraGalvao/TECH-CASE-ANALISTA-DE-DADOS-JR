import kagglehub
import os

# Especificar o nome do dataset no Kaggle
dataset_name = "martj42/international-football-results-from-1872-to-2017"

# Fazer o download da versão mais recente do dataset
try:
    path = kagglehub.dataset_download(dataset_name)
    print(f"Dataset baixado com sucesso! Arquivos disponíveis em: {path}")

    # Verificar os arquivos baixados
    files = os.listdir(path)
    print("Arquivos no dataset:", files)

except Exception as e:
    print("Erro ao baixar o dataset:", e)

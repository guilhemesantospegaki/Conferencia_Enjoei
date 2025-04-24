import os
import shutil
import subprocess

# Caminho do CSV no seu Google Drive (pasta sincronizada no seu PC)
CSV_ORIGEM = r"G:\Meu Drive\Projetos\5 - Conferência Enjoei\Db_Pacotes_Enjoei.csv"  

# Caminho do repositório local
REPO_DIR = r"C:\Users\guilherme.santos_int\Desktop\Projetos\Automações\Conferência Enjoei\Conferencia_Enjoei"
CSV_DESTINO = os.path.join(REPO_DIR, "Db_Pacotes_Enjoei.csv")

# Copiar o CSV
if os.path.exists(CSV_ORIGEM):
    shutil.copyfile(CSV_ORIGEM, CSV_DESTINO)
    print("✅ CSV copiado do Google Drive com sucesso.")
else:
    print("❌ Arquivo CSV não encontrado no Google Drive.")
    exit(1)

# Git: commit e push
subprocess.run(["git", "add", "Db_Pacotes_Enjoei.csv"], cwd=REPO_DIR)
subprocess.run(["git", "commit", "-m", "Atualiza CSV diário"], cwd=REPO_DIR)
subprocess.run(["git", "push"], cwd=REPO_DIR)
print("🚀 CSV atualizado no GitHub.")

# Excluir o arquivo da pasta local do Google Drive após o commit
if os.path.exists(CSV_ORIGEM):
    os.remove(CSV_ORIGEM)
    print("✅ Arquivo excluído da pasta do Google Drive local.")
else:
    print("❌ Arquivo não encontrado para exclusão.")

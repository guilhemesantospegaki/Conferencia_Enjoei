import pandas as pd
import requests
import io

def carregar_csv_github():
    url = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/refs/heads/main/App_Conferencia/Db_Pacotes_Enjoei.csv"
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        return df
    else:
        raise Exception(f"Erro {response.status_code} ao acessar CSV")

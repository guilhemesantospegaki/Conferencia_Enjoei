import tkinter as tk
from tkinter import ttk
import pandas as pd
import re

# --- Configuração inicial ---
csv_path = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/refs/heads/main/Db_Pacotes_Enjoei.csv"
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()
df = df.applymap(lambda x: str(x).strip())

# Expressão regular para validar o PUG
regex_pug = re.compile(r"^PUG\d{8}(CAM|BIR|GRU|FRC|RJO|GYN|JOI|CWB|MGA|DIV|CTG|PCD)$")

pacotes_bipados = set()
ultimo_codigo = None
contador_validos = 0
pug_atual = None
pug_contagem = {}

# --- Função principal de verificação ---
def verificar_codigo(codigo):
    global ultimo_codigo, contador_validos, pug_atual

    codigo = codigo.strip()
    if not codigo:
        return

    # Primeiro bip deve ser do PUG
    if pug_atual is None:
        if regex_pug.match(codigo):
            if codigo in pug_contagem:
                status_label.config(text="⚠️ Esse PUG já foi usado.", fg="orange")
                entrada_var.set("")
                return
            pug_atual = codigo
            status_label.config(text=f"✅ PUG registrado: {pug_atual}", fg="green")
        else:
            status_label.config(text="❌ PUG inválido. Formato incorreto.", fg="red")
        entrada_var.set("")
        return

    if codigo.startswith("PNL"):
        ultimo_codigo = {"rastreio": codigo, "etiqueta": None}
        status_label.config(text="🔄 Código de rastreio lido. Agora bipar a etiqueta.", fg="orange")
    else:
        if ultimo_codigo and ultimo_codigo["etiqueta"] is None:
            ultimo_codigo["etiqueta"] = codigo
            rastreio = ultimo_codigo["rastreio"]
            etiqueta = ultimo_codigo["etiqueta"]

            resultado = df[df["[Código de Rastreio]"] == rastreio]
            if not resultado.empty and resultado["[Etiqueta Last Mile]"].values[0] == etiqueta:
                if rastreio not in pacotes_bipados:
                    pacotes_bipados.add(rastreio)
                    contador_validos += 1
                    contador_label.config(text=f"📦 Pacotes válidos: {contador_validos}")
                    status_label.config(text="✅ Pacote válido registrado!", fg="green")
                    adicionar_na_tabela(pug_atual, rastreio, etiqueta)
                    atualizar_tabela_pug(pug_atual)
                else:
                    status_label.config(text="⚠️ Esse pacote já foi bipado.", fg="blue")
                    adicionar_na_tabela(pug_atual, rastreio, etiqueta, duplicado=True)
            else:
                status_label.config(text="❌ Código e etiqueta não correspondem.", fg="red")

            ultimo_codigo = None
        else:
            status_label.config(text="❗ Bipe primeiro um código de rastreio (começa com PNL).", fg="red")

    entrada_var.set("")

# --- Adicionar na tabela ---
def adicionar_na_tabela(pug, rastreio, etiqueta, duplicado=False):
    tags = ()
    if rastreio in [tabela.item(i)["values"][1] for i in tabela.get_children()]:
        tags = ("duplicado",)
    tabela.insert("", "end", values=(pug, rastreio, etiqueta), tags=tags)
    if tags:
        tabela.tag_configure("duplicado", background="#ff4d4d")

# --- Atualizar tabela de contagem de PUGs ---
def atualizar_tabela_pug(pug):
    if pug in pug_contagem:
        pug_contagem[pug] += 1
    else:
        pug_contagem[pug] = 1

    for item in tabela_pugs.get_children():
        if tabela_pugs.item(item)["values"][0] == pug:
            tabela_pugs.item(item, values=(pug, pug_contagem[pug]))
            return
    tabela_pugs.insert("", "end", values=(pug, pug_contagem[pug]))

# --- Resetar contagem e exigir novo PUG ---
def resetar():
    global ultimo_codigo, contador_validos, pug_atual
    ultimo_codigo = None
    contador_validos = 0
    pacotes_bipados.clear()
    pug_atual = None
    contador_label.config(text="📦 Pacotes válidos: 0")
    status_label.config(text="🔁 Reiniciado. Aguardando novo PUG...", fg="white")
    entrada_var.set("")
    entrada.focus()

# --- Interface Tkinter ---
root = tk.Tk()
root.title("Validador de Pacotes")
root.geometry("900x500")
root.configure(bg="#1e1e1e")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 12))
style.configure("TEntry", padding=5)
style.configure("TButton", background="#0078D7", foreground="white", font=("Segoe UI", 10, "bold"))

main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Lado esquerdo (maior)
left_frame = tk.Frame(main_frame, bg="#1e1e1e", width=500)
left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

content_frame = tk.Frame(left_frame, bg="#1e1e1e")
content_frame.place(relx=0.5, rely=0.5, anchor="center")

titulo = ttk.Label(content_frame, text="📦 Leitor de Pacotes", font=("Segoe UI", 16, "bold"))
titulo.pack(pady=10)

entrada_var = tk.StringVar()
entrada = ttk.Entry(content_frame, textvariable=entrada_var, font=("Segoe UI", 14), width=30)
entrada.pack(pady=10)
entrada.focus()
entrada.bind("<Return>", lambda event: verificar_codigo(entrada_var.get()))

contador_label = ttk.Label(content_frame, text="📦 Pacotes válidos: 0")
contador_label.pack(pady=10)

status_label = tk.Label(content_frame, text="Aguardando PUG...", font=("Segoe UI", 11), bg="#1e1e1e", fg="white")
status_label.pack(pady=10)

reset_btn = ttk.Button(content_frame, text="🔁 Resetar", command=resetar)
reset_btn.pack(pady=10)

# Lado direito (menor)
right_frame = tk.Frame(main_frame, bg="#1e1e1e", width=400)
right_frame.pack(side="right", fill="both", expand=False)

# --- Tabela principal de pacotes (em cima)
tabela = ttk.Treeview(right_frame, columns=("pug", "rastreio", "etiqueta"), show="headings", height=10)
tabela.heading("pug", text="PUG")
tabela.heading("rastreio", text="Código de Rastreio")
tabela.heading("etiqueta", text="Etiqueta Last Mile")

tabela.column("pug", anchor="center", width=180)
tabela.column("rastreio", anchor="center", width=180)
tabela.column("etiqueta", anchor="center", width=180)

scroll_y = ttk.Scrollbar(right_frame, orient="vertical", command=tabela.yview)
tabela.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")
tabela.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 5))

# --- Frame inferior direito para a tabela de PUGs (embaixo)
bottom_right_frame = tk.Frame(right_frame, bg="#1e1e1e")
bottom_right_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

tabela_pugs = ttk.Treeview(bottom_right_frame, columns=("pug", "contagem"), show="headings", height=4)
tabela_pugs.heading("pug", text="PUG")
tabela_pugs.heading("contagem", text="Qtd Pacotes")
tabela_pugs.column("pug", anchor="center", width=180)
tabela_pugs.column("contagem", anchor="center", width=180)
tabela_pugs.pack(fill="x")

style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), foreground="white", background="#0078D7")

root.mainloop()

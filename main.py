import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import re

# --- Configuração inicial ---
csv_path = "https://raw.githubusercontent.com/guilhemesantospegaki/Conferencia_Enjoei/refs/heads/main/Db_Pacotes_Enjoei.csv"
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()
df = df.applymap(lambda x: str(x).strip())

regex_pug = re.compile(r"^PUG\d{8}(CAM|BIR|GRU|FRC|RJO|GYN|JOI|CWB|MGA|DIV|CTG|PCD)$")

pacotes_bipados = set()
ultimo_codigo = None
contador_validos = 0
pug_atual = None
pug_contagem = {}
ordem_por_pug = {}
linhas_destacadas = {}

estado = "aguardando_pug"

# --- Função de bloqueio com senha ---
def solicitar_senha(mensagem):
    senha_valida = [False]

    def validar_senha():
        senha = senha_entry.get()
        if senha == "1234":
            # Quando a senha for validada, restaurar as linhas vermelhas para branco
            for item in tabela.get_children():
                if tabela.item(item, "tags") == ("duplicado",):  # Verificando as linhas com a tag "duplicado"
                    tabela.item(item, tags="")  # Remove a tag e a cor vermelha
            senha_valida[0] = True
            senha_window.destroy()
        else:
            erro_label.config(text="❌ Senha incorreta. Tente novamente.", fg="red")

    senha_window = tk.Toplevel(root)
    senha_window.title("⚠️ ERRO DETECTADO")
    senha_window.configure(bg="#1e1e1e")
    senha_window.protocol("WM_DELETE_WINDOW", lambda: None)

    # Centraliza na tela
    largura = 500
    altura = 250
    largura_tela = senha_window.winfo_screenwidth()
    altura_tela = senha_window.winfo_screenheight()
    pos_x = (largura_tela - largura) // 2
    pos_y = (altura_tela - altura) // 2
    senha_window.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    erro_label = tk.Label(
        senha_window,
        text=f"⚠️ {mensagem}",
        bg="#1e1e1e",
        fg="red",
        font=("Segoe UI", 14, "bold"),
        wraplength=480,
        justify="center"
    )
    erro_label.pack(pady=30)

    senha_entry = tk.Entry(senha_window, font=("Segoe UI", 14), show="*")
    senha_entry.pack(pady=10)
    senha_entry.focus()

    validar_btn = ttk.Button(senha_window, text="🔓 Validar Senha", command=validar_senha)
    validar_btn.pack(pady=10)

    senha_window.transient(root)
    senha_window.grab_set()
    senha_window.wait_window()

    return senha_valida[0]

# --- Função de verificação de códigos ---
def verificar_codigo(codigo):
    global ultimo_codigo, contador_validos, pug_atual, estado

    codigo = codigo.strip()
    if not codigo:
        return

    if estado == "aguardando_pug":
        if regex_pug.match(codigo):
            if codigo in pug_contagem:
                status_label.config(text="⚠️ Esse PUG já foi usado.", fg="orange")
            else:
                pug_atual = codigo
                contador_validos = 0
                ordem_por_pug[pug_atual] = 0 
                contador_label.config(text=f"📦 Pacotes válidos: {contador_validos}")
                status_label.config(text="✅ PUG registrado. Bipar código de rastreio (PNL).", fg="green")
                estado = "aguardando_rastreio"
        else:
            status_label.config(text="❌ PUG inválido. Formato incorreto.", fg="red")
        entrada_var.set("")
        return

    if estado == "aguardando_rastreio":
        if not codigo.startswith("PNL"):
            status_label.config(text="❌ Bipar código de rastreio que começa com PNL.", fg="red")
        elif codigo in pacotes_bipados:
            marcar_linha_duplicada(codigo)
            if not solicitar_senha("Código de rastreio duplicado detectado!"):
                entrada_var.set("")
                return
            else:
                limpar_destaque_linha(codigo)
                status_label.config(text="🔄 Bipar código de rastreio.", fg="orange")
                estado = "aguardando_rastreio"
        else:
            ultimo_codigo = {"rastreio": codigo, "etiqueta": None}
            status_label.config(text="🔄 Código de rastreio lido. Agora bipar a etiqueta.", fg="orange")
            estado = "aguardando_etiqueta"
        entrada_var.set("")
        return

    if estado == "aguardando_etiqueta":
        rastreio = ultimo_codigo["rastreio"]
        etiqueta = codigo
        resultado = df[df["[Codigo de Rastreio]"] == rastreio]

        if resultado.empty or resultado["[Etiqueta Last Mile]"].values[0] != etiqueta:
            if not solicitar_senha("Etiqueta não corresponde ao código de rastreio."):
                entrada_var.set("")
                return
            else:
                status_label.config(text="🔄 Bipar código de rastreio.", fg="orange")
                estado = "aguardando_rastreio"
                entrada_var.set("")
                return

        if rastreio in pacotes_bipados:
            marcar_linha_duplicada(rastreio)
            if not solicitar_senha("Código de rastreio duplicado detectado!"):
                entrada_var.set("")
                return
            else:
                limpar_destaque_linha(rastreio)
                status_label.config(text="🔄 Bipar código de rastreio.", fg="orange")
                estado = "aguardando_rastreio"
                entrada_var.set("")
                return

        adicionar_na_tabela(pug_atual, rastreio, etiqueta)
        pacotes_bipados.add(rastreio)
        contador_validos += 1
        contador_label.config(text=f"📦 Pacotes válidos: {contador_validos}")
        status_label.config(text="✅ Pacote válido registrado! Bipar próximo rastreio.", fg="green")
        atualizar_tabela_pug(pug_atual)
        estado = "aguardando_rastreio"
        entrada_var.set("")

# --- Adicionar na tabela ---
def adicionar_na_tabela(pug, rastreio, etiqueta):
    global linhas_destacadas, ordem_por_pug

    if pug not in ordem_por_pug:
        ordem_por_pug[pug] = 1
    else:
        ordem_por_pug[pug] += 1

    ordem = ordem_por_pug[pug]

    for item in tabela.get_children():
        if tabela.item(item)["values"][2] == rastreio:
            return
    item_id = tabela.insert("", "end", values=(ordem, pug, rastreio, etiqueta))
    linhas_destacadas[rastreio] = item_id

# --- Atualizar contagem por PUG ---
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

# --- Marcar linha duplicada ---
def marcar_linha_duplicada(rastreio):
    for item in tabela.get_children():
        if tabela.item(item)["values"][2] == rastreio:  # rastreio está na 3ª coluna agora (índice 2)
            tabela.item(item, tags=("duplicado",))
            tabela.tag_configure("duplicado", background="red")

# --- Limpar destaque da linha ---
def limpar_destaque_linha(rastreio):
    item_id = linhas_destacadas.get(rastreio)
    if item_id:
        tabela.item(item_id, tags=())
        del linhas_destacadas[rastreio]

# --- Resetar ---
def resetar():
    global ultimo_codigo, pug_atual, estado, contador_validos
    ultimo_codigo = None
    pug_atual = None
    estado = "aguardando_pug"
    contador_validos = 0
    # Adiciona uma linha em branco para começar o novo PUG
    linha_id = tabela.insert("", "end", values=("", "", "", ""))  # Linha em branco
    # Modifica a cor de fundo da linha em branco para azul
    tabela.item(linha_id, tags="linha_azul")
    # Aplica a tag de cor azul
    tabela.tag_configure("linha_azul", background="#ADD8E6")  # Azul claro
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
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), foreground="white", background="#0078D7")

main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

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

right_frame = tk.Frame(main_frame, bg="#1e1e1e", width=400)
right_frame.pack(side="right", fill="both", expand=False)

tabela = ttk.Treeview(right_frame, columns=("n", "pug", "rastreio", "etiqueta"), show="headings", height=10)
tabela.heading("n", text="N")
tabela.heading("pug", text="PUG")
tabela.heading("rastreio", text="Código de Rastreio")
tabela.heading("etiqueta", text="Etiqueta Last Mile")
tabela.column("n", anchor="center", width=50)
tabela.column("pug", anchor="center", width=180)
tabela.column("rastreio", anchor="center", width=180)
tabela.column("etiqueta", anchor="center", width=180)

scroll_y = ttk.Scrollbar(right_frame, orient="vertical", command=tabela.yview)
tabela.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")
tabela.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 5))

bottom_right_frame = tk.Frame(right_frame, bg="#1e1e1e")
bottom_right_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

tabela_pugs = ttk.Treeview(bottom_right_frame, columns=("pug", "contagem"), show="headings", height=4)
tabela_pugs.heading("pug", text="PUG")
tabela_pugs.heading("contagem", text="Qtd Pacotes")
tabela_pugs.column("pug", anchor="center", width=180)
tabela_pugs.column("contagem", anchor="center", width=180)
tabela_pugs.pack(fill="x")

root.mainloop()

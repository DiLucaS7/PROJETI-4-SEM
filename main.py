import tkinter as tk
from tkinter import messagebox, ttk
import db
import relatorios

# Centralizar a janela
def centralizar_janela(janela, largura=800, altura=800):
    tela_largura = janela.winfo_screenwidth()
    tela_altura = janela.winfo_screenheight()
    x = (tela_largura - largura) // 2
    y = (tela_altura - altura) // 2
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

# Configuração da interface e estilos
root = tk.Tk()
root.title("Sistema de PDV - Açaí")
root.geometry("800x640")
centralizar_janela(root, 800, 640)
root.configure(bg="#FFFFFF")

# Estilo personalizado
style = ttk.Style()
style.configure(
    "Rounded.TButton",
    font=("Arial", 12, "bold"),
    padding=10,
    relief="flat",
    anchor="center",
    width=25
)
style.map(
    "Rounded.TButton",
    background=[("active", "#E6E6E6"), ("!active", "#FFFFFF")],
    relief=[("active", "groove"), ("!active", "flat")]
)

# Título do sistema
titulo_frame = tk.Frame(root, bg="#FFFFFF")
titulo_frame.pack(pady=20)

titulo_principal = tk.Label(
    titulo_frame,
    text="SISTEMA\nDE\nPONTO DE VENDAS",
    font=("Arial", 24, "bold"),
    bg="#FFFFFF",
    fg="black",
    justify="center"
)
titulo_principal.pack()

subtitulo = tk.Label(
    titulo_frame,
    text="ENG. DA COMPUTAÇÃO, 4ª SEMESTRE.",
    font=("Arial", 14, "bold"),
    bg="#FFFFFF",
    fg="green"
)
subtitulo.pack()

# Botões centrais
botoes_frame = tk.Frame(root, bg="#FFFFFF")
botoes_frame.pack(pady=50)

# Funções principais
def abrir_cadastro_produto():
    janela_cadastro = tk.Toplevel(root)
    janela_cadastro.title("Cadastro de Produto")
    janela_cadastro.geometry("400x300")
    centralizar_janela(janela_cadastro, 400, 300)
    janela_cadastro.configure(bg="#FFFFFF")

    tk.Label(janela_cadastro, text="Nome do Produto").pack(pady=5)
    nome_produto = tk.Entry(janela_cadastro)
    nome_produto.pack()

    tk.Label(janela_cadastro, text="Preço por Litro (R$)").pack(pady=5)
    preco_produto = tk.Entry(janela_cadastro)
    preco_produto.pack()

    def salvar_produto():
        nome = nome_produto.get()
        preco = preco_produto.get()
        if nome and preco:
            resultado = db.salvar_produto(nome, preco)
            messagebox.showinfo("Resultado", resultado)
        else:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
            
    tk.Button(janela_cadastro, text="Salvar Produto", command=salvar_produto).pack(pady=10)

def abrir_listar_produtos():
    """Abre a janela para listar produtos com opções de alterar ou excluir."""
    janela_listar_produtos = tk.Toplevel(root)
    janela_listar_produtos.title("Lista de Produtos")
    janela_listar_produtos.geometry("800x400")
    centralizar_janela(janela_listar_produtos, 400, 300)
    janela_listar_produtos.configure(bg="#FFFFFF")

    frame_lista = tk.Frame(janela_listar_produtos, bg="#FFFFFF")
    frame_lista.pack(fill="both", expand=True)

    # Tabela de produtos
    produtos = db.listar_produtos()

    # Títulos da tabela
    tk.Label(frame_lista, text="ID", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
    tk.Label(frame_lista, text="Nome", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame_lista, text="Preço por Litro (R$)", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)

    for idx, (produto_id, nome, preco) in enumerate(produtos, start=1):
        tk.Label(frame_lista, text=produto_id).grid(row=idx, column=0, padx=5, pady=5)
        tk.Label(frame_lista, text=nome).grid(row=idx, column=1, padx=5, pady=5)
        tk.Label(frame_lista, text=f"R${preco:.2f}").grid(row=idx, column=2, padx=5, pady=5)

        # Botão para alterar o preço do produto
        tk.Button(frame_lista, text="Alterar Preço", 
                  command=lambda produto_id=produto_id, nome=nome: abrir_alterar_preco(produto_id, nome)).grid(row=idx, column=3, padx=5, pady=5)

        # Botão para excluir o produto
        tk.Button(frame_lista, text="Excluir", 
                  command=lambda produto_id=produto_id: excluir_produto(produto_id)).grid(row=idx, column=4, padx=5, pady=5)

def abrir_alterar_preco(produto_id, nome):
    """Abre uma janela para alterar o preço de um produto específico."""
    janela_alterar = tk.Toplevel(root)
    janela_alterar.title(f"Alterar Preço - {nome}")
    janela_alterar.geometry("400x200")
    centralizar_janela(janela_alterar, 400, 300)
    janela_alterar.configure(bg="#FFFFFF")

    tk.Label(janela_alterar, text=f"Alterar preço do produto: {nome}", font=("Arial", 12)).pack(pady=10)
    tk.Label(janela_alterar, text="Novo Preço (R$):").pack(pady=5)

    novo_preco_entry = tk.Entry(janela_alterar)
    novo_preco_entry.pack(pady=5)

    def salvar_alteracao():
        novo_preco = novo_preco_entry.get()
        if novo_preco:
            resultado = db.alterar_preco_produto_por_id(produto_id, novo_preco)
            messagebox.showinfo("Resultado", resultado)
            janela_alterar.destroy()  # Fecha a janela após salvar
        else:
            messagebox.showwarning("Atenção", "Por favor, insira o novo preço.")

    tk.Button(janela_alterar, text="Salvar Alteração", command=salvar_alteracao).pack(pady=10)

def excluir_produto(produto_id):
    """Exclui um produto do banco de dados."""
    confirmacao = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este produto?")
    if confirmacao:
        resultado = db.excluir_produto_por_id(produto_id)
        messagebox.showinfo("Resultado", resultado)
        abrir_listar_produtos()  # Recarrega a lista de produtos

def abrir_registrar_custos():
    janela_custo = tk.Toplevel(root)
    janela_custo.title("Registrar Custo da Saca")
    janela_custo.geometry("400x250")
    centralizar_janela(janela_custo, 400, 300)
    janela_custo.configure(bg="#FFFFFF")

    tk.Label(janela_custo, text="Valor da Saca (R$)").pack(pady=5)
    valor_custo = tk.Entry(janela_custo)
    valor_custo.pack()

    tk.Label(janela_custo, text="Quantidade de Sacas Compradas").pack(pady=5)
    quantidade_sacas = tk.Entry(janela_custo)
    quantidade_sacas.pack()

    def registrar_custo():
        valor = valor_custo.get()
        quantidade = quantidade_sacas.get()
        if valor and quantidade:
            resultado = db.registrar_custo("saca_acai", valor, quantidade)
            messagebox.showinfo("Resultado", resultado)
        else:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
    tk.Button(janela_custo, text="Salvar Custo", command=registrar_custo).pack(pady=20)

def abrir_registro_venda():
    janela_venda = tk.Toplevel(root)
    janela_venda.title("Registrar Venda")
    janela_venda.geometry("400x350")
    centralizar_janela(janela_venda, 400, 300)
    janela_venda.configure(bg="#FFFFFF")

    tk.Label(janela_venda, text="Produto").pack(pady=5)
    produto_combo = ttk.Combobox(janela_venda, values=db.carregar_produtos())
    produto_combo.pack()

    tk.Label(janela_venda, text="Quantidade de Produtos Vendidos").pack(pady=5)
    quantidade_produto = tk.Entry(janela_venda)
    quantidade_produto.pack()

    tk.Label(janela_venda, text="Volume por Unidade").pack(pady=5)
    volume_combo = ttk.Combobox(janela_venda, values=["1 Litro", "500 ml"])
    volume_combo.pack()

    def registrar_venda():
        produto = produto_combo.get()
        quantidade = quantidade_produto.get()
        volume_tipo = volume_combo.get()
        preco_por_litro = db.buscar_preco_produto(produto)

        if preco_por_litro is None:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        try:
            quantidade = float(quantidade)
            if volume_tipo == "1 Litro":
                volume_total = quantidade  # 1 litro por unidade
                preco_total = quantidade * preco_por_litro
            elif volume_tipo == "500 ml":
                volume_total = quantidade * 0.5  # 500ml = 0.5 litro
                preco_total = volume_total * preco_por_litro
            else:
                messagebox.showwarning("Atenção", "Por favor, selecione o volume.")
                return

            if produto and quantidade > 0:
                resultado = db.registrar_venda(produto, volume_total, preco_total)
                messagebox.showinfo("Resultado", resultado)
            else:
                messagebox.showwarning("Atenção", "Por favor, preencha todos os campos corretamente.")
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida. Insira um número.")

    tk.Button(janela_venda, text="Registrar Venda", command=registrar_venda).pack(pady=20)

def abrir_relatorio_vendas():
    """Exibe o relatório de vendas detalhado."""
    relatorio = db.obter_relatorio_vendas_com_total()

    vendas = relatorio["vendas"]
    total_geral = relatorio["total_geral"]

    janela_relatorio = tk.Toplevel(root)
    janela_relatorio.title("Relatório de Vendas")
    janela_relatorio.geometry("800x600")
    centralizar_janela(janela_relatorio, 400, 300)
    janela_relatorio.configure(bg="#FFFFFF")

    frame_relatorio = tk.Frame(janela_relatorio, bg="#FFFFFF")
    frame_relatorio.pack(fill="both", expand=True)

    tk.Label(frame_relatorio, text="Data", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
    tk.Label(frame_relatorio, text="Produto", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame_relatorio, text="Quantidade", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
    tk.Label(frame_relatorio, text="Valor Total", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5)

    for idx, venda in enumerate(vendas, start=1):
        tk.Label(frame_relatorio, text=venda[0]).grid(row=idx, column=0, padx=5, pady=5)
        tk.Label(frame_relatorio, text=venda[1]).grid(row=idx, column=1, padx=5, pady=5)
        tk.Label(frame_relatorio, text=f"{venda[2]:.2f}").grid(row=idx, column=2, padx=5, pady=5)
        tk.Label(frame_relatorio, text=f"R${venda[3]:.2f}").grid(row=idx, column=3, padx=5, pady=5)

    tk.Label(janela_relatorio, text=f"Total Geral: R${total_geral:.2f}", font=("Arial", 12, "bold")).pack(pady=10)

def abrir_relatorio_sacas_compradas():
    """Exibe o relatório de sacas compradas."""
    relatorio = db.obter_relatorio_geral()

    sacas_compradas = relatorio["sacas_compradas"]

    janela_relatorio_sacas = tk.Toplevel(root)
    janela_relatorio_sacas.title("Relatório de Sacas Compradas")
    janela_relatorio_sacas.geometry("800x600")
    centralizar_janela(janela_relatorio_sacas, 400, 300)
    janela_relatorio_sacas.configure(bg="#FFFFFF")

    frame_relatorio = tk.Frame(janela_relatorio_sacas, bg="#FFFFFF")
    frame_relatorio.pack(fill="both", expand=True)

    tk.Label(frame_relatorio, text="Data", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
    tk.Label(frame_relatorio, text="Quantidade de Sacas", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame_relatorio, text="Valor Total (R$)", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)

    for idx, saca in enumerate(sacas_compradas, start=1):
        tk.Label(frame_relatorio, text=saca[0]).grid(row=idx, column=0, padx=5, pady=5)
        tk.Label(frame_relatorio, text=f"{saca[1]:.2f}").grid(row=idx, column=1, padx=5, pady=5)
        tk.Label(frame_relatorio, text=f"R${saca[2]:.2f}").grid(row=idx, column=2, padx=5, pady=5)

    # Soma total
    total_sacas = sum(s[1] for s in sacas_compradas)
    total_valor = sum(s[2] for s in sacas_compradas)

    tk.Label(janela_relatorio_sacas, text=f"Total Geral de Sacas Compradas: {total_sacas:.2f}", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Label(janela_relatorio_sacas, text=f"Valor Total: R${total_valor:.2f}", font=("Arial", 12, "bold")).pack(pady=5)

def abrir_comparativo_sacas_vendas():
    """Exibe o comparativo entre sacas compradas e vendas realizadas."""
    relatorio = relatorios.obter_comparativo_sacas_vendas()

    janela_comparativo = tk.Toplevel(root)
    janela_comparativo.title("Comparativo Sacas x Vendas")
    janela_comparativo.geometry("900x600")
    centralizar_janela(janela_comparativo, 500, 300)
    janela_comparativo.configure(bg="#FFFFFF")

    frame_relatorio = tk.Frame(janela_comparativo, bg="#FFFFFF")
    frame_relatorio.pack(fill="both", expand=True)

    tk.Label(frame_relatorio, text="Data", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
    tk.Label(frame_relatorio, text="Custo Total Sacas", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame_relatorio, text="Receita Total Vendas", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
    tk.Label(frame_relatorio, text="Lucro/Prejuízo", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5)

    for idx, linha in enumerate(relatorio, start=1):
        tk.Label(frame_relatorio, text=linha[0]).grid(row=idx, column=0, padx=5, pady=5)
        tk.Label(frame_relatorio, text=f"R${linha[1]:.2f}").grid(row=idx, column=1, padx=5, pady=5)
        tk.Label(frame_relatorio, text=f"R${linha[2]:.2f}").grid(row=idx, column=2, padx=5, pady=5)
        tk.Label(frame_relatorio, text=f"R${linha[3]:.2f}").grid(row=idx, column=3, padx=5, pady=5)


botoes_texto = [
    "Cadastro de Produto", 
    "Registrar Custo da Saca", 
    "Registrar Venda", 
    "Listar Produtos", 
    "Relatório de Vendas", 
    "Relatório de Sacas Compradas", 
    "Comparativo Sacas x Vendas"
]

def abrir_janela(texto):
    if texto == "Cadastro de Produto":
        abrir_cadastro_produto()
    elif texto == "Registrar Custo da Saca":
        abrir_registrar_custos()
    elif texto == "Registrar Venda":
        abrir_registro_venda()
    elif texto == "Listar Produtos":
        abrir_listar_produtos()
    elif texto == "Relatório de Vendas":
        abrir_relatorio_vendas()
    elif texto == "Relatório de Sacas Compradas":
        abrir_relatorio_sacas_compradas()
    elif texto == "Comparativo Sacas x Vendas":
        abrir_comparativo_sacas_vendas()


for i, texto in enumerate(botoes_texto):
        row = i // 2
        col = i % 2
        ttk.Button(
        botoes_frame,
        text=texto,
        command=lambda t=texto: abrir_janela(t),
        style="Rounded.TButton"
    ).grid(row=row, column=col, padx=20, pady=10, ipadx=10, ipady=10)


# Inicializa o banco de dados
db.init_db()

# Loop principal
root.mainloop()

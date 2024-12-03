import sqlite3
from datetime import datetime, timedelta


def init_db():
    """Inicializa o banco de dados criando tabelas e índices."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()

    # Criação das tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            preco_por_litro REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            quantidade_vendida REAL,
            preco_por_litro REAL,
            total REAL,
            data_venda DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            quantidade REAL NOT NULL,
            data DATE DEFAULT CURRENT_DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            preco REAL NOT NULL,
            data DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    ''')

    # Índices para melhorar o desempenho
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_vendas ON vendas (data_venda)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_custos ON custos (data)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_historico_precos ON historico_precos (data)")

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso.")
def obter_relatorio_vendas_com_total():
    """Gera um relatório detalhado de vendas com total consolidado."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        # Consulta para obter as vendas detalhadas
        cursor.execute('''
            SELECT 
                v.data_venda AS data,
                p.nome AS produto,
                v.quantidade_vendida AS quantidade,
                v.total AS valor_total
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            ORDER BY v.data_venda ASC
        ''')
        vendas = cursor.fetchall()

        # Consulta para calcular o total consolidado de todas as vendas
        cursor.execute('''
            SELECT SUM(total) AS total_geral
            FROM vendas
        ''')
        total_geral = cursor.fetchone()[0] or 0  # Se não houver vendas, retorna 0.

        return {
            "vendas": vendas,  # Lista detalhada de vendas
            "total_geral": total_geral  # Soma total das vendas
        }
    finally:
        conn.close()
def obter_relatorio_vendas_com_total():
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.data_venda, p.nome, v.quantidade_vendida, v.total
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        ORDER BY v.data_venda ASC
    ''')
    vendas = cursor.fetchall()

    cursor.execute('SELECT SUM(total) FROM vendas')
    total_geral = cursor.fetchone()[0] or 0

    conn.close()
    return {"vendas": vendas, "total_geral": total_geral}
def obter_relatorio_geral():
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT data, quantidade, valor * quantidade AS valor_total
        FROM custos
        WHERE tipo = 'saca_acai'
        ORDER BY data ASC
    ''')
    sacas_compradas = cursor.fetchall()
    conn.close()
    return {"sacas_compradas": sacas_compradas}
def obter_comparativo_sacas_vendas():
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            DATE(v.data_venda) AS data,
            COALESCE(
                (SELECT SUM(valor * quantidade)
                 FROM custos
                 WHERE DATE(custos.data) = DATE(v.data_venda)
                 AND custos.tipo = 'saca_acai'), 0) AS custo_total_sacas,
            SUM(v.total) AS receita_total_vendas,
            SUM(v.total) - COALESCE(
                (SELECT SUM(valor * quantidade)
                 FROM custos
                 WHERE DATE(custos.data) = DATE(v.data_venda)
                 AND custos.tipo = 'saca_acai'), 0) AS lucro_prejuizo
        FROM vendas v
        GROUP BY DATE(v.data_venda)
    ''')
    comparativo = cursor.fetchall()
    conn.close()
    return comparativo

def alterar_preco_produto_por_id(produto_id, novo_preco):
    """Altera o preço de um produto usando seu ID."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE produtos SET preco_por_litro = ? WHERE id = ?", (float(novo_preco), produto_id))
        conn.commit()
        return "Preço do produto atualizado com sucesso!"
    finally:
        conn.close()
        
def excluir_produto_por_id(produto_id):
    """Exclui um produto do banco de dados usando seu ID."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        return "Produto excluído com sucesso!"
    finally:
        conn.close()

def salvar_produto(nome, preco):
    """Salva um novo produto no banco de dados."""
    try:
        conn = sqlite3.connect('pdv_acai.db')
        cursor = conn.cursor()

        # Verifica se a tabela 'produtos' existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos'")
        tabela = cursor.fetchone()
        if not tabela:
            print("Erro: A tabela 'produtos' não existe.")
            return "Erro: A tabela 'produtos' não foi encontrada no banco de dados."

        # Insere o produto
        cursor.execute("INSERT INTO produtos (nome, preco_por_litro) VALUES (?, ?)", (nome, float(preco)))
        conn.commit()
        return "Produto cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return "Erro: Produto já cadastrado."
    finally:
        conn.close()

def salvar_produto(nome, preco):
    """Salva um novo produto no banco de dados."""
    try:
        conn = sqlite3.connect('pdv_acai.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, preco_por_litro) VALUES (?, ?)", (nome, float(preco)))
        conn.commit()
        return "Produto cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return "Erro: Produto já cadastrado."
    finally:
        conn.close()


def registrar_venda(produto_nome, quantidade, preco_total):
    """Registra uma venda no banco de dados."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, preco_por_litro FROM produtos WHERE nome = ?", (produto_nome,))
        produto = cursor.fetchone()

        if produto:
            produto_id, preco_por_litro = produto

            if quantidade <= 0 or preco_total <= 0:
                return "Erro: Quantidade ou valor inválido."

            cursor.execute(
                "INSERT INTO vendas (produto_id, quantidade_vendida, preco_por_litro, total) VALUES (?, ?, ?, ?)",
                (produto_id, float(quantidade), preco_por_litro, preco_total)
            )
            conn.commit()
            return "Venda registrada com sucesso!"
        else:
            return "Erro: Produto não encontrado."
    except sqlite3.Error as e:
        return f"Erro ao registrar a venda: {e}"
    finally:
        conn.close()


def registrar_custo(tipo, valor, quantidade):
    """Registra um custo no banco de dados."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO custos (tipo, valor, quantidade) VALUES (?, ?, ?)", (tipo, float(valor), float(quantidade)))
        conn.commit()
        return "Custo registrado com sucesso!"
    finally:
        conn.close()


def alterar_preco_produto(produto_nome, novo_preco):
    """Altera o preço de um produto."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE produtos SET preco_por_litro = ? WHERE nome = ?", (float(novo_preco), produto_nome))
        conn.commit()
        return "Preço do produto atualizado com sucesso!"
    finally:
        conn.close()


def listar_produtos():
    """Lista todos os produtos cadastrados no banco de dados."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, preco_por_litro FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos


def listar_vendas():
    """Lista todas as vendas registradas no banco de dados."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vendas")
    vendas = cursor.fetchall()
    conn.close()
    return vendas


def buscar_preco_produto(produto_nome):
    """Busca o preço por litro de um produto pelo nome."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    cursor.execute("SELECT preco_por_litro FROM produtos WHERE nome = ?", (produto_nome,))
    produto = cursor.fetchone()
    conn.close()
    return produto[0] if produto else None


def carregar_produtos():
    """Carrega os nomes dos produtos cadastrados."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM produtos")
    produtos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return produtos


def obter_relatorio_vendas_diario(data):
    """Obtém o relatório de vendas para uma data específica."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT p.nome, v.quantidade_vendida, v.preco_por_litro, v.total
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            WHERE DATE(v.data_venda) = DATE(?)
            ORDER BY p.nome
        ''', (data,))
        vendas_diarias = cursor.fetchall()
        return vendas_diarias
    finally:
        conn.close()


def verificar_tabelas():
    """Verifica as tabelas existentes no banco de dados."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    conn.close()
    print("Tabelas no banco de dados:", tabelas)

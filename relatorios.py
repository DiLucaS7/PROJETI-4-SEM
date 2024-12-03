import sqlite3


def init_db():
    """Inicializa o banco de dados."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()


def media_sacas_compradas(data_inicio, data_fim):
    """Calcula a média de sacas compradas em um período."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT AVG(quantidade), AVG(valor * quantidade)
            FROM custos
            WHERE tipo = 'saca_acai' AND DATE(data) BETWEEN DATE(?) AND DATE(?)
        ''', (data_inicio, data_fim))
        resultado = cursor.fetchone()
        return {
            "media_quantidade_sacas": resultado[0] or 0,
            "media_valor_total": resultado[1] or 0
        }
    finally:
        conn.close()


def media_acai_vendido(data_inicio, data_fim):
    """Calcula a média de litros vendidos e o valor total no período."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT AVG(quantidade_vendida), AVG(total)
            FROM vendas
            WHERE DATE(data_venda) BETWEEN DATE(?) AND DATE(?)
        ''', (data_inicio, data_fim))
        resultado = cursor.fetchone()
        return {
            "media_litros_vendidos": resultado[0] or 0,
            "media_valor_vendas": resultado[1] or 0
        }
    finally:
        conn.close()


def calcular_lucro_diario(data):
    """Calcula o lucro diário baseado nas vendas e custos."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT SUM(total)
            FROM vendas
            WHERE DATE(data_venda) = DATE(?)
        ''', (data,))
        total_vendas = cursor.fetchone()[0] or 0

        cursor.execute('''
            SELECT SUM(valor * quantidade)
            FROM custos
            WHERE tipo = 'saca_acai' AND DATE(data) = DATE(?)
        ''', (data,))
        custo_sacas = cursor.fetchone()[0] or 0

        lucro_diario = total_vendas - custo_sacas
        return {
            "data": data,
            "total_vendas": total_vendas,
            "custo_sacas": custo_sacas,
            "lucro_diario": lucro_diario
        }
    finally:
        conn.close()


def obter_comparativo_sacas_vendas():
    """Compara custos das sacas e receitas das vendas por dia."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT 
                DATE(v.data_venda) AS data,
                COALESCE(
                    (SELECT SUM(valor * quantidade)
                     FROM custos
                     WHERE DATE(custos.data) = DATE(v.data_venda)
                     AND custos.tipo = 'saca_acai'
                    ), 0) AS custo_total_sacas,
                SUM(v.total) AS receita_total_litros,
                SUM(v.total) - COALESCE(
                    (SELECT SUM(valor * quantidade)
                     FROM custos
                     WHERE DATE(custos.data) = DATE(v.data_venda)
                     AND custos.tipo = 'saca_acai'
                    ), 0) AS lucro_prejuizo
            FROM vendas v
            GROUP BY DATE(v.data_venda)
        ''')
        return cursor.fetchall()
    finally:
        conn.close()


def obter_vendas_por_periodo(periodo):
    """Obtém as vendas agrupadas por dia, semana ou mês."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        if periodo == "dia":
            query = '''
                SELECT DATE(data_venda) AS periodo, SUM(total) AS total_vendas
                FROM vendas
                GROUP BY DATE(data_venda)
                ORDER BY DATE(data_venda) ASC
            '''
        elif periodo == "semana":
            query = '''
                SELECT strftime('%Y-%W', data_venda) AS periodo, SUM(total) AS total_vendas
                FROM vendas
                GROUP BY periodo
                ORDER BY periodo ASC
            '''
        elif periodo == "mes":
            query = '''
                SELECT strftime('%Y-%m', data_venda) AS periodo, SUM(total) AS total_vendas
                FROM vendas
                GROUP BY periodo
                ORDER BY periodo ASC
            '''
        else:
            return []

        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()


def obter_relatorio_geral():
    """Gera um relatório completo de vendas, produtos e sacas."""
    conn = sqlite3.connect('pdv_acai.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT v.data_venda, p.nome, v.quantidade_vendida, v.preco_por_litro, v.total
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            ORDER BY v.data_venda ASC
        ''')
        vendas_realizadas = cursor.fetchall()

        cursor.execute('''
            SELECT p.nome, SUM(v.quantidade_vendida), SUM(v.total)
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            GROUP BY p.nome
            ORDER BY SUM(v.quantidade_vendida) DESC
        ''')
        produtos_vendidos = cursor.fetchall()

        cursor.execute('''
            SELECT data, quantidade, valor * quantidade AS valor_total
            FROM custos
            WHERE tipo = 'saca_acai'
            ORDER BY data ASC
        ''')
        sacas_compradas = cursor.fetchall()

        return {
            "vendas_realizadas": vendas_realizadas,
            "produtos_vendidos": produtos_vendidos,
            "sacas_compradas": sacas_compradas
        }
    finally:
        conn.close()

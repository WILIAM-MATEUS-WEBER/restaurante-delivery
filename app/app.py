from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'restaurante-delivery-secret-2024')

# ─── Conexão com banco ───────────────────────────────────────────────────────
def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432'),
        database=os.environ.get('DB_NAME', 'restaurante'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres')
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(120) NOT NULL,
            descricao TEXT,
            preco NUMERIC(10,2) NOT NULL,
            categoria VARCHAR(60),
            disponivel BOOLEAN DEFAULT TRUE,
            criado_em TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(120) NOT NULL,
            telefone VARCHAR(20),
            endereco TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            status VARCHAR(30) DEFAULT 'recebido',
            total NUMERIC(10,2) DEFAULT 0,
            observacao TEXT,
            criado_em TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS itens_pedido (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER REFERENCES pedidos(id),
            produto_id INTEGER REFERENCES produtos(id),
            quantidade INTEGER NOT NULL,
            preco_unit NUMERIC(10,2) NOT NULL
        );
    """)
    # Seed inicial
    cur.execute("SELECT COUNT(*) FROM produtos")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO produtos (nome, descricao, preco, categoria) VALUES
            ('X-Burguer Clássico', 'Pão brioche, blend 180g, queijo, alface, tomate', 28.90, 'Lanches'),
            ('X-Bacon Duplo', 'Pão brioche, blend duplo 360g, bacon, queijo, maionese', 42.50, 'Lanches'),
            ('Batata Frita M', 'Batata palito crocante tamanho médio', 14.90, 'Acompanhamentos'),
            ('Batata Frita G', 'Batata palito crocante tamanho grande', 19.90, 'Acompanhamentos'),
            ('Coca-Cola Lata', 'Coca-Cola lata 350ml gelada', 7.00, 'Bebidas'),
            ('Suco de Laranja', 'Suco natural de laranja 400ml', 9.90, 'Bebidas'),
            ('Pizza Margherita', 'Molho de tomate, mozzarella, manjericão, borda recheada', 55.00, 'Pizzas'),
            ('Pizza Pepperoni', 'Molho de tomate, mozzarella, pepperoni, orégano', 62.00, 'Pizzas')
        """)
    conn.commit()
    cur.close()
    conn.close()

# ─── Rotas principais ────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── Produtos ──────────────────────────────────────────────────────────────────
@app.route('/produtos')
def produtos():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM produtos ORDER BY categoria, nome")
    items = cur.fetchall()
    cur.close(); conn.close()
    return render_template('produtos.html', produtos=items)

@app.route('/produtos/novo', methods=['GET', 'POST'])
def novo_produto():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO produtos (nome, descricao, preco, categoria, disponivel)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form['nome'],
            request.form['descricao'],
            request.form['preco'],
            request.form['categoria'],
            'disponivel' in request.form
        ))
        conn.commit(); cur.close(); conn.close()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('produtos'))
    return render_template('form_produto.html', produto=None)

@app.route('/produtos/editar/<int:pid>', methods=['GET', 'POST'])
def editar_produto(pid):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if request.method == 'POST':
        cur.execute("""
            UPDATE produtos SET nome=%s, descricao=%s, preco=%s, categoria=%s, disponivel=%s
            WHERE id=%s
        """, (
            request.form['nome'], request.form['descricao'],
            request.form['preco'], request.form['categoria'],
            'disponivel' in request.form, pid
        ))
        conn.commit(); cur.close(); conn.close()
        flash('Produto atualizado!', 'success')
        return redirect(url_for('produtos'))
    cur.execute("SELECT * FROM produtos WHERE id=%s", (pid,))
    produto = cur.fetchone()
    cur.close(); conn.close()
    return render_template('form_produto.html', produto=produto)

@app.route('/produtos/deletar/<int:pid>', methods=['POST'])
def deletar_produto(pid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE id=%s", (pid,))
    conn.commit(); cur.close(); conn.close()
    flash('Produto removido.', 'info')
    return redirect(url_for('produtos'))

# ── Clientes ──────────────────────────────────────────────────────────────────
@app.route('/clientes')
def clientes():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM clientes ORDER BY nome")
    items = cur.fetchall()
    cur.close(); conn.close()
    return render_template('clientes.html', clientes=items)

@app.route('/clientes/novo', methods=['GET', 'POST'])
def novo_cliente():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO clientes (nome, telefone, endereco) VALUES (%s, %s, %s)
        """, (request.form['nome'], request.form['telefone'], request.form['endereco']))
        conn.commit(); cur.close(); conn.close()
        flash('Cliente cadastrado!', 'success')
        return redirect(url_for('clientes'))
    return render_template('form_cliente.html', cliente=None)

@app.route('/clientes/editar/<int:cid>', methods=['GET', 'POST'])
def editar_cliente(cid):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if request.method == 'POST':
        cur.execute("""
            UPDATE clientes SET nome=%s, telefone=%s, endereco=%s WHERE id=%s
        """, (request.form['nome'], request.form['telefone'], request.form['endereco'], cid))
        conn.commit(); cur.close(); conn.close()
        flash('Cliente atualizado!', 'success')
        return redirect(url_for('clientes'))
    cur.execute("SELECT * FROM clientes WHERE id=%s", (cid,))
    cliente = cur.fetchone()
    cur.close(); conn.close()
    return render_template('form_cliente.html', cliente=cliente)

# ── Pedidos ───────────────────────────────────────────────────────────────────
@app.route('/pedidos')
def pedidos():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT p.*, c.nome AS cliente_nome
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.criado_em DESC
    """)
    items = cur.fetchall()
    cur.close(); conn.close()
    return render_template('pedidos.html', pedidos=items)

@app.route('/pedidos/novo', methods=['GET', 'POST'])
def novo_pedido():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if request.method == 'POST':
        # Cria pedido
        cur2 = conn.cursor()
        cur2.execute("""
            INSERT INTO pedidos (cliente_id, observacao, status) VALUES (%s, %s, 'recebido')
            RETURNING id
        """, (request.form['cliente_id'], request.form.get('observacao', '')))
        pedido_id = cur2.fetchone()[0]

        # Itens
        produto_ids = request.form.getlist('produto_id[]')
        quantidades = request.form.getlist('quantidade[]')
        total = 0
        for pid, qty in zip(produto_ids, quantidades):
            if pid and int(qty) > 0:
                cur.execute("SELECT preco FROM produtos WHERE id=%s", (pid,))
                preco = cur.fetchone()['preco']
                cur2.execute("""
                    INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unit)
                    VALUES (%s, %s, %s, %s)
                """, (pedido_id, pid, qty, preco))
                total += float(preco) * int(qty)

        cur2.execute("UPDATE pedidos SET total=%s WHERE id=%s", (total, pedido_id))
        conn.commit(); cur.close(); cur2.close(); conn.close()
        flash(f'Pedido #{pedido_id} criado! Total: R$ {total:.2f}', 'success')
        return redirect(url_for('pedidos'))

    cur.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes = cur.fetchall()
    cur.execute("SELECT id, nome, preco, categoria FROM produtos WHERE disponivel=TRUE ORDER BY categoria, nome")
    produtos = cur.fetchall()
    cur.close(); conn.close()
    return render_template('form_pedido.html', clientes=clientes, produtos=produtos)

@app.route('/pedidos/status/<int:pid>', methods=['POST'])
def atualizar_status(pid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE pedidos SET status=%s WHERE id=%s", (request.form['status'], pid))
    conn.commit(); cur.close(); conn.close()
    flash('Status atualizado!', 'success')
    return redirect(url_for('pedidos'))

@app.route('/pedidos/detalhe/<int:pid>')
def detalhe_pedido(pid):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT p.*, c.nome AS cliente_nome, c.telefone, c.endereco
        FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
        WHERE p.id=%s
    """, (pid,))
    pedido = cur.fetchone()
    cur.execute("""
        SELECT ip.*, pr.nome AS produto_nome
        FROM itens_pedido ip JOIN produtos pr ON pr.id = ip.produto_id
        WHERE ip.pedido_id=%s
    """, (pid,))
    itens = cur.fetchall()
    cur.close(); conn.close()
    return render_template('detalhe_pedido.html', pedido=pedido, itens=itens)

# ── API JSON (para futuras integrações) ──────────────────────────────────────
@app.route('/api/produtos')
def api_produtos():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM produtos WHERE disponivel=TRUE ORDER BY categoria, nome")
    items = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(items)

@app.route('/api/pedidos')
def api_pedidos():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT p.*, c.nome AS cliente_nome FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id ORDER BY p.criado_em DESC LIMIT 50
    """)
    items = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(items)

@app.route('/health')
def health():
    try:
        conn = get_db(); conn.close()
        return jsonify({"status": "ok", "db": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')

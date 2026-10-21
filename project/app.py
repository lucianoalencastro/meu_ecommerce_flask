from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///ecommerce.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    products = db.execute("SELECT * FROM products LIMIT 4")
    return render_template("shop/index.html", products=products)


@app.route("/products")
def products():
    products = db.execute("SELECT * FROM products")
    return render_template("shop/products.html", products=products)


@app.route("/product")
def product():
    # Pega o ID do produto passado pela URL (ex: /product?id=1)
    product_id = request.args.get("id")

    if not product_id:
        return redirect("/")

    # Busca o produto específico no banco de dados
    products = db.execute("SELECT * FROM products WHERE id = ?", product_id)

    if not products:
        return "Produto não encontrado", 404

    # Renderiza o template enviando o primeiro resultado encontrado
    return render_template("shop/product.html", product=products[0])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registra um novo usuário"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validações básicas
        if not username or not password or not confirmation:
            return "Preencha todos os campos!", 400
        if password != confirmation:
            return "As senhas não coincidem!", 400

        # Verifica se o usuário já existe
        hash_password = generate_password_hash(password)
        try:
            new_user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username, hash_password
            )
        except Exception:
            return "Nome de usuário já existe!", 400

        # Loga o usuário automaticamente após o cadastro
        session["user_id"] = new_user_id
        return redirect("/")

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Faz o login do usuário"""
    # Esquece qualquer user_id anterior
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Preencha usuário e senha!", 400

        # Consulta o banco de dados pelo usuário
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Verifica se o usuário existe e a senha está correta
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Usuário e/ou senha inválidos!", 400

        # Salva o ID do usuário na sessão
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    """Encerra a sessão do usuário"""
    session.clear()
    return redirect("/")


@app.route("/cart")
@login_required
def cart():
    # Busca os itens do carrinho e seleciona o ID real do produto
    cart_items = db.execute(
        "SELECT products.id AS product_id, products.name, products.price, products.image, cart_items.id, cart_items.quantity "
        "FROM cart_items JOIN products ON cart_items.product_id = products.id "
        "WHERE cart_items.user_id = ?",
        session["user_id"]
    )

    return render_template("shop/cart.html", cart=cart_items)


@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    product_id = request.form.get("product_id")

    # 1. Captura a quantidade selecionada no input do product.html (se não vier, assume 1)
    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        quantity = 1

    if not product_id:
        return redirect("/products")

    # 2. Busca o produto para validar o estoque disponível no banco
    product = db.execute("SELECT * FROM products WHERE id = ?", product_id)
    if not product:
        return "Produto não encontrado", 404

    stock_disponivel = product[0]["stock"]

    # Valida se a quantidade solicitada não é maior que o estoque atual
    if quantity > stock_disponivel:
        return "Quantidade solicitada maior que o estoque disponível!", 400

    # 3. Verifica se o produto já existe no carrinho do usuário
    existing = db.execute(
        "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?",
        session["user_id"], product_id
    )

    if existing:
        # Incrementa a quantidade no carrinho
        db.execute(
            "UPDATE cart_items SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?",
            quantity, session["user_id"], product_id
        )
    else:
        # Insere o item com a quantidade escolhida
        db.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
            session["user_id"], product_id, quantity
        )

    # 4. Diminui a quantidade correspondente no estoque da tabela de produtos
    db.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ?",
        quantity, product_id
    )

    return redirect("/cart")


@app.route("/remove_from_cart", methods=["POST"])
@login_required
def remove_from_cart():
    cart_id = request.form.get("cart_id")

    if not cart_id:
        return redirect("/cart")

    # Busca o item no carrinho e o produto correspondente para saber o ID do produto e a quantidade atual
    item = db.execute(
        "SELECT * FROM cart_items WHERE id = ? AND user_id = ?",
        cart_id, session["user_id"]
    )

    if not item:
        return redirect("/cart")

    product_id = item[0]["product_id"]
    current_quantity = item[0]["quantity"]

    if current_quantity > 1:
        # Se tem mais de 1, diminui apenas 1 unidade da quantidade no carrinho
        db.execute(
            "UPDATE cart_items SET quantity = quantity - 1 WHERE id = ?",
            cart_id
        )
    else:
        # Se a quantidade for 1, remove o item completamente do carrinho
        db.execute(
            "DELETE FROM cart_items WHERE id = ?",
            cart_id
        )

    # Devolve 1 unidade de volta para o estoque do produto
    db.execute(
        "UPDATE products SET stock = stock + 1 WHERE id = ?",
        product_id
    )

    return redirect("/cart")


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "POST":
        # 1. Busca os itens do carrinho e junta com os produtos para ter o preço atual
        cart_items = db.execute(
            "SELECT products.id AS product_id, products.price, cart_items.quantity "
            "FROM cart_items JOIN products ON cart_items.product_id = products.id "
            "WHERE cart_items.user_id = ?",
            session["user_id"]
        )

        if not cart_items:
            return redirect("/cart")

        # 2. Calcula o valor total do pedido
        total = sum(item["price"] * item["quantity"] for item in cart_items)

        # 3. Insere na tabela 'orders' e recupera o ID do pedido gerado
        cursor = db.execute(
            "INSERT INTO orders (user_id, total, status) VALUES (?, ?, ?)",
            session["user_id"], total, "concluido"
        )

        # Como o helper do CS50 (cs50 library) retorna o id do último insert diretamente ou via cursor:
        # (Se a sua função db.execute retornar o ID do insert diretamente:)
        order_id = cursor

        # 4. Insere cada item do carrinho na tabela 'order_items'
        for item in cart_items:
            db.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                order_id, item["product_id"], item["quantity"], item["price"]
            )

        # 5. Esvazia o carrinho do usuário
        db.execute(
            "DELETE FROM cart_items WHERE user_id = ?",
            session["user_id"]
        )

        # 6. Redireciona para a página de pedidos
        return redirect("/orders")

    else:
        # Método GET: Exibe a página de checkout com os itens do carrinho
        cart_items = db.execute(
            "SELECT products.name, products.price, cart_items.quantity "
            "FROM cart_items JOIN products ON cart_items.product_id = products.id "
            "WHERE cart_items.user_id = ?",
            session["user_id"]
        )

        # Calcula o subtotal para exibir na tela de checkout
        subtotal = sum(item["price"] * item["quantity"] for item in cart_items)

        return render_template("orders/checkout.html", cart=cart_items, subtotal=subtotal)


@app.route("/orders")
@login_required
def orders():
    # Busca todos os pedidos do usuário logado
    user_orders = db.execute(
        "SELECT id, total, status, timestamp FROM orders WHERE user_id = ? ORDER BY timestamp DESC",
        session["user_id"]
    )

    # Para cada pedido, busca os itens comprados usando uma chave diferente de 'items'
    for order in user_orders:
        order["product_list"] = db.execute(
            "SELECT products.name, products.image, order_items.quantity, order_items.price "
            "FROM order_items JOIN products ON order_items.product_id = products.id "
            "WHERE order_items.order_id = ?",
            order["id"]
        )

    return render_template("orders/orders.html", orders=user_orders)

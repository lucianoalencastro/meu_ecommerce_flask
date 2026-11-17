import uuid
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session

from helpers import login_required
from repositories import ProductRepository, CartRepository, OrderRepository, UserRepository
from services import ProductService, CartService, CheckoutService, AuthService

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///ecommerce.db")

# Injeção de Dependências (Repositories -> Services)
product_repo = ProductRepository(db)
cart_repo = CartRepository(db)
order_repo = OrderRepository(db)
user_repo = UserRepository(db)

product_service = ProductService(product_repo)
cart_service = CartService(cart_repo, product_repo)
checkout_service = CheckoutService(order_repo, cart_repo)
auth_service = AuthService(user_repo)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.context_processor
def inject_cart_count():
    if "user_id" in session:
        count = cart_service.get_cart_count(session["user_id"])
        return {"cart_count": count}
    return {"cart_count": 0}


# --- ROTAS DE PRODUTOS ---

@app.route("/")
def index():
    products = product_service.get_featured_products()
    return render_template("shop/index.html", products=products)


@app.route("/products")
def products():
    products = product_service.get_all_products()
    return render_template("shop/products.html", products=products)


@app.route("/product")
def product():
    product_id = request.args.get("id")
    if not product_id:
        return redirect("/")

    product = product_service.get_product_by_id(product_id)
    if not product:
        return "Produto não encontrado", 404

    return render_template("shop/product.html", product=product)


# --- ROTAS DE AUTENTICAÇÃO ---

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = auth_service.register(
            request.form.get("username"),
            request.form.get("password"),
            request.form.get("confirmation")
        )
        if not result["success"]:
            return result["message"], result["status"]

        session["user_id"] = result["user_id"]
        return redirect("/")

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        result = auth_service.login(
            request.form.get("username"),
            request.form.get("password")
        )
        if not result["success"]:
            return result["message"], result["status"]

        session["user_id"] = result["user_id"]
        return redirect("/")

    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


# --- ROTAS DO CARRINHO ---

@app.route("/cart")
@login_required
def cart():
    cart_items = cart_service.get_user_cart(session["user_id"])
    return render_template("shop/cart.html", cart=cart_items)


@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    product_id = request.form.get("product_id")
    if not product_id:
        return redirect("/products")

    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        quantity = 1

    result = cart_service.add_item(session["user_id"], product_id, quantity)
    if not result["success"]:
        return result["message"], result["status"]

    return redirect("/cart")


@app.route("/remove_from_cart", methods=["POST"])
@login_required
def remove_from_cart():
    cart_id = request.form.get("cart_id")
    if cart_id:
        cart_service.remove_item(session["user_id"], cart_id)

    return redirect("/cart")


# --- ROTAS DE CHECKOUT E PEDIDOS ---

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "POST":
        token = request.form.get("idempotency_token")
        result = checkout_service.process_order(session["user_id"], token)

        if not result["success"]:
            return result["message"], result["status"]

        return redirect("/orders")

    summary = checkout_service.get_checkout_summary(session["user_id"])
    idempotency_token = str(uuid.uuid4())
    return render_template(
        "orders/checkout.html",
        cart=summary["items"],
        subtotal=summary["subtotal"],
        idempotency_token=idempotency_token
    )


@app.route("/orders")
@login_required
def orders():
    user_orders = checkout_service.get_user_orders(session["user_id"])
    return render_template("orders/orders.html", orders=user_orders)

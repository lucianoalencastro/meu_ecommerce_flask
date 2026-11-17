from werkzeug.security import check_password_hash, generate_password_hash
from repositories import UserRepository, ProductRepository, CartRepository, OrderRepository

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, username, password, confirmation):
        if not username or not password or not confirmation:
            return {"success": False, "message": "Preencha todos os campos!", "status": 400}
        if password != confirmation:
            return {"success": False, "message": "As senhas não coincidem!", "status": 400}

        hash_password = generate_password_hash(password)
        try:
            user_id = self.user_repo.create(username, hash_password)
            return {"success": True, "user_id": user_id}
        except Exception:
            return {"success": False, "message": "Nome de usuário já existe!", "status": 400}

    def login(self, username, password):
        if not username or not password:
            return {"success": False, "message": "Preencha usuário e senha!", "status": 400}

        user = self.user_repo.get_by_username(username)
        if not user or not check_password_hash(user["hash"], password):
            return {"success": False, "message": "Usuário e/ou senha inválidos!", "status": 400}

        return {"success": True, "user_id": user["id"]}


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def get_featured_products(self, limit=4):
        return self.repository.get_featured(limit)

    def get_all_products(self):
        return self.repository.get_all()

    def get_product_by_id(self, product_id):
        return self.repository.get_by_id(product_id)


class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def add_item(self, user_id, product_id, quantity=1):
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return {"success": False, "message": "Produto não encontrado", "status": 404}

        available_stock = product["stock"]
        if quantity > available_stock:
            return {"success": False, "message": "Quantidade solicitada maior que o estoque disponível!", "status": 400}

        existing = self.cart_repo.get_item_by_user_and_product(user_id, product_id)

        if existing:
            self.cart_repo.increase_quantity(user_id, product_id, quantity)
        else:
            self.cart_repo.add_item(user_id, product_id, quantity)

        self.product_repo.decrease_stock(product_id, quantity)
        return {"success": True}

    def remove_item(self, user_id, cart_id):
        item = self.cart_repo.get_item_by_id_and_user(cart_id, user_id)
        if not item:
            return {"success": False}

        product_id = item["product_id"]
        current_quantity = item["quantity"]

        if current_quantity > 1:
            self.cart_repo.decrease_quantity(cart_id, 1)
        else:
            self.cart_repo.delete_item(cart_id)

        self.product_repo.increase_stock(product_id, 1)
        return {"success": True}

    def get_user_cart(self, user_id):
        return self.cart_repo.get_full_cart_by_user(user_id)

    def get_cart_count(self, user_id):
        if not user_id:
            return 0
        return self.cart_repo.get_total_items_count(user_id)



class CheckoutService:
    def __init__(self, order_repo: OrderRepository, cart_repo: CartRepository):
        self.order_repo = order_repo
        self.cart_repo = cart_repo

    def process_order(self, user_id, idempotency_token):
        if not idempotency_token:
            return {"success": False, "message": "Token de idempotência ausente.", "status": 400}

        existing_order = self.order_repo.get_by_idempotency_token(idempotency_token)
        if existing_order:
            return {"success": True, "message": "Pedido já processado anteriormente.", "already_processed": True}

        cart_items = self.cart_repo.get_cart_details_by_user(user_id)
        if not cart_items:
            return {"success": False, "message": "Carrinho vazio.", "status": 400}

        total = sum(item["price"] * item["quantity"] for item in cart_items)

        order_id = self.order_repo.create_order(
            user_id, total, "concluido", idempotency_token
        )

        for item in cart_items:
            self.order_repo.add_order_item(
                order_id, item["product_id"], item["quantity"], item["price"]
            )

        self.cart_repo.clear_by_user(user_id)
        return {"success": True, "message": "Pedido finalizado com sucesso!", "order_id": order_id}

    def get_checkout_summary(self, user_id):
        items = self.cart_repo.get_full_cart_by_user(user_id)
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        return {"items": items, "subtotal": subtotal}

    def get_user_orders(self, user_id):
        orders = self.order_repo.get_orders_by_user(user_id)
        for order in orders:
            order["product_list"] = self.order_repo.get_order_items(order["id"])
        return orders

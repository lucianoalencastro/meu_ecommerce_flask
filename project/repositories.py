class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_by_username(self, username):
        rows = self.db.execute("SELECT * FROM users WHERE username = ?", username)
        return rows[0] if rows else None

    def create(self, username, hash_password):
        return self.db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username, hash_password
        )

class ProductRepository:
    def __init__(self, db):
        self.db = db

    def get_featured(self, limit=4):
        return self.db.execute("SELECT * FROM products LIMIT ?", limit)

    def get_all(self):
        return self.db.execute("SELECT * FROM products")

    def get_by_id(self, product_id):
        rows = self.db.execute("SELECT * FROM products WHERE id = ?", product_id)
        return rows[0] if rows else None

    def decrease_stock(self, product_id, quantity):
        self.db.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            quantity, product_id
        )

    def increase_stock(self, product_id, quantity=1):
        self.db.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            quantity, product_id
        )

class CartRepository:
    def __init__(self, db):
        self.db = db

    def get_item_by_user_and_product(self, user_id, product_id):
        rows = self.db.execute(
            "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?",
            user_id, product_id
        )
        return rows[0] if rows else None

    def get_item_by_id_and_user(self, cart_id, user_id):
        rows = self.db.execute(
            "SELECT * FROM cart_items WHERE id = ? AND user_id = ?",
            cart_id, user_id
        )
        return rows[0] if rows else None

    def get_cart_details_by_user(self, user_id):
        return self.db.execute(
            "SELECT products.id AS product_id, products.price, cart_items.quantity "
            "FROM cart_items JOIN products ON cart_items.product_id = products.id "
            "WHERE cart_items.user_id = ?",
            user_id
        )

    def get_full_cart_by_user(self, user_id):
        return self.db.execute(
            "SELECT products.id AS product_id, products.name, products.price, products.image, "
            "cart_items.id, cart_items.quantity "
            "FROM cart_items JOIN products ON cart_items.product_id = products.id "
            "WHERE cart_items.user_id = ?",
            user_id
        )

    def add_item(self, user_id, product_id, quantity):
        self.db.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
            user_id, product_id, quantity
        )

    def increase_quantity(self, user_id, product_id, quantity):
        self.db.execute(
            "UPDATE cart_items SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?",
            quantity, user_id, product_id
        )

    def decrease_quantity(self, cart_id, quantity=1):
        self.db.execute(
            "UPDATE cart_items SET quantity = quantity - ? WHERE id = ?",
            quantity, cart_id
        )

    def delete_item(self, cart_id):
        self.db.execute("DELETE FROM cart_items WHERE id = ?", cart_id)

    def clear_by_user(self, user_id):
        self.db.execute("DELETE FROM cart_items WHERE user_id = ?", user_id)


class OrderRepository:
    def __init__(self, db):
        self.db = db

    def get_by_idempotency_token(self, token):
        rows = self.db.execute(
            "SELECT id FROM orders WHERE idempotency_token = ?",
            token
        )
        return rows[0] if rows else None

    def create_order(self, user_id, total, status, idempotency_token):
        return self.db.execute(
            "INSERT INTO orders (user_id, total, status, idempotency_token) VALUES (?, ?, ?, ?)",
            user_id, total, status, idempotency_token
        )

    def add_order_item(self, order_id, product_id, quantity, price):
        self.db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
            order_id, product_id, quantity, price
        )

    def get_orders_by_user(self, user_id):
        return self.db.execute(
            "SELECT id, total, status, timestamp FROM orders WHERE user_id = ? ORDER BY timestamp DESC",
            user_id
        )

    def get_order_items(self, order_id):
        return self.db.execute(
            "SELECT products.name, products.image, order_items.quantity, order_items.price "
            "FROM order_items JOIN products ON order_items.product_id = products.id "
            "WHERE order_items.order_id = ?",
            order_id
        )

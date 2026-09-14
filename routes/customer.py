from flask import Blueprint, render_template, abort

from models.product import Product


customer_bp = Blueprint(
    "customer",
    __name__
)


@customer_bp.route("/")
def index():
    products = Product.query.order_by(
        Product.created_at.desc()
    ).all()

    categories = [
        "Groceries",
        "Snacks",
        "Beverages",
        "Personal Care",
        "Household",
        "Dairy",
        "Other"
    ]

    return render_template(
        "index.html",
        products=products,
        categories=categories
    )


@customer_bp.route("/product/<int:product_id>")
def product_details(product_id):
    product = Product.query.get(product_id)

    if product is None:
        abort(404)

    return render_template(
        "product.html",
        product=product
    )


@customer_bp.route("/order")
def order():
    return render_template("order.html")
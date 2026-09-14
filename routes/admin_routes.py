from functools import wraps
import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from extensions import db
from models import Admin, Product


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# =========================================================
# IMAGE SETTINGS
# =========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


# =========================================================
# ADMIN LOGIN REQUIRED
# =========================================================

def admin_required(route_function):

    @wraps(route_function)
    def decorated_function(*args, **kwargs):

        if "admin_id" not in session:
            return redirect(
                url_for("admin.login")
            )

        return route_function(*args, **kwargs)

    return decorated_function


# =========================================================
# ADMIN LOGIN
# =========================================================

@admin_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password_hash,
            password
        ):

            session.clear()

            session["admin_id"] = admin.id
            session["admin_username"] = admin.username

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("admin.dashboard")
            )

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template(
        "admin/login.html"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@admin_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("admin.login")
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_bp.route("/dashboard")
@admin_required
def dashboard():

    total_products = Product.query.count()

    available_products = Product.query.filter_by(
        is_available=True
    ).count()

    out_of_stock_products = Product.query.filter_by(
        is_available=False
    ).count()

    products = Product.query.order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "admin/dashboard.html",
        total_products=total_products,
        available_products=available_products,
        out_of_stock_products=out_of_stock_products,
        products=products
    )


# =========================================================
# ADD PRODUCT
# =========================================================

@admin_bp.route(
    "/products/add",
    methods=["GET", "POST"]
)
@admin_required
def add_product():

    categories = [
        "Groceries",
        "Snacks",
        "Beverages",
        "Personal Care",
        "Household",
        "Dairy",
        "Other"
    ]

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        price_text = request.form.get(
            "price",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        stock = request.form.get(
            "stock"
        )

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not name or not price_text or not category:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return render_template(
                "admin/add_product.html",
                categories=categories
            )


        # -------------------------------------------------
        # CATEGORY VALIDATION
        # -------------------------------------------------

        if category not in categories:

            flash(
                "Invalid category selected.",
                "error"
            )

            return render_template(
                "admin/add_product.html",
                categories=categories
            )


        # -------------------------------------------------
        # PRICE VALIDATION
        # -------------------------------------------------

        try:

            price = float(price_text)

            if price < 0:
                raise ValueError

        except ValueError:

            flash(
                "Please enter a valid price.",
                "error"
            )

            return render_template(
                "admin/add_product.html",
                categories=categories
            )


        # -------------------------------------------------
        # IMAGE UPLOAD
        # -------------------------------------------------

        image = request.files.get("image")

        image_filename = None

        if image and image.filename:

            # Check extension
            if not allowed_image(image.filename):

                flash(
                    "Invalid image format. Use PNG, JPG, JPEG or WEBP.",
                    "error"
                )

                return render_template(
                    "admin/add_product.html",
                    categories=categories
                )


            # Secure original filename
            original_filename = secure_filename(
                image.filename
            )


            # Get extension
            extension = original_filename.rsplit(
                ".",
                1
            )[1].lower()


            # Generate unique filename
            unique_filename = (
                f"{uuid.uuid4().hex}.{extension}"
            )


            # Upload folder
            upload_folder = os.path.join(
                current_app.root_path,
                "uploads",
                "products"
            )


            # Create folder if it doesn't exist
            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            # Save image
            image.save(
                os.path.join(
                    upload_folder,
                    unique_filename
                )
            )


            image_filename = unique_filename


        # -------------------------------------------------
        # PRODUCT AVAILABILITY
        # -------------------------------------------------

        is_available = (
            stock == "available"
        )


        # -------------------------------------------------
        # CREATE PRODUCT
        # -------------------------------------------------

        product = Product(
            name=name,
            price=price,
            category=category,
            description=description,
            image=image_filename,
            is_available=is_available
        )


        db.session.add(product)

        db.session.commit()


        flash(
            "Product added successfully.",
            "success"
        )


        return redirect(
            url_for("admin.dashboard")
        )


    return render_template(
        "admin/add_product.html",
        categories=categories
    )


# =========================================================
# EDIT PRODUCT
# =========================================================

@admin_bp.route(
    "/products/edit/<int:product_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_product(product_id):

    product = Product.query.get_or_404(
        product_id
    )

    categories = [
        "Groceries",
        "Snacks",
        "Beverages",
        "Personal Care",
        "Household",
        "Dairy",
        "Other"
    ]

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        price_text = request.form.get(
            "price",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        stock = request.form.get(
            "stock"
        )


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not name or not price_text or not category:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return render_template(
                "admin/edit_product.html",
                product=product,
                categories=categories
            )


        # -------------------------------------------------
        # CATEGORY VALIDATION
        # -------------------------------------------------

        if category not in categories:

            flash(
                "Invalid category selected.",
                "error"
            )

            return render_template(
                "admin/edit_product.html",
                product=product,
                categories=categories
            )


        # -------------------------------------------------
        # PRICE VALIDATION
        # -------------------------------------------------

        try:

            price = float(price_text)

            if price < 0:
                raise ValueError

        except ValueError:

            flash(
                "Please enter a valid price.",
                "error"
            )

            return render_template(
                "admin/edit_product.html",
                product=product,
                categories=categories
            )


        # -------------------------------------------------
        # UPDATE PRODUCT INFORMATION
        # -------------------------------------------------

        product.name = name
        product.price = price
        product.category = category
        product.description = description


        # -------------------------------------------------
        # PRODUCT AVAILABILITY
        # -------------------------------------------------

        product.is_available = (
            stock == "available"
        )


        # -------------------------------------------------
        # REPLACE PRODUCT IMAGE
        # -------------------------------------------------

        image = request.files.get("image")

        if image and image.filename:

            # Check image extension

            if not allowed_image(image.filename):

                flash(
                    "Invalid image format. Use PNG, JPG, JPEG or WEBP.",
                    "error"
                )

                return render_template(
                    "admin/edit_product.html",
                    product=product,
                    categories=categories
                )


            # Secure original filename

            original_filename = secure_filename(
                image.filename
            )


            # Get extension

            extension = original_filename.rsplit(
                ".",
                1
            )[1].lower()


            # Generate unique filename

            unique_filename = (
                f"{uuid.uuid4().hex}.{extension}"
            )


            # Upload folder

            upload_folder = os.path.join(
                current_app.root_path,
                "uploads",
                "products"
            )


            # Create folder if it doesn't exist

            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            # Delete old image

            if product.image:

                old_image_path = os.path.join(
                    upload_folder,
                    product.image
                )

                if os.path.exists(
                    old_image_path
                ):

                    os.remove(
                        old_image_path
                    )


            # Save new image

            image.save(
                os.path.join(
                    upload_folder,
                    unique_filename
                )
            )


            # Store new filename in database

            product.image = unique_filename


        # -------------------------------------------------
        # SAVE CHANGES
        # -------------------------------------------------

        db.session.commit()


        flash(
            "Product updated successfully.",
            "success"
        )


        return redirect(
            url_for("admin.dashboard")
        )


    return render_template(
        "admin/edit_product.html",
        product=product,
        categories=categories
    )

# =========================================================
# DELETE PRODUCT
# =========================================================

@admin_bp.route(
    "/products/delete/<int:product_id>",
    methods=["POST"]
)
@admin_required
def delete_product(product_id):

    product = Product.query.get_or_404(
        product_id
    )

    # -------------------------------------------------
    # DELETE PRODUCT IMAGE
    # -------------------------------------------------

    if product.image:

        upload_folder = os.path.join(
            current_app.root_path,
            "uploads",
            "products"
        )

        image_path = os.path.join(
            upload_folder,
            product.image
        )

        if os.path.exists(image_path):

            os.remove(image_path)


    # -------------------------------------------------
    # DELETE PRODUCT FROM DATABASE
    # -------------------------------------------------

    product_name = product.name

    db.session.delete(product)

    db.session.commit()


    # -------------------------------------------------
    # SUCCESS MESSAGE
    # -------------------------------------------------

    flash(
        f"{product_name} deleted successfully.",
        "success"
    )


    return redirect(
        url_for("admin.dashboard")
    )

# =========================================================
# TOGGLE STOCK
# =========================================================

@admin_bp.route(
    "/products/toggle-stock/<int:product_id>",
    methods=["POST"]
)
@admin_required
def toggle_stock(product_id):

    product = Product.query.get_or_404(
        product_id
    )

    product.is_available = (
        not product.is_available
    )

    db.session.commit()


    if product.is_available:

        flash(
            f"{product.name} is now available.",
            "success"
        )

    else:

        flash(
            f"{product.name} is now out of stock.",
            "success"
        )


    return redirect(
        url_for("admin.dashboard")
    )
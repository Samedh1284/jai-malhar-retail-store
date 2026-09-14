from functools import wraps

import cloudinary
import cloudinary.uploader

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

from extensions import db
from models import Admin, Product


# =========================================================
# ADMIN BLUEPRINT
# =========================================================

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
# CLOUDINARY CONFIGURATION
# =========================================================

def configure_cloudinary():

    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
        secure=True
    )


# =========================================================
# UPLOAD IMAGE TO CLOUDINARY
# =========================================================

def upload_product_image(image):

    configure_cloudinary()

    result = cloudinary.uploader.upload(
        image,
        folder="jai-malhar-store/products",
        resource_type="image"
    )

    return result.get("secure_url")


# =========================================================
# DELETE IMAGE FROM CLOUDINARY
# =========================================================

def delete_product_image(image_url):

    if not image_url:
        return

    try:

        configure_cloudinary()

        # Cloudinary URLs look similar to:
        #
        # https://res.cloudinary.com/cloud_name/image/upload/
        # v1234567890/
        # jai-malhar-store/products/filename.jpg
        #
        # We extract the public ID from the URL.

        upload_marker = "/upload/"

        if upload_marker not in image_url:
            return

        public_id_with_extension = image_url.split(
            upload_marker,
            1
        )[1]

        # Remove version number if present
        parts = public_id_with_extension.split("/")

        if parts and parts[0].startswith("v") and parts[0][1:].isdigit():
            public_id_with_extension = "/".join(parts[1:])

        # Remove file extension
        public_id = public_id_with_extension.rsplit(
            ".",
            1
        )[0]

        cloudinary.uploader.destroy(
            public_id,
            resource_type="image"
        )

    except Exception as error:

        # Do not stop product deletion if Cloudinary
        # image deletion fails.

        print(
            f"Cloudinary image deletion failed: {error}"
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

        image_url = None

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

            try:

                # Upload directly to Cloudinary

                image_url = upload_product_image(
                    image
                )

                if not image_url:
                    raise Exception(
                        "Cloudinary did not return an image URL."
                    )

            except Exception as error:

                print(
                    f"Cloudinary upload failed: {error}"
                )

                flash(
                    "Image upload failed. Please try again.",
                    "error"
                )

                return render_template(
                    "admin/add_product.html",
                    categories=categories
                )

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
            image=image_url,
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

            try:

                # Upload new image first

                new_image_url = upload_product_image(
                    image
                )

                if not new_image_url:
                    raise Exception(
                        "Cloudinary did not return an image URL."
                    )

                # Delete old Cloudinary image

                if product.image:

                    delete_product_image(
                        product.image
                    )

                # Store new URL

                product.image = new_image_url

            except Exception as error:

                print(
                    f"Cloudinary image replacement failed: {error}"
                )

                flash(
                    "Image upload failed. Please try again.",
                    "error"
                )

                return render_template(
                    "admin/edit_product.html",
                    product=product,
                    categories=categories
                )

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
    # DELETE PRODUCT IMAGE FROM CLOUDINARY
    # -------------------------------------------------

    if product.image:

        delete_product_image(
            product.image
        )

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
import os

from flask import (
    Flask,
    send_from_directory,
    render_template
)

from config import Config
from extensions import db


def create_app():

    app = Flask(__name__)

    # =========================================================
    # LOAD CONFIGURATION
    # =========================================================

    app.config.from_object(Config)


    # =========================================================
    # INITIALIZE DATABASE
    # =========================================================

    db.init_app(app)


    # =========================================================
    # IMPORT MODELS
    # =========================================================

    from models.product import Product
    from models.admin import Admin


    # =========================================================
    # IMPORT ROUTES
    # =========================================================

    from routes.customer import customer_bp
    from routes.admin_routes import admin_bp


    # =========================================================
    # REGISTER BLUEPRINTS
    # =========================================================

    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)


    # =========================================================
    # 404 ERROR PAGE
    # =========================================================

    @app.errorhandler(404)
    def page_not_found(error):

        return render_template(
            "errors/404.html"
        ), 404


    # =========================================================
    # 500 ERROR PAGE
    # =========================================================

    @app.errorhandler(500)
    def internal_server_error(error):

        return render_template(
            "errors/500.html"
        ), 500


    return app


app = create_app()


# =========================================================
# SERVE PRODUCT IMAGES
# =========================================================

@app.route("/uploads/products/<filename>")
def uploaded_product_image(filename):

    upload_folder = os.path.join(
        app.root_path,
        "uploads",
        "products"
    )

    return send_from_directory(
        upload_folder,
        filename
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
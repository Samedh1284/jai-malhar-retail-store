/* =========================================================
   JAI MALHAR RETAIL STORE
   CUSTOMER + ADMIN JAVASCRIPT
========================================================= */


/* =========================================================
   CART
========================================================= */

let cart = JSON.parse(
    localStorage.getItem("jaiMalharCart")
) || [];


/* =========================================================
   CART COUNT
========================================================= */

function updateCartCount() {

    const cartCount =
        document.getElementById("cartCount");

    if (!cartCount) {
        return;
    }

    const totalItems = cart.reduce(
        (total, item) => total + item.quantity,
        0
    );

    cartCount.textContent = totalItems;
}


/* =========================================================
   SAVE CART
========================================================= */

function saveCart() {

    localStorage.setItem(
        "jaiMalharCart",
        JSON.stringify(cart)
    );

    updateCartCount();
}


/* =========================================================
   ADD TO ORDER
========================================================= */

function addToOrder(id, name, price) {

    const existingProduct = cart.find(
        item => item.id === id
    );


    if (existingProduct) {

        existingProduct.quantity += 1;

    } else {

        cart.push({

            id: id,

            name: name,

            price: Number(price),

            quantity: 1

        });

    }


    saveCart();


    alert(
        name + " added to your order."
    );
}


/* =========================================================
   CUSTOMER SEARCH PRODUCTS
========================================================= */

function filterProducts() {

    const searchInput =
        document.getElementById("searchInput");

    const productGrid =
        document.getElementById("productGrid");

    const noProductsMessage =
        document.getElementById(
            "noProductsMessage"
        );


    if (!searchInput || !productGrid) {
        return;
    }


    const searchText =
        searchInput.value
            .toLowerCase()
            .trim();


    const activeCategory =
        document.querySelector(
            ".category-btn.active"
        );


    const selectedCategory =
        activeCategory
            ? activeCategory.dataset.category
            : "all";


    const products =
        productGrid.querySelectorAll(
            ".product-card"
        );


    let visibleProducts = 0;


    products.forEach(product => {

        const productName =
            product.dataset.name || "";

        const productCategory =
            product.dataset.category || "";


        const matchesSearch =
            productName.includes(
                searchText
            );


        const matchesCategory =
            selectedCategory === "all" ||
            productCategory === selectedCategory;


        if (
            matchesSearch &&
            matchesCategory
        ) {

            product.style.display = "";

            visibleProducts++;

        } else {

            product.style.display = "none";

        }

    });


    if (noProductsMessage) {

        noProductsMessage.style.display =
            visibleProducts === 0
                ? "block"
                : "none";

    }
}


/* =========================================================
   CUSTOMER CATEGORY BUTTONS
========================================================= */

function setupCategoryButtons() {

    const buttons =
        document.querySelectorAll(
            ".category-btn"
        );


    buttons.forEach(button => {

        button.addEventListener(
            "click",
            function () {

                buttons.forEach(btn => {

                    btn.classList.remove(
                        "active"
                    );

                });


                this.classList.add(
                    "active"
                );


                filterProducts();

            }
        );

    });
}


/* =========================================================
   CUSTOMER ADD BUTTONS
========================================================= */

function setupAddButtons() {

    const buttons =
        document.querySelectorAll(
            ".add-to-order"
        );


    buttons.forEach(button => {

        button.addEventListener(
            "click",
            function () {

                const id =
                    Number(
                        this.dataset.id
                    );


                const name =
                    this.dataset.name;


                const price =
                    this.dataset.price;


                addToOrder(
                    id,
                    name,
                    price
                );

            }
        );

    });
}


/* =========================================================
   CUSTOMER SEARCH INPUT
========================================================= */

function setupSearch() {

    const searchInput =
        document.getElementById(
            "searchInput"
        );


    if (!searchInput) {
        return;
    }


    searchInput.addEventListener(
        "input",
        filterProducts
    );
}


/* =========================================================
   ORDER PAGE
========================================================= */

function renderOrderPage() {

    const orderItems =
        document.getElementById(
            "orderItems"
        );


    const emptyOrder =
        document.getElementById(
            "emptyOrder"
        );


    const orderSummary =
        document.getElementById(
            "orderSummary"
        );


    const orderTotal =
        document.getElementById(
            "orderTotal"
        );


    if (!orderItems) {
        return;
    }


    /* EMPTY ORDER */

    if (cart.length === 0) {

        orderItems.innerHTML = "";


        if (emptyOrder) {

            emptyOrder.style.display =
                "block";

        }


        if (orderSummary) {

            orderSummary.style.display =
                "none";

        }


        return;
    }


    if (emptyOrder) {

        emptyOrder.style.display =
            "none";

    }


    if (orderSummary) {

        orderSummary.style.display =
            "block";

    }


    let total = 0;


    orderItems.innerHTML = "";


    cart.forEach(item => {

        const itemTotal =
            item.price * item.quantity;


        total += itemTotal;


        const itemElement =
            document.createElement(
                "div"
            );


        itemElement.className =
            "order-item";


        itemElement.innerHTML = `

            <div class="order-item-info">

                <div class="order-item-name">
                    ${escapeHtml(item.name)}
                </div>

                <div class="order-item-price">
                    ₹${item.price.toFixed(2)} each
                </div>

            </div>


            <div class="quantity-controls">

                <button
                    type="button"
                    class="quantity-btn"
                    onclick="changeQuantity(${item.id}, -1)"
                >
                    −
                </button>


                <span class="quantity-value">
                    ${item.quantity}
                </span>


                <button
                    type="button"
                    class="quantity-btn"
                    onclick="changeQuantity(${item.id}, 1)"
                >
                    +
                </button>

            </div>


            <strong>
                ₹${itemTotal.toFixed(2)}
            </strong>


            <button
                type="button"
                class="remove-btn"
                onclick="removeFromOrder(${item.id})"
            >
                Remove
            </button>

        `;


        orderItems.appendChild(
            itemElement
        );

    });


    if (orderTotal) {

        orderTotal.textContent =
            "₹" + total.toFixed(2);

    }
}


/* =========================================================
   CHANGE QUANTITY
========================================================= */

function changeQuantity(id, change) {

    const item =
        cart.find(
            product => product.id === id
        );


    if (!item) {
        return;
    }


    item.quantity += change;


    if (item.quantity <= 0) {

        cart = cart.filter(
            product => product.id !== id
        );

    }


    saveCart();

    renderOrderPage();
}


/* =========================================================
   REMOVE PRODUCT
========================================================= */

function removeFromOrder(id) {

    cart = cart.filter(
        product => product.id !== id
    );


    saveCart();

    renderOrderPage();
}


/* =========================================================
   WHATSAPP ORDER
========================================================= */

function sendWhatsAppOrder() {

    if (cart.length === 0) {

        alert(
            "Your order is empty."
        );

        return;
    }


    const nameInput =
        document.getElementById(
            "customerName"
        );


    const phoneInput =
        document.getElementById(
            "customerPhone"
        );


    const addressInput =
        document.getElementById(
            "customerAddress"
        );


    const name =
        nameInput
            ? nameInput.value.trim()
            : "";


    const phone =
        phoneInput
            ? phoneInput.value.trim()
            : "";


    const address =
        addressInput
            ? addressInput.value.trim()
            : "";


    /* VALIDATE NAME */

    if (!name) {

        alert(
            "Please enter your name."
        );

        return;
    }


    /* VALIDATE PHONE */

    if (!/^[0-9]{10}$/.test(phone)) {

        alert(
            "Please enter a valid 10-digit mobile number."
        );

        return;
    }


    /* VALIDATE ADDRESS */

    if (!address) {

        alert(
            "Please enter your address."
        );

        return;
    }


    /* CREATE MESSAGE */

    let message =
        "*Jai Malhar Retail Store - New Order*%0A%0A";


    message +=
        "*Customer:* " +
        encodeURIComponent(name) +
        "%0A";


    message +=
        "*Mobile:* " +
        encodeURIComponent(phone) +
        "%0A";


    message +=
        "*Address:* " +
        encodeURIComponent(address) +
        "%0A%0A";


    message +=
        "*Order Details:*%0A";


    let total = 0;


    cart.forEach((item, index) => {

        const itemTotal =
            item.price * item.quantity;


        total += itemTotal;


        message +=
            `${index + 1}. ` +
            encodeURIComponent(item.name) +
            ` × ${item.quantity} = ₹${itemTotal.toFixed(2)}%0A`;

    });


    message +=
        "%0A*Total: ₹" +
        total.toFixed(2) +
        "*";


    /* =====================================================
       GET STORE WHATSAPP NUMBER

       .env
          ↓
       Flask Config
          ↓
       order.html
          ↓
       data-store-number
    ===================================================== */

    const button =
        document.getElementById(
            "whatsappOrderBtn"
        );


    const storeNumber =
        button
            ? button.dataset.storeNumber
            : "";


    /* CHECK STORE NUMBER */

    if (!storeNumber) {

        alert(
            "Store WhatsApp number is not configured."
        );

        return;
    }


    /* OPEN WHATSAPP */

    const whatsappUrl =
        "https://wa.me/" +
        storeNumber +
        "?text=" +
        message;


    window.open(
        whatsappUrl,
        "_blank"
    );
}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHtml(text) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent = text;


    return div.innerHTML;
}


/* =========================================================
   WHATSAPP BUTTON
========================================================= */

function setupWhatsAppButton() {

    const button =
        document.getElementById(
            "whatsappOrderBtn"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        sendWhatsAppOrder
    );
}


/* =========================================================
   ADMIN PRODUCT FILTERS
========================================================= */

function setupAdminProductFilters() {

    const searchInput =
        document.getElementById(
            "adminProductSearch"
        );


    const categoryFilter =
        document.getElementById(
            "adminCategoryFilter"
        );


    const stockFilter =
        document.getElementById(
            "adminStockFilter"
        );


    const productRows =
        document.querySelectorAll(
            ".admin-product-row"
        );


    const noResults =
        document.getElementById(
            "adminNoSearchResults"
        );


    /*
       These elements only exist
       on the Admin Dashboard.

       Therefore this function
       safely does nothing on
       customer pages.
    */

    if (
        !searchInput ||
        !categoryFilter ||
        !stockFilter ||
        productRows.length === 0
    ) {

        return;
    }


    function filterAdminProducts() {

        const searchText =
            searchInput.value
                .trim()
                .toLowerCase();


        const selectedCategory =
            categoryFilter.value
                .toLowerCase();


        const selectedStock =
            stockFilter.value;


        let visibleProducts = 0;


        productRows.forEach(
            function(row) {

                const productName =
                    row.dataset.name || "";


                const productCategory =
                    row.dataset.category || "";


                const productStock =
                    row.dataset.stock || "";


                /* SEARCH MATCH */

                const matchesSearch =
                    productName.includes(
                        searchText
                    );


                /* CATEGORY MATCH */

                const matchesCategory =
                    selectedCategory === "all" ||
                    productCategory ===
                        selectedCategory;


                /* STOCK MATCH */

                const matchesStock =
                    selectedStock === "all" ||
                    productStock ===
                        selectedStock;


                /* SHOW PRODUCT */

                if (
                    matchesSearch &&
                    matchesCategory &&
                    matchesStock
                ) {

                    row.style.display = "";

                    visibleProducts++;

                } else {

                    row.style.display =
                        "none";

                }

            }
        );


        /* NO RESULTS MESSAGE */

        if (noResults) {

            if (visibleProducts === 0) {

                noResults.style.display =
                    "block";

            } else {

                noResults.style.display =
                    "none";

            }

        }

    }


    /* SEARCH */

    searchInput.addEventListener(
        "input",
        filterAdminProducts
    );


    /* CATEGORY */

    categoryFilter.addEventListener(
        "change",
        filterAdminProducts
    );


    /* STOCK */

    stockFilter.addEventListener(
        "change",
        filterAdminProducts
    );

}


/* =========================================================
   PRODUCT IMAGE PREVIEW
========================================================= */

function setupImagePreview() {

    const imageInput =
        document.getElementById(
            "image"
        );


    const previewContainer =
        document.getElementById(
            "imagePreviewContainer"
        );


    const preview =
        document.getElementById(
            "imagePreview"
        );


    /*
       These elements only exist
       on Add Product / Edit Product.

       Therefore this function
       safely does nothing on
       other pages.
    */

    if (
        !imageInput ||
        !previewContainer ||
        !preview
    ) {

        return;
    }


    imageInput.addEventListener(
        "change",
        function () {

            const file =
                this.files[0];


            /* NO FILE */

            if (!file) {

                previewContainer.style.display =
                    "none";

                preview.src = "";

                return;
            }


            /* =================================================
               CHECK FILE TYPE
            ================================================= */

            const allowedTypes = [

                "image/jpeg",

                "image/png",

                "image/webp"

            ];


            if (
                !allowedTypes.includes(
                    file.type
                )
            ) {

                alert(
                    "Please select a JPG, JPEG, PNG or WEBP image."
                );


                this.value = "";


                previewContainer.style.display =
                    "none";


                preview.src = "";


                return;
            }


            /* =================================================
               CHECK FILE SIZE
            ================================================= */

            const maxSize =
                5 * 1024 * 1024;


            if (file.size > maxSize) {

                alert(
                    "Image size must be less than 5MB."
                );


                this.value = "";


                previewContainer.style.display =
                    "none";


                preview.src = "";


                return;
            }


            /* =================================================
               CREATE IMAGE PREVIEW
            ================================================= */

            const reader =
                new FileReader();


            reader.onload =
                function (event) {

                    preview.src =
                        event.target.result;


                    previewContainer.style.display =
                        "block";

                };


            reader.onerror =
                function () {

                    alert(
                        "Unable to preview this image."
                    );


                    previewContainer.style.display =
                        "none";

                };


            reader.readAsDataURL(
                file
            );

        }
    );

}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        /* =========================================
           CUSTOMER FEATURES
        ========================================= */

        updateCartCount();

        setupCategoryButtons();

        setupAddButtons();

        setupSearch();

        renderOrderPage();

        setupWhatsAppButton();


        /* =========================================
           ADMIN FEATURES
        ========================================= */

        setupAdminProductFilters();

        setupImagePreview();

    }
);
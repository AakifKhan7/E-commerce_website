document.addEventListener('DOMContentLoaded', function () {
    // Smooth Scroll for Anchor Links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').slice(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Confirm Deletion of Items from Cart
    const deleteButtons = document.querySelectorAll('.delete-item-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to remove this item from your cart?')) {
                e.preventDefault();
            }
        });
    });

    // Update Cart Quantity
    const updateQuantityButtons = document.querySelectorAll('.update-quantity-btn');
    updateQuantityButtons.forEach(button => {
        button.addEventListener('click', function () {
            const quantityInput = this.previousElementSibling;
            const quantity = parseInt(quantityInput.value, 10);

            if (isNaN(quantity) || quantity < 1) {
                alert('Please enter a valid quantity!');
                return;
            }

            fetch(`/update-cart/${this.dataset.productId}`, {
                method: 'POST',
                body: JSON.stringify({ quantity: quantity }),
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Optionally update the cart count and quantity on the page without reloading
                    quantityInput.value = quantity;
                    const cartCount = document.querySelector('#cart-count');
                    if (cartCount && data.cartCount !== undefined) {
                        cartCount.textContent = data.cartCount;
                    }
                } else {
                    alert('Failed to update cart. Please try again.');
                }
            })
            .catch(() => alert('An error occurred. Please try again later.'));
        });
    });

    // Form Validation for Required Fields
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            let isValid = true;
            form.querySelectorAll('[required]').forEach(input => {
                if (input.value.trim() === '') {
                    isValid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Alert for Empty Cart on Page Load
    const cartCount = document.querySelector('#cart-count');
    if (cartCount && parseInt(cartCount.textContent) === 0) {
        setTimeout(() => alert('Your cart is empty!'), 500);
    }
});

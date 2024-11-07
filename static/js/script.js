document.addEventListener('DOMContentLoaded', function () {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').slice(1);
            const targetElement = document.getElementById(targetId);
            window.scrollTo({
                top: targetElement.offsetTop - 70,
                behavior: 'smooth'
            });
        });
    });

    const deleteButtons = document.querySelectorAll('.delete-item-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            const confirmation = confirm('Are you sure you want to remove this item from your cart?');
            if (!confirmation) {
                e.preventDefault();
            }
        });
    });

    const updateQuantityButtons = document.querySelectorAll('.update-quantity-btn');
    updateQuantityButtons.forEach(button => {
        button.addEventListener('click', function () {
            const quantityInput = this.previousElementSibling;
            const quantity = quantityInput.value;
            if (quantity < 1 || isNaN(quantity)) {
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
                    window.location.reload();
                } else {
                    alert('Failed to update cart. Please try again.');
                }
            });
        });
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            let isValid = true;
            form.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.hasAttribute('required') && input.value.trim() === '') {
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

    const cartCount = document.querySelector('#cart-count');
    if (cartCount && parseInt(cartCount.textContent) === 0) {
        alert('Your cart is empty!');
    }
});

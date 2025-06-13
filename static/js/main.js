// Enable Bootstrap tooltips everywhere
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Enable Bootstrap popovers
const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
});

// Add active class to current nav link
document.addEventListener('DOMContentLoaded', function() {
    const currentPage = location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref && currentPage.includes(linkHref.split('/').pop())) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
            
            // Also set parent item as active for dropdowns
            const parentItem = link.closest('.dropdown-item')?.parentElement.closest('.dropdown');
            if (parentItem) {
                const dropdownToggle = parentItem.querySelector('.dropdown-toggle');
                if (dropdownToggle) {
                    dropdownToggle.classList.add('active');
                }
            }
        }
    });
    
    // Initialize quantity selectors
    initQuantitySelectors();
    
    // Initialize cart functionality
    initCart();
    
    // Initialize forms
    initForms();
});

// Quantity selector functionality
function initQuantitySelectors() {
    document.querySelectorAll('.quantity-selector').forEach(selector => {
        const input = selector.querySelector('.quantity-input');
        const minusBtn = selector.querySelector('.quantity-minus');
        const plusBtn = selector.querySelector('.quantity-plus');
        const max = parseInt(input.getAttribute('max')) || 99;
        const min = parseInt(input.getAttribute('min')) || 1;
        
        function updateButtons() {
            minusBtn.disabled = parseInt(input.value) <= min;
            plusBtn.disabled = parseInt(input.value) >= max;
        }
        
        minusBtn?.addEventListener('click', () => {
            let value = parseInt(input.value) - 1;
            if (value >= min) {
                input.value = value;
                updateButtons();
                triggerChangeEvent(input);
            }
        });
        
        plusBtn?.addEventListener('click', () => {
            let value = parseInt(input.value) + 1;
            if (value <= max) {
                input.value = value;
                updateButtons();
                triggerChangeEvent(input);
            }
        });
        
        input?.addEventListener('change', () => {
            let value = parseInt(input.value);
            if (isNaN(value) || value < min) {
                input.value = min;
            } else if (value > max) {
                input.value = max;
            }
            updateButtons();
            triggerChangeEvent(input);
        });
        
        updateButtons();
    });
}

// Trigger change event
function triggerChangeEvent(element) {
    const event = new Event('change', { bubbles: true });
    element.dispatchEvent(event);
}

// Cart functionality
function initCart() {
    // Update cart item quantity
    document.querySelectorAll('.update-quantity').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const form = this.closest('form');
            const url = form.getAttribute('action');
            const formData = new FormData(form);
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Update cart total
                    const cartTotal = document.querySelector('.cart-total');
                    if (cartTotal) {
                        cartTotal.textContent = `$${data.cart_total}`;
                    }
                    
                    // Update item subtotal
                    const itemSubtotal = this.closest('.cart-item').querySelector('.item-subtotal');
                    if (itemSubtotal) {
                        itemSubtotal.textContent = `$${data.item_total}`;
                    }
                    
                    // Update cart count in navbar
                    updateCartCount(data.cart_count);
                    
                    showToast('Cart updated', 'success');
                } else {
                    showToast(data.message || 'An error occurred', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('An error occurred while updating the cart', 'danger');
            }
        });
    });
    
    // Remove item from cart
    document.querySelectorAll('.remove-from-cart').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (!confirm('Are you sure you want to remove this item from your cart?')) {
                return;
            }
            
            const url = this.getAttribute('href');
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                    },
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Remove item from DOM
                    const cartItem = this.closest('.cart-item');
                    cartItem.style.animation = 'fadeOut 0.3s ease-out';
                    
                    setTimeout(() => {
                        cartItem.remove();
                        
                        // Update cart total
                        const cartTotal = document.querySelector('.cart-total');
                        if (cartTotal) {
                            cartTotal.textContent = `$${data.cart_total}`;
                        }
                        
                        // Update cart count in navbar
                        updateCartCount(data.cart_count);
                        
                        // If cart is empty, show empty state
                        if (data.cart_count === 0) {
                            const cartTable = document.querySelector('.cart-table');
                            if (cartTable) {
                                cartTable.innerHTML = `
                                    <div class="empty-state py-5">
                                        <i class="fas fa-shopping-cart fa-3x mb-3"></i>
                                        <h4>Your cart is empty</h4>
                                        <p class="text-muted">Looks like you haven't added anything to your cart yet.</p>
                                        <a href="${data.products_url || '/products'}" class="btn btn-primary">Continue Shopping</a>
                                    </div>
                                `;
                            }
                        }
                    }, 300);
                    
                    showToast('Item removed from cart', 'success');
                } else {
                    showToast(data.message || 'An error occurred', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('An error occurred while removing the item', 'danger');
            }
        });
    });
}

// Update cart count in navbar
function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        if (count > 0) {
            element.textContent = count;
            element.style.display = 'inline-block';
        } else {
            element.style.display = 'none';
        }
    });
}

// Form handling
function initForms() {
    // Add loading state to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...';
            }
        });
    });
    
    // Image preview for file uploads
    document.querySelectorAll('.image-upload').forEach(input => {
        input.addEventListener('change', function() {
            const preview = document.getElementById(this.dataset.preview);
            const file = this.files[0];
            
            if (file) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    
                    const removeButton = preview.nextElementSibling;
                    if (removeButton && removeButton.classList.contains('remove-image')) {
                        removeButton.style.display = 'block';
                    }
                }
                
                reader.readAsDataURL(file);
            }
        });
    });
    
    // Remove image preview
    document.querySelectorAll('.remove-image').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const preview = this.previousElementSibling;
            const input = document.getElementById(this.dataset.target);
            
            if (preview && input) {
                preview.src = '#';
                preview.style.display = 'none';
                input.value = '';
                this.style.display = 'none';
            }
        });
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    
    bsToast.show();
    
    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1100';
    document.body.appendChild(container);
    return container;
}

// Debounce function for resize/scroll events
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Throttle function for scroll/resize events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(price);
}

// Add animation on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementTop < windowHeight - 100) {
            element.classList.add('animate__animated', 'animate__fadeInUp');
        }
    });
}

// Initialize animations on scroll
window.addEventListener('scroll', throttle(animateOnScroll, 200));
document.addEventListener('DOMContentLoaded', animateOnScroll);

// Handle back to top button
const backToTopButton = document.querySelector('.back-to-top');
if (backToTopButton) {
    window.addEventListener('scroll', debounce(() => {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    }, 100));
    
    backToTopButton.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Add smooth scrolling to all links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

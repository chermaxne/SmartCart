// AuroraMart - Main JavaScript

// Add to Cart functionality
function addToCart(productSku, quantity = 1) {
  fetch("/api/cart/add/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": window.csrfToken,
    },
    body: JSON.stringify({
      sku: productSku,
      quantity: quantity,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Update cart count
        const cartBadge = document.querySelector(".cart-badge")
        if (cartBadge) {
          cartBadge.textContent = data.cart_count
        }
        // Show success message
        showMessage("Product added to cart!", "success")
      }
    })
    .catch((error) => {
      showMessage("Error adding to cart", "error")
    })
}

// Update cart quantity
function updateCartQuantity(productSku, quantity) {
  fetch("/api/cart/update/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": window.csrfToken,
    },
    body: JSON.stringify({
      sku: productSku,
      quantity: quantity,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        location.reload()
      }
    })
}

// Remove from cart
function removeFromCart(productSku) {
  if (confirm("Remove this item from cart?")) {
    fetch("/api/cart/remove/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": window.csrfToken,
      },
      body: JSON.stringify({
        sku: productSku,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          location.reload()
        }
      })
  }
}

// Show message
function showMessage(message, type = "info") {
  const alertDiv = document.createElement("div")
  alertDiv.className = `alert alert-${type}`
  alertDiv.style.cssText =
    "position: fixed; top: 80px; right: 20px; padding: 1rem 1.5rem; border-radius: 0.5rem; z-index: 1000; animation: slideIn 0.3s;"

  if (type === "success") {
    alertDiv.style.background = "#dcfce7"
    alertDiv.style.color = "#166534"
  } else if (type === "error") {
    alertDiv.style.background = "#fee2e2"
    alertDiv.style.color = "#991b1b"
  } else {
    alertDiv.style.background = "#e0f2fe"
    alertDiv.style.color = "#075985"
  }

  alertDiv.textContent = message
  document.body.appendChild(alertDiv)

  setTimeout(() => {
    alertDiv.remove()
  }, 3000)
}

// Filter products
function filterProducts() {
  const form = document.getElementById("filter-form")
  if (form) {
    form.submit()
  }
}

// Image lazy loading
document.addEventListener("DOMContentLoaded", () => {
  const images = document.querySelectorAll("img[data-src]")
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target
        img.src = img.dataset.src
        img.removeAttribute("data-src")
        observer.unobserve(img)
      }
    })
  })

  images.forEach((img) => imageObserver.observe(img))
})

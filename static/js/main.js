// Global JS for ajax handlers and toasts
function showToast(title, message, type = 'normal', duration = 3000) {
    const toast = document.getElementById('toast-component');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');
    
    if (!toast) return;

    // Reset type classes
    toast.classList.remove(
        'bg-red-50','border-red-500','text-red-600',
        'bg-green-50','border-green-500','text-green-600',
        'bg-white','border-gray-300','text-gray-800'
    );

    // Set type styles
    if(type==='success'){
        toast.classList.add('bg-green-50','border-green-500','text-green-600');
        toast.style.border='1px solid #22c55e';
    } else if(type==='error'){
        toast.classList.add('bg-red-50','border-red-500','text-red-600');
        toast.style.border='1px solid #ef4444';
    } else {
        toast.classList.add('bg-white','border-gray-300','text-gray-800');
        toast.style.border='1px solid #d1d5db';
    }

    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Show toast
    toast.classList.remove('opacity-0','translate-y-64');
    toast.classList.add('opacity-100','translate-y-0');

    // Hide after duration
    setTimeout(()=>{
        toast.classList.remove('opacity-100','translate-y-0');
        toast.classList.add('opacity-0','translate-y-64');
    }, duration);
}

// ======= Helper to get CSRF =======
function getCookie(name){
    const cookieValue = document.cookie.split('; ').find(row => row.startsWith(name+'='));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
}

// ======= AJAX Add to Cart =======
document.addEventListener('submit', function(e){
    const form = e.target;
    if(form.classList.contains('ajax-add-to-cart')){
        e.preventDefault();

        const action = form.getAttribute('action').replace('/cart/add/','/cart/add-ajax/');
        const formData = new FormData(form);
        const payload = {};
        formData.forEach((v,k)=> payload[k]=v);

        fetch(action, {
            method:'POST',
            headers:{
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        })
        .then(async r=>{
            let data = null;
            try { data = await r.json(); } catch(e){}

            if(!data){
                showToast('Error','Server response error','error');
                return;
            }

            if(!r.ok){
                showToast('Error', data.message || 'Server error','error');
                return;
            }

            if(data.login_required){
                showToast('Info', data.message || 'Please login','normal');
                return;
            }

            if(data.success){
                // Update cart HTML jika ada
                if(data.cart_html){
                    const cartContainer = document.getElementById('cart-items');
                    if(cartContainer) cartContainer.innerHTML = data.cart_html;
                }
                showToast('Success', data.message || 'Added to cart','success');
            } else {
                showToast('Error', data.message || 'Failed to add to cart','error');
            }
        })
        .catch(()=> showToast('Error','Network error','error'));
    }
});
// Intercept remove buttons
document.addEventListener('click', function(e){
  if(e.target && e.target.matches && e.target.matches('.remove-ajax')){
    const id = e.target.dataset.id;
    fetch((e.target.dataset.href || (`/rental/cart/remove-ajax/${id}/`)), {method:'POST', headers:{'X-CSRFToken':getCookie('csrftoken')}})
      .then(async r=>{
        const j = await r.json().catch(()=>null);
        if(!j){ showToast('Error', 'Server error', 'error'); return; }
        if(j.login_required){ showToast('Info', 'Please login to continue', 'normal'); return; }
        if(j.success){
          showToast('Success', j.message || 'Removed', 'success');
          const el = e.target.closest('.cart-item'); if(el) el.remove();
        } else showToast('Error', j.message || 'Error', 'error');
      }).catch(()=> showToast('Error', 'Network error', 'error'));
  }
});

// Checkout button
document.addEventListener('click', function(e){
  if(e.target && e.target.matches && e.target.matches('.checkout-ajax')){
    fetch((e.target.dataset.href || '/rental/checkout-ajax/'), {method:'POST', headers:{'X-CSRFToken':getCookie('csrftoken')}})
      .then(async r=>{
        const j = await r.json().catch(()=>null);
        if(!j){ showToast('Error', 'Server error', 'error'); return; }
        if(j.login_required){ showToast('Info', 'Please login to continue', 'normal'); return; }
        if(j.success){ showToast('Success', j.message || 'Checkout success', 'success'); window.location.href = (j.rental_id?('/rental/checkout/'+j.rental_id+'/success/'):'#'); }
        else showToast('Error', j.message || 'Error', 'error');
      }).catch(()=> showToast('Error', 'Network error', 'error'));
  }
});

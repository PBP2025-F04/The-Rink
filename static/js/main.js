// Global JS for ajax handlers and toasts
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function showToast(html, timeout=3000){
  const t = document.getElementById('toast') || (()=>{
    const el = document.createElement('div'); el.id='toast'; document.body.appendChild(el); return el; })();
  t.innerHTML = html;
  t.style.display = 'block';
  clearTimeout(t._hide);
  t._hide = setTimeout(()=> t.style.display='none', timeout);
}

// Intercept add-to-cart forms (progressive enhancement)
document.addEventListener('submit', function(e){
  const f = e.target;
  if(f && f.classList && f.classList.contains('ajax-add-to-cart')){
    e.preventDefault();
    const action = f.getAttribute('action');
    const formData = new FormData(f);
    const payload = {};
    formData.forEach((v,k)=> payload[k]=v);
    fetch(action.replace('/cart/add/','/cart/add-ajax/'),{
      method:'POST',
      headers:{'X-CSRFToken':getCookie('csrftoken'),'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    }).then(async r=>{
      const j = await r.json().catch(()=>null);
      if(!j){ showToast('Server response error'); return; }
      if(j.login_required){ showToast('Please login to continue'); return; }
      if(j.success){ showToast(j.message || 'Added to cart'); }
      else{ showToast(j.message || 'Error'); }
    }).catch(()=> showToast('Network error'));
  }
});

// Intercept remove buttons
document.addEventListener('click', function(e){
  if(e.target && e.target.matches && e.target.matches('.remove-ajax')){
    const id = e.target.dataset.id;
    fetch((e.target.dataset.href || (`/rental/cart/remove-ajax/${id}/`)), {method:'POST', headers:{'X-CSRFToken':getCookie('csrftoken')}})
      .then(async r=>{
        const j = await r.json().catch(()=>null);
        if(!j){ showToast('Server error'); return; }
        if(j.login_required){ showToast('Please login to continue'); return; }
        if(j.success){
          showToast(j.message || 'Removed');
          const el = e.target.closest('.cart-item'); if(el) el.remove();
        } else showToast(j.message || 'Error');
      }).catch(()=> showToast('Network error'));
  }
});

// Checkout button
document.addEventListener('click', function(e){
  if(e.target && e.target.matches && e.target.matches('.checkout-ajax')){
    fetch((e.target.dataset.href || '/rental/checkout-ajax/'), {method:'POST', headers:{'X-CSRFToken':getCookie('csrftoken')}})
      .then(async r=>{
        const j = await r.json().catch(()=>null);
        if(!j){ showToast('Server error'); return; }
        if(j.login_required){ showToast('Please login to continue'); return; }
        if(j.success){ showToast(j.message || 'Checkout success'); window.location.href = (j.rental_id?('/rental/checkout/'+j.rental_id+'/success/'):'#'); }
        else showToast(j.message || 'Error');
      }).catch(()=> showToast('Network error'));
  }
});

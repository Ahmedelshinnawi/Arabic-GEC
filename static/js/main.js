// Copy text to clipboard
function copyText(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'alert alert-success position-fixed top-0 end-0 m-3';
        toast.style.zIndex = '9999';
        toast.textContent = 'تم نسخ النص بنجاح!';
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
}

// Form submission with loading state
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('correctionForm');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = submitBtn?.querySelector('.spinner-border');
    
    if (form && submitBtn) {
        form.addEventListener('submit', function() {
            submitBtn.classList.add('loading');
            spinner?.classList.remove('d-none');
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> جارِ التصحيح...';
            submitBtn.disabled = true;
        });
    }
});

// Character counter for textarea
const textarea = document.getElementById('text');
if (textarea) {
    const maxLength = textarea.getAttribute('maxlength');
    const counter = document.createElement('small');
    counter.className = 'text-muted';
    textarea.parentNode.appendChild(counter);
    
    function updateCounter() {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${remaining} حرف متبقي`;
        
        if (remaining < 100) {
            counter.className = 'text-warning';
        } else if (remaining < 50) {
            counter.className = 'text-danger';
        } else {
            counter.className = 'text-muted';
        }
    }
    
    textarea.addEventListener('input', updateCounter);
    updateCounter();
}
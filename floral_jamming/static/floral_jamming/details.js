document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('uuid') === null) {
        localStorage.setItem('uuid', crypto.randomUUID());
    }
    document.getElementById('guest_id').value = localStorage.getItem('uuid');
})
async function connectMetaMask() {
    if (window.ethereum) {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            console.log('Connected account:', accounts[0]);
            // Add code to handle the account data
            handleAccountChanged(accounts)
        } catch (error) {
            console.error('User denied account access', error);
        }
    } else {
        alert('MetaMask is not installed. Please install it to use this feature.');
    }
}


async function handleAccountChanged(accounts) {
    if (accounts.length === 0) {
        console.log('Please connect to MetaMask.');
    } else {
        const account = accounts[0];
        console.log('Selected account:', account);
        // Send the account to the Django backend
        fetch('/path-to-your-django-view/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Ensure CSRF token is sent
            },
            body: JSON.stringify({ account: account })
        }).then(response => response.json())
          .then(data => {
            console.log('Success:', data);
            // Handle response data
        }).catch((error) => {
            console.error('Error:', error);
        });
    }
}

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

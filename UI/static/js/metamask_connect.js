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
        
        // Store the account in localStorage or sessionStorage
        localStorage.setItem('ethereumAccount', account);

        // Redirect to the details form
        window.location.href = '/metamask_signin/?account=' + account;
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

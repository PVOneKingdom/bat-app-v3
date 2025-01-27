function tokenLoginCheck() {
    const accessToken = window.localStorage.getItem("access_token");

    if (accessToken) {
        const headers = new Headers();
        headers.append("Authorization", `Bearer ${accessToken}`); // Prefixing with Bearer is standard for tokens

        fetch(tokenCheckUrl, {
            method: 'GET',
            headers: headers
        })
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error(`Request failed with status ${response.status}`);
                }
            })
            .then((data) => {
                console.log(data);
                window.location.href = data.redirect_to;
            })
            .catch((error) => {
                console.error("Error during token validation:", error);
            });
    } else {
        console.warn("No access token found in localStorage");
    }
}

// Run the check after 300ms
setTimeout(() => {
    tokenLoginCheck();
}, 300);


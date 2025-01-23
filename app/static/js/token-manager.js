class TokenManager {
    constructor() {
        if (TokenManager.instance) {
            console.log("TokenManager instance already exists.");
            return TokenManager.instance;
        }

        this.intervalId = null;
        this.init();
        TokenManager.instance = this;
    }

    // Initialize the TokenManager
    init() {
        this.checkTokenTimeToExpire();
        this.startInterval();
        this.storeLastPageUrl();
    }

    // Check time left until token expiration and take necessary actions
    checkTokenTimeToExpire() {
        const tokenInfo = this.getTokenTimeInfo();

        if (!tokenInfo) {
            console.error("Token not found or invalid.");
            return;
        }

        const { time_to_expire } = tokenInfo;

        if (time_to_expire > 10 * 60 * 1000) { // More than 10 minutes left
            console.log("Token is valid. No action needed.");
        } else if (time_to_expire > 0) { // Less than 10 minutes left
            console.log("Token is close to expiration. Attempting to renew token.");
            this.renewToken();
        } else { // Token is expired
            console.warn("Token is expired. Removing token and stopping interval.");
            this.removeToken();
            this.stopInterval();
        }
    }

    // Decode the token and return time-to-expire information
    getTokenTimeInfo() {
        const token = localStorage.getItem('access_token');

        if (!token) {
            return null;
        }

        if (!token.startsWith("Bearer ")) {
            console.error("Invalid token format. Expected 'Bearer <token>'.");
            return null;
        }

        const jwtToken = token.split(' ')[1];

        try {
            const parts = jwtToken.split('.');
            if (parts.length !== 3) {
                throw new Error('Invalid JWT token format.');
            }

            const payload = JSON.parse(atob(parts[1]));
            const expTime = payload.exp * 1000; // Convert expiration time to milliseconds
            const currentTime = Date.now(); // Current time in milliseconds
            const timeToExpire = expTime - currentTime; // Time left until expiration

            const absTimeToExpire = Math.abs(timeToExpire);
            const hours = Math.floor(absTimeToExpire / (3600 * 1000));
            const minutes = Math.floor((absTimeToExpire % (3600 * 1000)) / (60 * 1000));
            const seconds = Math.floor((absTimeToExpire % (60 * 1000)) / 1000);
            const humanReadableTime = `${hours}h ${minutes}m ${seconds}s`;

            return {
                time_to_expire: timeToExpire, // Time left in milliseconds (negative if expired)
                time_to_expire_h: humanReadableTime, // Human-readable format
            };
        } catch (error) {
            console.error("Failed to parse the JWT token:", error.message);
            return null;
        }
    }

    // Start the interval to check token expiration every 3 minutes
    startInterval() {
        if (this.intervalId) {
            console.log("Interval already running.");
            return;
        }

        this.intervalId = setInterval(() => {
            this.checkTokenTimeToExpire();
        }, 3 * 60 * 1000); // Every 3 minutes

        console.log("TokenManager interval started.");
    }

    // Stop the interval
    stopInterval() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            console.log("TokenManager interval stopped.");
        }
    }

    // Restart the interval
    restartInterval() {
        console.log("Restarting TokenManager interval...");
        this.stopInterval();
        this.startInterval();
    }

    // Handle token refresh and restart interval
    handleTokenRefresh(newToken) {
        console.log("Handling token refresh...");
        localStorage.setItem('access_token', `Bearer ${newToken}`);
        this.restartInterval();
        console.log("Token refreshed and interval restarted.");
    }

    // Remove the token from localStorage
    removeToken() {
        localStorage.removeItem('access_token');
        console.log("Token removed from localStorage.");
    }

    // Store the currently open page URL to localStorage
    storeLastPageUrl() {
        const currentPage = window.location.href;
        localStorage.setItem('last_page_url', currentPage);
        console.log("Last page URL stored:", currentPage);
    }

    // Function to renew the token
    renewToken() {
        console.log("Renewing token...");

        const accessToken = window.localStorage.getItem("access_token");

        if (!accessToken) {
            console.error("No access token found in localStorage.");
            return;
        }

        const headers = new Headers();
        headers.append("Authorization", accessToken);
        headers.append("HX-Request", "true"); // Ensure the value is a string

        fetch(tokenRenewUrl, {
            method: 'GET',
            headers: headers,
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Token renewal failed with status: ${response.status}`);
                }
                return response.json(); // Parse JSON response
            })
            .then((data) => {
                if (data && data.access_token) {
                    console.log("Token successfully renewed:", data);
                    window.localStorage.setItem("access_token", data.access_token);
                } else {
                    console.error("Token renewal response is missing 'access_token'.", data);
                }
            })
            .catch((error) => {
                console.error("Token renewal error:", error);
            });
    }
}

// Automatically initialize the TokenManager on page load and expose it globally
window.addEventListener('load', () => {
    window.tokenManager = new TokenManager(); // Assign the instance to a global variable
    console.log("TokenManager initialized and accessible as 'window.tokenManager'.");
});


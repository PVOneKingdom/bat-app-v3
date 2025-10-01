class JwtManager {
    constructor() {
        this.expiryKey = "jwt_expiry_time";
        this.checkIntervalMs = 60 * 1000; // 1 minute
        this.renewThresholdSec = 180; // 3 minutes
        this.intervalId = null;
    }

    /**
     * Initialize manager: fetch expiry if missing, start monitoring.
     */
    async init() {
        let expiry = this.getStoredExpiry();
        if (!expiry) {
            expiry = await this.fetchTokenInfo();
        }
        if (expiry) {
            this.storeExpiry(expiry);
        }

        this.startMonitoring();
        this.checkRenewalNow();
    }

    /**
     * Start background monitoring every minute.
     */
    startMonitoring() {
        if (this.intervalId) clearInterval(this.intervalId);

        this.intervalId = setInterval(async () => {
            const expiry = this.getStoredExpiry();
            if (!expiry) {
                // Missing info → fetch again
                await this.fetchTokenInfo();
                return;
            }

            const now = Math.floor(Date.now() / 1000);
            if (expiry - now < this.renewThresholdSec) {
                await this.fetchTokenInfo(true); // force renew
            }
        }, this.checkIntervalMs);
    }

    /**
     * Fetch token info (and renew if needed).
     * @param {boolean} renew 
     * @returns {number|null} expiry timestamp (seconds)
     */
    async fetchTokenInfo() {
        try {
            const url = tokenCheckUrl
            const resp = await fetch(url, {
                method: "GET",
            });
            if (!resp.ok) throw new Error("Failed token check");

            const data = await resp.json();
            if (data.exp) {
                this.storeExpiry(data.exp);
                this.checkRenewalNow(); // immediate re-check
                return data.exp;
            }
        } catch (err) {
            console.error("Error fetching token info:", err);
        }
        return null;
    }

    /**
     * Store expiry timestamp in localStorage.
     */
    storeExpiry(expiry) {
        localStorage.setItem(this.expiryKey, expiry.toString());
    }

    /**
     * Get expiry timestamp from localStorage.
     */
    getStoredExpiry() {
        const val = localStorage.getItem(this.expiryKey);
        return val ? parseInt(val, 10) : null;
    }

    /**
     * Run immediate renewal check after fresh token info fetch.
     */
    async checkRenewalNow() {
        const expiry = this.getStoredExpiry();
        if (!expiry) return;
        const now = Math.floor(Date.now() / 1000);
        if (expiry - now < this.renewThresholdSec) {
            await this.fetchTokenInfo(true);
        }
    }
}

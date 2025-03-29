(async function () {
    // Backend URL (Update this)
    const TRACKING_URL = "https://lamprey-included-lion.ngrok-free.app/api/pixel/track_pixel/";

    let startTime = new Date().getTime(); // Initialize timer

    async function getVisitorIP() {
        try {
            let response = await fetch("https://api64.ipify.org?format=json");
            let data = await response.json();
            return data.ip;
        } catch (error) {
            console.error("Failed to get IP:", error);
            return null;
        }
    }

    function getBodyContent() {
        return document.body.outerHTML; // Get only the <body> content
    }

    async function sendTrackingData() {
        let ip = await getVisitorIP();
        if (!ip) return; // Stop if IP is not available
        let endTime = new Date().getTime();
        let timeSpent = (endTime - startTime) / 1000; // Convert ms to seconds

        let data = {
            url: window.location.href,
            referrer: document.referrer,
            userAgent: navigator.userAgent,
            ip: ip,
            timeSpent: timeSpent,
            bodyContent: getBodyContent() // Capture only <body> content
        };

        console.log("Tracking Data Sent:", data);

        // Send data to the backend
        fetch(TRACKING_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }).catch(error => console.error("Tracking failed:", error));

        startTime = new Date().getTime(); // Reset timer for new page
    }

    // Track page load
    window.addEventListener("load", sendTrackingData);

    // Track when user navigates within a React SPA
    window.addEventListener("popstate", sendTrackingData);

    // Override pushState & replaceState to detect React Router navigation
    const originalPushState = history.pushState;
    history.pushState = function () {
        sendTrackingData();
        return originalPushState.apply(history, arguments);
    };

    const originalReplaceState = history.replaceState;
    history.replaceState = function () {
        sendTrackingData();
        return originalReplaceState.apply(history, arguments);
    };

    // Track page exit
    window.addEventListener("beforeunload", sendTrackingData);

})();

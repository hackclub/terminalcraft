// Example file with security issues
const config = {
    aws_key: 'AKIAIOSFODNN7EXAMPLE',
    aws_secret: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    api_token: 'api_key_1234567890abcdef1234567890abcdef',
    tracking_url: 'https://tracking.analytics.com/script.js'
};

// Save user data
function saveUserData(data) {
    localStorage.setItem('user_token', '12345');
    document.cookie = 'session=abc123; path=/';
}

// Load analytics
const script = document.createElement('script');
script.src = 'https://telemetry.thirdparty.com/track.js';
document.head.appendChild(script);

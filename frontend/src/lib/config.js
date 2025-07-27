// Environment detection
const isDev = import.meta.env.DEV;
const isProduction = import.meta.env.PROD;

// API Configuration
export const API_CONFIG = {
    baseURL: isDev 
        ? 'http://localhost:8000' 
        : (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000'),
    
    endpoints: {
        auth: {
            login: '/api/auth/login',
            register: '/api/auth/register',
            me: '/api/auth/me',
            users: '/api/auth/users'
        },
        issues: {
            base: '/api/issues',
            create: '/api/issues',
            list: '/api/issues',
            detail: (id) => `/api/issues/${id}`,
            update: (id) => `/api/issues/${id}`,
            delete: (id) => `/api/issues/${id}`
        },
        dashboard: {
            stats: '/api/dashboard/stats',
            dailyStats: '/api/dashboard/daily-stats',
            analytics: '/api/dashboard/analytics'
        },
        ai: {
            classify: '/api/ai/classify-issue',
            analyze: '/api/ai/analyze-issue',
            chat: '/api/ai/chat',
            insights: '/api/ai/insights/dashboard'
        }
    }
};

// WebSocket Configuration
export const WS_CONFIG = {
    url: isDev 
        ? 'ws://localhost:8000/ws' 
        : (typeof window !== 'undefined' 
            ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`
            : 'ws://localhost:8000/ws'),
    reconnectInterval: 5000,
    maxReconnectAttempts: 10
};

// Helper function to get full API URL
export const getApiUrl = (endpoint) => {
    const baseURL = API_CONFIG.baseURL;
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${baseURL}/${cleanEndpoint}`;
};

// Helper function to get auth headers
export const getAuthHeaders = () => {
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('auth_token');
        if (token) {
            return {
                'Authorization': `Bearer ${token}`
            };
        }
    }
    return {};
};

// Export environment flags
export { isDev, isProduction };

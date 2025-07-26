const isDev = import.meta.env.DEV;
const isProduction = import.meta.env.PROD;

// API Configuration
export const API_CONFIG = {
    // Base URL for API calls
    baseURL: isDev 
        ? 'http://localhost:8000' 
        : window.location.origin,
    
    // API endpoints
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
            insights: '/api/ai/insights/dashboard',
            processDocument: '/api/ai/process-document',
            predictResolution: '/api/ai/predict-resolution',
            suggestAssignment: '/api/ai/suggest-assignment',
            teamAnalytics: '/api/ai/team-analytics',
            notifications: '/api/ai/smart-notifications',
            health: '/api/ai/health',
            stats: '/api/ai/stats',
            batchClassify: '/api/ai/batch-classify',
            retrainModels: '/api/ai/retrain-models'
        }
    }
};

// WebSocket Configuration
export const WS_CONFIG = {
    url: isDev 
        ? 'ws://localhost:8000/ws' 
        : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10
};

// Application Configuration
export const APP_CONFIG = {
    name: 'AI-Enhanced Issues Tracker',
    version: '2.0.0',
    description: 'Intelligent issue tracking with AI capabilities',
    
    // Features flags
    features: {
        aiEnabled: true,
        chatAssistant: true,
        predictiveAnalytics: true,
        smartNotifications: true,
        documentProcessing: true,
        realTimeUpdates: true
    },
    
    // UI Configuration
    ui: {
        theme: 'light', // 'light' | 'dark' | 'auto'
        sidebar: {
            collapsed: false
        },
        dashboard: {
            refreshInterval: 30000, // 30 seconds
            showAIInsights: true,
            autoRefresh: true
        },
        notifications: {
            position: 'top-right',
            duration: 5000,
            maxVisible: 5
        }
    },
    
    // Pagination defaults
    pagination: {
        defaultPageSize: 20,
        pageSizeOptions: [10, 20, 50, 100]
    },
    
    // File upload configuration
    upload: {
        maxSizeBytes: 10 * 1024 * 1024, // 10MB
        allowedTypes: [
            'image/jpeg',
            'image/png', 
            'image/gif',
            'application/pdf',
            'text/plain',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ],
        allowedExtensions: ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.doc', '.docx']
    }
};

// Environment variables (with fallbacks)
export const ENV = {
    isDev,
    isProduction,
    apiUrl: import.meta.env.VITE_API_URL || API_CONFIG.baseURL,
    wsUrl: import.meta.env.VITE_WS_URL || WS_CONFIG.url,
    enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    logLevel: import.meta.env.VITE_LOG_LEVEL || (isDev ? 'debug' : 'warn')
};

// Helper functions
export const getApiUrl = (endpoint) => {
    return `${ENV.apiUrl}${endpoint}`;
};

export const getFullUrl = (path) => {
    // Handle absolute URLs
    if (path.startsWith('http://') || path.startsWith('https://')) {
        return path;
    }
    
    // Handle API paths
    if (path.startsWith('/api/')) {
        return getApiUrl(path);
    }
    
    // Handle relative paths
    return `${ENV.apiUrl}${path.startsWith('/') ? path : `/${path}`}`;
};

// Export default configuration
export default {
    API_CONFIG,
    WS_CONFIG,
    APP_CONFIG,
    ENV,
    getApiUrl,
    getFullUrl
};

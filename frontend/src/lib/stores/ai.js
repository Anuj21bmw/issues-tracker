// src/lib/stores/ai.js
import { writable } from 'svelte/store';
import { API_CONFIG, getApiUrl, getAuthHeaders } from '$lib/config.js';

// AI store
const createAIStore = () => {
    const { subscribe, set, update } = writable({
        analyzing: false,
        insights: null,
        predictions: null,
        suggestions: null,
        chatMessages: [],
        chatLoading: false,
        error: null,
        analytics: null
    });

    return {
        subscribe,

        async analyzeIssue(issueData) {
            update(state => ({ ...state, analyzing: true, error: null }));

            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.analyze), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    },
                    body: JSON.stringify(issueData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Analysis failed' }));
                    throw new Error(errorData.detail || 'Analysis failed');
                }

                const analysis = await response.json();

                update(state => ({
                    ...state,
                    insights: analysis,
                    analyzing: false
                }));

                return analysis;

            } catch (error) {
                update(state => ({
                    ...state,
                    analyzing: false,
                    error: error.message
                }));
                throw error;
            }
        },

        async classifyIssue(issueData) {
            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.classify), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    },
                    body: JSON.stringify(issueData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Classification failed' }));
                    throw new Error(errorData.detail || 'Classification failed');
                }

                return await response.json();

            } catch (error) {
                throw error;
            }
        },

        async predictResolution(issueId) {
            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.predictResolution), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    },
                    body: JSON.stringify({ issue_id: issueId })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Prediction failed' }));
                    throw new Error(errorData.detail || 'Prediction failed');
                }

                const prediction = await response.json();

                update(state => ({
                    ...state,
                    predictions: prediction
                }));

                return prediction;

            } catch (error) {
                throw error;
            }
        },

        async suggestAssignment(issueId) {
            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.suggestAssignment), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    },
                    body: JSON.stringify({ issue_id: issueId })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Assignment suggestion failed' }));
                    throw new Error(errorData.detail || 'Assignment suggestion failed');
                }

                const suggestions = await response.json();

                update(state => ({
                    ...state,
                    suggestions
                }));

                return suggestions;

            } catch (error) {
                throw error;
            }
        },

        async sendChatMessage(message, context = {}) {
            update(state => ({
                ...state,
                chatLoading: true,
                chatMessages: [...state.chatMessages, { role: 'user', content: message }]
            }));

            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.chat), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    },
                    body: JSON.stringify({
                        message,
                        context,
                        conversation_history: this.get().chatMessages.slice(-10) // Last 10 messages
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Chat failed' }));
                    throw new Error(errorData.detail || 'Chat failed');
                }

                const chatResponse = await response.json();

                update(state => ({
                    ...state,
                    chatLoading: false,
                    chatMessages: [...state.chatMessages, { role: 'assistant', content: chatResponse.response }]
                }));

                return chatResponse;

            } catch (error) {
                update(state => ({
                    ...state,
                    chatLoading: false,
                    error: error.message
                }));
                throw error;
            }
        },

        async getDashboardInsights() {
            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.insights), {
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to get insights' }));
                    throw new Error(errorData.detail || 'Failed to get insights');
                }

                const insights = await response.json();

                update(state => ({
                    ...state,
                    analytics: insights
                }));

                return insights;

            } catch (error) {
                throw error;
            }
        },

        async getTeamAnalytics() {
            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.teamAnalytics), {
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Failed to get team analytics' }));
                    throw new Error(errorData.detail || 'Failed to get team analytics');
                }

                return await response.json();

            } catch (error) {
                throw error;
            }
        },

        clearChat() {
            update(state => ({ ...state, chatMessages: [] }));
        },

        clearError() {
            update(state => ({ ...state, error: null }));
        },

        // Get current state
        get() {
            let currentState;
            subscribe(state => currentState = state)();
            return currentState;
        }
    };
};

export const aiStore = createAIStore();
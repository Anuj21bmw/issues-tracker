import { writable, derived } from 'svelte/store';
import { authStore } from './auth.js';
import { API_CONFIG, getApiUrl } from './config.js';

const createAIStore = () => {
    const { subscribe, set, update } = writable({
        insights: [],
        chatHistory: [],
        isTyping: false,
        services: {
            classification: true,
            chat: true,
            analytics: true,
            predictions: true
        },
        health: null,
        stats: null,
        loading: false,
        error: null
    });

    const getAuthHeaders = () => authStore.getAuthHeaders();

    return {
        subscribe,

        async getInsights() {
            update(state => ({ ...state, loading: true }));

            try {
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.insights), {
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders()
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    update(state => ({
                        ...state,
                        insights: data.insights || [],
                        loading: false
                    }));
                }
            } catch (error) {
                update(state => ({ ...state, loading: false, error: error.message }));
            }
        },

        async sendChatMessage(message) {
            update(state => ({ 
                ...state, 
                isTyping: true,
                chatHistory: [...state.chatHistory, { type: 'user', message, timestamp: new Date() }]
            }));

            try {
                const formData = new FormData();
                formData.append('message', message);

                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.chat), {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Failed to get AI response');
                }

                const data = await response.json();

                update(state => ({
                    ...state,
                    isTyping: false,
                    chatHistory: [...state.chatHistory, {
                        type: 'ai',
                        message: data.response.response,
                        confidence: data.response.confidence,
                        suggestions: data.response.suggestions || [],
                        timestamp: new Date()
                    }]
                }));

                return data.response;

            } catch (error) {
                update(state => ({
                    ...state,
                    isTyping: false,
                    chatHistory: [...state.chatHistory, {
                        type: 'ai',
                        message: 'Sorry, I encountered an error processing your request.',
                        timestamp: new Date()
                    }]
                }));
                throw error;
            }
        },

        async classifyIssue(title, description) {
            try {
                const formData = new FormData();
                formData.append('title', title);
                formData.append('description', description);

                const response = await fetch(getApiUrl(API_CONFIG.endpoints.ai.classify), {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Classification failed');
                }

                const data = await response.json();
                return data.classification;

            } catch (error) {
                throw new Error(error.message || 'Classification service unavailable');
            }
        },

        async analyzeIssue(issueData) {
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
                    throw new Error('Analysis failed');
                }

                const data = await response.json();
                return data.analysis;

            } catch (error) {
                throw new Error(error.message || 'Analysis service unavailable');
            }
        },

        clearChatHistory() {
            update(state => ({ ...state, chatHistory: [] }));
        }
    };
};

export const aiStore = createAIStore();

// Derived stores
export const aiInsights = derived(aiStore, $store => $store.insights);
export const chatHistory = derived(aiStore, $store => $store.chatHistory);
export const aiLoading = derived(aiStore, $store => $store.loading);

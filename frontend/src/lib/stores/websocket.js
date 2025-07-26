import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { WS_CONFIG } from './config.js';
import { toastStore } from './toast.js';

const createWebSocketStore = () => {
    const { subscribe, set, update } = writable({
        connected: false,
        connecting: false,
        messages: [],
        error: null
    });

    let ws = null;
    let reconnectAttempts = 0;
    let reconnectTimeout = null;

    const connect = () => {
        if (!browser || ws?.readyState === WebSocket.OPEN) return;

        update(state => ({ ...state, connecting: true, error: null }));

        try {
            ws = new WebSocket(WS_CONFIG.url);

            ws.onopen = () => {
                console.log('WebSocket connected');
                reconnectAttempts = 0;
                update(state => ({
                    ...state,
                    connected: true,
                    connecting: false,
                    error: null
                }));
            };

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    update(state => ({
                        ...state,
                        messages: [...state.messages.slice(-99), message] // Keep last 100 messages
                    }));

                    // Handle specific message types
                    handleMessage(message);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                update(state => ({
                    ...state,
                    connected: false,
                    connecting: false
                }));

                // Attempt to reconnect
                if (reconnectAttempts < WS_CONFIG.maxReconnectAttempts) {
                    reconnectAttempts++;
                    reconnectTimeout = setTimeout(() => {
                        console.log(`Reconnecting... (attempt ${reconnectAttempts})`);
                        connect();
                    }, WS_CONFIG.reconnectInterval);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                update(state => ({
                    ...state,
                    error: 'WebSocket connection failed',
                    connecting: false
                }));
            };

        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            update(state => ({
                ...state,
                error: error.message,
                connecting: false
            }));
        }
    };

    const disconnect = () => {
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout);
            reconnectTimeout = null;
        }

        if (ws) {
            ws.close();
            ws = null;
        }

        set({
            connected: false,
            connecting: false,
            messages: [],
            error: null
        });
    };

    const send = (message) => {
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send(typeof message === 'string' ? message : JSON.stringify(message));
            return true;
        }
        return false;
    };

    const handleMessage = (message) => {
        // Handle different message types
        switch (message.type) {
            case 'issue_created':
                toastStore.success(`New issue created: ${message.data.title}`);
                break;
            case 'issue_updated':
                toastStore.info(`Issue updated: ${message.data.title}`);
                break;
            case 'issue_assigned':
                toastStore.info(`Issue assigned: ${message.data.title}`);
                break;
            case 'notification':
                toastStore.add({
                    type: message.data.type || 'info',
                    message: message.data.message,
                    duration: message.data.duration || 5000
                });
                break;
            default:
                console.log('Unhandled WebSocket message:', message);
        }
    };

    // Auto-connect when store is created
    if (browser) {
        connect();
    }

    return {
        subscribe,
        connect,
        disconnect,
        send
    };
};

export const wsStore = createWebSocketStore();
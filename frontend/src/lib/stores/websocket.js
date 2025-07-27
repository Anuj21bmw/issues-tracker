// src/lib/stores/websocket.js
import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { WS_CONFIG } from '$lib/config.js';
import { toastStore } from './toast.js';

// WebSocket store
const createWebSocketStore = () => {
    const { subscribe, set, update } = writable({
        connected: false,
        connecting: false,
        error: null,
        lastMessage: null,
        reconnectAttempts: 0
    });

    let ws = null;
    let reconnectTimer = null;
    let pingTimer = null;
    let reconnectInterval = WS_CONFIG.reconnectInterval;

    const connect = () => {
        if (!browser || ws?.readyState === WebSocket.OPEN) return;

        update(state => ({ ...state, connecting: true, error: null }));

        try {
            // Get auth token for connection
            const token = localStorage.getItem('auth_token');
            const wsUrl = token ? `${WS_CONFIG.url}?token=${token}` : WS_CONFIG.url;
            
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket connected');
                update(state => ({
                    ...state,
                    connected: true,
                    connecting: false,
                    error: null,
                    reconnectAttempts: 0
                }));

                // Reset reconnect interval
                reconnectInterval = WS_CONFIG.reconnectInterval;

                // Start ping/pong to keep connection alive
                startPing();
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('WebSocket message:', data);

                    update(state => ({ ...state, lastMessage: data }));

                    // Handle different message types
                    handleMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                update(state => ({
                    ...state,
                    connected: false,
                    connecting: false
                }));

                stopPing();

                // Attempt to reconnect if not a normal closure
                if (event.code !== 1000 && event.code !== 1001) {
                    scheduleReconnect();
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                update(state => ({
                    ...state,
                    connected: false,
                    connecting: false,
                    error: 'Connection error'
                }));
            };

        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            update(state => ({
                ...state,
                connected: false,
                connecting: false,
                error: error.message
            }));
        }
    };

    const disconnect = () => {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }

        stopPing();

        if (ws) {
            ws.close(1000, 'User disconnect');
            ws = null;
        }

        update(state => ({
            ...state,
            connected: false,
            connecting: false,
            reconnectAttempts: 0
        }));
    };

    const send = (data) => {
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(data));
            return true;
        }
        return false;
    };

    const scheduleReconnect = () => {
        if (reconnectTimer) return;

        update(state => {
            const attempts = state.reconnectAttempts + 1;
            
            if (attempts > WS_CONFIG.reconnectAttempts) {
                return {
                    ...state,
                    error: 'Max reconnection attempts reached',
                    reconnectAttempts: attempts
                };
            }

            // Exponential backoff
            const delay = Math.min(
                reconnectInterval * Math.pow(WS_CONFIG.reconnectBackoffFactor, attempts - 1),
                WS_CONFIG.maxReconnectInterval
            );

            console.log(`Scheduling reconnect attempt ${attempts} in ${delay}ms`);

            reconnectTimer = setTimeout(() => {
                reconnectTimer = null;
                connect();
            }, delay);

            return { ...state, reconnectAttempts: attempts };
        });
    };

    const startPing = () => {
        stopPing();
        pingTimer = setInterval(() => {
            if (ws?.readyState === WebSocket.OPEN) {
                send({ type: 'ping' });
            }
        }, 30000); // Ping every 30 seconds
    };

    const stopPing = () => {
        if (pingTimer) {
            clearInterval(pingTimer);
            pingTimer = null;
        }
    };

    const handleMessage = (data) => {
        switch (data.type) {
            case 'pong':
                // Keep-alive response
                break;
                
            case 'issue_update':
                toastStore.info(`Issue "${data.title}" has been updated`);
                break;
                
            case 'issue_assignment':
                toastStore.info(`You have been assigned to issue: ${data.title}`);
                break;
                
            case 'notification':
                toastStore.info(data.message);
                break;
                
            default:
                console.log('Unhandled WebSocket message type:', data.type);
        }
    };

    return {
        subscribe,
        connect,
        disconnect,
        send
    };
};

export const wsStore = createWebSocketStore();
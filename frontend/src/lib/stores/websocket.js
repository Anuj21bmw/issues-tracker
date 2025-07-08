import { writable } from 'svelte/stores';
import { browser } from '$app/environment';
import { toastStore } from './toast.js';

function createWebSocketStore() {
	const { subscribe, set, update } = writable({
		connected: false,
		socket: null
	});

	let reconnectInterval;
	let reconnectAttempts = 0;
	const maxReconnectAttempts = 5;

	return {
		subscribe,
		connect() {
			if (!browser) return;

			try {
				const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
				const wsUrl = `${protocol}//${window.location.host}/ws`;
				const socket = new WebSocket(wsUrl);

				socket.onopen = () => {
					console.log('WebSocket connected');
					set({ connected: true, socket });
					reconnectAttempts = 0;
					if (reconnectInterval) {
						clearInterval(reconnectInterval);
						reconnectInterval = null;
					}
				};

				socket.onmessage = (event) => {
					try {
						const message = JSON.parse(event.data);
						handleMessage(message);
					} catch (error) {
						console.error('Error parsing WebSocket message:', error);
					}
				};

				socket.onclose = () => {
					console.log('WebSocket disconnected');
					set({ connected: false, socket: null });
					attemptReconnect();
				};

				socket.onerror = (error) => {
					console.error('WebSocket error:', error);
				};

			} catch (error) {
				console.error('Failed to create WebSocket:', error);
			}
		},

		disconnect() {
			update(state => {
				if (state.socket) {
					state.socket.close();
				}
				return { connected: false, socket: null };
			});

			if (reconnectInterval) {
				clearInterval(reconnectInterval);
				reconnectInterval = null;
			}
		}
	};

	function handleMessage(message) {
		switch (message.type) {
			case 'issue_created':
				toastStore.add({
					type: 'info',
					message: `New issue created: ${message.data.title} by ${message.data.reporter}`,
					duration: 4000
				});
				// Trigger refresh of issues list if on issues page
				window.dispatchEvent(new CustomEvent('refresh-issues'));
				break;

			case 'issue_status_changed':
				toastStore.add({
					type: 'info',
					message: `Issue "${message.data.title}" status changed from ${message.data.old_status} to ${message.data.new_status}`,
					duration: 4000
				});
				// Trigger refresh of issues list if on issues page
				window.dispatchEvent(new CustomEvent('refresh-issues'));
				break;

			default:
				console.log('Unknown message type:', message.type);
		}
	}

	function attemptReconnect() {
		if (reconnectAttempts >= maxReconnectAttempts) {
			console.log('Max reconnect attempts reached');
			return;
		}

		if (!reconnectInterval) {
			reconnectInterval = setInterval(() => {
				if (reconnectAttempts < maxReconnectAttempts) {
					console.log(`Attempting to reconnect... (${reconnectAttempts + 1}/${maxReconnectAttempts})`);
					reconnectAttempts++;
					// Try to reconnect
					createWebSocketStore().connect();
				} else {
					clearInterval(reconnectInterval);
					reconnectInterval = null;
				}
			}, 5000);
		}
	}
}

export const websocketStore = createWebSocketStore();
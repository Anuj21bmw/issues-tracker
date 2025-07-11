import { writable } from 'svelte/store';
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
				const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;
				const socket = new WebSocket(wsUrl);

				socket.onopen = () => {
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
					message: `New issue created: ${message.data.title}`,
					duration: 4000
				});
				window.dispatchEvent(new CustomEvent('refresh-issues'));
				break;

			case 'issue_status_changed':
				toastStore.add({
					type: 'info',
					message: `Issue "${message.data.title}" status changed to ${message.data.new_status}`,
					duration: 4000
				});
				window.dispatchEvent(new CustomEvent('refresh-issues'));
				break;

			default:
				console.log('Unknown message type:', message.type);
		}
	}

	function attemptReconnect() {
		if (reconnectAttempts >= maxReconnectAttempts) {
			return;
		}

		if (!reconnectInterval) {
			reconnectInterval = setInterval(() => {
				if (reconnectAttempts < maxReconnectAttempts) {
					reconnectAttempts++;
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
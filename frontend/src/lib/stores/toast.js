import { writable } from 'svelte/store';

function createToastStore() {
	const { subscribe, update } = writable([]);

	return {
		subscribe,
		add(toast) {
			const id = Date.now() + Math.random();
			const newToast = {
				id,
				type: toast.type || 'info',
				message: toast.message,
				duration: toast.duration || 5000
			};

			update(toasts => [...toasts, newToast]);

			setTimeout(() => {
				update(toasts => toasts.filter(t => t.id !== id));
			}, newToast.duration);
		},
		remove(id) {
			update(toasts => toasts.filter(t => t.id !== id));
		}
	};
}

export const toastStore = createToastStore();
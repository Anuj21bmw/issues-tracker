// src/lib/stores/toast.js
import { writable } from 'svelte/store';

// Toast store for notifications
const createToastStore = () => {
    const { subscribe, update } = writable([]);

    let nextId = 1;

    const addToast = (message, type = 'info', duration = 5000) => {
        const id = nextId++;
        const toast = {
            id,
            message,
            type,
            duration,
            timestamp: Date.now()
        };

        update(toasts => [...toasts, toast]);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }

        return id;
    };

    const removeToast = (id) => {
        update(toasts => toasts.filter(t => t.id !== id));
    };

    return {
        subscribe,
        success: (message, duration) => addToast(message, 'success', duration),
        error: (message, duration) => addToast(message, 'error', duration),
        warning: (message, duration) => addToast(message, 'warning', duration),
        info: (message, duration) => addToast(message, 'info', duration),
        remove: removeToast,
        clear: () => update(() => [])
    };
};

export const toastStore = createToastStore();
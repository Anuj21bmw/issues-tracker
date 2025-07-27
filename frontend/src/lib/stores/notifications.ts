import { writable } from 'svelte/store';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}

function createNotificationStore() {
  const { subscribe, update } = writable<Notification[]>([]);

  function addNotification(notification: Omit<Notification, 'id'>) {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration ?? 5000
    };

    update(notifications => [...notifications, newNotification]);

    if (newNotification.duration > 0) {
      setTimeout(() => {
        remove(id);
      }, newNotification.duration);
    }

    return id;
  }

  function remove(id: string) {
    update(notifications => notifications.filter(n => n.id !== id));
  }

  return {
    subscribe,
    
    success: (title: string, message?: string, duration?: number) =>
      addNotification({ type: 'success', title, message, duration }),
    
    error: (title: string, message?: string, duration?: number) =>
      addNotification({ type: 'error', title, message, duration: duration ?? 8000 }),
    
    warning: (title: string, message?: string, duration?: number) =>
      addNotification({ type: 'warning', title, message, duration }),
    
    info: (title: string, message?: string, duration?: number) =>
      addNotification({ type: 'info', title, message, duration }),
    
    custom: (notification: Omit<Notification, 'id'>) =>
      addNotification(notification),
    
    remove
  };
}

export const notifications = createNotificationStore();

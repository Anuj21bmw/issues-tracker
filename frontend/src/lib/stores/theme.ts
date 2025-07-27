import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

function createThemeStore() {
  const { subscribe, set } = writable<Theme>('light');

  return {
    subscribe,
    
    init() {
      if (!browser) return;
      
      const saved = localStorage.getItem('theme') as Theme;
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const theme = saved || (prefersDark ? 'dark' : 'light');
      
      this.setTheme(theme);
    },
    
    setTheme(theme: Theme) {
      if (browser) {
        localStorage.setItem('theme', theme);
        document.documentElement.classList.toggle('dark', theme === 'dark');
      }
      set(theme);
    },
    
    toggle() {
      this.setTheme(get(this) === 'light' ? 'dark' : 'light');
    }
  };
}

export const themeStore = createThemeStore();

function get(store: any) {
  let value;
  store.subscribe((v: any) => value = v)();
  return value;
}

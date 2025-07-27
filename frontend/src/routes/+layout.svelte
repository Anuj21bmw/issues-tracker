<script>
    import '../app.css';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { authStore } from '$lib/stores/auth.js';
    import { toastStore } from '$lib/stores/toast.js';
    import { uiStore } from '$lib/stores/ui.js';
    import { wsStore } from '$lib/stores/websocket.js';
    import ToastNotifications from '$lib/components/ToastNotifications.svelte';

    $: isAuthPage = $page.url.pathname.startsWith('/auth');
    $: showChat = $authStore.isAuthenticated && !isAuthPage;

    onMount(() => {
        const savedTheme = localStorage.getItem('ui_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        if ($authStore.isAuthenticated) {
            wsStore.connect();
        }

        return () => {
            wsStore.disconnect();
        };
    });

    $: {
        if ($authStore.isAuthenticated) {
            wsStore.connect();
        } else {
            wsStore.disconnect();
        }
    }
</script>

<svelte:head>
    <title>AI Issues Tracker - Smart Issue Management</title>
    <meta name="description" content="AI-enhanced issue tracking and management platform for modern teams" />
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="alternate icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<main class="min-h-screen">
    <slot />
</main>

<ToastNotifications />

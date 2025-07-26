<script>
    import '../app.css';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { authStore } from '$lib/stores/auth.js';
    import { toastStore } from '$lib/stores/toast.js';
    import { uiStore } from '$lib/stores/ui.js';
    import { wsStore } from '$lib/stores/websocket.js';
    import ToastNotifications from '$lib/components/ToastNotifications.svelte';
    // import AIChatAssistant from '$lib/components/ai/AIChatAssistant.svelte';

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
    <title>AI-Enhanced Issues Tracker</title>
</svelte:head>

<main class="min-h-screen">
    <slot />
</main>

<ToastNotifications />

<!-- Uncomment when AIChatAssistant is ready -->
<!-- {#if showChat}
    <AIChatAssistant />
{/if} -->

<script>
    import { fly } from 'svelte/transition';
    import { toastStore } from '$lib/stores/toast.js';

    function getToastIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || 'ℹ️';
    }

    function getToastClasses(type) {
        const classes = {
            success: 'bg-green-50 border-green-200 text-green-800',
            error: 'bg-red-50 border-red-200 text-red-800',
            warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
            info: 'bg-blue-50 border-blue-200 text-blue-800'
        };
        return classes[type] || classes.info;
    }
</script>

<div class="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
    {#each $toastStore as toast (toast.id)}
        <div
            class="flex items-center p-4 border rounded-lg shadow-lg {getToastClasses(toast.type)}"
            transition:fly="{{ x: 300, duration: 300 }}"
        >
            <span class="text-lg mr-3">{getToastIcon(toast.type)}</span>
            <div class="flex-1">
                <p class="text-sm font-medium">{toast.message}</p>
            </div>
            {#if toast.dismissible}
                <button
                    class="ml-3 text-sm opacity-70 hover:opacity-100 focus:outline-none"
                    on:click={() => toastStore.remove(toast.id)}
                >
                    ✕
                </button>
            {/if}
        </div>
    {/each}
</div>
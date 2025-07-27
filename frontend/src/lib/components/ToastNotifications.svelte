<script>
    import { toastStore } from '$lib/stores/toast.js';
    import { fly } from 'svelte/transition';

    $: toasts = $toastStore;

    const getIcon = (type) => {
        switch (type) {
            case 'success': return '✓';
            case 'error': return '✕';
            case 'warning': return '⚠';
            default: return 'ℹ';
        }
    };

    const getColorClass = (type) => {
        switch (type) {
            case 'success': return 'bg-green-500';
            case 'error': return 'bg-red-500';
            case 'warning': return 'bg-yellow-500';
            default: return 'bg-blue-500';
        }
    };
</script>

<div class="fixed top-4 right-4 z-50 space-y-2">
    {#each toasts as toast (toast.id)}
        <div
            in:fly={{ x: 300, duration: 300 }}
            out:fly={{ x: 300, duration: 300 }}
            class="flex items-center p-4 rounded-lg shadow-lg text-white max-w-sm {getColorClass(toast.type)}"
        >
            <span class="text-lg mr-3">{getIcon(toast.type)}</span>
            <span class="flex-1">{toast.message}</span>
            <button
                on:click={() => toastStore.remove(toast.id)}
                class="ml-2 text-white hover:text-gray-200 text-xl leading-none"
            >
                ×
            </button>
        </div>
    {/each}
</div>

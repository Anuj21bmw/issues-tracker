<!-- Create/Update: frontend/src/routes/+layout.svelte -->
<script>
    import Toast from '$lib/components/Toast.svelte';
    import '../app.css';
</script>

<main>
    <slot />
</main>

<!-- Toast notifications -->
<Toast />

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
</style>
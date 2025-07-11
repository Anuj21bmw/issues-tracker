<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';
	import { websocketStore } from '$lib/stores/websocket';
	import Navbar from '$lib/components/Navbar.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Toast from '$lib/components/Toast.svelte';

	let sidebarOpen = false;

	onMount(() => {
		authStore.checkAuth();
		websocketStore.connect();
	});

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	$: isAuthRoute = $page.url.pathname.startsWith('/auth');
	$: requiresAuth = !isAuthRoute && $page.url.pathname !== '/';
	
	// Only redirect on client side
	$: if (browser && requiresAuth && !$authStore.isAuthenticated) {
		goto('/auth/login');
	}
</script>

<svelte:head>
	<title>Issues & Insights Tracker</title>
</svelte:head>

{#if $authStore.isAuthenticated && !isAuthRoute}
	<div class="min-h-screen bg-gray-50">
		<Navbar {toggleSidebar} />
		
		<div class="flex pt-16">
			<Sidebar bind:open={sidebarOpen} />
			
			<main class="flex-1 p-6 lg:ml-64 transition-all duration-300">
				<div class="max-w-7xl mx-auto">
					<slot />
				</div>
			</main>
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
		<slot />
	</div>
{/if}

<!-- Only render toasts on client side -->
{#if browser && $toastStore}
	{#each $toastStore as toast (toast.id)}
		<Toast {toast} />
	{/each}
{/if}
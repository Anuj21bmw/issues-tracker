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
		if ($authStore.isAuthenticated) {
			websocketStore.connect();
		}
	});

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	$: isAuthRoute = $page.url.pathname.startsWith('/auth');
	$: isHomePage = $page.url.pathname === '/';
	$: requiresAuth = !isAuthRoute && !isHomePage;
	
	// Only redirect on client side
	$: if (browser && requiresAuth && !$authStore.isAuthenticated) {
		goto('/auth/login');
	}
</script>

<svelte:head>
	<title>Issues & Insights Tracker</title>
	<meta name="description" content="Professional issue tracking and insights platform" />
</svelte:head>

{#if $authStore.isAuthenticated && !isAuthRoute && !isHomePage}
	<!-- Authenticated App Layout -->
	<div class="min-h-screen bg-gray-50">
		<Navbar {toggleSidebar} />
		
		<div class="flex">
			<Sidebar bind:open={sidebarOpen} />
			
			<!-- Main Content Area -->
			<main class="flex-1 lg:ml-64">
				<div class="pt-16"> <!-- Add padding for fixed navbar -->
					<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
						<slot />
					</div>
				</div>
			</main>
		</div>
	</div>
{:else}
	<!-- Landing Page / Auth Layout -->
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
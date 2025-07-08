<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import Navbar from '$lib/components/Navbar.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Toast from '$lib/components/Toast.svelte';
	import { toastStore } from '$lib/stores/toast';
	import { websocketStore } from '$lib/stores/websocket';

	let sidebarOpen = false;
	let darkMode = false;

	// Check for saved theme preference or default to light mode
	onMount(() => {
		if (typeof window !== 'undefined') {
			const savedTheme = localStorage.getItem('theme');
			darkMode = savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
			updateTheme();
			
			// Initialize WebSocket connection
			websocketStore.connect();
			
			// Check if user is authenticated
			authStore.checkAuth();
		}
	});

	function updateTheme() {
		if (typeof document !== 'undefined') {
			if (darkMode) {
				document.documentElement.classList.add('dark');
				localStorage.setItem('theme', 'dark');
			} else {
				document.documentElement.classList.remove('dark');
				localStorage.setItem('theme', 'light');
			}
		}
	}

	function toggleTheme() {
		darkMode = !darkMode;
		updateTheme();
	}

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	// Check if current route requires authentication
	$: isAuthRoute = $page.url.pathname.startsWith('/auth');
	$: requiresAuth = !isAuthRoute && $page.url.pathname !== '/';
	
	// Redirect to login if not authenticated and route requires auth
	$: if (requiresAuth && !$authStore.isAuthenticated) {
		goto('/auth/login');
	}
</script>

<svelte:head>
	<title>Issues & Insights Tracker</title>
</svelte:head>

{#if $authStore.isAuthenticated && !isAuthRoute}
	<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
		<Navbar {darkMode} {toggleTheme} {toggleSidebar} />
		
		<div class="flex">
			<Sidebar bind:open={sidebarOpen} />
			
			<main class="flex-1 p-6 lg:ml-64 transition-all duration-300">
				<div class="max-w-7xl mx-auto">
					<slot />
				</div>
			</main>
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-gradient-to-br from-primary-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
		<slot />
	</div>
{/if}

<!-- Toast notifications -->
{#each $toastStore as toast (toast.id)}
	<Toast {toast} />
{/each}
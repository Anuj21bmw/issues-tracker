// frontend/src/routes/+layout.svelte - Updated with AI components
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
	import AIChatAssistant from '$lib/components/ai/AIChatAssistant.svelte';

	let sidebarOpen = false;
	let showAIChat = false;

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
	<title>AI-Enhanced Issues & Insights Tracker</title>
	<meta name="description" content="Next-generation issue tracking with AI-powered insights and automation" />
</svelte:head>

{#if $authStore.isAuthenticated && !isAuthRoute && !isHomePage}
	<!-- Authenticated App Layout with AI -->
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

		<!-- AI Chat Assistant -->
		<AIChatAssistant bind:isOpen={showAIChat} />
		
		<!-- AI Toggle FAB -->
		{#if !showAIChat}
			<button
				on:click={() => showAIChat = true}
				class="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center z-40 hover:scale-110 animate-pulse"
				title="Open AI Assistant"
			>
				<span class="text-2xl">🤖</span>
			</button>
		{/if}

		<!-- AI Status Indicator -->
		<div class="fixed top-20 right-4 z-30">
			<div class="bg-white rounded-lg border border-gray-200 shadow-sm px-3 py-2 flex items-center space-x-2">
				<div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
				<span class="text-xs text-gray-600 font-medium">AI Services Active</span>
			</div>
		</div>
	</div>
{:else}
	<!-- Landing Page / Auth Layout -->
	<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
		<slot />
	</div>
{/if}

<!-- Global Toast Notifications -->
{#if browser && $toastStore}
	{#each $toastStore as toast (toast.id)}
		<Toast {toast} />
	{/each}
{/if}

<!-- Global Styles for AI Features -->
<style>
	:global(.ai-glow) {
		box-shadow: 0 0 20px rgba(147, 51, 234, 0.4);
	}
	
	:global(.ai-gradient) {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}
	
	:global(.ai-pulse) {
		animation: ai-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
	
	@keyframes ai-pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: .7;
		}
	}
	
	:global(.shadow-3xl) {
		box-shadow: 0 35px 60px -12px rgba(0, 0, 0, 0.25);
	}
</style>
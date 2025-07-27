<!-- src/routes/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	
	let mounted = false;

	onMount(() => {
		mounted = true;
		// If user is already authenticated, redirect to appropriate page
		if ($authStore.isAuthenticated) {
			if ($authStore.user?.role === 'ADMIN' || $authStore.user?.role === 'MAINTAINER') {
				goto('/dashboard');
			} else {
				goto('/issues');
			}
		}
	});

	function navigateToLogin() {
		goto('/auth/login');
	}

	function navigateToRegister() {
		goto('/auth/register');
	}
</script>

<svelte:head>
	<title>Issues & Insights Tracker - Professional Issue Management</title>
	<meta name="description" content="Streamline your workflow with our professional issue tracking and insights platform. Perfect for teams of all sizes." />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
	<!-- Navigation Header -->
	<nav class="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center h-16">
				<div class="flex items-center">
					<div class="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
						<span class="text-white font-bold text-sm">IT</span>
					</div>
					<span class="text-xl font-bold text-gray-900">Issues Tracker</span>
				</div>
				<div class="flex items-center space-x-4">
					<button 
						on:click={navigateToLogin}
						class="text-gray-600 hover:text-gray-900 font-medium transition-colors"
					>
						Sign In
					</button>
					<button 
						on:click={navigateToLogin}
						class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
					>
						Get Started
					</button>
				</div>
			</div>
		</div>
	</nav>

	<!-- Hero Section -->
	<div class="relative overflow-hidden">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
			<div class="text-center">
				<h1 class="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
					Streamline Your
					<span class="text-blue-600">Issue Management</span>
				</h1>
				<p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
					Track, manage, and resolve issues efficiently with our powerful platform. 
					Built for teams that value productivity and insights.
				</p>
				<div class="flex flex-col sm:flex-row gap-4 justify-center">
					<button 
						on:click={navigateToLogin}
						class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all transform hover:scale-105"
					>
						Try Demo Accounts
					</button>
					<button 
						on:click={navigateToRegister}
						class="bg-white hover:bg-gray-50 text-gray-900 px-8 py-4 rounded-lg text-lg font-semibold border border-gray-300 transition-all"
					>
						Create Account
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Features Section -->
	<div class="py-20 bg-white">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<h2 class="text-3xl font-bold text-gray-900 mb-4">
					Everything you need to manage issues effectively
				</h2>
				<p class="text-xl text-gray-600">
					Powerful features designed for modern teams
				</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				<!-- Feature 1 -->
				<div class="text-center p-6">
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
						<span class="text-2xl">🤖</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">AI-Powered Insights</h3>
					<p class="text-gray-600">
						Get intelligent suggestions for issue classification, priority, and resolution strategies powered by advanced AI.
					</p>
				</div>

				<!-- Feature 2 -->
				<div class="text-center p-6">
					<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
						<span class="text-2xl">⚡</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Real-time Collaboration</h3>
					<p class="text-gray-600">
						Work together seamlessly with real-time updates, notifications, and collaborative tools for your entire team.
					</p>
				</div>

				<!-- Feature 3 -->
				<div class="text-center p-6">
					<div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
						<span class="text-2xl">📊</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Advanced Analytics</h3>
					<p class="text-gray-600">
						Gain deep insights into your team's performance with comprehensive analytics and customizable dashboards.
					</p>
				</div>

				<!-- Feature 4 -->
				<div class="text-center p-6">
					<div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
						<span class="text-2xl">🔐</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Role-based Access</h3>
					<p class="text-gray-600">
						Secure your workflow with granular permissions and role-based access controls for admins, maintainers, and reporters.
					</p>
				</div>

				<!-- Feature 5 -->
				<div class="text-center p-6">
					<div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
						<span class="text-2xl">📱</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Mobile Friendly</h3>
					<p class="text-gray-600">
						Access your issues anywhere with our responsive design that works perfectly on desktop, tablet, and mobile.
					</p>
				</div>

				<!-- Feature 6 -->
				<div class="text-center p-6">
					<div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-4">
						<span class="text-2xl">🎯</span>
					</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Smart Prioritization</h3>
					<p class="text-gray-600">
						Automatically prioritize issues based on severity, impact, and urgency to focus on what matters most.
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Demo Section -->
	<div class="py-20 bg-gray-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center">
				<h2 class="text-3xl font-bold text-gray-900 mb-4">
					Try it out with demo accounts
				</h2>
				<p class="text-xl text-gray-600 mb-8">
					Experience the full power of our platform with pre-configured demo accounts
				</p>
				
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-8">
					<!-- Admin Demo -->
					<div class="bg-white p-6 rounded-lg shadow-md">
						<div class="text-2xl mb-3">👑</div>
						<h3 class="text-lg font-semibold text-gray-900 mb-2">Admin Account</h3>
						<p class="text-gray-600 text-sm mb-3">Full access to all features, analytics, and user management</p>
						<div class="text-xs text-gray-500">
							admin@example.com
						</div>
					</div>

					<!-- Maintainer Demo -->
					<div class="bg-white p-6 rounded-lg shadow-md">
						<div class="text-2xl mb-3">🔧</div>
						<h3 class="text-lg font-semibold text-gray-900 mb-2">Maintainer Account</h3>
						<p class="text-gray-600 text-sm mb-3">Manage and resolve issues, assign tasks, update statuses</p>
						<div class="text-xs text-gray-500">
							maintainer@example.com
						</div>
					</div>

					<!-- Reporter Demo -->
					<div class="bg-white p-6 rounded-lg shadow-md">
						<div class="text-2xl mb-3">📝</div>
						<h3 class="text-lg font-semibold text-gray-900 mb-2">Reporter Account</h3>
						<p class="text-gray-600 text-sm mb-3">Create new issues, track progress, add comments</p>
						<div class="text-xs text-gray-500">
							reporter@example.com
						</div>
					</div>
				</div>

				<button 
					on:click={navigateToLogin}
					class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all transform hover:scale-105"
				>
					Try Demo Now
				</button>
			</div>
		</div>
	</div>

	<!-- CTA Section -->
	<div class="py-20 bg-blue-600">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
			<h2 class="text-3xl font-bold text-white mb-4">
				Ready to get started?
			</h2>
			<p class="text-xl text-blue-100 mb-8">
				Join thousands of teams who trust our platform for their issue management
			</p>
			<div class="flex flex-col sm:flex-row gap-4 justify-center">
				<button 
					on:click={navigateToRegister}
					class="bg-white hover:bg-gray-100 text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold transition-all"
				>
					Create Free Account
				</button>
				<button 
					on:click={navigateToLogin}
					class="bg-blue-500 hover:bg-blue-400 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all"
				>
					Try Demo
				</button>
			</div>
		</div>
	</div>

	<!-- Footer -->
	<footer class="bg-gray-900 text-white py-12">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center">
				<div class="flex items-center justify-center mb-4">
					<div class="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
						<span class="text-white font-bold text-sm">IT</span>
					</div>
					<span class="text-xl font-bold">Issues Tracker</span>
				</div>
				<p class="text-gray-400 mb-6">
					Professional issue management for modern teams
				</p>
				<div class="flex justify-center space-x-8">
					<button 
						on:click={navigateToLogin}
						class="text-gray-400 hover:text-white transition-colors"
					>
						Sign In
					</button>
					<button 
						on:click={navigateToRegister}
						class="text-gray-400 hover:text-white transition-colors"
					>
						Register
					</button>
				</div>
			</div>
		</div>
	</footer>
</div>
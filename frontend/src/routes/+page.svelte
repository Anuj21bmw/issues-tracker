<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	
	let mounted = false;

	onMount(() => {
		mounted = true;
		// If user is already authenticated, redirect to dashboard
		if ($authStore.isAuthenticated) {
			if ($authStore.user?.role === 'ADMIN' || $authStore.user?.role === 'MAINTAINER') {
				goto('/dashboard');
			} else {
				goto('/issues');
			}
		}
	});
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
					<a href="/auth/login" class="text-gray-600 hover:text-gray-900 font-medium">
						Sign In
					</a>
					<a href="/auth/login" class="btn-primary">
						Get Started
					</a>
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
					<a href="/auth/login" class="btn-primary text-lg px-8 py-3">
						Start Tracking Issues
					</a>
					<a href="#features" class="btn-outline text-lg px-8 py-3">
						Learn More
					</a>
				</div>
			</div>
		</div>
	</div>

	<!-- Features Section -->
	<div id="features" class="py-20 bg-white">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<h2 class="text-4xl font-bold text-gray-900 mb-4">
					Everything You Need
				</h2>
				<p class="text-xl text-gray-600">
					Powerful features designed for modern teams
				</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
				<div class="text-center p-6">
					<div class="text-5xl mb-4">🎫</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Issue Tracking</h3>
					<p class="text-gray-600">
						Create, assign, and track issues with detailed information and file attachments.
					</p>
				</div>

				<div class="text-center p-6">
					<div class="text-5xl mb-4">📊</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Analytics & Insights</h3>
					<p class="text-gray-600">
						Get detailed analytics and insights to improve your team's productivity.
					</p>
				</div>

				<div class="text-center p-6">
					<div class="text-5xl mb-4">👥</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Team Collaboration</h3>
					<p class="text-gray-600">
						Role-based access control and real-time updates keep everyone in sync.
					</p>
				</div>

				<div class="text-center p-6">
					<div class="text-5xl mb-4">⚡</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Real-time Updates</h3>
					<p class="text-gray-600">
						Get instant notifications when issues are updated or status changes.
					</p>
				</div>

				<div class="text-center p-6">
					<div class="text-5xl mb-4">🔒</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Secure & Reliable</h3>
					<p class="text-gray-600">
						Enterprise-grade security with role-based permissions and data protection.
					</p>
				</div>

				<div class="text-center p-6">
					<div class="text-5xl mb-4">📱</div>
					<h3 class="text-xl font-semibold text-gray-900 mb-2">Mobile Friendly</h3>
					<p class="text-gray-600">
						Access your issues from anywhere with our responsive design.
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- CTA Section -->
	<div class="py-20 bg-blue-600">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
			<h2 class="text-4xl font-bold text-white mb-4">
				Ready to Get Started?
			</h2>
			<p class="text-xl text-blue-100 mb-8">
				Join teams already using Issues Tracker to streamline their workflow.
			</p>
			<a href="/auth/login" class="bg-white text-blue-600 hover:bg-gray-100 font-semibold px-8 py-3 rounded-lg transition-colors inline-block">
				Start Your Free Trial
			</a>
		</div>
	</div>

	<!-- Footer -->
	<footer class="bg-gray-900 text-white py-12">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex flex-col md:flex-row justify-between items-center">
				<div class="flex items-center mb-4 md:mb-0">
					<div class="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
						<span class="text-white font-bold text-sm">IT</span>
					</div>
					<span class="text-xl font-bold">Issues Tracker</span>
				</div>
				<div class="text-gray-400">
					© 2024 Issues Tracker. Built for productivity.
				</div>
			</div>
		</div>
	</footer>
</div>
<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';

	let dashboardData = null;
	let loading = true;
	let error = null;

	onMount(async () => {
		await loadDashboardData();
	});

	async function loadDashboardData() {
		try {
			loading = true;
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch('http://localhost:8000/api/dashboard/stats', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (!response.ok) {
				throw new Error('Failed to load dashboard data');
			}

			dashboardData = await response.json();
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	}

	function getSeverityClass(severity) {
		const classes = {
			LOW: 'severity-low',
			MEDIUM: 'severity-medium',
			HIGH: 'severity-high',
			CRITICAL: 'severity-critical'
		};
		return classes[severity] || 'badge';
	}
</script>

<svelte:head>
	<title>Dashboard - Issues & Insights Tracker</title>
</svelte:head>

<div class="space-y-8">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
			<p class="mt-2 text-gray-600">
				Welcome back, {$authStore.user?.full_name}! Here's an overview of your issues.
			</p>
		</div>
		<div class="flex items-center space-x-3">
			<button 
				on:click={loadDashboardData}
				class="btn-outline"
				disabled={loading}
			>
				🔄 Refresh
			</button>
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			<span class="ml-3 text-gray-600">Loading dashboard...</span>
		</div>
	{:else if error}
		<div class="card">
			<div class="text-center">
				<div class="text-red-500 text-6xl mb-4">⚠️</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Dashboard</h3>
				<p class="text-gray-600 mb-4">{error}</p>
				<button on:click={loadDashboardData} class="btn-primary">
					Try Again
				</button>
			</div>
		</div>
	{:else if dashboardData}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<div class="card">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="text-3xl">🎫</div>
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 truncate">
								Total Issues
							</dt>
							<dd class="text-lg font-medium text-gray-900">
								{dashboardData.total_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="text-3xl">⏰</div>
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 truncate">
								Open Issues
							</dt>
							<dd class="text-lg font-medium text-gray-900">
								{dashboardData.open_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="text-3xl">🚀</div>
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 truncate">
								In Progress
							</dt>
							<dd class="text-lg font-medium text-gray-900">
								{dashboardData.in_progress_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="text-3xl">✅</div>
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 truncate">
								Completed
							</dt>
							<dd class="text-lg font-medium text-gray-900">
								{dashboardData.done_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>
		</div>

		<div class="card">
			<h3 class="text-lg font-medium text-gray-900 mb-4">
				Quick Actions
			</h3>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<a href="/issues/create" class="btn-primary text-center block">
					<div class="text-2xl mb-2">➕</div>
					Create New Issue
				</a>
				<a href="/issues" class="btn-outline text-center block">
					<div class="text-2xl mb-2">📋</div>
					View All Issues
				</a>
				{#if $authStore.user?.role === 'ADMIN'}
					<a href="/users" class="btn-outline text-center block">
						<div class="text-2xl mb-2">👥</div>
						Manage Users
					</a>
				{/if}
			</div>
		</div>
	{/if}
</div>

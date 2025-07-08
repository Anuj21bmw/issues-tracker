<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'svelte-chartjs';
	import { 
		AlertTriangle, 
		CheckCircle, 
		Clock, 
		Users, 
		TrendingUp,
		Activity
	} from 'lucide-svelte';

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

	$: chartData = dashboardData ? {
		labels: ['Low', 'Medium', 'High', 'Critical'],
		datasets: [{
			label: 'Issues by Severity',
			data: [
				dashboardData.issues_by_severity.LOW || 0,
				dashboardData.issues_by_severity.MEDIUM || 0,
				dashboardData.issues_by_severity.HIGH || 0,
				dashboardData.issues_by_severity.CRITICAL || 0
			],
			backgroundColor: [
				'rgba(34, 197, 94, 0.8)',   // Green for Low
				'rgba(251, 191, 36, 0.8)',  // Yellow for Medium
				'rgba(249, 115, 22, 0.8)',  // Orange for High
				'rgba(239, 68, 68, 0.8)'    // Red for Critical
			],
			borderColor: [
				'rgba(34, 197, 94, 1)',
				'rgba(251, 191, 36, 1)',
				'rgba(249, 115, 22, 1)',
				'rgba(239, 68, 68, 1)'
			],
			borderWidth: 1
		}]
	} : null;

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}

	function formatTime(dateString) {
		return new Date(dateString).toLocaleTimeString();
	}

	function getSeverityColor(severity) {
		switch (severity) {
			case 'LOW': return 'text-green-600 bg-green-100 dark:bg-green-900/20 dark:text-green-400';
			case 'MEDIUM': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400';
			case 'HIGH': return 'text-orange-600 bg-orange-100 dark:bg-orange-900/20 dark:text-orange-400';
			case 'CRITICAL': return 'text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400';
			default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20 dark:text-gray-400';
		}
	}

	function getStatusColor(status) {
		switch (status) {
			case 'OPEN': return 'text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400';
			case 'TRIAGED': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400';
			case 'IN_PROGRESS': return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400';
			case 'DONE': return 'text-green-600 bg-green-100 dark:bg-green-900/20 dark:text-green-400';
			default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20 dark:text-gray-400';
		}
	}
</script>

<svelte:head>
	<title>Dashboard - Issues & Insights Tracker</title>
</svelte:head>

<div class="space-y-8">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
			<p class="mt-2 text-gray-600 dark:text-gray-400">
				Welcome back, {$authStore.user?.full_name}! Here's an overview of your issues.
			</p>
		</div>
		<div class="flex items-center space-x-3">
			<button 
				on:click={loadDashboardData}
				class="btn-outline"
				disabled={loading}
			>
				<Activity class="h-4 w-4 mr-2" />
				Refresh
			</button>
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
			<span class="ml-3 text-gray-600 dark:text-gray-400">Loading dashboard...</span>
		</div>
	{:else if error}
		<div class="card p-6">
			<div class="text-center">
				<AlertTriangle class="h-12 w-12 text-red-500 mx-auto mb-4" />
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Error Loading Dashboard</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
				<button on:click={loadDashboardData} class="btn-primary">
					Try Again
				</button>
			</div>
		</div>
	{:else if dashboardData}
		<!-- Stats Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<div class="card p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<AlertTriangle class="h-8 w-8 text-primary-600" />
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
								Total Issues
							</dt>
							<dd class="text-lg font-medium text-gray-900 dark:text-white">
								{dashboardData.total_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<Clock class="h-8 w-8 text-red-600" />
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
								Open Issues
							</dt>
							<dd class="text-lg font-medium text-gray-900 dark:text-white">
								{dashboardData.open_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<TrendingUp class="h-8 w-8 text-blue-600" />
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
								In Progress
							</dt>
							<dd class="text-lg font-medium text-gray-900 dark:text-white">
								{dashboardData.in_progress_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<CheckCircle class="h-8 w-8 text-green-600" />
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
								Completed
							</dt>
							<dd class="text-lg font-medium text-gray-900 dark:text-white">
								{dashboardData.done_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>
		</div>

		<!-- Charts and Activity -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
			<!-- Issues by Severity Chart -->
			<div class="card p-6">
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
					Issues by Severity
				</h3>
				{#if chartData}
					<div class="h-64">
						<Bar data={chartData} options={{
							responsive: true,
							maintainAspectRatio: false,
							plugins: {
								legend: {
									display: false
								}
							},
							scales: {
								y: {
									beginAtZero: true,
									ticks: {
										stepSize: 1
									}
								}
							}
						}} />
					</div>
				{/if}
			</div>

			<!-- Recent Activity -->
			<div class="card p-6">
				<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
					Recent Activity
				</h3>
				<div class="space-y-4 max-h-64 overflow-y-auto">
					{#each dashboardData.recent_activity as issue}
						<div class="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
							<div class="flex-shrink-0">
								<AlertTriangle class="h-5 w-5 text-gray-400" />
							</div>
							<div class="flex-1 min-w-0">
								<p class="text-sm font-medium text-gray-900 dark:text-white truncate">
									{issue.title}
								</p>
								<div class="flex items-center space-x-2 mt-1">
									<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {getSeverityColor(issue.severity)}">
										{issue.severity}
									</span>
									<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {getStatusColor(issue.status)}">
										{issue.status}
									</span>
								</div>
							</div>
							<div class="text-xs text-gray-500 dark:text-gray-400">
								{formatTime(issue.updated_at || issue.created_at)}
							</div>
						</div>
					{:else}
						<div class="text-center py-8">
							<Users class="h-12 w-12 text-gray-400 mx-auto mb-4" />
							<p class="text-gray-500 dark:text-gray-400">No recent activity</p>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="card p-6">
			<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
				Quick Actions
			</h3>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<a href="/issues/create" class="btn-primary text-center">
					<AlertTriangle class="h-5 w-5 mx-auto mb-2" />
					Create New Issue
				</a>
				<a href="/issues" class="btn-outline text-center">
					<Clock class="h-5 w-5 mx-auto mb-2" />
					View All Issues
				</a>
				{#if $authStore.user?.role === 'ADMIN'}
					<a href="/users" class="btn-outline text-center">
						<Users class="h-5 w-5 mx-auto mb-2" />
						Manage Users
					</a>
				{/if}
			</div>
		</div>
	{/if}
</div>
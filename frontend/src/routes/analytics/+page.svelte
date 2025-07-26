<!-- // frontend/src/routes/analytics/+page.svelte - Fixed API URLs -->
<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';

	let dashboardData = null;
	let dailyStats = [];
	let loading = true;
	let error = null;
	let chartCanvas;
	let chart = null;

	onMount(async () => {
		if ($authStore.user?.role === 'REPORTER') {
			toastStore.add({
				type: 'error',
				message: 'Access denied. Maintainer or Admin role required.'
			});
			return;
		}
		
		await loadAnalyticsData();
		
		// Load Chart.js dynamically
		try {
			const Chart = (await import('chart.js')).default;
			const { registerables } = await import('chart.js');
			Chart.register(...registerables);
			
			if (dailyStats.length > 0) {
				createChart(Chart);
			}
		} catch (err) {
			console.error('Error loading Chart.js:', err);
		}
	});

	async function loadAnalyticsData() {
		try {
			loading = true;
			const headers = authStore.getAuthHeaders();
			
			// Load dashboard stats
			const statsResponse = await fetch('/api/dashboard/stats', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (!statsResponse.ok) {
				if (statsResponse.status === 401) {
					authStore.logout();
					return;
				}
				throw new Error('Failed to load analytics data');
			}

			dashboardData = await statsResponse.json();

			// Load daily stats for charts
			const dailyResponse = await fetch('/api/dashboard/daily-stats?days=30', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (dailyResponse.ok) {
				dailyStats = await dailyResponse.json();
				dailyStats.reverse(); // Show oldest to newest
			}

		} catch (err) {
			error = err.message;
			console.error('Error loading analytics:', err);
		} finally {
			loading = false;
		}
	}

	function createChart(Chart) {
		if (!chartCanvas || dailyStats.length === 0) return;

		const ctx = chartCanvas.getContext('2d');
		
		if (chart) {
			chart.destroy();
		}

		chart = new Chart(ctx, {
			type: 'line',
			data: {
				labels: dailyStats.map(stat => new Date(stat.date).toLocaleDateString()),
				datasets: [
					{
						label: 'Open Issues',
						data: dailyStats.map(stat => stat.open_count),
						borderColor: 'rgb(239, 68, 68)',
						backgroundColor: 'rgba(239, 68, 68, 0.1)',
						tension: 0.4
					},
					{
						label: 'In Progress',
						data: dailyStats.map(stat => stat.in_progress_count),
						borderColor: 'rgb(59, 130, 246)',
						backgroundColor: 'rgba(59, 130, 246, 0.1)',
						tension: 0.4
					},
					{
						label: 'Done',
						data: dailyStats.map(stat => stat.done_count),
						borderColor: 'rgb(34, 197, 94)',
						backgroundColor: 'rgba(34, 197, 94, 0.1)',
						tension: 0.4
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Issues Trend (Last 30 Days)'
					},
					legend: {
						position: 'top'
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
			}
		});
	}

	function getSeverityColor(severity) {
		const colors = {
			LOW: '#6b7280',
			MEDIUM: '#f59e0b',
			HIGH: '#f97316',
			CRITICAL: '#ef4444'
		};
		return colors[severity] || '#6b7280';
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}

	function calculateTrends() {
		if (!dashboardData) return null;
		
		const total = dashboardData.total_issues;
		const done = dashboardData.done_issues;
		const inProgress = dashboardData.in_progress_issues;
		const open = dashboardData.open_issues;
		
		return {
			completionRate: total > 0 ? Math.round((done / total) * 100) : 0,
			activeRate: total > 0 ? Math.round(((inProgress + done) / total) * 100) : 0,
			pendingRate: total > 0 ? Math.round((open / total) * 100) : 0
		};
	}

	$: trends = calculateTrends();
</script>

<svelte:head>
	<title>Analytics - Issues & Insights Tracker</title>
</svelte:head>

<div class="space-y-8">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Analytics</h1>
			<p class="mt-2 text-gray-600">
				Insights and trends for issue management
			</p>
		</div>
		<div class="flex items-center space-x-3">
			<button 
				on:click={loadAnalyticsData}
				class="btn-outline"
				disabled={loading}
			>
				🔄 Refresh Data
			</button>
		</div>
	</div>

	{#if $authStore.user?.role === 'REPORTER'}
		<div class="card">
			<div class="text-center">
				<div class="text-yellow-500 text-6xl mb-4">🚫</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Access Restricted</h3>
				<p class="text-gray-600">Analytics are available for Maintainers and Admins only.</p>
			</div>
		</div>
	{:else if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			<span class="ml-3 text-gray-600">Loading analytics...</span>
		</div>
	{:else if error}
		<div class="card">
			<div class="text-center">
				<div class="text-red-500 text-6xl mb-4">⚠️</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Analytics</h3>
				<p class="text-gray-600 mb-4">{error}</p>
				<button on:click={loadAnalyticsData} class="btn-primary">
					Try Again
				</button>
			</div>
		</div>
	{:else if dashboardData}
		<!-- KPI Cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<div class="card">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="text-3xl">📊</div>
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 truncate">
								Completion Rate
							</dt>
							<dd class="text-lg font-medium text-gray-900">
								{trends?.completionRate || 0}%
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="text-3xl">⚡</div>
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 truncate">
								Active Issues
							</dt>
							<dd class="text-lg font-medium text-gray-900">
								{dashboardData.in_progress_issues + dashboardData.triaged_issues}
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="text-3xl">🎯</div>
					</div>
					<div class="ml-5 w-0 flex-1">
						<dl>
							<dt class="text-sm font-medium text-gray-500 truncate">
								Resolution Rate
							</dt>
							<dd class="text-lg font-medium text-gray-900">
								{trends?.activeRate || 0}%
							</dd>
						</dl>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="text-3xl">📈</div>
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
		</div>

		<!-- Charts and Detailed Analytics -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
			<!-- Trend Chart -->
			<div class="card">
				<h3 class="text-lg font-medium text-gray-900 mb-4">
					Issues Trend
				</h3>
				<div class="h-80">
					<canvas bind:this={chartCanvas}></canvas>
				</div>
			</div>

			<!-- Issues by Severity -->
			<div class="card">
				<h3 class="text-lg font-medium text-gray-900 mb-4">
					Issues by Severity
				</h3>
				<div class="space-y-4">
					{#each Object.entries(dashboardData.issues_by_severity) as [severity, count]}
						<div class="flex items-center justify-between">
							<div class="flex items-center">
								<div 
									class="w-4 h-4 rounded mr-3" 
									style="background-color: {getSeverityColor(severity)}"
								></div>
								<span class="text-sm font-medium text-gray-900">{severity}</span>
							</div>
							<div class="flex items-center">
								<span class="text-lg font-semibold text-gray-900 mr-2">{count}</span>
								<div class="w-20 bg-gray-200 rounded-full h-2">
									<div 
										class="h-2 rounded-full" 
										style="width: {dashboardData.total_issues > 0 ? (count / dashboardData.total_issues) * 100 : 0}%; background-color: {getSeverityColor(severity)}"
									></div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Status Distribution -->
		<div class="card">
			<h3 class="text-lg font-medium text-gray-900 mb-6">
				Status Distribution
			</h3>
			<div class="grid grid-cols-1 md:grid-cols-4 gap-6">
				<div class="text-center">
					<div class="text-2xl font-bold text-red-600 mb-2">
						{dashboardData.open_issues}
					</div>
					<div class="text-sm text-gray-500">Open Issues</div>
					<div class="w-full bg-gray-200 rounded-full h-2 mt-2">
						<div 
							class="bg-red-600 h-2 rounded-full" 
							style="width: {dashboardData.total_issues > 0 ? (dashboardData.open_issues / dashboardData.total_issues) * 100 : 0}%"
						></div>
					</div>
				</div>
				
				<div class="text-center">
					<div class="text-2xl font-bold text-yellow-600 mb-2">
						{dashboardData.triaged_issues}
					</div>
					<div class="text-sm text-gray-500">Triaged</div>
					<div class="w-full bg-gray-200 rounded-full h-2 mt-2">
						<div 
							class="bg-yellow-600 h-2 rounded-full" 
							style="width: {dashboardData.total_issues > 0 ? (dashboardData.triaged_issues / dashboardData.total_issues) * 100 : 0}%"
						></div>
					</div>
				</div>
				
				<div class="text-center">
					<div class="text-2xl font-bold text-blue-600 mb-2">
						{dashboardData.in_progress_issues}
					</div>
					<div class="text-sm text-gray-500">In Progress</div>
					<div class="w-full bg-gray-200 rounded-full h-2 mt-2">
						<div 
							class="bg-blue-600 h-2 rounded-full" 
							style="width: {dashboardData.total_issues > 0 ? (dashboardData.in_progress_issues / dashboardData.total_issues) * 100 : 0}%"
						></div>
					</div>
				</div>
				
				<div class="text-center">
					<div class="text-2xl font-bold text-green-600 mb-2">
						{dashboardData.done_issues}
					</div>
					<div class="text-sm text-gray-500">Completed</div>
					<div class="w-full bg-gray-200 rounded-full h-2 mt-2">
						<div 
							class="bg-green-600 h-2 rounded-full" 
							style="width: {dashboardData.total_issues > 0 ? (dashboardData.done_issues / dashboardData.total_issues) * 100 : 0}%"
						></div>
					</div>
				</div>
			</div>
		</div>

		<!-- Recent Activity Summary -->
		<div class="card">
			<h3 class="text-lg font-medium text-gray-900 mb-4">
				Recent Activity Summary
			</h3>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
				<div class="text-center p-4 bg-blue-50 rounded-lg">
					<div class="text-lg font-semibold text-blue-900">
						{dashboardData.recent_activity.length}
					</div>
					<div class="text-sm text-blue-700">Recent Updates</div>
				</div>
				
				<div class="text-center p-4 bg-green-50 rounded-lg">
					<div class="text-lg font-semibold text-green-900">
						{dashboardData.recent_activity.filter(issue => issue.status === 'DONE').length}
					</div>
					<div class="text-sm text-green-700">Recently Completed</div>
				</div>
				
				<div class="text-center p-4 bg-yellow-50 rounded-lg">
					<div class="text-lg font-semibold text-yellow-900">
						{dashboardData.recent_activity.filter(issue => issue.severity === 'CRITICAL' || issue.severity === 'HIGH').length}
					</div>
					<div class="text-sm text-yellow-700">High Priority</div>
				</div>
			</div>
		</div>
	{/if}
</div>
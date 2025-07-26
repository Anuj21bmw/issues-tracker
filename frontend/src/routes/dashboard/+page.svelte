<!-- // frontend/src/routes/dashboard/+page.svelte  -->


<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';

	let dashboardData = null;
	let aiInsights = [];
	let loading = true;
	let error = null;
	let showAIPanel = false;
	let analyticsData = null;
	let dailyStats = [];

	// Real-time updates
	let wsConnection = null;

	onMount(async () => {
		await loadDashboardData();
		await loadAIInsights();
		await loadAnalytics();
		await loadDailyStats();
		connectWebSocket();
		
		// Auto-refresh every 30 seconds
		const interval = setInterval(() => {
			if (!loading) {
				loadDashboardData();
				loadAIInsights();
			}
		}, 30000);
		
		return () => {
			clearInterval(interval);
			if (wsConnection) {
				wsConnection.close();
			}
		};
	});

	async function loadDashboardData() {
		try {
			loading = true;
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch('/api/dashboard/stats', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: Failed to load dashboard data`);
			}

			const result = await response.json();
			dashboardData = result.stats;
		} catch (err) {
			error = err.message;
			toastStore.add({
				type: 'error',
				message: `Dashboard loading failed: ${err.message}`
			});
		} finally {
			loading = false;
		}
	}

	async function loadAIInsights() {
		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch('/api/ai/insights/dashboard', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (response.ok) {
				const data = await response.json();
				aiInsights = data.insights || [];
			}
		} catch (err) {
			console.log('AI insights not available:', err);
		}
	}

	async function loadAnalytics() {
		if ($authStore.user?.role !== 'ADMIN' && $authStore.user?.role !== 'MAINTAINER') {
			return;
		}

		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch('/api/dashboard/analytics', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (response.ok) {
				const result = await response.json();
				analyticsData = result.analytics;
			}
		} catch (err) {
			console.log('Analytics not available:', err);
		}
	}

	async function loadDailyStats() {
		if ($authStore.user?.role !== 'ADMIN' && $authStore.user?.role !== 'MAINTAINER') {
			return;
		}

		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch('/api/dashboard/daily-stats?days=14', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (response.ok) {
				const result = await response.json();
				dailyStats = result.daily_stats || [];
			}
		} catch (err) {
			console.log('Daily stats not available:', err);
		}
	}

	function connectWebSocket() {
		try {
			const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
			const wsUrl = `${protocol}//${window.location.host}/ws`;
			wsConnection = new WebSocket(wsUrl);
			
			wsConnection.onmessage = (event) => {
				const data = JSON.parse(event.data);
				if (data.type === 'issue_created' || data.type === 'issue_updated') {
					// Refresh dashboard data on issue changes
					loadDashboardData();
					loadAIInsights();
				}
			};
			
			wsConnection.onerror = (error) => {
				console.log('WebSocket error:', error);
			};
		} catch (err) {
			console.log('WebSocket connection failed:', err);
		}
	}

	function getSeverityClass(severity) {
		const classes = {
			LOW: 'bg-green-100 text-green-800',
			MEDIUM: 'bg-yellow-100 text-yellow-800',
			HIGH: 'bg-orange-100 text-orange-800',
			CRITICAL: 'bg-red-100 text-red-800'
		};
		return classes[severity] || 'bg-gray-100 text-gray-800';
	}

	function getStatusClass(status) {
		const classes = {
			OPEN: 'bg-blue-100 text-blue-800',
			TRIAGED: 'bg-purple-100 text-purple-800',
			IN_PROGRESS: 'bg-orange-100 text-orange-800',
			DONE: 'bg-green-100 text-green-800'
		};
		return classes[status] || 'bg-gray-100 text-gray-800';
	}

	function getInsightIcon(type) {
		const icons = {
			warning: '⚠️',
			success: '✅',
			info: 'ℹ️',
			prediction: '🔮',
			error: '❌'
		};
		return icons[type] || 'ℹ️';
	}

	function getInsightClass(type) {
		const classes = {
			warning: 'border-orange-200 bg-orange-50',
			success: 'border-green-200 bg-green-50',
			info: 'border-blue-200 bg-blue-50',
			prediction: 'border-purple-200 bg-purple-50',
			error: 'border-red-200 bg-red-50'
		};
		return classes[type] || 'border-gray-200 bg-gray-50';
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}

	function formatTime(dateString) {
		return new Date(dateString).toLocaleTimeString();
	}

	async function refreshAllData() {
		await Promise.all([
			loadDashboardData(),
			loadAIInsights(),
			loadAnalytics(),
			loadDailyStats()
		]);
		toastStore.add({
			type: 'success',
			message: 'Dashboard refreshed successfully'
		});
	}
</script>

<svelte:head>
	<title>AI-Enhanced Dashboard - Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="flex items-center justify-between mb-8">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">AI-Enhanced Dashboard</h1>
				<p class="mt-2 text-gray-600">
					Welcome back, {$authStore.user?.full_name}! Here's your intelligent overview.
				</p>
			</div>
			<div class="flex items-center space-x-3">
				<button 
					on:click={() => showAIPanel = !showAIPanel}
					class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all duration-200 shadow-lg"
				>
					🤖 {showAIPanel ? 'Hide' : 'Show'} AI Insights
				</button>
				<button 
					on:click={refreshAllData}
					class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
				>
					🔄 Refresh
				</button>
			</div>
		</div>

		{#if loading}
			<div class="flex items-center justify-center h-64">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
				<span class="ml-3 text-gray-600">Loading dashboard data...</span>
			</div>
		{:else if error}
			<div class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
				<div class="flex">
					<div class="flex-shrink-0">
						<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
						</svg>
					</div>
					<div class="ml-3">
						<h3 class="text-sm font-medium text-red-800">Error loading dashboard</h3>
						<p class="mt-1 text-sm text-red-700">{error}</p>
					</div>
				</div>
			</div>
		{:else if dashboardData}
			<!-- AI Insights Panel -->
			{#if showAIPanel && aiInsights.length > 0}
				<div class="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6 mb-8">
					<h2 class="text-xl font-semibold text-gray-900 mb-4">🤖 AI Insights & Recommendations</h2>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						{#each aiInsights as insight}
							<div class="border rounded-lg p-4 {getInsightClass(insight.type)}">
								<div class="flex items-start">
									<span class="text-lg mr-2">{getInsightIcon(insight.type)}</span>
									<div class="flex-1">
										<p class="text-sm font-medium text-gray-900">{insight.message}</p>
										<p class="text-xs text-gray-600 mt-1">{insight.recommendation}</p>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
				<div class="bg-white overflow-hidden shadow rounded-lg">
					<div class="p-5">
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
									<span class="text-white text-sm font-medium">📊</span>
								</div>
							</div>
							<div class="ml-5 w-0 flex-1">
								<dl>
									<dt class="text-sm font-medium text-gray-500 truncate">Total Issues</dt>
									<dd class="text-2xl font-semibold text-gray-900">{dashboardData.total_issues}</dd>
								</dl>
							</div>
						</div>
					</div>
				</div>

				<div class="bg-white overflow-hidden shadow rounded-lg">
					<div class="p-5">
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div class="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
									<span class="text-white text-sm font-medium">🔓</span>
								</div>
							</div>
							<div class="ml-5 w-0 flex-1">
								<dl>
									<dt class="text-sm font-medium text-gray-500 truncate">Open Issues</dt>
									<dd class="text-2xl font-semibold text-gray-900">{dashboardData.open_issues}</dd>
								</dl>
							</div>
						</div>
					</div>
				</div>

				<div class="bg-white overflow-hidden shadow rounded-lg">
					<div class="p-5">
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
									<span class="text-white text-sm font-medium">⚡</span>
								</div>
							</div>
							<div class="ml-5 w-0 flex-1">
								<dl>
									<dt class="text-sm font-medium text-gray-500 truncate">In Progress</dt>
									<dd class="text-2xl font-semibold text-gray-900">{dashboardData.in_progress_issues}</dd>
								</dl>
							</div>
						</div>
					</div>
				</div>

				<div class="bg-white overflow-hidden shadow rounded-lg">
					<div class="p-5">
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
									<span class="text-white text-sm font-medium">✅</span>
								</div>
							</div>
							<div class="ml-5 w-0 flex-1">
								<dl>
									<dt class="text-sm font-medium text-gray-500 truncate">Completed</dt>
									<dd class="text-2xl font-semibold text-gray-900">{dashboardData.done_issues}</dd>
								</dl>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Performance Metrics -->
			{#if dashboardData.performance}
				<div class="bg-white shadow rounded-lg p-6 mb-8">
					<h2 class="text-lg font-medium text-gray-900 mb-4">📈 Performance Metrics</h2>
					<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
						<div class="text-center">
							<dt class="text-sm font-medium text-gray-500">This Week</dt>
							<dd class="text-2xl font-semibold text-indigo-600">{dashboardData.performance.issues_this_week}</dd>
							<dd class="text-xs text-gray-500">New Issues</dd>
						</div>
						<div class="text-center">
							<dt class="text-sm font-medium text-gray-500">Resolved</dt>
							<dd class="text-2xl font-semibold text-green-600">{dashboardData.performance.resolved_this_week}</dd>
							<dd class="text-xs text-gray-500">This Week</dd>
						</div>
						<div class="text-center">
							<dt class="text-sm font-medium text-gray-500">Resolution Rate</dt>
							<dd class="text-2xl font-semibold text-blue-600">{dashboardData.performance.resolution_rate.toFixed(1)}%</dd>
							<dd class="text-xs text-gray-500">Success Rate</dd>
						</div>
						<div class="text-center">
							<dt class="text-sm font-medium text-gray-500">Avg Response</dt>
							<dd class="text-2xl font-semibold text-purple-600">{dashboardData.performance.avg_response_time}</dd>
							<dd class="text-xs text-gray-500">Response Time</dd>
						</div>
					</div>
				</div>
			{/if}

			<!-- Charts Section -->
			{#if dailyStats.length > 0}
				<div class="bg-white shadow rounded-lg p-6 mb-8">
					<h2 class="text-lg font-medium text-gray-900 mb-4">📊 Daily Trends</h2>
					<div class="h-64 flex items-end justify-between space-x-1">
						{#each dailyStats as stat}
							<div class="flex flex-col items-center flex-1">
								<div class="w-full max-w-8 bg-gray-200 rounded-t" style="height: {Math.max(10, stat.created * 8)}px">
									<div class="w-full bg-blue-500 rounded-t" style="height: {Math.max(5, stat.created * 8)}px" title="Created: {stat.created}"></div>
								</div>
								<div class="w-full max-w-8 bg-gray-200" style="height: {Math.max(10, stat.resolved * 8)}px">
									<div class="w-full bg-green-500" style="height: {Math.max(5, stat.resolved * 8)}px" title="Resolved: {stat.resolved}"></div>
								</div>
								<span class="text-xs text-gray-500 mt-1 transform rotate-45 origin-left">{new Date(stat.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
							</div>
						{/each}
					</div>
					<div class="flex justify-center mt-4 space-x-4 text-sm">
						<div class="flex items-center">
							<div class="w-3 h-3 bg-blue-500 rounded mr-1"></div>
							<span>Created</span>
						</div>
						<div class="flex items-center">
							<div class="w-3 h-3 bg-green-500 rounded mr-1"></div>
							<span>Resolved</span>
						</div>
					</div>
				</div>
			{/if}

			<!-- Two Column Layout -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
				<!-- Issues by Severity -->
				<div class="bg-white shadow rounded-lg">
					<div class="px-6 py-4 border-b border-gray-200">
						<h2 class="text-lg font-medium text-gray-900">🚨 Issues by Severity</h2>
					</div>
					<div class="p-6">
						<div class="space-y-4">
							{#each Object.entries(dashboardData.issues_by_severity) as [severity, count]}
								<div class="flex items-center justify-between">
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getSeverityClass(severity)}">
										{severity}
									</span>
									<span class="text-sm font-medium text-gray-900">{count} issues</span>
								</div>
							{/each}
						</div>
					</div>
				</div>

				<!-- Recent Activity -->
				<div class="bg-white shadow rounded-lg">
					<div class="px-6 py-4 border-b border-gray-200">
						<h2 class="text-lg font-medium text-gray-900">🕒 Recent Activity</h2>
					</div>
					<div class="divide-y divide-gray-200">
						{#each dashboardData.recent_activity.slice(0, 8) as issue}
							<div class="px-6 py-4">
								<div class="flex items-center justify-between">
									<div class="flex-1 min-w-0">
										<p class="text-sm font-medium text-gray-900 truncate">
											<a href="/issues/{issue.id}" class="hover:text-indigo-600">
												#{issue.id} {issue.title}
											</a>
										</p>
										<p class="text-sm text-gray-500">
											by {issue.reporter} • {formatDate(issue.created_at)}
										</p>
									</div>
									<div class="flex items-center space-x-2 ml-4">
										<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {getSeverityClass(issue.severity)}">
											{issue.severity}
										</span>
										<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {getStatusClass(issue.status)}">
											{issue.status}
										</span>
									</div>
								</div>
							</div>
						{/each}
					</div>
					<div class="px-6 py-3 bg-gray-50 text-center">
						<a href="/issues" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
							View all issues →
						</a>
					</div>
				</div>
			</div>

			<!-- Team Analytics (Admin/Maintainer only) -->
			{#if analyticsData && ($authStore.user?.role === 'ADMIN' || $authStore.user?.role === 'MAINTAINER')}
				<div class="mt-8 bg-white shadow rounded-lg">
					<div class="px-6 py-4 border-b border-gray-200">
						<h2 class="text-lg font-medium text-gray-900">👥 Team Performance</h2>
					</div>
					<div class="p-6">
						{#if analyticsData.team_performance && analyticsData.team_performance.length > 0}
							<div class="overflow-x-auto">
								<table class="min-w-full divide-y divide-gray-200">
									<thead class="bg-gray-50">
										<tr>
											<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team Member</th>
											<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned</th>
											<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resolved</th>
											<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
										</tr>
									</thead>
									<tbody class="bg-white divide-y divide-gray-200">
										{#each analyticsData.team_performance as member}
											<tr>
												<td class="px-6 py-4 whitespace-nowrap">
													<div>
														<div class="text-sm font-medium text-gray-900">{member.name}</div>
														<div class="text-sm text-gray-500">{member.email}</div>
													</div>
												</td>
												<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{member.total_assigned}</td>
												<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{member.resolved}</td>
												<td class="px-6 py-4 whitespace-nowrap">
													<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {member.resolution_rate >= 80 ? 'bg-green-100 text-green-800' : member.resolution_rate >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}">
														{member.resolution_rate.toFixed(1)}%
													</span>
												</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						{:else}
							<p class="text-gray-500 text-center py-4">No team performance data available</p>
						{/if}
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>

<style>
	.ai-glow {
		box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
	}
	
	.ai-glow:hover {
		box-shadow: 0 0 25px rgba(139, 92, 246, 0.5);
	}
</style>
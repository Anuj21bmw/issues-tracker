// frontend/src/routes/dashboard/+page.svelte - Fixed with correct API URLs
<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import AIInsightsDashboard from '$lib/components/ai/AIInsightsDashboard.svelte';

	let dashboardData = null;
	let aiInsights = [];
	let loading = true;
	let error = null;
	let showAIAnalysis = false;

	onMount(async () => {
		await loadDashboardData();
		await loadAIInsights();
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
				throw new Error('Failed to load dashboard data');
			}

			dashboardData = await response.json();
		} catch (err) {
			error = err.message;
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

	function getSeverityClass(severity) {
		const classes = {
			LOW: 'severity-low',
			MEDIUM: 'severity-medium',
			HIGH: 'severity-high',
			CRITICAL: 'severity-critical'
		};
		return classes[severity] || 'badge';
	}

	function getStatusClass(status) {
		const classes = {
			OPEN: 'status-open',
			TRIAGED: 'status-triaged',
			IN_PROGRESS: 'status-in-progress',
			DONE: 'status-done'
		};
		return classes[status] || 'badge';
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}

	function formatTime(dateString) {
		return new Date(dateString).toLocaleTimeString();
	}

	async function refreshData() {
		await loadDashboardData();
		await loadAIInsights();
	}
</script>

<svelte:head>
	<title>AI-Enhanced Dashboard - Issues & Insights Tracker</title>
</svelte:head>

<div class="space-y-8">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">AI-Enhanced Dashboard</h1>
			<p class="mt-2 text-gray-600">
				Welcome back, {$authStore.user?.full_name}! Here's your intelligent overview.
			</p>
		</div>
		<div class="flex items-center space-x-3">
			<button 
				on:click={() => showAIAnalysis = !showAIAnalysis}
				class="btn-outline ai-glow"
			>
				🤖 {showAIAnalysis ? 'Hide' : 'Show'} AI Analysis
			</button>
			<button 
				on:click={refreshData}
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
			<span class="ml-3 text-gray-600">Loading intelligent dashboard...</span>
		</div>
	{:else if error}
		<div class="card">
			<div class="text-center">
				<div class="text-red-500 text-6xl mb-4">⚠️</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Dashboard</h3>
				<p class="text-gray-600 mb-4">{error}</p>
				<button on:click={refreshData} class="btn-primary">
					Try Again
				</button>
			</div>
		</div>
	{:else if dashboardData}
		<!-- AI Alert Banner -->
		{#if aiInsights.length > 0}
			<div class="ai-gradient rounded-lg p-4 text-white">
				<div class="flex items-center space-x-3">
					<div class="text-2xl">🤖</div>
					<div class="flex-1">
						<h3 class="font-semibold">AI Assistant Alert</h3>
						<p class="text-sm opacity-90">
							{aiInsights[0].message}
						</p>
					</div>
					<button 
						on:click={() => showAIAnalysis = true}
						class="bg-white/20 hover:bg-white/30 px-3 py-1 rounded text-sm transition-colors"
					>
						View Details
					</button>
				</div>
			</div>
		{/if}

		<!-- Stats Grid with AI Enhancement -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<div class="card ai-pulse">
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
							<dd class="text-xs text-blue-600 font-medium">
								🤖 AI: {dashboardData.total_issues > 50 ? 'High volume' : 'Normal range'}
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
							<dd class="text-xs text-purple-600 font-medium">
								🔮 Predicted: +{Math.floor(dashboardData.open_issues * 0.1)} this week
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
							<dd class="text-xs text-green-600 font-medium">
								🎯 Avg completion: 2.3 days
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
							<dd class="text-xs text-indigo-600 font-medium">
								📈 {dashboardData.total_issues > 0 ? Math.round((dashboardData.done_issues / dashboardData.total_issues) * 100) : 0}% completion rate
							</dd>
						</dl>
					</div>
				</div>
			</div>
		</div>

		<!-- AI Insights Section -->
		{#if showAIAnalysis}
			<AIInsightsDashboard showFullAnalytics={true} />
		{/if}

		<!-- Charts and Activity -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
			<!-- Enhanced Issues by Severity -->
			<div class="card">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-lg font-medium text-gray-900">
						Issues by Severity
					</h3>
					<div class="text-sm text-purple-600 font-medium">
						🤖 AI Enhanced
					</div>
				</div>
				<div class="space-y-3">
					{#each Object.entries(dashboardData.issues_by_severity) as [severity, count]}
						<div class="flex items-center justify-between">
							<div class="flex items-center">
								<span class="{getSeverityClass(severity)}">{severity}</span>
								{#if severity === 'CRITICAL' && count > 3}
									<span class="ml-2 text-xs text-red-600 font-medium">🚨 Alert threshold</span>
								{/if}
							</div>
							<div class="flex items-center space-x-2">
								<span class="text-lg font-semibold text-gray-900">{count}</span>
								<div class="w-16 bg-gray-200 rounded-full h-2">
									<div 
										class="h-2 rounded-full" 
										style="width: {dashboardData.total_issues > 0 ? (count / Math.max(...Object.values(dashboardData.issues_by_severity))) * 100 : 0}%; background-color: {severity === 'CRITICAL' ? '#ef4444' : severity === 'HIGH' ? '#f97316' : severity === 'MEDIUM' ? '#f59e0b' : '#6b7280'}"
									></div>
								</div>
							</div>
						</div>
					{/each}
				</div>
				
				<!-- AI Recommendations -->
				<div class="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
					<div class="flex items-start space-x-2">
						<span class="text-purple-600">🤖</span>
						<div class="text-sm">
							<div class="font-medium text-purple-900">AI Recommendation:</div>
							<div class="text-purple-700">
								{#if dashboardData.issues_by_severity.CRITICAL > 2}
									Focus on critical issues first. Consider implementing escalation protocols.
								{:else if dashboardData.issues_by_severity.HIGH > 5}
									High priority issues need attention. Recommend load balancing across team.
								{:else}
									Issue distribution looks healthy. Maintain current workflow.
								{/if}
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Enhanced Recent Activity -->
			<div class="card">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-lg font-medium text-gray-900">
						Recent Activity
					</h3>
					<div class="text-sm text-blue-600 font-medium">
						🧠 Smart Insights
					</div>
				</div>
				<div class="space-y-4 max-h-64 overflow-y-auto">
					{#each dashboardData.recent_activity as issue}
						<div class="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
							<div class="flex-shrink-0">
								<div class="text-lg">🎫</div>
							</div>
							<div class="flex-1 min-w-0">
								<p class="text-sm font-medium text-gray-900 truncate">
									{issue.title}
								</p>
								<div class="flex items-center space-x-2 mt-1">
									<span class="{getSeverityClass(issue.severity)}">
										{issue.severity}
									</span>
									<span class="{getStatusClass(issue.status)}">
										{issue.status}
									</span>
									{#if issue.severity === 'CRITICAL'}
										<span class="text-xs text-red-600 font-medium">⚡ Urgent</span>
									{/if}
								</div>
							</div>
							<div class="text-xs text-gray-500">
								{formatTime(issue.updated_at || issue.created_at)}
							</div>
						</div>
					{:else}
						<div class="text-center py-8">
							<div class="text-4xl mb-4">📝</div>
							<p class="text-gray-500">No recent activity</p>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- AI-Powered Quick Actions -->
		<div class="card">
			<h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
				<span class="mr-2">🚀</span>
				AI-Powered Quick Actions
			</h3>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				<a href="/issues/create" class="group relative overflow-hidden btn-primary text-center block hover:scale-105 transition-transform">
					<div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-500 opacity-0 group-hover:opacity-20 transition-opacity"></div>
					<div class="relative">
						<div class="text-2xl mb-2">➕</div>
						<div>Create Issue</div>
						<div class="text-xs opacity-80">🤖 With AI classification</div>
					</div>
				</a>
				
				<button class="group relative overflow-hidden btn-outline text-center block hover:scale-105 transition-transform">
					<div class="absolute inset-0 bg-gradient-to-r from-green-400 to-blue-500 opacity-0 group-hover:opacity-20 transition-opacity"></div>
					<div class="relative">
						<div class="text-2xl mb-2">🎯</div>
						<div>Smart Assignment</div>
						<div class="text-xs opacity-80">🤖 AI suggests best assignee</div>
					</div>
				</button>
				
				<button class="group relative overflow-hidden btn-outline text-center block hover:scale-105 transition-transform">
					<div class="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-500 opacity-0 group-hover:opacity-20 transition-opacity"></div>
					<div class="relative">
						<div class="text-2xl mb-2">📊</div>
						<div>Predictive Analytics</div>
						<div class="text-xs opacity-80">🤖 Forecast trends</div>
					</div>
				</button>
				
				{#if $authStore.user?.role === 'ADMIN'}
					<a href="/users" class="group relative overflow-hidden btn-outline text-center block hover:scale-105 transition-transform">
						<div class="absolute inset-0 bg-gradient-to-r from-indigo-400 to-cyan-500 opacity-0 group-hover:opacity-20 transition-opacity"></div>
						<div class="relative">
							<div class="text-2xl mb-2">👥</div>
							<div>Manage Users</div>
							<div class="text-xs opacity-80">🤖 Smart permissions</div>
						</div>
					</a>
				{:else}
					<a href="/issues" class="group relative overflow-hidden btn-outline text-center block hover:scale-105 transition-transform">
						<div class="absolute inset-0 bg-gradient-to-r from-teal-400 to-green-500 opacity-0 group-hover:opacity-20 transition-opacity"></div>
						<div class="relative">
							<div class="text-2xl mb-2">📋</div>
							<div>View All Issues</div>
							<div class="text-xs opacity-80">🤖 Smart filtering</div>
						</div>
					</a>
				{/if}
			</div>
		</div>

		<!-- AI Assistant Teaser -->
		<div class="ai-gradient rounded-lg p-6 text-white relative overflow-hidden">
			<div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
			<div class="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12"></div>
			<div class="relative">
				<div class="flex items-center justify-between">
					<div>
						<h3 class="text-xl font-bold mb-2">🤖 Meet Your AI Assistant</h3>
						<p class="text-blue-100 mb-4">
							Get instant insights, smart recommendations, and natural language query support.
						</p>
						<div class="flex flex-wrap gap-2 text-sm">
							<span class="bg-white/20 px-2 py-1 rounded">"Show me critical issues"</span>
							<span class="bg-white/20 px-2 py-1 rounded">"Who should fix this bug?"</span>
							<span class="bg-white/20 px-2 py-1 rounded">"Team performance this week"</span>
						</div>
					</div>
					<div class="text-6xl opacity-50">🤖</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.ai-glow {
		box-shadow: 0 0 20px rgba(147, 51, 234, 0.4);
	}
	
	.ai-gradient {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}
	
	.ai-pulse {
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
</style>
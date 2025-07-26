<!-- // frontend/src/routes/issues/+page.svelte - Fixed API URLs -->
<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';

	let issues = [];
	let loading = true;
	let error = null;
	let search = '';
	let statusFilter = '';
	let severityFilter = '';
	let pagination = {
		page: 1,
		per_page: 10,
		total: 0,
		total_pages: 0
	};

	onMount(async () => {
		await loadIssues();
		// Listen for real-time updates
		window.addEventListener('refresh-issues', loadIssues);
		return () => {
			window.removeEventListener('refresh-issues', loadIssues);
		};
	});

	async function loadIssues() {
		try {
			loading = true;
			const headers = authStore.getAuthHeaders();
			
			const params = new URLSearchParams();
			if (search) params.append('search', search);
			if (statusFilter) params.append('status', statusFilter);
			if (severityFilter) params.append('severity', severityFilter);
			params.append('skip', ((pagination.page - 1) * pagination.per_page).toString());
			params.append('limit', pagination.per_page.toString());
			
			const response = await fetch(`/api/issues/?${params.toString()}`, {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (!response.ok) {
				if (response.status === 401) {
					authStore.logout();
					return;
				}
				throw new Error('Failed to load issues');
			}

			const data = await response.json();
			issues = data.items || [];
			pagination = {
				page: data.page || 1,
				per_page: data.per_page || 10,
				total: data.total || 0,
				total_pages: data.total_pages || 0
			};
		} catch (err) {
			error = err.message;
			console.error('Error loading issues:', err);
		} finally {
			loading = false;
		}
	}

	async function updateIssueStatus(issueId, newStatus) {
		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch(`/api/issues/${issueId}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					...headers
				},
				body: JSON.stringify({ status: newStatus })
			});

			if (!response.ok) {
				throw new Error('Failed to update issue');
			}

			toastStore.add({
				type: 'success',
				message: 'Issue status updated successfully'
			});

			await loadIssues();
		} catch (err) {
			toastStore.add({
				type: 'error',
				message: err.message
			});
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

	function changePage(newPage) {
		pagination.page = newPage;
		loadIssues();
	}

	// Reactive filters
	$: {
		if (search !== undefined || statusFilter !== undefined || severityFilter !== undefined) {
			pagination.page = 1; // Reset to first page when filtering
			loadIssues();
		}
	}
</script>

<svelte:head>
	<title>Issues - Issues & Insights Tracker</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Issues</h1>
			<p class="mt-2 text-gray-600">Manage and track all issues</p>
		</div>
		<div class="flex items-center space-x-3">
			<a href="/issues/create" class="btn-primary">
				➕ Create Issue
			</a>
		</div>
	</div>

	<!-- Filters -->
	<div class="card">
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
			<div>
				<label class="label">Search</label>
				<input
					type="text"
					bind:value={search}
					placeholder="Search issues..."
					class="input"
				/>
			</div>
			<div>
				<label class="label">Status</label>
				<select bind:value={statusFilter} class="input">
					<option value="">All Statuses</option>
					<option value="OPEN">Open</option>
					<option value="TRIAGED">Triaged</option>
					<option value="IN_PROGRESS">In Progress</option>
					<option value="DONE">Done</option>
				</select>
			</div>
			<div>
				<label class="label">Severity</label>
				<select bind:value={severityFilter} class="input">
					<option value="">All Severities</option>
					<option value="LOW">Low</option>
					<option value="MEDIUM">Medium</option>
					<option value="HIGH">High</option>
					<option value="CRITICAL">Critical</option>
				</select>
			</div>
			<div class="flex items-end">
				<button on:click={loadIssues} class="btn-outline w-full">
					🔄 Refresh
				</button>
			</div>
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			<span class="ml-3 text-gray-600">Loading issues...</span>
		</div>
	{:else if error}
		<div class="card">
			<div class="text-center">
				<div class="text-red-500 text-6xl mb-4">⚠️</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Issues</h3>
				<p class="text-gray-600 mb-4">{error}</p>
				<button on:click={loadIssues} class="btn-primary">Try Again</button>
			</div>
		</div>
	{:else}
		<!-- Issues Grid -->
		<div class="grid grid-cols-1 gap-6">
			{#each issues as issue}
				<div class="card-hover">
					<div class="flex items-start justify-between">
						<div class="flex-1">
							<div class="flex items-center space-x-3 mb-2">
								<h3 class="text-lg font-medium text-gray-900">
									<a href="/issues/{issue.id}" class="hover:text-blue-600 transition-colors">
										{issue.title}
									</a>
								</h3>
								<span class="{getSeverityClass(issue.severity)}">{issue.severity}</span>
								<span class="{getStatusClass(issue.status)}">{issue.status}</span>
							</div>
							
							<p class="text-gray-600 mb-3 line-clamp-2">
								{issue.description}
							</p>
							
							<div class="flex items-center space-x-4 text-sm text-gray-500">
								<span>👤 {issue.reporter.full_name}</span>
								<span>📅 {formatDate(issue.created_at)}</span>
								{#if issue.assignee}
									<span>👨‍💼 Assigned: {issue.assignee.full_name}</span>
								{/if}
								{#if issue.file_name}
									<span>📎 {issue.file_name}</span>
								{/if}
							</div>
						</div>
						
						{#if $authStore.user?.role !== 'REPORTER' || issue.reporter_id === $authStore.user?.id}
							<div class="ml-4 flex items-center space-x-2">
								{#if $authStore.user?.role !== 'REPORTER'}
									<select 
										value={issue.status} 
										on:change={(e) => updateIssueStatus(issue.id, e.target.value)}
										class="text-sm border border-gray-300 rounded px-2 py-1"
									>
										<option value="OPEN">Open</option>
										<option value="TRIAGED">Triaged</option>
										<option value="IN_PROGRESS">In Progress</option>
										<option value="DONE">Done</option>
									</select>
								{/if}
								<a href="/issues/{issue.id}" class="btn-outline btn-sm">
									View
								</a>
							</div>
						{/if}
					</div>
				</div>
			{:else}
				<div class="card">
					<div class="text-center py-12">
						<div class="text-6xl mb-4">📝</div>
						<h3 class="text-lg font-medium text-gray-900 mb-2">No Issues Found</h3>
						<p class="text-gray-600 mb-4">
							{search || statusFilter || severityFilter 
								? 'No issues match your current filters.' 
								: 'Get started by creating your first issue.'}
						</p>
						<a href="/issues/create" class="btn-primary">
							Create Your First Issue
						</a>
					</div>
				</div>
			{/each}
		</div>

		<!-- Pagination -->
		{#if pagination.total_pages > 1}
			<div class="flex items-center justify-between">
				<div class="text-sm text-gray-700">
					Showing {((pagination.page - 1) * pagination.per_page) + 1} to {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total} results
				</div>
				<div class="flex items-center space-x-2">
					<button 
						on:click={() => changePage(pagination.page - 1)}
						disabled={pagination.page <= 1}
						class="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
					>
						Previous
					</button>
					
					{#each Array.from({length: Math.min(5, pagination.total_pages)}, (_, i) => i + Math.max(1, pagination.page - 2)) as pageNum}
						{#if pageNum <= pagination.total_pages}
							<button 
								on:click={() => changePage(pageNum)}
								class="px-3 py-2 text-sm border rounded {pageNum === pagination.page ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}"
							>
								{pageNum}
							</button>
						{/if}
					{/each}
					
					<button 
						on:click={() => changePage(pagination.page + 1)}
						disabled={pagination.page >= pagination.total_pages}
						class="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
					>
						Next
					</button>
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
	
	.btn-sm {
		@apply px-2 py-1 text-xs;
	}
</style>
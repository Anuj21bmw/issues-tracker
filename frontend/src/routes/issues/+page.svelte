<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';

	let issues = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		await loadIssues();
	});

	async function loadIssues() {
		try {
			loading = true;
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch('http://localhost:8000/api/issues/', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (!response.ok) {
				throw new Error('Failed to load issues');
			}

			const data = await response.json();
			issues = data.items || [];
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
		<div class="grid grid-cols-1 gap-6">
			{#each issues as issue}
				<div class="card-hover">
					<div class="flex items-start justify-between">
						<div class="flex-1">
							<div class="flex items-center space-x-3 mb-2">
								<h3 class="text-lg font-medium text-gray-900">
									{issue.title}
								</h3>
								<span class="{getSeverityClass(issue.severity)}">{issue.severity}</span>
								<span class="{getStatusClass(issue.status)}">{issue.status}</span>
							</div>
							
							<p class="text-gray-600 mb-3">
								{issue.description}
							</p>
							
							<div class="flex items-center space-x-4 text-sm text-gray-500">
								<span>👤 {issue.reporter.full_name}</span>
								<span>📅 {formatDate(issue.created_at)}</span>
								{#if issue.file_name}
									<span>📎 {issue.file_name}</span>
								{/if}
							</div>
						</div>
					</div>
				</div>
			{:else}
				<div class="card">
					<div class="text-center py-12">
						<div class="text-6xl mb-4">📝</div>
						<h3 class="text-lg font-medium text-gray-900 mb-2">No Issues Found</h3>
						<p class="text-gray-600 mb-4">Get started by creating your first issue.</p>
						<a href="/issues/create" class="btn-primary">
							Create Your First Issue
						</a>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

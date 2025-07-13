<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';

	let issue = null;
	let loading = true;
	let error = null;
	let editing = false;
	let editForm = {
		title: '',
		description: '',
		severity: 'LOW',
		status: 'OPEN',
		tags: '',
		assignee_id: null
	};

	$: issueId = $page.params.id;

	onMount(async () => {
		await loadIssue();
	});

	async function loadIssue() {
		try {
			loading = true;
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch(`http://localhost:8000/api/issues/${issueId}`, {
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
				if (response.status === 404) {
					error = 'Issue not found';
					return;
				}
				throw new Error('Failed to load issue');
			}

			issue = await response.json();
			
			// Populate edit form
			editForm = {
				title: issue.title,
				description: issue.description,
				severity: issue.severity,
				status: issue.status,
				tags: issue.tags || '',
				assignee_id: issue.assignee_id
			};
		} catch (err) {
			error = err.message;
			console.error('Error loading issue:', err);
		} finally {
			loading = false;
		}
	}

	async function updateIssue() {
		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch(`http://localhost:8000/api/issues/${issueId}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					...headers
				},
				body: JSON.stringify(editForm)
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Failed to update issue');
			}

			issue = await response.json();
			editing = false;
			
			toastStore.add({
				type: 'success',
				message: 'Issue updated successfully!'
			});
		} catch (err) {
			toastStore.add({
				type: 'error',
				message: err.message
			});
		}
	}

	async function deleteIssue() {
		if (!confirm('Are you sure you want to delete this issue?')) {
			return;
		}

		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch(`http://localhost:8000/api/issues/${issueId}`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Failed to delete issue');
			}

			toastStore.add({
				type: 'success',
				message: 'Issue deleted successfully!'
			});

			goto('/issues');
		} catch (err) {
			toastStore.add({
				type: 'error',
				message: err.message
			});
		}
	}

	function canEdit() {
		if (!$authStore.user || !issue) return false;
		
		// Admins and maintainers can edit any issue
		if ($authStore.user.role === 'ADMIN' || $authStore.user.role === 'MAINTAINER') {
			return true;
		}
		
		// Reporters can only edit their own issues
		return $authStore.user.role === 'REPORTER' && issue.reporter_id === $authStore.user.id;
	}

	function canDelete() {
		if (!$authStore.user) return false;
		return $authStore.user.role === 'ADMIN' || $authStore.user.role === 'MAINTAINER';
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
		return new Date(dateString).toLocaleString();
	}

	function cancelEdit() {
		editing = false;
		// Reset form to original values
		editForm = {
			title: issue.title,
			description: issue.description,
			severity: issue.severity,
			status: issue.status,
			tags: issue.tags || '',
			assignee_id: issue.assignee_id
		};
	}
</script>

<svelte:head>
	<title>{issue?.title || 'Issue'} - Issues & Insights Tracker</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<a href="/issues" class="text-blue-600 hover:text-blue-800 flex items-center mb-2">
				← Back to Issues
			</a>
			<h1 class="text-3xl font-bold text-gray-900">Issue Details</h1>
		</div>
		<div class="flex items-center space-x-3">
			{#if issue && canEdit()}
				{#if editing}
					<button on:click={cancelEdit} class="btn-outline">
						Cancel
					</button>
					<button on:click={updateIssue} class="btn-primary">
						Save Changes
					</button>
				{:else}
					<button on:click={() => editing = true} class="btn-outline">
						✏️ Edit
					</button>
				{/if}
			{/if}
			{#if issue && canDelete()}
				<button on:click={deleteIssue} class="btn-danger">
					🗑️ Delete
				</button>
			{/if}
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			<span class="ml-3 text-gray-600">Loading issue...</span>
		</div>
	{:else if error}
		<div class="card">
			<div class="text-center">
				<div class="text-red-500 text-6xl mb-4">⚠️</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Issue</h3>
				<p class="text-gray-600 mb-4">{error}</p>
				<button on:click={loadIssue} class="btn-primary">Try Again</button>
			</div>
		</div>
	{:else if issue}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
			<!-- Main Content -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Issue Header -->
				<div class="card">
					{#if editing}
						<div class="space-y-4">
							<div>
								<label class="label">Title</label>
								<input
									type="text"
									bind:value={editForm.title}
									class="input"
									required
								/>
							</div>
							<div>
								<label class="label">Description</label>
								<textarea
									bind:value={editForm.description}
									rows="6"
									class="input"
									required
								></textarea>
							</div>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div>
									<label class="label">Severity</label>
									<select bind:value={editForm.severity} class="input">
										<option value="LOW">Low</option>
										<option value="MEDIUM">Medium</option>
										<option value="HIGH">High</option>
										<option value="CRITICAL">Critical</option>
									</select>
								</div>
								<div>
									<label class="label">Status</label>
									<select bind:value={editForm.status} class="input">
										<option value="OPEN">Open</option>
										<option value="TRIAGED">Triaged</option>
										<option value="IN_PROGRESS">In Progress</option>
										<option value="DONE">Done</option>
									</select>
								</div>
							</div>
							<div>
								<label class="label">Tags</label>
								<input
									type="text"
									bind:value={editForm.tags}
									class="input"
									placeholder="Comma-separated tags"
								/>
							</div>
						</div>
					{:else}
						<div>
							<div class="flex items-center space-x-3 mb-4">
								<h2 class="text-2xl font-bold text-gray-900">{issue.title}</h2>
								<span class="{getSeverityClass(issue.severity)}">{issue.severity}</span>
								<span class="{getStatusClass(issue.status)}">{issue.status}</span>
							</div>
							
							<div class="prose max-w-none">
								<p class="text-gray-700 whitespace-pre-wrap">{issue.description}</p>
							</div>
							
							{#if issue.tags}
								<div class="mt-4">
									<div class="flex flex-wrap gap-2">
										{#each issue.tags.split(',') as tag}
											<span class="badge badge-info">{tag.trim()}</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					{/if}
				</div>

				<!-- File Attachment -->
				{#if issue.file_name}
					<div class="card">
						<h3 class="text-lg font-medium text-gray-900 mb-3">Attachment</h3>
						<div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
							<div class="text-blue-500">📎</div>
							<div class="flex-1">
								<div class="font-medium text-gray-900">{issue.file_name}</div>
								<div class="text-sm text-gray-500">Attached file</div>
							</div>
							{#if issue.file_path}
								<a 
									href="http://localhost:8000/{issue.file_path}"
									target="_blank"
									class="btn-outline btn-sm"
								>
									Download
								</a>
							{/if}
						</div>
					</div>
				{/if}
			</div>

			<!-- Sidebar -->
			<div class="space-y-6">
				<!-- Issue Info -->
				<div class="card">
					<h3 class="text-lg font-medium text-gray-900 mb-4">Issue Information</h3>
					<dl class="space-y-3">
						<div>
							<dt class="text-sm font-medium text-gray-500">ID</dt>
							<dd class="text-sm text-gray-900">#{issue.id}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-gray-500">Reporter</dt>
							<dd class="text-sm text-gray-900">{issue.reporter.full_name}</dd>
						</div>
						{#if issue.assignee}
							<div>
								<dt class="text-sm font-medium text-gray-500">Assignee</dt>
								<dd class="text-sm text-gray-900">{issue.assignee.full_name}</dd>
							</div>
						{/if}
						<div>
							<dt class="text-sm font-medium text-gray-500">Created</dt>
							<dd class="text-sm text-gray-900">{formatDate(issue.created_at)}</dd>
						</div>
						{#if issue.updated_at}
							<div>
								<dt class="text-sm font-medium text-gray-500">Last Updated</dt>
								<dd class="text-sm text-gray-900">{formatDate(issue.updated_at)}</dd>
							</div>
						{/if}
					</dl>
				</div>

				<!-- Quick Actions -->
				<div class="card">
					<h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
					<div class="space-y-2">
						{#if canEdit()}
							<button 
								on:click={() => editing = !editing}
								class="w-full btn-outline text-left"
							>
								{editing ? '❌ Cancel Edit' : '✏️ Edit Issue'}
							</button>
						{/if}
						
						{#if canDelete()}
							<button 
								on:click={deleteIssue}
								class="w-full btn-danger text-left"
							>
								🗑️ Delete Issue
							</button>
						{/if}
						
						<a href="/issues/create" class="w-full btn-outline text-left block">
							➕ Create New Issue
						</a>
						
						<a href="/issues" class="w-full btn-primary text-left block">
							📋 Back to Issues
						</a>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.btn-sm {
		@apply px-2 py-1 text-xs;
	}
</style>
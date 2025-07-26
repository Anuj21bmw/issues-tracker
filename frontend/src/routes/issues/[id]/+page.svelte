<!-- src/routes/issues/[id]/+page.svelte - Fixed CSS Syntax -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.js';
	import { toastStore } from '$lib/stores/toast.js';
	import { issuesStore } from '$lib/stores/issues.js';
	import { aiStore } from '$lib/stores/ai.js';
	import { API_CONFIG, getApiUrl } from '$lib/config.js';
	import Navigation from '$lib/components/Navigation.svelte';

	let issue = null;
	let loading = true;
	let error = null;
	let editing = false;
	let aiAnalyzing = false;
	let aiInsights = null;
	let resolutionSuggestions = null;
	let timeEstimate = null;
	let escalationRisk = null;
	let similarIssues = [];
	let showAIPanel = false;
	let showResolutionSteps = false;

	let editForm = {
		title: '',
		description: '',
		severity: 'LOW',
		status: 'OPEN',
		tags: '',
		assignee_id: null
	};

	let availableUsers = [];

	$: issueId = $page.params.id;
	$: user = $authStore.user;
	$: canEdit = user && (user.role === 'ADMIN' || user.role === 'MAINTAINER' || (user.role === 'REPORTER' && issue?.reporter_id === user.id));

	onMount(async () => {
		await loadIssue();
		await loadAvailableUsers();
		if (issue) {
			await loadAIAnalysis();
		}
	});

	async function loadIssue() {
		try {
			loading = true;
			error = null;
			
			const response = await fetch(getApiUrl(`/api/issues/${issueId}`), {
				headers: {
					'Content-Type': 'application/json',
					...authStore.getAuthHeaders()
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
				title: issue.title || '',
				description: issue.description || '',
				severity: issue.severity || 'LOW',
				status: issue.status || 'OPEN',
				tags: issue.tags || '',
				assignee_id: issue.assignee_id || null
			};

		} catch (err) {
			error = err.message;
			console.error('Error loading issue:', err);
			toastStore.error('Failed to load issue: ' + err.message);
		} finally {
			loading = false;
		}
	}

	async function loadAvailableUsers() {
		if (!user || (user.role !== 'ADMIN' && user.role !== 'MAINTAINER')) {
			return;
		}

		try {
			const response = await fetch(getApiUrl('/api/auth/users'), {
				headers: {
					'Content-Type': 'application/json',
					...authStore.getAuthHeaders()
				}
			});

			if (response.ok) {
				const users = await response.json();
				availableUsers = users.filter(u => 
					u.role === 'MAINTAINER' || u.role === 'ADMIN'
				);
			}
		} catch (err) {
			console.error('Error loading users:', err);
		}
	}

	async function loadAIAnalysis() {
		if (!issue || !user) return;

		try {
			aiAnalyzing = true;

			// Get AI analysis
			const analysisData = {
				title: issue.title,
				description: issue.description,
				severity: issue.severity,
				tags: issue.tags,
				status: issue.status,
				age_hours: Math.floor((new Date() - new Date(issue.created_at)) / (1000 * 60 * 60))
			};

			const analysis = await aiStore.analyzeIssue(analysisData);
			
			if (analysis) {
				aiInsights = analysis.classification;
				timeEstimate = analysis.time_prediction;
				escalationRisk = analysis.escalation_risk;
				resolutionSuggestions = analysis.resolution_suggestions;
			}

		} catch (error) {
			console.log('AI analysis not available:', error);
		} finally {
			aiAnalyzing = false;
		}
	}

	async function saveIssue() {
		if (!canEdit) {
			toastStore.error('You do not have permission to edit this issue');
			return;
		}

		try {
			const updateData = {
				title: editForm.title.trim(),
				description: editForm.description.trim(),
				severity: editForm.severity,
				status: editForm.status,
				tags: editForm.tags.trim() || null,
				assignee_id: editForm.assignee_id || null
			};

			// Validate required fields
			if (!updateData.title) {
				toastStore.error('Title is required');
				return;
			}

			if (!updateData.description) {
				toastStore.error('Description is required');
				return;
			}

			const updatedIssue = await issuesStore.updateIssue(issueId, updateData);
			
			issue = updatedIssue;
			editing = false;
			
			toastStore.success('Issue updated successfully');

			// Reload AI analysis with updated data
			await loadAIAnalysis();

		} catch (error) {
			toastStore.error('Failed to update issue: ' + error.message);
		}
	}

	async function deleteIssue() {
		if (!canEdit) {
			toastStore.error('You do not have permission to delete this issue');
			return;
		}

		if (!confirm('Are you sure you want to delete this issue? This action cannot be undone.')) {
			return;
		}

		try {
			const response = await fetch(getApiUrl(`/api/issues/${issueId}`), {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json',
					...authStore.getAuthHeaders()
				}
			});

			if (!response.ok) {
				throw new Error('Failed to delete issue');
			}

			toastStore.success('Issue deleted successfully');
			goto('/issues');

		} catch (error) {
			toastStore.error('Failed to delete issue: ' + error.message);
		}
	}

	function cancelEdit() {
		editing = false;
		// Reset form to original values
		editForm = {
			title: issue.title || '',
			description: issue.description || '',
			severity: issue.severity || 'LOW',
			status: issue.status || 'OPEN',
			tags: issue.tags || '',
			assignee_id: issue.assignee_id || null
		};
	}

	function getSeverityClass(severity) {
		const classes = {
			LOW: 'severity-low',
			MEDIUM: 'severity-medium',
			HIGH: 'severity-high',
			CRITICAL: 'severity-critical'
		};
		return classes[severity] || 'severity-low';
	}

	function getStatusClass(status) {
		const classes = {
			OPEN: 'status-open',
			TRIAGED: 'status-triaged',
			IN_PROGRESS: 'status-in-progress',
			DONE: 'status-done'
		};
		return classes[status] || 'status-open';
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function getAssigneeName(assigneeId) {
		const assignee = availableUsers.find(u => u.id === assigneeId);
		return assignee ? assignee.full_name : 'Unassigned';
	}

	async function getSmartAssignment() {
		if (!issue) return;

		try {
			const suggestion = await fetch(getApiUrl('/api/ai/suggest-assignment'), {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					...authStore.getAuthHeaders()
				},
				body: JSON.stringify({
					title: issue.title,
					description: issue.description,
					severity: issue.severity,
					tags: issue.tags
				})
			});

			if (suggestion.ok) {
				const data = await suggestion.json();
				const assignee = availableUsers.find(u => u.email === data.suggestion.suggested_assignee);
				if (assignee) {
					editForm.assignee_id = assignee.id;
					toastStore.success(`AI suggests assigning to ${assignee.full_name} (${(data.suggestion.confidence * 100).toFixed(0)}% confidence)`);
				}
			}
		} catch (error) {
			toastStore.error('Smart assignment unavailable');
		}
	}
</script>

<svelte:head>
	<title>Issue #{issue?.id || issueId} - AI Issues Tracker</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<Navigation {user} />
	
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		{#if loading}
			<div class="flex items-center justify-center h-64">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
				<span class="ml-3 text-gray-600">Loading issue...</span>
			</div>
		{:else if error}
			<div class="bg-red-50 border border-red-200 rounded-md p-4">
				<div class="flex">
					<div class="flex-shrink-0">
						<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
						</svg>
					</div>
					<div class="ml-3">
						<h3 class="text-sm font-medium text-red-800">Error loading issue</h3>
						<p class="mt-1 text-sm text-red-700">{error}</p>
					</div>
				</div>
			</div>
		{:else if issue}
			<!-- Header -->
			<div class="bg-white shadow rounded-lg mb-6">
				<div class="px-6 py-4 border-b border-gray-200">
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-3">
							<h1 class="text-2xl font-bold text-gray-900">
								Issue #{issue.id}
							</h1>
							<span class="{getSeverityClass(issue.severity)}">{issue.severity}</span>
							<span class="{getStatusClass(issue.status)}">{issue.status}</span>
						</div>
						<div class="flex items-center space-x-3">
							{#if canEdit}
								<button
									class="btn-secondary"
									on:click={() => editing = !editing}
								>
									{editing ? 'Cancel' : 'Edit'}
								</button>
								
								{#if user?.role === 'ADMIN'}
									<button
										class="inline-flex items-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
										on:click={deleteIssue}
									>
										Delete
									</button>
								{/if}
							{/if}
							
							<button
								class="btn-outline ai-glow"
								on:click={() => showAIPanel = !showAIPanel}
							>
								🤖 {showAIPanel ? 'Hide' : 'Show'} AI Insights
							</button>
						</div>
					</div>
				</div>
				
				<!-- AI Insights Panel -->
				{#if showAIPanel}
					<div class="px-6 py-4 bg-gradient-to-r from-purple-50 to-blue-50 border-b border-gray-200">
						<h2 class="text-lg font-semibold text-gray-900 mb-4">🤖 AI Analysis</h2>
						
						{#if aiAnalyzing}
							<div class="flex items-center text-gray-600">
								<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mr-2"></div>
								Analyzing issue with AI...
							</div>
						{:else}
							<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
								<!-- Time Estimate -->
								{#if timeEstimate}
									<div class="bg-white rounded-lg p-4 border">
										<h3 class="font-medium text-gray-900 mb-2">⏰ Time Estimate</h3>
										<p class="text-2xl font-bold text-blue-600">{timeEstimate.predicted_hours}h</p>
										<p class="text-sm text-gray-600">Confidence: {(timeEstimate.confidence * 100).toFixed(0)}%</p>
										<p class="text-xs text-gray-500 mt-1">{timeEstimate.reasoning}</p>
									</div>
								{/if}
								
								<!-- Escalation Risk -->
								{#if escalationRisk}
									<div class="bg-white rounded-lg p-4 border">
										<h3 class="font-medium text-gray-900 mb-2">🚨 Escalation Risk</h3>
										<p class="text-2xl font-bold {escalationRisk.risk_level === 'HIGH' ? 'text-red-600' : escalationRisk.risk_level === 'MEDIUM' ? 'text-yellow-600' : 'text-green-600'}">
											{escalationRisk.risk_level}
										</p>
										<p class="text-sm text-gray-600">{(escalationRisk.escalation_risk * 100).toFixed(0)}% risk</p>
										{#if escalationRisk.factors}
											<ul class="text-xs text-gray-500 mt-1">
												{#each escalationRisk.factors as factor}
													<li>• {factor}</li>
												{/each}
											</ul>
										{/if}
									</div>
								{/if}
								
								<!-- AI Classification -->
								{#if aiInsights}
									<div class="bg-white rounded-lg p-4 border">
										<h3 class="font-medium text-gray-900 mb-2">🎯 AI Classification</h3>
										<p class="text-sm text-gray-600 mb-1">
											Suggested Severity: <span class="font-medium">{aiInsights.suggested_severity}</span>
										</p>
										<p class="text-sm text-gray-600 mb-1">
											Tags: <span class="font-medium">{aiInsights.suggested_tags?.join(', ')}</span>
										</p>
										<p class="text-xs text-gray-500">Confidence: {(aiInsights.confidence * 100).toFixed(0)}%</p>
									</div>
								{/if}
							</div>
							
							<!-- Resolution Steps -->
							{#if resolutionSuggestions && resolutionSuggestions.length > 0}
								<div class="mt-4">
									<button
										class="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900"
										on:click={() => showResolutionSteps = !showResolutionSteps}
									>
										<span class="mr-2">{showResolutionSteps ? '📖' : '📋'}</span>
										{showResolutionSteps ? 'Hide' : 'Show'} Resolution Steps
									</button>
									
									{#if showResolutionSteps}
										<div class="mt-3 bg-white rounded-lg p-4 border">
											<h4 class="font-medium text-gray-900 mb-3">🛠️ Suggested Resolution Steps</h4>
											<div class="space-y-3">
												{#each resolutionSuggestions as step}
													<div class="flex items-start">
														<span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-sm font-medium mr-3 mt-0.5">
															{step.step}
														</span>
														<div class="flex-1">
															<h5 class="font-medium text-gray-900">{step.action}</h5>
															<p class="text-sm text-gray-600">{step.description}</p>
															<div class="flex items-center mt-1 text-xs text-gray-500">
																<span class="mr-3">⏱️ {step.estimated_time}</span>
																<span class="{step.priority === 'high' ? 'text-red-600' : step.priority === 'medium' ? 'text-yellow-600' : 'text-green-600'}">
																	{step.priority} priority
																</span>
															</div>
														</div>
													</div>
												{/each}
											</div>
										</div>
									{/if}
								</div>
							{/if}
						{/if}
					</div>
				{/if}
			</div>

			<!-- Main Content -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<!-- Issue Details -->
				<div class="lg:col-span-2 space-y-6">
					<!-- Title and Description -->
					<div class="bg-white shadow rounded-lg p-6">
						{#if editing}
							<div class="space-y-4">
								<div>
									<label for="title" class="block text-sm font-medium text-gray-700 mb-2">Title</label>
									<input
										type="text"
										id="title"
										bind:value={editForm.title}
										class="input-field"
										placeholder="Enter issue title"
										required
									/>
								</div>
								
								<div>
									<label for="description" class="block text-sm font-medium text-gray-700 mb-2">Description</label>
									<textarea
										id="description"
										bind:value={editForm.description}
										rows="8"
										class="input-field"
										placeholder="Describe the issue in detail"
										required
									></textarea>
								</div>
								
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div>
										<label for="severity" class="block text-sm font-medium text-gray-700 mb-2">Severity</label>
										<select id="severity" bind:value={editForm.severity} class="input-field">
											<option value="LOW">Low</option>
											<option value="MEDIUM">Medium</option>
											<option value="HIGH">High</option>
											<option value="CRITICAL">Critical</option>
										</select>
									</div>
									
									<div>
										<label for="status" class="block text-sm font-medium text-gray-700 mb-2">Status</label>
										<select id="status" bind:value={editForm.status} class="input-field">
											<option value="OPEN">Open</option>
											<option value="TRIAGED">Triaged</option>
											<option value="IN_PROGRESS">In Progress</option>
											<option value="DONE">Done</option>
										</select>
									</div>
								</div>
								
								<div>
									<label for="tags" class="block text-sm font-medium text-gray-700 mb-2">Tags</label>
									<input
										type="text"
										id="tags"
										bind:value={editForm.tags}
										class="input-field"
										placeholder="Enter tags separated by commas"
									/>
								</div>
								
								{#if availableUsers.length > 0}
									<div>
										<label for="assignee" class="block text-sm font-medium text-gray-700 mb-2">Assignee</label>
										<div class="flex space-x-2">
											<select id="assignee" bind:value={editForm.assignee_id} class="input-field flex-1">
												<option value={null}>Unassigned</option>
												{#each availableUsers as user}
													<option value={user.id}>{user.full_name} ({user.email})</option>
												{/each}
											</select>
											<button
												type="button"
												class="btn-outline ai-glow"
												on:click={getSmartAssignment}
												title="Get AI assignment suggestion"
											>
												🤖 AI
											</button>
										</div>
									</div>
								{/if}
								
								<div class="flex space-x-3 pt-4 border-t">
									<button class="btn-primary" on:click={saveIssue}>
										Save Changes
									</button>
									<button class="btn-secondary" on:click={cancelEdit}>
										Cancel
									</button>
								</div>
							</div>
						{:else}
							<div>
								<h2 class="text-xl font-semibold text-gray-900 mb-4">{issue.title}</h2>
								<div class="prose max-w-none">
									<p class="text-gray-700 whitespace-pre-wrap">{issue.description}</p>
								</div>
								
								{#if issue.tags}
									<div class="mt-4">
										<span class="text-sm font-medium text-gray-500">Tags: </span>
										{#each issue.tags.split(',') as tag}
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mr-2">
												{tag.trim()}
											</span>
										{/each}
									</div>
								{/if}
							</div>
						{/if}
					</div>

					<!-- File Attachment -->
					{#if issue.file_path}
						<div class="bg-white shadow rounded-lg p-6">
							<h3 class="text-lg font-medium text-gray-900 mb-4">📎 Attachment</h3>
							<div class="flex items-center space-x-3">
								<div class="flex-shrink-0">
									<svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
									</svg>
								</div>
								<div>
									<p class="text-sm font-medium text-gray-900">{issue.file_name}</p>
									<a 
										href="/uploads/{issue.file_path.split('/').pop()}" 
										target="_blank"
										class="text-sm text-indigo-600 hover:text-indigo-500"
									>
										Download file
									</a>
								</div>
							</div>
						</div>
					{/if}
				</div>

				<!-- Sidebar -->
				<div class="space-y-6">
					<!-- Issue Metadata -->
					<div class="bg-white shadow rounded-lg p-6">
						<h3 class="text-lg font-medium text-gray-900 mb-4">Issue Details</h3>
						<div class="space-y-3">
							<div class="flex justify-between">
								<span class="text-sm font-medium text-gray-500">Status:</span>
								<span class="{getStatusClass(issue.status)}">{issue.status}</span>
							</div>
							
							<div class="flex justify-between">
								<span class="text-sm font-medium text-gray-500">Severity:</span>
								<span class="{getSeverityClass(issue.severity)}">{issue.severity}</span>
							</div>
							
							<div class="flex justify-between">
								<span class="text-sm font-medium text-gray-500">Reporter:</span>
								<span class="text-sm text-gray-900">{issue.reporter?.full_name || 'Unknown'}</span>
							</div>
							
							<div class="flex justify-between">
								<span class="text-sm font-medium text-gray-500">Assignee:</span>
								<span class="text-sm text-gray-900">{getAssigneeName(issue.assignee_id)}</span>
							</div>
							
							<div class="flex justify-between">
								<span class="text-sm font-medium text-gray-500">Created:</span>
								<span class="text-sm text-gray-900">{formatDate(issue.created_at)}</span>
							</div>
							
							<div class="flex justify-between">
								<span class="text-sm font-medium text-gray-500">Updated:</span>
								<span class="text-sm text-gray-900">{formatDate(issue.updated_at)}</span>
							</div>
						</div>
					</div>

					<!-- Quick Actions -->
					{#if canEdit}
						<div class="bg-white shadow rounded-lg p-6">
							<h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
							<div class="space-y-2">
								{#if issue.status !== 'IN_PROGRESS'}
									<button
										class="w-full btn-primary"
										on:click={() => {
											editForm.status = 'IN_PROGRESS';
											saveIssue();
										}}
									>
										Start Working
									</button>
								{/if}
								
								{#if issue.status !== 'DONE'}
									<button
										class="w-full btn-secondary"
										on:click={() => {
											editForm.status = 'DONE';
											saveIssue();
										}}
									>
										Mark as Done
									</button>
								{/if}
								
								<button
									class="w-full btn-outline"
									on:click={() => editing = true}
								>
									Edit Issue
								</button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.ai-glow {
		box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
		transition: all 0.3s ease;
	}
	
	.ai-glow:hover {
		box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
		transform: translateY(-1px);
	}
	
	.prose {
		line-height: 1.6;
	}
	
	.loading-spinner {
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
</style>
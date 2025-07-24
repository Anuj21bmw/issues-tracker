// frontend/src/routes/issues/[id]/+page.svelte - AI Enhanced
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
	let aiAnalyzing = false;
	let aiInsights = null;
	let resolutionSuggestions = null;
	let timeEstimate = null;
	let escalationRisk = null;
	let similarIssues = [];
	let showAIPanel = false;

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

	onMount(async () => {
		await loadIssue();
		await loadAvailableUsers();
		await loadAIAnalysis();
	});

	async function loadIssue() {
		try {
			loading = true;
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch(`/api/issues/${issueId}`, {
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

	async function loadAvailableUsers() {
		try {
			const headers = authStore.getAuthHeaders();
			const response = await fetch('/api/auth/users', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (response.ok) {
				const users = await response.json();
				availableUsers = users.filter(user => 
					user.role === 'MAINTAINER' || user.role === 'ADMIN'
				);
			}
		} catch (err) {
			console.error('Error loading users:', err);
		}
	}

	async function loadAIAnalysis() {
		if (!issue) return;

		try {
			aiAnalyzing = true;
			const headers = authStore.getAuthHeaders();

			// Load AI insights for this issue
			const analysisResponse = await fetch('/api/ai/analyze-issue', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					...headers
				},
				body: JSON.stringify({
					title: issue.title,
					description: issue.description,
					severity: issue.severity,
					tags: issue.tags,
					reporter_experience: 5 // Could be calculated based on user data
				})
			});

			if (analysisResponse.ok) {
				const analysisData = await analysisResponse.json();
				if (analysisData.success) {
					const analysis = analysisData.analysis;
					aiInsights = analysis.classification;
					timeEstimate = analysis.time_prediction;
					escalationRisk = analysis.escalation_risk;
					similarIssues = analysis.classification.similar_issues || [];
				}
			}

			// Load resolution suggestions
			const suggestionsResponse = await fetch(`/api/ai/resolution-suggestions/${issueId}`, {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (suggestionsResponse.ok) {
				const suggestionsData = await suggestionsResponse.json();
				resolutionSuggestions = suggestionsData.suggestions;
			}

		} catch (err) {
			console.error('AI analysis failed:', err);
		} finally {
			aiAnalyzing = false;
		}
	}

	async function updateIssue() {
		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch(`/api/issues/${issueId}`, {
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

			// Reload AI analysis if the issue changed significantly
			if (editForm.title !== issue.title || editForm.description !== issue.description) {
				await loadAIAnalysis();
			}
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
			
			const response = await fetch(`/api/issues/${issueId}`, {
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

	async function suggestSmartAssignment() {
		try {
			const headers = authStore.getAuthHeaders();
			const response = await fetch('/api/ai/suggest-assignment', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					...headers
				},
				body: JSON.stringify({
					title: issue.title,
					description: issue.description,
					severity: issue.severity,
					tags: issue.tags
				})
			});

			if (response.ok) {
				const data = await response.json();
				if (data.success && data.suggestion.suggested_assignee) {
					const suggestedUser = data.suggestion.suggested_assignee;
					editForm.assignee_id = suggestedUser.id;
					
					toastStore.add({
						type: 'success',
						message: `AI suggests: ${suggestedUser.name} (${data.suggestion.reason})`
					});
				}
			}
		} catch (err) {
			toastStore.add({
				type: 'error',
				message: 'Failed to get AI assignment suggestion'
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

	function getRiskColor(risk) {
		const colors = {
			HIGH: 'text-red-600',
			MEDIUM: 'text-yellow-600',
			LOW: 'text-green-600',
			MINIMAL: 'text-gray-600'
		};
		return colors[risk] || 'text-gray-600';
	}

	function getConfidenceColor(confidence) {
		if (confidence >= 0.8) return 'text-green-600';
		if (confidence >= 0.6) return 'text-yellow-600';
		return 'text-red-600';
	}
</script>

<svelte:head>
	<title>{issue?.title || 'Issue'} - AI-Enhanced Issues Tracker</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<a href="/issues" class="text-blue-600 hover:text-blue-800 flex items-center mb-2">
				← Back to Issues
			</a>
			<h1 class="text-3xl font-bold text-gray-900 flex items-center">
				Issue Details
				{#if aiInsights}
					<div class="ml-3 text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
						🤖 AI Enhanced
					</div>
				{/if}
			</h1>
		</div>
		<div class="flex items-center space-x-3">
			<button 
				on:click={() => showAIPanel = !showAIPanel}
				class="btn-outline ai-glow"
				disabled={aiAnalyzing}
			>
				{#if aiAnalyzing}
					<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mr-2"></div>
					AI Analyzing...
				{:else}
					🤖 {showAIPanel ? 'Hide' : 'Show'} AI Insights
				{/if}
			</button>
			
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
		<!-- AI Alert Banner -->
		{#if escalationRisk?.needs_escalation}
			<div class="bg-red-50 border-l-4 border-red-400 p-4">
				<div class="flex">
					<div class="flex-shrink-0">
						<span class="text-red-400 text-xl">🚨</span>
					</div>
					<div class="ml-3">
						<h3 class="text-sm font-medium text-red-800">
							AI Alert: Escalation Needed
						</h3>
						<p class="text-sm text-red-700 mt-1">
							This issue shows {escalationRisk.escalation_level} escalation risk and needs immediate attention.
						</p>
					</div>
				</div>
			</div>
		{/if}

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
										<option value="LOW">🟢 Low</option>
										<option value="MEDIUM">🟡 Medium</option>
										<option value="HIGH">🟠 High</option>
										<option value="CRITICAL">🔴 Critical</option>
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
							{#if $authStore.user?.role !== 'REPORTER'}
								<div>
									<div class="flex items-center justify-between">
										<label class="label">Assignee</label>
										<button 
											on:click={suggestSmartAssignment}
											class="text-sm bg-purple-100 text-purple-700 px-2 py-1 rounded hover:bg-purple-200 transition-colors"
										>
											🤖 AI Suggest
										</button>
									</div>
									<select bind:value={editForm.assignee_id} class="input">
										<option value={null}>Unassigned</option>
										{#each availableUsers as user}
											<option value={user.id}>{user.full_name}</option>
										{/each}
									</select>
								</div>
							{/if}
						</div>
					{:else}
						<div>
							<div class="flex items-center space-x-3 mb-4">
								<h2 class="text-2xl font-bold text-gray-900">{issue.title}</h2>
								<span class="{getSeverityClass(issue.severity)}">{issue.severity}</span>
								<span class="{getStatusClass(issue.status)}">{issue.status}</span>
								{#if timeEstimate}
									<span class="badge bg-purple-100 text-purple-800">
										🤖 Est: {timeEstimate.predicted_hours}h
									</span>
								{/if}
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

							<!-- AI Suggested Tags -->
							{#if aiInsights?.suggested_tags?.length > 0}
								<div class="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
									<div class="flex items-center space-x-2 mb-2">
										<span class="text-purple-600">🤖</span>
										<span class="text-sm font-medium text-purple-900">AI Suggested Tags:</span>
									</div>
									<div class="flex flex-wrap gap-2">
										{#each aiInsights.suggested_tags as tag}
											<span class="badge bg-purple-200 text-purple-800">{tag}</span>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					{/if}
				</div>

				<!-- AI Insights Panel -->
				{#if showAIPanel && (aiInsights || timeEstimate || escalationRisk)}
					<div class="card ai-glow border-purple-200">
						<h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
							<span class="mr-2">🤖</span>
							AI Analysis & Insights
						</h3>

						<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
							<!-- Time Prediction -->
							{#if timeEstimate}
								<div class="bg-blue-50 p-4 rounded-lg">
									<div class="text-sm font-medium text-blue-900">Resolution Time</div>
									<div class="text-lg font-bold text-blue-600">
										{timeEstimate.predicted_hours} hours
									</div>
									<div class="text-xs text-blue-700">
										≈ {timeEstimate.predicted_days} days
									</div>
									<div class="text-xs {getConfidenceColor(timeEstimate.confidence_score)} mt-1">
										{Math.round(timeEstimate.confidence_score * 100)}% confidence
									</div>
								</div>
							{/if}

							<!-- Escalation Risk -->
							{#if escalationRisk}
								<div class="bg-yellow-50 p-4 rounded-lg">
									<div class="text-sm font-medium text-yellow-900">Escalation Risk</div>
									<div class="text-lg font-bold {getRiskColor(escalationRisk.risk_level)}">
										{escalationRisk.risk_level}
									</div>
									<div class="text-xs text-yellow-700">
										{Math.round(escalationRisk.escalation_probability * 100)}% probability
									</div>
								</div>
							{/if}

							<!-- Severity Confidence -->
							{#if aiInsights}
								<div class="bg-green-50 p-4 rounded-lg">
									<div class="text-sm font-medium text-green-900">AI Classification</div>
									<div class="text-lg font-bold text-green-600">
										{aiInsights.suggested_severity}
									</div>
									<div class="text-xs text-green-700">
										{Math.round(aiInsights.confidence_score * 100)}% confidence
									</div>
								</div>
							{/if}
						</div>

						<!-- AI Insights -->
						{#if aiInsights?.ai_insights?.analysis}
							<div class="bg-gray-50 p-4 rounded-lg mb-4">
								<h4 class="font-medium text-gray-900 mb-2">🧠 AI Analysis</h4>
								<p class="text-sm text-gray-700 whitespace-pre-wrap">{aiInsights.ai_insights.analysis}</p>
							</div>
						{/if}

						<!-- Resolution Factors -->
						{#if timeEstimate?.factors?.length > 0}
							<div class="mb-4">
								<h4 class="font-medium text-gray-900 mb-2">📊 Time Factors</h4>
								<ul class="text-sm text-gray-700 space-y-1">
									{#each timeEstimate.factors as factor}
										<li>• {factor}</li>
									{/each}
								</ul>
							</div>
						{/if}

						<!-- Recommendations -->
						{#if timeEstimate?.recommendation || escalationRisk?.recommendations?.length > 0}
							<div>
								<h4 class="font-medium text-gray-900 mb-2">💡 AI Recommendations</h4>
								{#if timeEstimate?.recommendation}
									<p class="text-sm text-gray-700 mb-2">{timeEstimate.recommendation}</p>
								{/if}
								{#if escalationRisk?.recommendations?.length > 0}
									<ul class="text-sm text-gray-700 space-y-1">
										{#each escalationRisk.recommendations as rec}
											<li>• {rec}</li>
										{/each}
									</ul>
								{/if}
							</div>
						{/if}
					</div>
				{/if}

				<!-- Similar Issues -->
				{#if similarIssues?.length > 0}
					<div class="card">
						<h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
							<span class="mr-2">🔍</span>
							Similar Resolved Issues
						</h3>
						<div class="space-y-3">
							{#each similarIssues.slice(0, 3) as similar}
								<div class="border border-gray-200 rounded-lg p-3 hover:bg-gray-50">
									<div class="flex items-center justify-between">
										<div>
											<div class="font-medium text-gray-900">#{similar.id} {similar.title}</div>
											<div class="text-sm text-gray-600">
												Similarity: {Math.round(similar.similarity_score * 100)}%
												{#if similar.resolution_time_hours}
													• Resolved in: {similar.resolution_time_hours}h
												{/if}
											</div>
										</div>
										<a href="/issues/{similar.id}" class="btn-outline btn-sm">
											View
										</a>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<!-- File Attachment -->
				{#if issue.file_name}
					<div class="card">
						<h3 class="text-lg font-medium text-gray-900 mb-3">📎 Attachment</h3>
						<div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
							<div class="text-blue-500">📎</div>
							<div class="flex-1">
								<div class="font-medium text-gray-900">{issue.file_name}</div>
								<div class="text-sm text-gray-500">Attached file</div>
							</div>
							{#if issue.file_path}
								<a 
									href="/{issue.file_path}"
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

				<!-- AI-Powered Quick Actions -->
				<div class="card">
					<h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
						<span class="mr-2">🚀</span>
						Smart Actions
					</h3>
					<div class="space-y-2">
						{#if canEdit()}
							<button 
								on:click={() => editing = !editing}
								class="w-full btn-outline text-left"
							>
								{editing ? '❌ Cancel Edit' : '✏️ Edit Issue'}
							</button>
						{/if}

						{#if $authStore.user?.role !== 'REPORTER'}
							<button 
								on:click={suggestSmartAssignment}
								class="w-full btn-outline text-left bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100"
							>
								🤖 AI Assignment Suggestion
							</button>
						{/if}

						<button 
							on:click={() => showAIPanel = !showAIPanel}
							class="w-full btn-outline text-left bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100"
						>
							🔮 {showAIPanel ? 'Hide' : 'Show'} AI Insights
						</button>
						
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

				<!-- AI Status -->
				<div class="card bg-purple-50 border-purple-200">
					<h3 class="text-sm font-medium text-purple-900 mb-2">🤖 AI Enhancement Status</h3>
					<div class="space-y-2 text-xs text-purple-800">
						<div class="flex items-center justify-between">
							<span>Classification</span>
							<span class="flex items-center">
								{#if aiInsights}
									<span class="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
									Active
								{:else}
									<span class="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
									Pending
								{/if}
							</span>
						</div>
						<div class="flex items-center justify-between">
							<span>Time Prediction</span>
							<span class="flex items-center">
								{#if timeEstimate}
									<span class="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
									{timeEstimate.predicted_hours}h
								{:else}
									<span class="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
									N/A
								{/if}
							</span>
						</div>
						<div class="flex items-center justify-between">
							<span>Risk Assessment</span>
							<span class="flex items-center">
								{#if escalationRisk}
									<span class="w-2 h-2 {escalationRisk.needs_escalation ? 'bg-red-500' : 'bg-green-500'} rounded-full mr-2"></span>
									{escalationRisk.risk_level}
								{:else}
									<span class="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
									N/A
								{/if}
							</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style lang="postcss">
	.btn-sm {
		@apply px-2 py-1 text-xs;
	}
	
	.ai-glow {
		box-shadow: 0 0 15px rgba(147, 51, 234, 0.3);
	}
	
	.ai-glow:hover {
		box-shadow: 0 0 20px rgba(147, 51, 234, 0.5);
		transform: translateY(-1px);
		transition: all 0.3s ease;
	}

	/* Severity badges */
	.severity-low {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800;
	}
	
	.severity-medium {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800;
	}
	
	.severity-high {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800;
	}
	
	.severity-critical {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800;
	}

	/* Status badges */
	.status-open {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800;
	}
	
	.status-triaged {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800;
	}
	
	.status-in-progress {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800;
	}
	
	.status-done {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800;
	}

	/* Base badge styles */
	.badge {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
	}
	
	.badge-info {
		@apply bg-blue-100 text-blue-800;
	}

	/* Card styles */
	.card {
		@apply bg-white shadow rounded-lg p-6 border border-gray-200;
	}

	/* Button styles */
	.btn-primary {
		@apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors;
	}
	
	.btn-outline {
		@apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors;
	}
	
	.btn-danger {
		@apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors;
	}

	/* Form styles */
	.label {
		@apply block text-sm font-medium text-gray-700 mb-1;
	}
	
	.input {
		@apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm;
	}

	/* AI-specific animations */
	.ai-pulse {
		animation: ai-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
	
	@keyframes ai-pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.7;
		}
	}

	/* Responsive design improvements */
	@media (max-width: 768px) {
		.ai-glow {
			box-shadow: 0 0 10px rgba(147, 51, 234, 0.2);
		}
		
		.ai-glow:hover {
			box-shadow: 0 0 15px rgba(147, 51, 234, 0.4);
			transform: none;
		}
		
		.card {
			@apply p-4;
		}
	}

	/* Loading states */
	.loading-shimmer {
		background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
	}
	
	@keyframes shimmer {
		0% {
			background-position: -200% 0;
		}
		100% {
			background-position: 200% 0;
		}
	}

	/* AI insight cards hover effects */
	.ai-insight-card {
		transition: all 0.3s ease;
	}
	
	.ai-insight-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	/* Success/Error states for AI predictions */
	.prediction-high-confidence {
		@apply border-l-4 border-green-400 bg-green-50;
	}
	
	.prediction-medium-confidence {
		@apply border-l-4 border-yellow-400 bg-yellow-50;
	}
	
	.prediction-low-confidence {
		@apply border-l-4 border-red-400 bg-red-50;
	}
</style>
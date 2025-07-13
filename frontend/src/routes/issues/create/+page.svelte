<script>
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';

	let title = '';
	let description = '';
	let severity = 'LOW';
	let tags = '';
	let file = null;
	let submitting = false;

	async function handleSubmit() {
		if (!title.trim() || !description.trim()) {
			toastStore.add({
				type: 'error',
				message: 'Please fill in all required fields'
			});
			return;
		}

		try {
			submitting = true;
			const headers = authStore.getAuthHeaders();
			
			const formData = new FormData();
			formData.append('title', title.trim());
			formData.append('description', description.trim());
			formData.append('severity', severity);
			if (tags.trim()) formData.append('tags', tags.trim());
			if (file) formData.append('file', file);

			const response = await fetch('http://localhost:8000/api/issues/', {
				method: 'POST',
				headers: {
					...headers
				},
				body: formData
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.detail || 'Failed to create issue');
			}

			toastStore.add({
				type: 'success',
				message: 'Issue created successfully!'
			});

			goto('/issues');
		} catch (err) {
			toastStore.add({
				type: 'error',
				message: err.message
			});
		} finally {
			submitting = false;
		}
	}

	function handleFileChange(event) {
		const selectedFile = event.target.files[0];
		if (selectedFile) {
			// Check file size (10MB limit)
			if (selectedFile.size > 10 * 1024 * 1024) {
				toastStore.add({
					type: 'error',
					message: 'File size must be less than 10MB'
				});
				event.target.value = '';
				return;
			}
			
			// Check file type
			const allowedTypes = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.txt'];
			const fileExt = '.' + selectedFile.name.split('.').pop().toLowerCase();
			if (!allowedTypes.includes(fileExt)) {
				toastStore.add({
					type: 'error',
					message: 'File type not allowed. Allowed types: ' + allowedTypes.join(', ')
				});
				event.target.value = '';
				return;
			}
			
			file = selectedFile;
		}
	}

	function removeFile() {
		file = null;
		const fileInput = document.getElementById('file');
		if (fileInput) {
			fileInput.value = '';
		}
	}
</script>

<svelte:head>
	<title>Create Issue - Issues & Insights Tracker</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Create New Issue</h1>
			<p class="mt-2 text-gray-600">Report a new issue or request</p>
		</div>
		<div>
			<a href="/issues" class="btn-outline">
				← Back to Issues
			</a>
		</div>
	</div>

	<div class="card max-w-2xl">
		<form on:submit|preventDefault={handleSubmit} class="space-y-6">
			<div>
				<label for="title" class="label">
					Title <span class="text-red-500">*</span>
				</label>
				<input
					id="title"
					type="text"
					bind:value={title}
					required
					class="input"
					placeholder="Brief description of the issue"
				/>
			</div>

			<div>
				<label for="description" class="label">
					Description <span class="text-red-500">*</span>
				</label>
				<textarea
					id="description"
					bind:value={description}
					required
					rows="6"
					class="input"
					placeholder="Detailed description of the issue. You can use Markdown formatting."
				></textarea>
				<p class="mt-1 text-sm text-gray-500">
					💡 Tip: Use Markdown for formatting (e.g., **bold**, *italic*, `code`)
				</p>
			</div>

			<div>
				<label for="severity" class="label">Severity</label>
				<select id="severity" bind:value={severity} class="input">
					<option value="LOW">🟢 Low</option>
					<option value="MEDIUM">🟡 Medium</option>
					<option value="HIGH">🟠 High</option>
					<option value="CRITICAL">🔴 Critical</option>
				</select>
			</div>

			<div>
				<label for="tags" class="label">Tags</label>
				<input
					id="tags"
					type="text"
					bind:value={tags}
					class="input"
					placeholder="Optional tags (comma-separated)"
				/>
				<p class="mt-1 text-sm text-gray-500">
					Example: bug, ui, performance
				</p>
			</div>

			<div>
				<label for="file" class="label">Attachment</label>
				<input
					id="file"
					type="file"
					on:change={handleFileChange}
					class="input"
					accept=".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.txt"
				/>
				<p class="mt-1 text-sm text-gray-500">
					📎 Optional file attachment (max 10MB). Allowed: PDF, images, documents, text files.
				</p>
				{#if file}
					<div class="mt-2 p-2 bg-blue-50 rounded border">
						<span class="text-sm text-blue-700">📎 {file.name}</span>
						<button 
							type="button" 
							on:click={removeFile}
							class="ml-2 text-red-500 hover:text-red-700"
						>
							Remove
						</button>
					</div>
				{/if}
			</div>

			<div class="flex items-center justify-end space-x-4 pt-6 border-t">
				<a href="/issues" class="btn-outline">
					Cancel
				</a>
				<button
					type="submit"
					disabled={submitting || !title.trim() || !description.trim()}
					class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if submitting}
						<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
						Creating...
					{:else}
						✨ Create Issue
					{/if}
				</button>
			</div>
		</form>
	</div>

	<!-- Guidelines -->
	<div class="card max-w-2xl bg-blue-50 border-blue-200">
		<h3 class="text-lg font-medium text-blue-900 mb-3">📋 Issue Guidelines</h3>
		<ul class="text-sm text-blue-800 space-y-2">
			<li>• <strong>Be specific:</strong> Include clear steps to reproduce the issue</li>
			<li>• <strong>Add context:</strong> Mention your environment, browser, or device</li>
			<li>• <strong>Choose severity wisely:</strong> Critical = system down, High = major feature broken</li>
			<li>• <strong>Use attachments:</strong> Screenshots and logs help diagnose issues faster</li>
		</ul>
	</div>
</div>
// frontend/src/lib/components/ai/AIEnhancedIssueForm.svelte
<script>
    import { createEventDispatcher } from 'svelte';
    import { authStore } from '$lib/stores/auth';
    import { toastStore } from '$lib/stores/toast';

    const dispatch = createEventDispatcher();

    export let initialData = {};

    let title = initialData.title || '';
    let description = initialData.description || '';
    let severity = initialData.severity || 'MEDIUM';
    let tags = initialData.tags || '';
    let file = null;

    let aiSuggestions = null;
    let loadingSuggestions = false;
    let autoClassifyEnabled = true;

    // AI-powered auto-classification
    $: if (autoClassifyEnabled && (title || description)) {
        debouncedClassify();
    }

    let classifyTimeout;
    function debouncedClassify() {
        clearTimeout(classifyTimeout);
        classifyTimeout = setTimeout(async () => {
            if (title.length > 5 || description.length > 20) {
                await getAIClassification();
            }
        }, 1000); // Wait 1 second after user stops typing
    }

    async function getAIClassification() {
        if (!title && !description) return;
        
        loadingSuggestions = true;
        
        try {
            const formData = new FormData();
            formData.append('title', title);
            formData.append('description', description);
            
            const response = await fetch('/api/ai/classify-issue', {
                method: 'POST',
                headers: authStore.getAuthHeaders(),
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                aiSuggestions = data.classification;
                
                // Auto-apply suggestions if confidence is high
                if (data.classification.confidence > 0.8) {
                    severity = data.classification.severity;
                    if (data.classification.suggested_tags?.length > 0) {
                        const existingTags = tags.split(',').map(t => t.trim()).filter(t => t);
                        const newTags = data.classification.suggested_tags.filter(tag => 
                            !existingTags.includes(tag)
                        );
                        tags = [...existingTags, ...newTags].join(', ');
                    }
                }
            }
        } catch (error) {
            console.error('AI classification failed:', error);
        } finally {
            loadingSuggestions = false;
        }
    }

    async function handleSubmit() {
        if (!title.trim() || !description.trim()) {
            toastStore.add({
                type: 'error',
                message: 'Title and description are required'
            });
            return;
        }
        
        const formData = new FormData();
        formData.append('title', title.trim());
        formData.append('description', description.trim());
        formData.append('severity', severity);
        formData.append('tags', tags.trim());
        
        if (file) {
            formData.append('file', file);
        }
        
        try {
            const response = await fetch('/api/issues', {
                method: 'POST',
                headers: authStore.getAuthHeaders(),
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                toastStore.add({
                    type: 'success',
                    message: 'Issue created successfully'
                });
                dispatch('created', data.issue);
                
                // Reset form
                title = '';
                description = '';
                severity = 'MEDIUM';
                tags = '';
                file = null;
                aiSuggestions = null;
            } else {
                throw new Error(data.message || 'Failed to create issue');
            }
        } catch (error) {
            toastStore.add({
                type: 'error',
                message: error.message || 'Failed to create issue'
            });
        }
    }

    function applySuggestion(field, value) {
        if (field === 'severity') {
            severity = value;
        } else if (field === 'tags') {
            const existingTags = tags.split(',').map(t => t.trim()).filter(t => t);
            if (!existingTags.includes(value)) {
                tags = tags ? `${tags}, ${value}` : value;
            }
        }
    }
</script>

<div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span class="text-3xl mr-3">🎫</span>
        Create New Issue
        <div class="ml-auto">
            <label class="flex items-center text-sm">
                <input 
                    type="checkbox" 
                    bind:checked={autoClassifyEnabled}
                    class="mr-2"
                />
                <span class="text-purple-600">🤖 AI Assist</span>
            </label>
        </div>
    </h2>
    
    <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        <!-- Title with AI assistance indicator -->
        <div>
            <label for="title" class="block text-sm font-medium text-gray-700 mb-1">
                Title *
                {#if loadingSuggestions}
                    <span class="text-purple-500 animate-pulse">🤖 Analyzing...</span>
                {/if}
            </label>
            <input
                id="title"
                type="text"
                bind:value={title}
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Brief description of the issue"
            />
        </div>
        
        <!-- Description -->
        <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
                Description *
            </label>
            <textarea
                id="description"
                bind:value={description}
                required
                rows="6"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Detailed description of the issue. You can use Markdown formatting."
            ></textarea>
            <p class="mt-1 text-sm text-gray-500">
                💡 Tip: Include error messages, steps to reproduce, and expected behavior
            </p>
        </div>
        
        <!-- AI Suggestions Panel -->
        {#if aiSuggestions && autoClassifyEnabled}
            <div class="bg-purple-50 border border-purple-200 rounded-md p-4">
                <h3 class="font-medium text-purple-900 mb-3 flex items-center">
                    <span class="mr-2">🤖</span>
                    AI Suggestions
                    <span class="ml-2 text-sm font-normal text-purple-600">
                        (Confidence: {Math.round(aiSuggestions.confidence * 100)}%)
                    </span>
                </h3>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <!-- Severity Suggestion -->
                    <div class="flex items-center justify-between">
                        <span class="text-gray-700">Suggested Severity:</span>
                        <button
                            type="button"
                            on:click={() => applySuggestion('severity', aiSuggestions.severity)}
                            class="px-2 py-1 bg-purple-100 text-purple-800 rounded hover:bg-purple-200 transition-colors"
                        >
                            {aiSuggestions.severity}
                        </button>
                    </div>
                    
                    <!-- Category -->
                    <div class="flex items-center justify-between">
                        <span class="text-gray-700">Category:</span>
                        <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                            {aiSuggestions.category}
                        </span>
                    </div>
                    
                    <!-- Technology -->
                    <div class="flex items-center justify-between">
                        <span class="text-gray-700">Technology:</span>
                        <span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                            {aiSuggestions.technology}
                        </span>
                    </div>
                    
                    <!-- Complexity -->
                    <div class="flex items-center justify-between">
                        <span class="text-gray-700">Complexity:</span>
                        <span class="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs">
                            {aiSuggestions.estimated_complexity}
                        </span>
                    </div>
                </div>
                
                <!-- Suggested Tags -->
                {#if aiSuggestions.suggested_tags?.length > 0}
                    <div class="mt-3">
                        <span class="text-gray-700 text-sm">Suggested Tags:</span>
                        <div class="flex flex-wrap gap-2 mt-1">
                            {#each aiSuggestions.suggested_tags as tag}
                                <button
                                    type="button"
                                    on:click={() => applySuggestion('tags', tag)}
                                    class="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs hover:bg-indigo-200 transition-colors"
                                >
                                    + {tag}
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
        {/if}
        
        <!-- Severity Selection -->
        <div>
            <label for="severity" class="block text-sm font-medium text-gray-700 mb-1">
                Severity
                {#if aiSuggestions && aiSuggestions.severity !== severity}
                    <span class="text-purple-600 text-xs">(AI suggests: {aiSuggestions.severity})</span>
                {/if}
            </label>
            <select 
                id="severity" 
                bind:value={severity} 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
                <option value="LOW">🟢 Low</option>
                <option value="MEDIUM">🟡 Medium</option>
                <option value="HIGH">🟠 High</option>
                <option value="CRITICAL">🔴 Critical</option>
            </select>
        </div>
        
        <!-- Tags -->
        <div>
            <label for="tags" class="block text-sm font-medium text-gray-700 mb-1">
                Tags
            </label>
            <input
                id="tags"
                type="text"
                bind:value={tags}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Optional tags (comma-separated)"
            />
            <p class="mt-1 text-sm text-gray-500">
                Example: bug, ui, performance
            </p>
        </div>
        
        <!-- File Attachment -->
        <div>
            <label for="file" class="block text-sm font-medium text-gray-700 mb-1">
                Attachment
            </label>
            <input
                id="file"
                type="file"
                on:change={(e) => file = e.target.files[0]}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                accept=".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.txt,.log"
            />
            <p class="mt-1 text-sm text-gray-500">
                📎 Optional file attachment (max 10MB). Screenshots and logs help with faster resolution.
            </p>
        </div>
        
        <!-- Submit Button -->
        <div class="flex justify-end space-x-3">
            <button
                type="button"
                on:click={() => dispatch('cancel')}
                class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            >
                Cancel
            </button>
            <button
                type="submit"
                class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center"
            >
                <span class="mr-2">🚀</span>
                Create Issue
            </button>
        </div>
    </form>
</div>
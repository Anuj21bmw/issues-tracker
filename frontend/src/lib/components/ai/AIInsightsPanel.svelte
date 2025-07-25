// frontend/src/lib/components/ai/AIInsightsPanel.svelte
<script>
    import { onMount } from 'svelte';
    import { authStore } from '$lib/stores/auth';
    
    export let issueId = null;
    
    let insights = null;
    let loading = false;
    let error = null;
    
    onMount(() => {
        if (issueId) {
            loadInsights();
        }
    });
    
    async function loadInsights() {
        loading = true;
        error = null;
        
        try {
            const response = await fetch(`/api/ai/insights/issue/${issueId}`, {
                headers: authStore.getAuthHeaders()
            });
            
            const data = await response.json();
            
            if (data.success) {
                insights = data.insights;
            } else {
                error = 'Failed to load AI insights';
            }
        } catch (err) {
            error = 'Error loading insights';
            console.error('Insights loading error:', err);
        } finally {
            loading = false;
        }
    }
    
    function formatConfidence(confidence) {
        return Math.round(confidence * 100) + '%';
    }
    
    function getConfidenceColor(confidence) {
        if (confidence >= 0.8) return 'text-green-600';
        if (confidence >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    }
</script>

<div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span class="text-2xl mr-2">🤖</span>
        AI Insights
    </h3>
    
    {#if loading}
        <div class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span class="ml-2 text-gray-600">Analyzing issue...</span>
        </div>
    {:else if error}
        <div class="bg-red-50 border border-red-200 rounded-md p-4">
            <p class="text-red-600">{error}</p>
            <button 
                on:click={loadInsights}
                class="mt-2 text-sm text-red-700 hover:text-red-900 underline"
            >
                Try again
            </button>
        </div>
    {:else if insights}
        <div class="space-y-6">
            <!-- Classification -->
            {#if insights.classification}
                <div class="border-l-4 border-blue-500 pl-4">
                    <h4 class="font-medium text-gray-900 mb-2">Classification</h4>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="text-gray-600">Severity:</span>
                            <span class="ml-2 font-medium">{insights.classification.severity}</span>
                        </div>
                        <div>
                            <span class="text-gray-600">Category:</span>
                            <span class="ml-2 font-medium">{insights.classification.category}</span>
                        </div>
                        <div>
                            <span class="text-gray-600">Technology:</span>
                            <span class="ml-2 font-medium">{insights.classification.technology}</span>
                        </div>
                        <div>
                            <span class="text-gray-600">Confidence:</span>
                            <span class="ml-2 font-medium {getConfidenceColor(insights.classification.confidence)}">
                                {formatConfidence(insights.classification.confidence)}
                            </span>
                        </div>
                    </div>
                </div>
            {/if}
            
            <!-- Time Prediction -->
            {#if insights.time_prediction}
                <div class="border-l-4 border-green-500 pl-4">
                    <h4 class="font-medium text-gray-900 mb-2">Resolution Time Prediction</h4>
                    <div class="text-sm space-y-2">
                        <div class="flex items-center">
                            <span class="text-gray-600">Estimated:</span>
                            <span class="ml-2 font-medium text-lg text-green-600">
                                {insights.time_prediction.predicted_time_formatted}
                            </span>
                        </div>
                        <div class="text-gray-600">
                            Range: {insights.time_prediction.prediction_range.min_hours}h - {insights.time_prediction.prediction_range.max_hours}h
                        </div>
                        <div class="text-xs text-gray-500">
                            Confidence: {formatConfidence(insights.time_prediction.confidence)}
                        </div>
                    </div>
                </div>
            {/if}
            
            <!-- Escalation Risk -->
            {#if insights.escalation_risk}
                <div class="border-l-4 border-orange-500 pl-4">
                    <h4 class="font-medium text-gray-900 mb-2">Escalation Risk</h4>
                    <div class="text-sm space-y-2">
                        <div class="flex items-center">
                            <span class="text-gray-600">Risk Level:</span>
                            <span class="ml-2 px-2 py-1 rounded text-xs font-medium
                                {insights.escalation_risk.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                                 insights.escalation_risk.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                 'bg-green-100 text-green-800'}">
                                {insights.escalation_risk.risk_level.toUpperCase()}
                            </span>
                        </div>
                        {#if insights.escalation_risk.risk_factors?.length > 0}
                            <div>
                                <span class="text-gray-600">Risk Factors:</span>
                                <ul class="mt-1 list-disc list-inside text-xs text-gray-600">
                                    {#each insights.escalation_risk.risk_factors as factor}
                                        <li>{factor}</li>
                                    {/each}
                                </ul>
                            </div>
                        {/if}
                    </div>
                </div>
            {/if}
            
            <!-- Assignment Suggestion -->
            {#if insights.assignment_suggestion}
                <div class="border-l-4 border-purple-500 pl-4">
                    <h4 class="font-medium text-gray-900 mb-2">Assignment Suggestion</h4>
                    <div class="text-sm space-y-2">
                        {#if insights.assignment_suggestion.recommended_assignee}
                            <div>
                                <span class="text-gray-600">Recommended:</span>
                                <span class="ml-2 font-medium">{insights.assignment_suggestion.recommended_assignee.name}</span>
                            </div>
                            <div class="text-xs text-gray-500">
                                {insights.assignment_suggestion.reason}
                            </div>
                        {:else}
                            <div class="text-gray-600">No specific assignee recommendation available</div>
                        {/if}
                    </div>
                </div>
            {/if}
            
            <!-- Suggested Tags -->
            {#if insights.classification?.suggested_tags?.length > 0}
                <div class="border-l-4 border-indigo-500 pl-4">
                    <h4 class="font-medium text-gray-900 mb-2">Suggested Tags</h4>
                    <div class="flex flex-wrap gap-2">
                        {#each insights.classification.suggested_tags as tag}
                            <span class="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full">
                                {tag}
                            </span>
                        {/each}
                    </div>
                </div>
            {/if}
            
            <!-- Resolution Suggestions -->
            {#if insights.resolution_suggestions?.immediate_steps?.length > 0}
                <div class="border-l-4 border-teal-500 pl-4">
                    <h4 class="font-medium text-gray-900 mb-2">Next Steps</h4>
                    <ul class="text-sm space-y-1">
                        {#each insights.resolution_suggestions.immediate_steps.slice(0, 3) as step}
                            <li class="flex items-start">
                                <span class="text-teal-500 mr-2">•</span>
                                <span>{step}</span>
                            </li>
                        {/each}
                    </ul>
                </div>
            {/if}
        </div>
        
        <div class="mt-4 pt-4 border-t border-gray-200">
            <button 
                on:click={loadInsights}
                class="text-sm text-blue-600 hover:text-blue-800 flex items-center"
            >
                <span class="mr-1">🔄</span>
                Refresh Insights
            </button>
        </div>
    {:else}
        <div class="text-center py-8 text-gray-500">
            No insights available. Click to analyze this issue.
            <button 
                on:click={loadInsights}
                class="block mx-auto mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
                Analyze with AI
            </button>
        </div>
    {/if}
</div>

<!-- AI-Enhanced Issue Creation Form Component -->
<script>
// frontend/src/lib/components/ai/AIEnhancedIssueForm.svelte
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

<!-- AI Dashboard Widget Component -->
<script>
// frontend/src/lib/components/ai/AIDashboardWidget.svelte
import { onMount } from 'svelte';
import { authStore } from '$lib/stores/auth';

let dashboardInsights = null;
let loading = true;

onMount(() => {
    loadDashboardInsights();
    
    // Refresh insights every 5 minutes
    const interval = setInterval(loadDashboardInsights, 5 * 60 * 1000);
    return () => clearInterval(interval);
});

async function loadDashboardInsights() {
    try {
        const response = await fetch('/api/ai/insights/dashboard', {
            headers: authStore.getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            dashboardInsights = data.insights;
        }
    } catch (error) {
        console.error('Dashboard insights loading failed:', error);
    } finally {
        loading = false;
    }
}

function formatTrend(value) {
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
}

function getTrendColor(value) {
    if (value > 0) return 'text-red-600';
    if (value < 0) return 'text-green-600';
    return 'text-gray-600';
}
</script>

<div class="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg shadow-md p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span class="text-2xl mr-2">🧠</span>
        AI Insights
        <span class="ml-auto text-xs text-gray-500">Live</span>
    </h3>
    
    {#if loading}
        <div class="animate-pulse space-y-4">
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-4 bg-gray-200 rounded w-1/2"></div>
            <div class="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
    {:else if dashboardInsights}
        <div class="space-y-4">
            <!-- Quick Stats -->
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div class="bg-white rounded p-3 shadow-sm">
                    <div class="text-gray-600 text-xs">Issues This Week</div>
                    <div class="text-xl font-bold text-gray-900">
                        {dashboardInsights.weekly_stats?.total_issues || 0}
                    </div>
                    {#if dashboardInsights.weekly_stats?.trend}
                        <div class="text-xs {getTrendColor(dashboardInsights.weekly_stats.trend)}">
                            {formatTrend(dashboardInsights.weekly_stats.trend)} from last week
                        </div>
                    {/if}
                </div>
                
                <div class="bg-white rounded p-3 shadow-sm">
                    <div class="text-gray-600 text-xs">Avg Resolution</div>
                    <div class="text-xl font-bold text-gray-900">
                        {dashboardInsights.resolution_stats?.avg_time || 'N/A'}
                    </div>
                    {#if dashboardInsights.resolution_stats?.trend}
                        <div class="text-xs {getTrendColor(-dashboardInsights.resolution_stats.trend)}">
                            {formatTrend(dashboardInsights.resolution_stats.trend)} from last week
                        </div>
                    {/if}
                </div>
            </div>
            
            <!-- AI Alerts -->
            {#if dashboardInsights.alerts?.length > 0}
                <div class="space-y-2">
                    <h4 class="font-medium text-gray-900 text-sm">🚨 Smart Alerts</h4>
                    {#each dashboardInsights.alerts.slice(0, 3) as alert}
                        <div class="bg-white rounded p-3 shadow-sm border-l-4 
                            {alert.urgency === 'high' ? 'border-red-500' : 
                             alert.urgency === 'medium' ? 'border-yellow-500' : 'border-blue-500'}">
                            <div class="text-sm font-medium text-gray-900">{alert.title}</div>
                            <div class="text-xs text-gray-600 mt-1">{alert.message}</div>
                        </div>
                    {/each}
                </div>
            {/if}
            
            <!-- Predictions -->
            {#if dashboardInsights.predictions}
                <div class="bg-white rounded p-3 shadow-sm">
                    <h4 class="font-medium text-gray-900 text-sm mb-2">📊 Predictions</h4>
                    <div class="space-y-1 text-xs">
                        {#if dashboardInsights.predictions.next_week_issues}
                            <div>
                                <span class="text-gray-600">Next week estimate:</span>
                                <span class="font-medium">{dashboardInsights.predictions.next_week_issues} issues</span>
                            </div>
                        {/if}
                        {#if dashboardInsights.predictions.bottleneck_risk}
                            <div>
                                <span class="text-gray-600">Bottleneck risk:</span>
                                <span class="font-medium text-orange-600">{dashboardInsights.predictions.bottleneck_risk}</span>
                            </div>
                        {/if}
                    </div>
                </div>
            {/if}
            
            <!-- Quick Actions -->
            <div class="flex space-x-2 text-xs">
                <button 
                    on:click={loadDashboardInsights}
                    class="flex-1 bg-purple-100 text-purple-700 px-3 py-2 rounded hover:bg-purple-200 transition-colors"
                >
                    🔄 Refresh
                </button>
                <button 
                    class="flex-1 bg-blue-100 text-blue-700 px-3 py-2 rounded hover:bg-blue-200 transition-colors"
                >
                    📊 Details
                </button>
            </div>
        </div>
    {:else}
        <div class="text-center text-gray-500 py-8">
            <div class="text-4xl mb-2">🤖</div>
            <div class="text-sm">AI insights are being prepared...</div>
            <button 
                on:click={loadDashboardInsights}
                class="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
            >
                Try loading again
            </button>
        </div>
    {/if}
</div>
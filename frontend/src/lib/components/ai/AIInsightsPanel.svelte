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
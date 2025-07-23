// frontend/src/lib/components/ai/AIInsightsDashboard.svelte
<script>
    import { onMount } from 'svelte';
    import { authStore } from '$lib/stores/auth';
    
    export let showFullAnalytics = false;
    
    let insights = [];
    let loading = true;
    let error = null;
    let predictiveData = null;
    let teamAnalytics = null;
    
    onMount(async () => {
        await loadInsights();
    });
    
    async function loadInsights() {
        try {
            loading = true;
            const headers = authStore.getAuthHeaders();
            
            // Load dashboard insights
            const insightsResponse = await fetch('/api/ai/insights/dashboard', {
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                }
            });
            
            if (insightsResponse.ok) {
                const insightsData = await insightsResponse.json();
                insights = insightsData.insights || [];
            }
            
            // Load team analytics if user has permissions
            if ($authStore.user?.role !== 'REPORTER') {
                const analyticsResponse = await fetch('/api/ai/team-analytics?days=14', {
                    headers: {
                        'Content-Type': 'application/json',
                        ...headers
                    }
                });
                
                if (analyticsResponse.ok) {
                    const analyticsData = await analyticsResponse.json();
                    teamAnalytics = analyticsData.analytics;
                }
            }
            
        } catch (err) {
            error = err.message;
            console.error('AI insights loading failed:', err);
        } finally {
            loading = false;
        }
    }
    
    function getInsightIcon(type) {
        const icons = {
            'warning': '⚠️',
            'info': 'ℹ️',
            'prediction': '🔮',
            'success': '✅',
            'error': '❌'
        };
        return icons[type] || '💡';
    }
    
    function getInsightClass(type) {
        const classes = {
            'warning': 'bg-yellow-50 border-yellow-200 text-yellow-800',
            'info': 'bg-blue-50 border-blue-200 text-blue-800',
            'prediction': 'bg-purple-50 border-purple-200 text-purple-800',
            'success': 'bg-green-50 border-green-200 text-green-800',
            'error': 'bg-red-50 border-red-200 text-red-800'
        };
        return classes[type] || 'bg-gray-50 border-gray-200 text-gray-800';
    }
    
    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }
</script>

<div class="space-y-6">
    <!-- AI Insights Header -->
    <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-sm">AI</span>
            </div>
            <div>
                <h3 class="text-lg font-semibold text-gray-900">AI Insights</h3>
                <p class="text-sm text-gray-600">Intelligent analysis and recommendations</p>
            </div>
        </div>
        <button 
            on:click={loadInsights}
            class="btn-outline"
            disabled={loading}
        >
            {#if loading}
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
            {/if}
            Refresh
        </button>
    </div>
    
    {#if loading}
        <div class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            <span class="ml-3 text-gray-600">Loading AI insights...</span>
        </div>
    {:else if error}
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-center">
                <span class="text-red-500 text-xl mr-3">⚠️</span>
                <div>
                    <h4 class="font-medium text-red-800">Unable to load AI insights</h4>
                    <p class="text-red-700 text-sm">{error}</p>
                </div>
            </div>
        </div>
    {:else}
        <!-- Main Insights Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Key Insights -->
            <div class="bg-white rounded-lg border border-gray-200 p-6">
                <h4 class="font-medium text-gray-900 mb-4 flex items-center">
                    <span class="mr-2">🧠</span>
                    Key Insights
                </h4>
                
                {#if insights.length > 0}
                    <div class="space-y-3">
                        {#each insights as insight}
                            <div class="border rounded-lg p-3 {getInsightClass(insight.type)}">
                                <div class="flex items-start space-x-3">
                                    <span class="text-lg">{getInsightIcon(insight.type)}</span>
                                    <div class="flex-1">
                                        <p class="text-sm font-medium">{insight.message}</p>
                                        {#if insight.recommendation}
                                            <p class="text-xs mt-1 opacity-80">💡 {insight.recommendation}</p>
                                        {/if}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="text-center py-6">
                        <span class="text-4xl mb-2 block">🎉</span>
                        <p class="text-gray-600 text-sm">All systems running smoothly!</p>
                        <p class="text-gray-500 text-xs">No critical insights at this time</p>
                    </div>
                {/if}
            </div>
            
            <!-- Team Performance Preview -->
            {#if teamAnalytics && $authStore.user?.role !== 'REPORTER'}
                <div class="bg-white rounded-lg border border-gray-200 p-6">
                    <h4 class="font-medium text-gray-900 mb-4 flex items-center">
                        <span class="mr-2">📊</span>
                        Team Performance
                    </h4>
                    
                    <div class="space-y-4">
                        <!-- Quick Stats -->
                        <div class="grid grid-cols-2 gap-4">
                            <div class="text-center p-3 bg-blue-50 rounded-lg">
                                <div class="text-lg font-bold text-blue-600">{teamAnalytics.total_issues || 0}</div>
                                <div class="text-xs text-blue-800">Total Issues</div>
                            </div>
                            <div class="text-center p-3 bg-green-50 rounded-lg">
                                <div class="text-lg font-bold text-green-600">
                                    {Math.round(((teamAnalytics.total_issues - teamAnalytics.open_issues || 0) / Math.max(teamAnalytics.total_issues, 1)) * 100)}%
                                </div>
                                <div class="text-xs text-green-800">Resolution Rate</div>
                            </div>
                        </div>
                        
                        <!-- Trends -->
                        {#if teamAnalytics.insights}
                            <div class="space-y-2">
                                {#each teamAnalytics.insights.slice(0, 3) as insight}
                                    <div class="text-sm p-2 bg-gray-50 rounded border-l-2 border-blue-400">
                                        {insight}
                                    </div>
                                {/each}
                            </div>
                        {/if}
                        
                        {#if showFullAnalytics}
                            <a href="/analytics" class="block w-full text-center py-2 text-blue-600 hover:text-blue-800 text-sm font-medium">
                                View Full Analytics →
                            </a>
                        {/if}
                    </div>
                </div>
            {/if}
        </div>
        
        <!-- Predictive Analytics Section -->
        {#if teamAnalytics?.predictions && $authStore.user?.role !== 'REPORTER'}
            <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200 p-6">
                <h4 class="font-medium text-purple-900 mb-4 flex items-center">
                    <span class="mr-2">🔮</span>
                    Predictive Analysis
                </h4>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-white rounded-lg p-4 border border-purple-200">
                        <div class="text-sm text-purple-600 font-medium">Next Week Forecast</div>
                        <div class="text-lg font-bold text-purple-900 mt-1">
                            {teamAnalytics.predictions.next_week_issues || 'N/A'} issues expected
                        </div>
                        <div class="text-xs text-purple-700 mt-1">
                            Based on current trends
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg p-4 border border-purple-200">
                        <div class="text-sm text-purple-600 font-medium">Bottleneck Risk</div>
                        <div class="text-lg font-bold text-purple-900 mt-1">
                            {teamAnalytics.predictions.bottleneck_risk || 'Low'}
                        </div>
                        <div class="text-xs text-purple-700 mt-1">
                            Workload distribution analysis
                        </div>
                    </div>
                    
                    <div class="bg-white rounded-lg p-4 border border-purple-200">
                        <div class="text-sm text-purple-600 font-medium">Recommended Action</div>
                        <div class="text-sm font-medium text-purple-900 mt-1">
                            {teamAnalytics.predictions.recommended_action || 'Continue monitoring'}
                        </div>
                        <div class="text-xs text-purple-700 mt-1">
                            AI recommendation
                        </div>
                    </div>
                </div>
            </div>
        {/if}
        
        <!-- Quick Actions -->
        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h4 class="font-medium text-gray-900 mb-4 flex items-center">
                <span class="mr-2">⚡</span>
                AI-Powered Actions
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                <button class="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <div class="text-lg mb-1">🎯</div>
                    <div class="text-sm font-medium text-gray-900">Smart Assignment</div>
                    <div class="text-xs text-gray-600">AI suggests best assignee</div>
                </button>
                
                <button class="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <div class="text-lg mb-1">⏰</div>
                    <div class="text-sm font-medium text-gray-900">Time Prediction</div>
                    <div class="text-xs text-gray-600">Estimate resolution time</div>
                </button>
                
                <button class="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <div class="text-lg mb-1">🚨</div>
                    <div class="text-sm font-medium text-gray-900">Escalation Check</div>
                    <div class="text-xs text-gray-600">Identify issues needing attention</div>
                </button>
                
                <button class="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <div class="text-lg mb-1">📋</div>
                    <div class="text-sm font-medium text-gray-900">Pattern Analysis</div>
                    <div class="text-xs text-gray-600">Detect trends and patterns</div>
                </button>
            </div>
        </div>
        
        <!-- AI Health Status -->
        <div class="bg-gray-50 rounded-lg border border-gray-200 p-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                    <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span class="text-sm text-gray-600">AI Services Status: Operational</span>
                </div>
                <div class="text-xs text-gray-500">
                    Last updated: {formatDate(new Date())}
                </div>
            </div>
        </div>
    {/if}
</div>
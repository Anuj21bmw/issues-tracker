// frontend/src/lib/components/ai/AIDashboardWidget.svelte
<script>
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
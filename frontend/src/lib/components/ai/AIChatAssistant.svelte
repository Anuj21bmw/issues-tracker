a// frontend/src/lib/components/ai/AIChatAssistant.svelte
<script>
    import { onMount, onDestroy } from 'svelte';
    import { authStore } from '$lib/stores/auth';
    import { toastStore } from '$lib/stores/toast';
    
    export let isOpen = false;
    
    let chatMessages = [];
    let userInput = '';
    let thinking = false;
    let conversationId = null;
    let chatContainer;
    let inputElement;
    
    // Pre-defined quick actions
    const quickActions = [
        { text: 'Show my issues', icon: '📋' },
        { text: 'Show open issues', icon: '🔴' },
        { text: 'Show critical issues', icon: '🚨' },
        { text: 'Team stats', icon: '📊' },
        { text: 'Help', icon: '❓' }
    ];
    
    onMount(() => {
        // Initialize conversation
        conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Add welcome message
        chatMessages = [{
            role: 'assistant',
            content: `Hi ${$authStore.user?.full_name}! 👋 I'm your AI assistant. I can help you with:
            
• Finding and managing issues
• Getting team statistics
• Analyzing trends and patterns
• Providing recommendations

What would you like to know?`,
            timestamp: new Date(),
            suggestions: quickActions.map(action => action.text)
        }];
    });
    
    onDestroy(() => {
        // Clean up any resources
    });
    
    async function sendMessage(message = null) {
        const messageText = message || userInput.trim();
        
        if (!messageText) return;
        
        // Add user message
        chatMessages = [...chatMessages, {
            role: 'user',
            content: messageText,
            timestamp: new Date()
        }];
        
        userInput = '';
        thinking = true;
        
        // Scroll to bottom
        setTimeout(scrollToBottom, 100);
        
        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...authStore.getAuthHeaders()
                },
                body: JSON.stringify({
                    message: messageText,
                    conversation_id: conversationId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const aiResponse = data.response;
                
                chatMessages = [...chatMessages, {
                    role: 'assistant',
                    content: aiResponse.message,
                    type: aiResponse.type || 'text',
                    data: aiResponse.data,
                    suggestions: aiResponse.suggestions || [],
                    timestamp: new Date()
                }];
            } else {
                throw new Error('AI service unavailable');
            }
        } catch (error) {
            console.error('Chat error:', error);
            chatMessages = [...chatMessages, {
                role: 'assistant',
                content: "I'm sorry, I'm having trouble processing your request right now. Please try again.",
                type: 'error',
                timestamp: new Date()
            }];
        } finally {
            thinking = false;
            setTimeout(scrollToBottom, 100);
        }
    }
    
    function scrollToBottom() {
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    function handleKeydown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }
    
    function clearChat() {
        chatMessages = chatMessages.slice(0, 1); // Keep welcome message
        conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    function formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Focus input when chat opens
    $: if (isOpen && inputElement) {
        setTimeout(() => inputElement.focus(), 100);
    }
</script>

{#if isOpen}
    <div class="fixed bottom-4 right-4 w-96 h-[32rem] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-t-lg">
            <div class="flex items-center space-x-2">
                <div class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                    <span class="text-lg">🤖</span>
                </div>
                <div>
                    <h3 class="font-semibold">AI Assistant</h3>
                    <p class="text-xs opacity-90">Always here to help</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button 
                    on:click={clearChat}
                    class="p-1 hover:bg-white/20 rounded"
                    title="Clear chat"
                >
                    🗑️
                </button>
                <button 
                    on:click={() => isOpen = false}
                    class="p-1 hover:bg-white/20 rounded"
                    title="Close chat"
                >
                    ✕
                </button>
            </div>
        </div>
        
        <!-- Messages Container -->
        <div 
            bind:this={chatContainer}
            class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50"
        >
            {#each chatMessages as message}
                <div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
                    <div class="max-w-[80%] {message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-white border border-gray-200'} rounded-lg p-3 shadow-sm">
                        <!-- Message Content -->
                        <div class="text-sm whitespace-pre-wrap">{message.content}</div>
                        
                        <!-- Data Display -->
                        {#if message.data && Array.isArray(message.data)}
                            <div class="mt-2 space-y-1">
                                {#each message.data.slice(0, 5) as item}
                                    <div class="text-xs bg-gray-100 p-2 rounded border">
                                        <div class="font-medium">#{item.id} {item.title}</div>
                                        {#if item.severity}
                                            <span class="inline-block px-1 py-0.5 text-xs rounded {item.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' : item.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' : 'bg-yellow-100 text-yellow-800'}">{item.severity}</span>
                                        {/if}
                                        {#if item.status}
                                            <span class="inline-block px-1 py-0.5 text-xs rounded bg-blue-100 text-blue-800 ml-1">{item.status}</span>
                                        {/if}
                                    </div>
                                {/each}
                                {#if message.data.length > 5}
                                    <div class="text-xs text-gray-500">...and {message.data.length - 5} more</div>
                                {/if}
                            </div>
                        {/if}
                        
                        <!-- Suggestions -->
                        {#if message.suggestions && message.suggestions.length > 0}
                            <div class="mt-2 flex flex-wrap gap-1">
                                {#each message.suggestions.slice(0, 3) as suggestion}
                                    <button 
                                        on:click={() => sendMessage(suggestion)}
                                        class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                                    >
                                        {suggestion}
                                    </button>
                                {/each}
                            </div>
                        {/if}
                        
                        <!-- Timestamp -->
                        <div class="text-xs opacity-50 mt-1">
                            {formatTimestamp(message.timestamp)}
                        </div>
                    </div>
                </div>
            {/each}
            
            <!-- Thinking Indicator -->
            {#if thinking}
                <div class="flex justify-start">
                    <div class="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
                        <div class="flex items-center space-x-2">
                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                            <span class="text-sm text-gray-600">AI is thinking...</span>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
        
        <!-- Quick Actions -->
        <div class="p-2 border-t border-gray-200 bg-white">
            <div class="flex flex-wrap gap-1 mb-2">
                {#each quickActions.slice(0, 4) as action}
                    <button 
                        on:click={() => sendMessage(action.text)}
                        class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors flex items-center space-x-1"
                        disabled={thinking}
                    >
                        <span>{action.icon}</span>
                        <span>{action.text}</span>
                    </button>
                {/each}
            </div>
        </div>
        
        <!-- Input Area -->
        <div class="p-3 border-t border-gray-200 bg-white rounded-b-lg">
            <div class="flex space-x-2">
                <input
                    bind:this={inputElement}
                    bind:value={userInput}
                    on:keydown={handleKeydown}
                    placeholder="Ask me anything about your issues..."
                    class="flex-1 text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={thinking}
                />
                <button
                    on:click={() => sendMessage()}
                    disabled={thinking || !userInput.trim()}
                    class="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    <span class="text-sm">Send</span>
                </button>
            </div>
        </div>
    </div>
{/if}

<!-- Chat Toggle Button -->
{#if !isOpen}
    <button
        on:click={() => isOpen = true}
        class="fixed bottom-4 right-4 w-14 h-14 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-40"
        title="Open AI Assistant"
    >
        <span class="text-2xl">🤖</span>
    </button>
{/if}

<style>
    /* Custom scrollbar for chat */
    .overflow-y-auto::-webkit-scrollbar {
        width: 4px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    .overflow-y-auto::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 2px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
<script>
	import { authStore } from '$lib/stores/auth';
	
	export let toggleSidebar;
	
	let showUserMenu = false;
	
	function handleLogout() {
		authStore.logout();
		showUserMenu = false;
	}

	function handleKeydown(event) {
		if (event.key === 'Escape') {
			showUserMenu = false;
		}
	}
</script>

<nav class="bg-white shadow-sm border-b border-gray-200 fixed w-full z-50">
	<div class="px-4 sm:px-6 lg:px-8">
		<div class="flex justify-between h-16">
			<div class="flex items-center">
				<button
					on:click={toggleSidebar}
					class="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 lg:hidden"
					aria-label="Toggle sidebar"
				>
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				
				<div class="flex-shrink-0 flex items-center ml-4 lg:ml-0">
					<h1 class="text-xl font-bold text-blue-600">
						Issues & Insights Tracker
					</h1>
				</div>
			</div>

			<div class="flex items-center space-x-4">
				<div class="relative">
					<button
						on:click={() => showUserMenu = !showUserMenu}
						on:keydown={handleKeydown}
						class="flex items-center space-x-3 p-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
						aria-expanded={showUserMenu}
						aria-haspopup="true"
					>
						<div class="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
							<span class="text-sm font-medium text-blue-600">
								{$authStore.user?.full_name?.charAt(0) || 'U'}
							</span>
						</div>
						<span class="hidden md:block text-sm font-medium">
							{$authStore.user?.full_name || 'User'}
						</span>
					</button>

					{#if showUserMenu}
						<div class="absolute right-0 mt-2 w-48 rounded-lg shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50" role="menu">
							<div class="py-1">
								<div class="px-4 py-2 text-sm text-gray-700 border-b border-gray-200">
									<div class="font-medium">{$authStore.user?.full_name}</div>
									<div class="text-xs text-gray-500">{$authStore.user?.email}</div>
									<div class="text-xs text-gray-500 mt-1">
										<span class="badge badge-info">
											{$authStore.user?.role}
										</span>
									</div>
								</div>
								
								<button
									on:click={handleLogout}
									class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
									role="menuitem"
								>
									<svg class="h-4 w-4 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
									</svg>
									Sign out
								</button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</nav>

{#if showUserMenu}
	<button 
		class="fixed inset-0 z-40" 
		on:click={() => showUserMenu = false}
		on:keydown={(e) => e.key === 'Escape' && (showUserMenu = false)}
		aria-label="Close menu"
	></button>
{/if}
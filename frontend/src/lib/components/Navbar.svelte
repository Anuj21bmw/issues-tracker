<script>
	import { authStore } from '$lib/stores/auth';
	import { Menu, Sun, Moon, Bell, User, LogOut } from 'lucide-svelte';
	
	export let darkMode;
	export let toggleTheme;
	export let toggleSidebar;
	
	let showUserMenu = false;
	
	function handleLogout() {
		authStore.logout();
		showUserMenu = false;
	}
</script>

<nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 fixed w-full z-50">
	<div class="px-4 sm:px-6 lg:px-8">
		<div class="flex justify-between h-16">
			<div class="flex items-center">
				<button
					on:click={toggleSidebar}
					class="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 lg:hidden"
				>
					<Menu class="h-6 w-6" />
				</button>
				
				<div class="flex-shrink-0 flex items-center ml-4 lg:ml-0">
					<h1 class="text-xl font-bold text-gray-900 dark:text-white">
						Issues & Insights Tracker
					</h1>
				</div>
			</div>

			<div class="flex items-center space-x-4">
				<!-- Theme toggle -->
				<button
					on:click={toggleTheme}
					class="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
				>
					{#if darkMode}
						<Sun class="h-5 w-5" />
					{:else}
						<Moon class="h-5 w-5" />
					{/if}
				</button>

				<!-- Notifications -->
				<button class="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative">
					<Bell class="h-5 w-5" />
					<span class="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-400"></span>
				</button>

				<!-- User menu -->
				<div class="relative">
					<button
						on:click={() => showUserMenu = !showUserMenu}
						class="flex items-center space-x-3 p-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					>
						<User class="h-5 w-5" />
						<span class="hidden md:block text-sm font-medium">
							{$authStore.user?.full_name || 'User'}
						</span>
					</button>

					{#if showUserMenu}
						<div class="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 z-50">
							<div class="py-1">
								<div class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-700">
									<div class="font-medium">{$authStore.user?.full_name}</div>
									<div class="text-xs text-gray-500">{$authStore.user?.email}</div>
									<div class="text-xs text-gray-500 mt-1">
										<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
											{$authStore.user?.role}
										</span>
									</div>
								</div>
								
								<button
									on:click={handleLogout}
									class="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
								>
									<LogOut class="h-4 w-4 mr-3" />
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

<!-- Click outside to close user menu -->
{#if showUserMenu}
	<div class="fixed inset-0 z-40" on:click={() => showUserMenu = false}></div>
{/if}
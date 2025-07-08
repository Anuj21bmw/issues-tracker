<script>
	import { authStore } from '$lib/stores/auth';
	import { Eye, EyeOff, Mail, Lock, LogIn } from 'lucide-svelte';
	
	let email = '';
	let password = '';
	let showPassword = false;
	
	async function handleSubmit() {
		if (!email || !password) return;
		await authStore.login(email, password);
	}
	
	function handleKeydown(event) {
		if (event.key === 'Enter') {
			handleSubmit();
		}
	}
</script>

<svelte:head>
	<title>Login - Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div class="text-center">
			<div class="mx-auto h-12 w-12 bg-primary-600 rounded-xl flex items-center justify-center">
				<LogIn class="h-6 w-6 text-white" />
			</div>
			<h2 class="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
				Sign in to your account
			</h2>
			<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
				Or 
				<a href="/auth/register" class="font-medium text-primary-600 hover:text-primary-500 transition-colors">
					create a new account
				</a>
			</p>
		</div>

		<div class="card p-8">
			<form on:submit|preventDefault={handleSubmit} class="space-y-6">
				<div>
					<label for="email" class="label">Email address</label>
					<div class="mt-1 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<Mail class="h-5 w-5 text-gray-400" />
						</div>
						<input
							id="email"
							name="email"
							type="email"
							autocomplete="email"
							required
							bind:value={email}
							on:keydown={handleKeydown}
							class="input pl-10"
							placeholder="Enter your email"
						/>
					</div>
				</div>

				<div>
					<label for="password" class="label">Password</label>
					<div class="mt-1 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<Lock class="h-5 w-5 text-gray-400" />
						</div>
						<input
							id="password"
							name="password"
							type={showPassword ? 'text' : 'password'}
							autocomplete="current-password"
							required
							bind:value={password}
							on:keydown={handleKeydown}
							class="input pl-10 pr-10"
							placeholder="Enter your password"
						/>
						<button
							type="button"
							class="absolute inset-y-0 right-0 pr-3 flex items-center"
							on:click={() => showPassword = !showPassword}
						>
							{#if showPassword}
								<EyeOff class="h-5 w-5 text-gray-400 hover:text-gray-500" />
							{:else}
								<Eye class="h-5 w-5 text-gray-400 hover:text-gray-500" />
							{/if}
						</button>
					</div>
				</div>

				<div class="flex items-center justify-between">
					<div class="flex items-center">
						<input
							id="remember-me"
							name="remember-me"
							type="checkbox"
							class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
						/>
						<label for="remember-me" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">
							Remember me
						</label>
					</div>

					<div class="text-sm">
						<a href="/auth/forgot-password" class="font-medium text-primary-600 hover:text-primary-500 transition-colors">
							Forgot your password?
						</a>
					</div>
				</div>

				<div>
					<button
						type="submit"
						disabled={$authStore.loading || !email || !password}
						class="btn-primary w-full flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{#if $authStore.loading}
							<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
							Signing in...
						{:else}
							<LogIn class="h-4 w-4 mr-2" />
							Sign in
						{/if}
					</button>
				</div>

				<!-- Demo accounts -->
				<div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
					<h3 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Demo Accounts:</h3>
					<div class="space-y-1 text-xs text-gray-600 dark:text-gray-400">
						<div><strong>Admin:</strong> admin@example.com / admin123</div>
						<div><strong>Maintainer:</strong> maintainer@example.com / maintainer123</div>
						<div><strong>Reporter:</strong> reporter@example.com / reporter123</div>
					</div>
				</div>
			</form>
		</div>
	</div>
</div>
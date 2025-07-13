<script>
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';
	
	let email = '';
	let password = '';
	let passwordElement;
	
	async function handleSubmit() {
		if (!email || !password) {
			toastStore.add({
				type: 'error',
				message: 'Please fill in all fields'
			});
			return;
		}

		try {
			await authStore.login(email, password);
			toastStore.add({
				type: 'success',
				message: 'Login successful!'
			});
		} catch (error) {
			toastStore.add({
				type: 'error',
				message: error.message
			});
		}
	}
	
	function quickLogin(role) {
		const accounts = {
			admin: { email: 'admin@example.com', password: 'admin123' },
			maintainer: { email: 'maintainer@example.com', password: 'maintainer123' },
			reporter: { email: 'reporter@example.com', password: 'reporter123' }
		};
		
		const account = accounts[role];
		email = account.email;
		password = account.password;
		handleSubmit();
	}

	function togglePasswordVisibility() {
		if (passwordElement) {
			const currentType = passwordElement.type;
			passwordElement.type = currentType === 'password' ? 'text' : 'password';
		}
	}
</script>

<svelte:head>
	<title>Login - Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div class="text-center">
			<div class="mx-auto h-12 w-12 bg-blue-600 rounded-xl flex items-center justify-center">
				<svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m0 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
				</svg>
			</div>
			<h2 class="mt-6 text-3xl font-bold text-gray-900">
				Sign in to your account
			</h2>
			<p class="mt-2 text-sm text-gray-600">
				Or 
				<a href="/auth/register" class="font-medium text-blue-600 hover:text-blue-500 transition-colors">
					create a new account
				</a>
			</p>
		</div>

		<div class="card">
			<form on:submit|preventDefault={handleSubmit} class="space-y-6">
				<div>
					<label for="email" class="label">Email address</label>
					<input
						id="email"
						name="email"
						type="email"
						autocomplete="email"
						required
						bind:value={email}
						class="input"
						placeholder="Enter your email"
					/>
				</div>

				<div>
					<label for="password" class="label">Password</label>
					<div class="relative">
						<input
							bind:this={passwordElement}
							id="password"
							name="password"
							type="password"
							autocomplete="current-password"
							required
							bind:value={password}
							class="input pr-10"
							placeholder="Enter your password"
						/>
						<button
							type="button"
							class="absolute inset-y-0 right-0 pr-3 flex items-center"
							on:click={togglePasswordVisibility}
							aria-label="Toggle password visibility"
						>
							<svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
							</svg>
						</button>
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
							Sign in
						{/if}
					</button>
				</div>

				<div class="mt-6 p-4 bg-blue-50 rounded-lg">
					<h3 class="text-sm font-medium text-blue-900 mb-3">Demo Accounts:</h3>
					<div class="space-y-2">
						<button
							type="button"
							on:click={() => quickLogin('admin')}
							class="w-full text-left p-2 text-xs bg-white rounded border hover:bg-gray-50 transition-colors"
						>
							<strong class="text-blue-600">Admin:</strong> admin@example.com / admin123
						</button>
						<button
							type="button"
							on:click={() => quickLogin('maintainer')}
							class="w-full text-left p-2 text-xs bg-white rounded border hover:bg-gray-50 transition-colors"
						>
							<strong class="text-indigo-600">Maintainer:</strong> maintainer@example.com / maintainer123
						</button>
						<button
							type="button"
							on:click={() => quickLogin('reporter')}
							class="w-full text-left p-2 text-xs bg-white rounded border hover:bg-gray-50 transition-colors"
						>
							<strong class="text-green-600">Reporter:</strong> reporter@example.com / reporter123
						</button>
					</div>
				</div>
			</form>
		</div>
	</div>
</div>
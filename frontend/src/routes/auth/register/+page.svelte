<script>
	import { authStore } from '$lib/stores/auth';
	import { Eye, EyeOff, Mail, Lock, User, UserPlus } from 'lucide-svelte';
	
	let email = '';
	let password = '';
	let confirmPassword = '';
	let fullName = '';
	let showPassword = false;
	let showConfirmPassword = false;
	
	$: passwordsMatch = password === confirmPassword;
	$: isValid = email && password && fullName && passwordsMatch && password.length >= 6;
	
	async function handleSubmit() {
		if (!isValid) return;
		
		await authStore.register({
			email,
			password,
			full_name: fullName,
			role: 'REPORTER'
		});
	}
	
	function handleKeydown(event) {
		if (event.key === 'Enter' && isValid) {
			handleSubmit();
		}
	}
</script>

<svelte:head>
	<title>Register - Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div class="text-center">
			<div class="mx-auto h-12 w-12 bg-primary-600 rounded-xl flex items-center justify-center">
				<UserPlus class="h-6 w-6 text-white" />
			</div>
			<h2 class="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
				Create your account
			</h2>
			<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
				Or 
				<a href="/auth/login" class="font-medium text-primary-600 hover:text-primary-500 transition-colors">
					sign in to your existing account
				</a>
			</p>
		</div>

		<div class="card p-8">
			<form on:submit|preventDefault={handleSubmit} class="space-y-6">
				<div>
					<label for="fullName" class="label">Full name</label>
					<div class="mt-1 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<User class="h-5 w-5 text-gray-400" />
						</div>
						<input
							id="fullName"
							name="fullName"
							type="text"
							autocomplete="name"
							required
							bind:value={fullName}
							on:keydown={handleKeydown}
							class="input pl-10"
							placeholder="Enter your full name"
						/>
					</div>
				</div>

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
							autocomplete="new-password"
							required
							bind:value={password}
							on:keydown={handleKeydown}
							class="input pl-10 pr-10"
							placeholder="Create a password"
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
					{#if password && password.length < 6}
						<p class="mt-1 text-sm text-red-600 dark:text-red-400">
							Password must be at least 6 characters long
						</p>
					{/if}
				</div>

				<div>
					<label for="confirmPassword" class="label">Confirm password</label>
					<div class="mt-1 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<Lock class="h-5 w-5 text-gray-400" />
						</div>
						<input
							id="confirmPassword"
							name="confirmPassword"
							type={showConfirmPassword ? 'text' : 'password'}
							autocomplete="new-password"
							required
							bind:value={confirmPassword}
							on:keydown={handleKeydown}
							class="input pl-10 pr-10"
							placeholder="Confirm your password"
						/>
						<button
							type="button"
							class="absolute inset-y-0 right-0 pr-3 flex items-center"
							on:click={() => showConfirmPassword = !showConfirmPassword}
						>
							{#if showConfirmPassword}
								<EyeOff class="h-5 w-5 text-gray-400 hover:text-gray-500" />
							{:else}
								<Eye class="h-5 w-5 text-gray-400 hover:text-gray-500" />
							{/if}
						</button>
					</div>
					{#if confirmPassword && !passwordsMatch}
						<p class="mt-1 text-sm text-red-600 dark:text-red-400">
							Passwords do not match
						</p>
					{/if}
				</div>

				<div>
					<button
						type="submit"
						disabled={$authStore.loading || !isValid}
						class="btn-primary w-full flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{#if $authStore.loading}
							<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
							Creating account...
						{:else}
							<UserPlus class="h-4 w-4 mr-2" />
							Create account
						{/if}
					</button>
				</div>

				<div class="text-xs text-gray-500 dark:text-gray-400 text-center">
					By creating an account, you agree to our Terms of Service and Privacy Policy.
				</div>
			</form>
		</div>
	</div>
</div>
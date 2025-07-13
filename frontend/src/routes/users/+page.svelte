<script>
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';

	let users = [];
	let loading = true;
	let error = null;
	let showCreateModal = false;
	let showEditModal = false;
	let selectedUser = null;

	// Form data
	let newUser = {
		email: '',
		full_name: '',
		role: 'REPORTER',
		password: ''
	};

	let editUser = {
		id: null,
		full_name: '',
		role: 'REPORTER',
		is_active: true
	};

	onMount(async () => {
		if ($authStore.user?.role !== 'ADMIN') {
			toastStore.add({
				type: 'error',
				message: 'Access denied. Admin role required.'
			});
			return;
		}
		await loadUsers();
	});

	async function loadUsers() {
		try {
			loading = true;
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch('http://localhost:8000/api/auth/users', {
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (!response.ok) {
				if (response.status === 401) {
					authStore.logout();
					return;
				}
				throw new Error('Failed to load users');
			}

			users = await response.json();
		} catch (err) {
			error = err.message;
			console.error('Error loading users:', err);
		} finally {
			loading = false;
		}
	}

	async function createUser() {
		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch('http://localhost:8000/api/auth/register', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					...headers
				},
				body: JSON.stringify(newUser)
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Failed to create user');
			}

			toastStore.add({
				type: 'success',
				message: 'User created successfully!'
			});

			showCreateModal = false;
			newUser = { email: '', full_name: '', role: 'REPORTER', password: '' };
			await loadUsers();
		} catch (err) {
			toastStore.add({
				type: 'error',
				message: err.message
			});
		}
	}

	async function updateUser() {
		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch(`http://localhost:8000/api/auth/users/${editUser.id}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					...headers
				},
				body: JSON.stringify({
					full_name: editUser.full_name,
					role: editUser.role,
					is_active: editUser.is_active
				})
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Failed to update user');
			}

			toastStore.add({
				type: 'success',
				message: 'User updated successfully!'
			});

			showEditModal = false;
			await loadUsers();
		} catch (err) {
			toastStore.add({
				type: 'error',
				message: err.message
			});
		}
	}

	async function deleteUser(userId, userName) {
		if (!confirm(`Are you sure you want to delete user "${userName}"?`)) {
			return;
		}

		try {
			const headers = authStore.getAuthHeaders();
			
			const response = await fetch(`http://localhost:8000/api/auth/users/${userId}`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json',
					...headers
				}
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || 'Failed to delete user');
			}

			toastStore.add({
				type: 'success',
				message: 'User deleted successfully!'
			});

			await loadUsers();
		} catch (err) {
			toastStore.add({
				type: 'error',
				message: err.message
			});
		}
	}

	function openEditModal(user) {
		editUser = {
			id: user.id,
			full_name: user.full_name,
			role: user.role,
			is_active: user.is_active
		};
		showEditModal = true;
	}

	function getRoleColor(role) {
		const colors = {
			ADMIN: 'bg-red-100 text-red-800',
			MAINTAINER: 'bg-blue-100 text-blue-800',
			REPORTER: 'bg-green-100 text-green-800'
		};
		return colors[role] || 'bg-gray-100 text-gray-800';
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}
</script>

<svelte:head>
	<title>Users - Issues & Insights Tracker</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">User Management</h1>
			<p class="mt-2 text-gray-600">Manage user accounts and permissions</p>
		</div>
		<div class="flex items-center space-x-3">
			<button on:click={() => showCreateModal = true} class="btn-primary">
				➕ Create User
			</button>
		</div>
	</div>

	{#if $authStore.user?.role !== 'ADMIN'}
		<div class="card">
			<div class="text-center">
				<div class="text-red-500 text-6xl mb-4">🚫</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
				<p class="text-gray-600">You need admin privileges to access this page.</p>
			</div>
		</div>
	{:else if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			<span class="ml-3 text-gray-600">Loading users...</span>
		</div>
	{:else if error}
		<div class="card">
			<div class="text-center">
				<div class="text-red-500 text-6xl mb-4">⚠️</div>
				<h3 class="text-lg font-medium text-gray-900 mb-2">Error Loading Users</h3>
				<p class="text-gray-600 mb-4">{error}</p>
				<button on:click={loadUsers} class="btn-primary">Try Again</button>
			</div>
		</div>
	{:else}
		<!-- Users Table -->
		<div class="card overflow-hidden">
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
							<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each users as user}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										<div class="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
											<span class="text-sm font-medium text-blue-600">
												{user.full_name.charAt(0)}
											</span>
										</div>
										<div class="ml-4">
											<div class="text-sm font-medium text-gray-900">
												{user.full_name}
											</div>
											<div class="text-sm text-gray-500">
												{user.email}
											</div>
										</div>
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="badge {getRoleColor(user.role)}">
										{user.role}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="badge {user.is_active ? 'badge-success' : 'badge-danger'}">
										{user.is_active ? 'Active' : 'Inactive'}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{formatDate(user.created_at)}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
									<div class="flex items-center justify-end space-x-2">
										<button 
											on:click={() => openEditModal(user)}
											class="text-blue-600 hover:text-blue-900"
										>
											Edit
										</button>
										{#if user.id !== $authStore.user?.id}
											<button 
												on:click={() => deleteUser(user.id, user.full_name)}
												class="text-red-600 hover:text-red-900"
											>
												Delete
											</button>
										{/if}
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div>

<!-- Create User Modal -->
{#if showCreateModal}
	<div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
		<div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
			<div class="mt-3">
				<h3 class="text-lg font-medium text-gray-900 mb-4">Create New User</h3>
				<form on:submit|preventDefault={createUser} class="space-y-4">
					<div>
						<label class="label">Full Name</label>
						<input
							type="text"
							bind:value={newUser.full_name}
							required
							class="input"
							placeholder="Enter full name"
						/>
					</div>
					<div>
						<label class="label">Email</label>
						<input
							type="email"
							bind:value={newUser.email}
							required
							class="input"
							placeholder="Enter email address"
						/>
					</div>
					<div>
						<label class="label">Password</label>
						<input
							type="password"
							bind:value={newUser.password}
							required
							class="input"
							placeholder="Enter password"
						/>
					</div>
					<div>
						<label class="label">Role</label>
						<select bind:value={newUser.role} class="input">
							<option value="REPORTER">Reporter</option>
							<option value="MAINTAINER">Maintainer</option>
							<option value="ADMIN">Admin</option>
						</select>
					</div>
					<div class="flex items-center justify-end space-x-3 pt-4">
						<button 
							type="button" 
							on:click={() => showCreateModal = false}
							class="btn-outline"
						>
							Cancel
						</button>
						<button type="submit" class="btn-primary">
							Create User
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Edit User Modal -->
{#if showEditModal}
	<div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
		<div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
			<div class="mt-3">
				<h3 class="text-lg font-medium text-gray-900 mb-4">Edit User</h3>
				<form on:submit|preventDefault={updateUser} class="space-y-4">
					<div>
						<label class="label">Full Name</label>
						<input
							type="text"
							bind:value={editUser.full_name}
							required
							class="input"
						/>
					</div>
					<div>
						<label class="label">Role</label>
						<select bind:value={editUser.role} class="input">
							<option value="REPORTER">Reporter</option>
							<option value="MAINTAINER">Maintainer</option>
							<option value="ADMIN">Admin</option>
						</select>
					</div>
					<div>
						<label class="flex items-center">
							<input
								type="checkbox"
								bind:checked={editUser.is_active}
								class="mr-2"
							/>
							Active User
						</label>
					</div>
					<div class="flex items-center justify-end space-x-3 pt-4">
						<button 
							type="button" 
							on:click={() => showEditModal = false}
							class="btn-outline"
						>
							Cancel
						</button>
						<button type="submit" class="btn-primary">
							Update User
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}
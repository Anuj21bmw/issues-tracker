<script>
	import { onMount } from 'svelte';
	import { toastStore } from '$lib/stores/toast';
	import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-svelte';
	
	export let toast;
	
	let toastElement;
	let visible = false;
	
	onMount(() => {
		// Animate in
		setTimeout(() => {
			visible = true;
		}, 50);
	});
	
	function getIcon(type) {
		switch (type) {
			case 'success':
				return CheckCircle;
			case 'error':
				return AlertCircle;
			case 'warning':
				return AlertTriangle;
			default:
				return Info;
		}
	}
	
	function getColorClasses(type) {
		switch (type) {
			case 'success':
				return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200';
			case 'error':
				return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200';
			case 'warning':
				return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200';
			default:
				return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200';
		}
	}
	
	function handleClose() {
		visible = false;
		setTimeout(() => {
			toastStore.remove(toast.id);
		}, 300);
	}
</script>

<div 
	bind:this={toastElement}
	class="fixed top-4 right-4 z-50 max-w-sm w-full transform transition-all duration-300 ease-in-out {
		visible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
	}"
>
	<div class="rounded-lg border shadow-lg p-4 {getColorClasses(toast.type)}">
		<div class="flex items-start">
			<div class="flex-shrink-0">
				<svelte:component this={getIcon(toast.type)} class="h-5 w-5" />
			</div>
			<div class="ml-3 flex-1">
				<p class="text-sm font-medium">
					{toast.message}
				</p>
			</div>
			<div class="ml-4 flex-shrink-0">
				<button
					on:click={handleClose}
					class="inline-flex rounded-md p-1.5 hover:bg-black hover:bg-opacity-10 transition-colors"
				>
					<X class="h-4 w-4" />
				</button>
			</div>
		</div>
	</div>
</div>
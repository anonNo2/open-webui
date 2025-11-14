<script lang="ts">
	import { getContext, onMount } from 'svelte';
	const i18n = getContext('i18n');

	import Switch from '$lib/components/common/Switch.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	// Default values for permissions
	const defaultPermissions = {
		workspace: {
			models: false,
			knowledge: false,
			prompts: false,
			tools: false
		},
		chat: {
			controls: true,
			delete: true,
			edit: true,
			temporary: true,
			file_upload: true
		},
		// MARK 添加TAG
		features: {
			web_search: true,
			image_generation: true,
			code_interpreter: true,
			knowledge_base: true,
			deep_web_search: true,
			deep_research: true,
			draw_up: true
		}
	};

	export let permissions = {};

	// Reactive statement to ensure all fields are present in `permissions`
	$: {
		permissions = fillMissingProperties(permissions, defaultPermissions);
	}

	function fillMissingProperties(obj: any, defaults: any) {
		return {
			...defaults,
			...obj,
			workspace: { ...defaults.workspace, ...obj.workspace },
			chat: { ...defaults.chat, ...obj.chat },
			features: { ...defaults.features, ...obj.features }
		};
	}

	onMount(() => {
		permissions = fillMissingProperties(permissions, defaultPermissions);
	});
</script>

<div>
	

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Workspace Permissions')}</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Models Access')}
			</div>
			<Switch bind:state={permissions.workspace.models} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Knowledge Access')}
			</div>
			<Switch bind:state={permissions.workspace.knowledge} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Prompts Access')}
			</div>
			<Switch bind:state={permissions.workspace.prompts} />
		</div>

		<div class=" ">
			<Tooltip
				className=" flex w-full justify-between my-2 pr-2"
				content={$i18n.t(
					'Warning: Enabling this will allow users to upload arbitrary code on the server.'
				)}
				placement="top-start"
			>
				<div class=" self-center text-xs font-medium">
					{$i18n.t('Tools Access')}
				</div>
				<Switch bind:state={permissions.workspace.tools} />
			</Tooltip>
		</div>
	</div>

	<hr class=" border-gray-100 dark:border-gray-850 my-2" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Chat Permissions')}</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat Controls')}
			</div>

			<Switch bind:state={permissions.chat.controls} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow File Upload')}
			</div>

			<Switch bind:state={permissions.chat.file_upload} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat Delete')}
			</div>

			<Switch bind:state={permissions.chat.delete} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat Edit')}
			</div>

			<Switch bind:state={permissions.chat.edit} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Temporary Chat')}
			</div>

			<Switch bind:state={permissions.chat.temporary} />
		</div>
	</div>

	<hr class=" border-gray-100 dark:border-gray-850 my-2" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Features Permissions')}</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Web Search')}
			</div>

			<Switch bind:state={permissions.features.web_search} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Image Generation')}
			</div>

			<Switch bind:state={permissions.features.image_generation} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Code Interpreter')}
			</div>

			<Switch bind:state={permissions.features.code_interpreter} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Knowledge Base')}
			</div>

			<Switch bind:state={permissions.features.knowledge_base} />
		</div>

		<!-- MARK 添加TAG -->
		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Deep Web Search')}
			</div>

			<Switch bind:state={permissions.features.deep_web_search} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Deep Research')}
			</div>

			<Switch bind:state={permissions.features.deep_research} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Draw Up')}
			</div>

			<Switch bind:state={permissions.features.draw_up} />
		</div>
	</div>
</div>

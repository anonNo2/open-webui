<script>
	import { marked } from 'marked';
	import { replaceTokens, processResponseContent } from '$lib/utils';
	import { user } from '$lib/stores';

	import markedExtension from '$lib/utils/marked/extension';
	import markedKatexExtension from '$lib/utils/marked/katex-extension';

	import MarkdownTokens from './Markdown/MarkdownTokens.svelte';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let id;
	export let content;
	export let model = null;
	export let save = false;

	export let sourceIds = [];

	export let onSourceClick = () => {};
	export let onTaskClick = () => {};

	let tokens = [];

	const options = {
		throwOnError: false
	};

	marked.use(markedKatexExtension(options));
	marked.use(markedExtension(options));

	// 彻底禁用 marked 的删除线语法，保留所有 ~，并添加调试信息
	marked.setOptions({ gfm: false });
	marked.use({
		extensions: [
			{
				name: 'strikethrough',
				level: 'inline',
				start(src) {
					const match = src.match(/~+/);
					if (match) {
						console.log('[DEBUG] [CUSTOM] strikethrough start matched:', match[0], 'at', match.index, 'in', src);
					}
					return undefined; // 永远不匹配
				},
				tokenizer(src) {
					const match = src.match(/~+/);
					if (match) {
						console.log('[DEBUG] [CUSTOM] strikethrough tokenizer matched:', match[0], 'in', src);
					}
					return undefined; // 永远不处理
				},
				renderer(token) {
					console.log('[DEBUG] [CUSTOM] strikethrough renderer called:', token);
					return token.raw;
				}
			}
		]
	});

	$: (async () => {
		if (content) {
			tokens = marked.lexer(
				replaceTokens(processResponseContent(content), sourceIds, model?.name, $user?.name)
			);
		}
	})();
</script>

{#key id}
	<MarkdownTokens
		{tokens}
		{id}
		{save}
		{onTaskClick}
		{onSourceClick}
		on:update={(e) => {
			dispatch('update', e.detail);
		}}
		on:code={(e) => {
			dispatch('code', e.detail);
		}}
	/>
{/key}

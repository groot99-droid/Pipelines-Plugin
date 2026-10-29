// Shape of overlay.json (written by `ve overlay --engine remotion`). Times are seconds on the overlay's own clock.
export type TitleItem = {type: 'title'; text: string; start: number; end: number};
export type CaptionPage = {text: string; start: number; end: number};
export type CaptionsItem = {type: 'captions'; pages: CaptionPage[]};
export type Item = TitleItem | CaptionsItem;

export type OverlayProps = {
	width: number;
	height: number;
	fps: number;
	durationSeconds: number;
	// 'transparent' renders only the items (render as WebM with alpha); otherwise a CSS colour fills the frame.
	background: string;
	color: string;
	accent: string;
	// Must be installed on the machine rendering; the composition throws if the browser cannot use it.
	fontFamily: string;
	items: Item[];
};

export const defaultProps: OverlayProps = {
	width: 1920,
	height: 1080,
	fps: 30,
	durationSeconds: 3,
	background: '#0a0a0a',
	color: '#ffffff',
	accent: '#ff5a00',
	fontFamily: 'DejaVu Sans Mono',
	items: [{type: 'title', text: 'Title', start: 0, end: 3}],
};

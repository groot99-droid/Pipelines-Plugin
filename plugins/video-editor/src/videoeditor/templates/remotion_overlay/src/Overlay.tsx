import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CaptionPage, OverlayProps, TitleItem} from './types';

// Never linear: slow landing on reveals, symmetrical on holds.
const easeOut = Easing.out(Easing.cubic);

const Title: React.FC<{item: TitleItem; props: OverlayProps}> = ({item, props}) => {
	const frame = useCurrentFrame();
	const {fps, height} = useVideoConfig();
	const t = frame / fps;
	if (t < item.start || t >= item.end) return null;
	const reveal = Math.min(0.6, (item.end - item.start) / 2);
	const p = interpolate(t, [item.start, item.start + reveal], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
		easing: easeOut,
	});
	return (
		<AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
			<div
				style={{
					color: props.accent,
					fontFamily: props.fontFamily,
					fontWeight: 700,
					fontSize: Math.round(height * 0.07),
					opacity: p,
					transform: `translateY(${(1 - p) * 40}px)`,
				}}
			>
				{item.text}
			</div>
		</AbsoluteFill>
	);
};

const Captions: React.FC<{pages: CaptionPage[]; props: OverlayProps}> = ({pages, props}) => {
	const frame = useCurrentFrame();
	const {fps, height} = useVideoConfig();
	const t = frame / fps;
	const page = pages.find((p) => t >= p.start && t < p.end);
	if (!page) return null;
	return (
		<AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: Math.round(height * 0.3)}}>
			<div
				style={{
					color: props.color,
					fontFamily: props.fontFamily,
					fontWeight: 800,
					fontSize: Math.round(height * 0.05),
					textTransform: 'uppercase',
					textShadow: '0 0 12px rgba(0,0,0,0.9)',
					textAlign: 'center',
					maxWidth: '85%',
				}}
			>
				{page.text}
			</div>
		</AbsoluteFill>
	);
};

// document.fonts.check() returns true for any installed-or-not system family, so it cannot catch a missing font.
// Instead compare text widths against two generic fallbacks: a real font differs from both, a missing one
// collapses onto whichever fallback the browser substitutes.
export const fontAvailable = (family: string): boolean => {
	const ctx = document.createElement('canvas').getContext('2d');
	if (!ctx) return true;
	const sample = 'mmmmmmmmmmlli WwQq0123456789';
	const width = (font: string) => {
		ctx.font = `700 72px ${font}`;
		return ctx.measureText(sample).width;
	};
	return ['monospace', 'sans-serif', 'serif'].some((fb) => width(`"${family}", ${fb}`) !== width(fb));
};

export const Overlay: React.FC<OverlayProps> = (props) => {
	// Fonts fail silently in browsers (a missing face falls back to "almost Arial"): assert before drawing.
	if (typeof document !== 'undefined' && !fontAvailable(props.fontFamily)) {
		throw new Error(`font "${props.fontFamily}" is not available to the renderer; install it or set fontFamily`);
	}
	return (
		<AbsoluteFill style={{backgroundColor: props.background === 'transparent' ? undefined : props.background}}>
			{props.items.map((item, i) =>
				item.type === 'title' ? (
					<Title key={i} item={item} props={props} />
				) : (
					<Captions key={i} pages={item.pages} props={props} />
				),
			)}
		</AbsoluteFill>
	);
};

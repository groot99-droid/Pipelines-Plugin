import React from 'react';
import {Composition} from 'remotion';
import {Overlay} from './Overlay';
import {defaultProps, type OverlayProps} from './types';

export const Root: React.FC = () => (
	<Composition
		id="Overlay"
		component={Overlay}
		durationInFrames={Math.round(defaultProps.durationSeconds * defaultProps.fps)}
		fps={defaultProps.fps}
		width={defaultProps.width}
		height={defaultProps.height}
		defaultProps={defaultProps}
		calculateMetadata={({props}: {props: OverlayProps}) => ({
			durationInFrames: Math.max(1, Math.round(props.durationSeconds * props.fps)),
			fps: props.fps,
			width: props.width,
			height: props.height,
		})}
	/>
);

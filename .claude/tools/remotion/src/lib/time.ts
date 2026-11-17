import {FPS} from '../theme';

export type Word = {word: string; start: number; end: number; prob?: number};
export type Seg = {start: number; end: number; text: string; words: Word[]};
export type Card = {from: number; to: number; title: string; items: string[]};
export type ClipCut = {src: string; from: number; to: number; sourceStart?: number};

// seconds (composition timeline) -> frames
export const sec = (s: number) => Math.round(s * FPS);

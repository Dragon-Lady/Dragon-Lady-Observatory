// Personal Pins system — Phase 1
// Local-only, private, high-joy pinning for Dragon Lady’s Observatory
// All data stays in .local/pins.json (gitignored)

import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

const REPO_ROOT = path.resolve(process.cwd(), '..');
const LOCAL_DIR = path.join(REPO_ROOT, '.local');
const PINS_FILE = path.join(LOCAL_DIR, 'pins.json');
const THUMBNAILS_DIR = path.join(REPO_ROOT, 'pinned locations', 'thumbnails');

export interface ViewState {
  lat: number;
  lng: number;
  altitude: number;
}

export interface PersonalPin {
  id: string;
  createdAt: string;
  updatedAt?: string;

  viewState: ViewState;
  label: string;
  note?: string;

  thumbnailPath: string;

  recoveryMeta?: {
    originalCoordinates?: Record<string, any>;
    description?: string;
  };

  sourceEventId?: string; // if pinned from Sky Events dashboard
}

// Ensure folders exist
function ensureDirs() {
  if (!fs.existsSync(LOCAL_DIR)) fs.mkdirSync(LOCAL_DIR, { recursive: true });
  if (!fs.existsSync(THUMBNAILS_DIR)) fs.mkdirSync(THUMBNAILS_DIR, { recursive: true });
}

function loadPins(): PersonalPin[] {
  ensureDirs();
  if (!fs.existsSync(PINS_FILE)) return [];
  try {
    const data = JSON.parse(fs.readFileSync(PINS_FILE, 'utf8'));
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function savePins(pins: PersonalPin[]) {
  ensureDirs();
  fs.writeFileSync(PINS_FILE, JSON.stringify(pins, null, 2), 'utf8');
}

export function createPin(
  viewState: ViewState,
  label: string,
  note?: string,
  thumbnailPath?: string,
  sourceEventId?: string
): PersonalPin {
  const pin: PersonalPin = {
    id: randomUUID(),
    createdAt: new Date().toISOString(),
    viewState,
    label: label || 'Untitled Pin',
    note,
    thumbnailPath: thumbnailPath || '',
    sourceEventId,
  };

  const pins = loadPins();
  pins.unshift(pin); // newest first
  savePins(pins);
  return pin;
}

export function getAllPins(): PersonalPin[] {
  return loadPins();
}

export function getPinById(id: string): PersonalPin | undefined {
  return loadPins().find((p) => p.id === id);
}

export function updatePin(id: string, updates: Partial<PersonalPin>): PersonalPin | null {
  const pins = loadPins();
  const index = pins.findIndex((p) => p.id === id);
  if (index === -1) return null;

  pins[index] = {
    ...pins[index],
    ...updates,
    updatedAt: new Date().toISOString(),
  };
  savePins(pins);
  return pins[index];
}

export function deletePin(id: string): boolean {
  const pins = loadPins();
  const filtered = pins.filter((p) => p.id !== id);
  if (filtered.length === pins.length) return false;
  savePins(filtered);
  return true;
}

export function getThumbnailPath(filename: string): string {
  return path.join(THUMBNAILS_DIR, filename);
}
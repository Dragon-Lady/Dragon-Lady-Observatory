export const prerender = false;
import type { APIRoute } from 'astro';
import fs from 'fs';
import path from 'path';

const REPO_ROOT = path.resolve(process.cwd(), '..');
const PINS_FILE = path.join(REPO_ROOT, '.local', 'pins.json');

function ensureDirs() {
  const dir = path.dirname(PINS_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

export const GET: APIRoute = async () => {
  try {
    if (!fs.existsSync(PINS_FILE)) {
      return new Response(JSON.stringify({ pins: [], lastSynced: null }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const raw = fs.readFileSync(PINS_FILE, 'utf-8');
    const data = JSON.parse(raw);

    if (!Array.isArray(data.pins)) {
      return new Response(JSON.stringify({ pins: [], lastSynced: null }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err) {
    return new Response(JSON.stringify({ pins: [], lastSynced: null }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();

    if (!Array.isArray(body.pins)) {
      return new Response(JSON.stringify({ ok: false, error: 'Invalid pins array' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    ensureDirs();

    const payload = {
      pins: body.pins,
      lastSynced: body.lastSynced || new Date().toISOString()
    };

    fs.writeFileSync(PINS_FILE, JSON.stringify(payload, null, 2));

    return new Response(JSON.stringify({ ok: true, lastSynced: payload.lastSynced }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err: any) {
    return new Response(JSON.stringify({ ok: false, error: 'Write failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

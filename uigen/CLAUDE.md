# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

UIGen is an AI-powered React component generator with live preview. Users describe components in chat; Claude generates JSX/TSX files into an in-memory virtual file system, and the app renders them live in an iframe using browser-native ES module import maps.

## Commands

```bash
npm run setup          # First-time: installs deps, generates Prisma client, runs migrations
npm run dev            # Start dev server (Turbopack) at http://localhost:3000
npm run build          # Production build
npm run lint           # ESLint
npm run test           # Vitest (run all tests)
npx vitest run src/lib/__tests__/file-system.test.ts  # Run a single test file
npm run db:reset       # Reset SQLite database (destructive)
npx prisma generate    # Regenerate Prisma client after schema changes
npx prisma migrate dev # Apply new migrations
```

All `dev`/`build`/`start` scripts require `NODE_OPTIONS='--require ./node-compat.cjs'` (already in package.json scripts) for Node.js compatibility with the Prisma/Turbopack setup.

## Environment

Copy `.env.example` or create `.env` at the project root:

```
ANTHROPIC_API_KEY=...   # Optional — falls back to MockLanguageModel if absent
JWT_SECRET=...          # Optional — defaults to a hardcoded dev value
```

Without `ANTHROPIC_API_KEY`, the app uses `MockLanguageModel` in `src/lib/provider.ts` and returns static component code.

## Architecture

### AI Generation Pipeline

1. **Chat UI** (`src/lib/contexts/chat-context.tsx`) calls `POST /api/chat` with the current messages and serialized file system.
2. **API route** (`src/app/api/chat/route.ts`) runs `streamText` (Vercel AI SDK) with two tools:
   - `str_replace_editor` — create/view/replace/insert in files (`src/lib/tools/str-replace.ts`)
   - `file_manager` — rename/delete files (`src/lib/tools/file-manager.ts`)
3. Both tools operate on a **`VirtualFileSystem`** instance reconstructed from the request payload. No files are written to disk.
4. On finish, the updated file system and full message history are persisted to the `Project` row in SQLite (for authenticated users only).

### Virtual File System

`src/lib/file-system.ts` — `VirtualFileSystem` is an in-memory tree of `FileNode` objects. It serializes/deserializes to/from plain JSON for DB storage and API transport. The `FileSystemContext` (`src/lib/contexts/file-system-context.tsx`) holds the live client-side instance.

### Live Preview

`src/components/preview/PreviewFrame.tsx` renders an iframe with a full HTML document.
`src/lib/transform/jsx-transformer.ts` handles:
- Babel-transforming JSX/TSX to plain JS (`@babel/standalone`)
- Wrapping each file as a `Blob` URL
- Building a browser `importmap` so modules resolve by path
- Resolving third-party imports via `esm.sh`
- Reporting syntax errors back to the preview pane

The entry point for preview is `App.jsx` (or `App.tsx`) at the root of the virtual file system.

### Auth

`src/lib/auth.ts` — JWT-based sessions stored in an `httpOnly` cookie. Uses `jose`. Server-only module.
`src/middleware.ts` — protects routes.
`src/hooks/use-auth.ts` — client-side auth state.

### Database

Prisma with SQLite (`prisma/dev.db`). Schema has two models:
- `User` — email + bcrypt password
- `Project` — stores `messages` (JSON array) and `data` (serialized `VirtualFileSystem` JSON) as text columns

Prisma client is generated to `src/generated/prisma/`.

### Key Files

| Path | Purpose |
|------|---------|
| `src/app/api/chat/route.ts` | Streaming AI endpoint |
| `src/lib/file-system.ts` | VirtualFileSystem class |
| `src/lib/transform/jsx-transformer.ts` | Babel transform + import map builder |
| `src/lib/provider.ts` | Returns real or mock language model |
| `src/lib/prompts/generation.tsx` | System prompt for component generation |
| `src/lib/tools/str-replace.ts` | AI tool: file create/edit |
| `src/lib/tools/file-manager.ts` | AI tool: rename/delete |
| `src/lib/contexts/chat-context.tsx` | Chat state + API calls |
| `src/lib/contexts/file-system-context.tsx` | File system state |
| `src/components/preview/PreviewFrame.tsx` | Iframe-based live preview |

## Testing

Tests use Vitest + jsdom + `@testing-library/react`. Test files live alongside source in `__tests__/` subdirectories. Run all with `npm run test`; run one file with `npx vitest run <path>`.

# Todo App Frontend

Phase II: Full-Stack Web Application - Frontend

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` from `.env.example`:
```bash
cp .env.example .env.local
```

3. Update environment variables in `.env.local`

4. Run development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

See `CLAUDE.md` for detailed structure and guidelines.

## Specifications

- See `../specs/ui/components.md` for component specifications
- See `../specs/ui/pages.md` for page specifications
- See `../specs/api/rest-endpoints.md` for API contract

## Deployment

### Vercel (Recommended)

```bash
vercel deploy
```

Set environment variables in Vercel dashboard.

## Phase II Features

- User authentication (signup/login)
- Task CRUD operations
- Responsive UI
- Protected routes

## Future Phases

- Phase III: AI chatbot interface
- Phase IV: Kubernetes deployment
- Phase V: Advanced cloud features

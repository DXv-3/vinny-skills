# MarketLaunch Pro (Toto) - AI Coding Agent Guide

## Project Overview

**MarketLaunch Pro** (codename: Toto) is an enterprise-grade marketing platform featuring an intelligent, transparent recommendation engine and a voice-powered content creation studio. It enables marketing teams to plan, execute, and analyze multi-channel campaigns with AI assistance.

### Key Features
- Voice-powered content creation studio (TOTO AI)
- Multi-tenant organization support with RBAC
- Campaign management and analytics
- AI-powered recommendations
- Video upload and streaming
- GDPR compliance tools
- Comprehensive audit logging (SOC 2 ready)
- Real-time collaboration features

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS, Shadcn UI |
| **Backend** | NestJS 10, TypeScript, REST API, Swagger/OpenAPI |
| **Database** | PostgreSQL 16, Drizzle ORM, Redis 7 (caching/sessions) |
| **AI/ML** | OpenAI GPT-4, Anthropic Claude |
| **Auth** | JWT-based with refresh tokens, MFA support |
| **Testing** | Vitest (unit/integration), Supertest (e2e) |
| **Build** | TurboRepo, pnpm workspaces |
| **DevOps** | Docker, Docker Compose |

---

## Project Structure

This is a **monorepo** managed by [Turborepo](https://turbo.build/) and [pnpm](https://pnpm.io/) workspaces.

```
market-launch-pro/
├── apps/
│   ├── api/                    # NestJS backend (Port 4000)
│   │   ├── src/
│   │   │   ├── main.ts         # Application bootstrap
│   │   │   ├── app.module.ts   # Root module
│   │   │   ├── modules/        # Feature modules
│   │   │   │   ├── auth/       # JWT auth, login, register
│   │   │   │   ├── users/      # User CRUD
│   │   │   │   ├── organizations/  # Multi-tenant orgs
│   │   │   │   ├── campaigns/  # Campaign management
│   │   │   │   ├── projects/   # TOTO projects
│   │   │   │   ├── videos/     # Video upload/streaming
│   │   │   │   ├── ai/         # OpenAI integration
│   │   │   │   ├── audit/      # Audit logging (SOC 2)
│   │   │   │   ├── gdpr/       # GDPR compliance
│   │   │   │   └── ...
│   │   │   ├── common/         # Guards, filters, decorators
│   │   │   └── database/       # Database module
│   │   ├── test/               # E2E tests
│   │   └── vitest.config.ts    # Test configuration
│   │
│   └── web/                    # Next.js frontend (Port 3001)
│       ├── src/
│       │   ├── app/            # Next.js App Router
│       │   │   ├── (auth)/     # Auth routes (login, register)
│       │   │   ├── (dashboard)/ # Protected dashboard routes
│       │   │   └── page.tsx    # Landing page
│       │   ├── components/
│       │   │   ├── ui/         # Shadcn UI components
│       │   │   ├── toto-voice-assistant.tsx  # Main voice UI
│       │   │   └── dashboard/  # Dashboard components
│       │   ├── hooks/          # React hooks (TanStack Query)
│       │   ├── lib/            # Utilities, API client, stores
│       │   └── styles/         # Global CSS
│       └── next.config.ts      # Next.js configuration
│
├── packages/
│   ├── db/                     # Database schema & client
│   │   ├── src/schema/         # Drizzle table definitions
│   │   │   ├── users.ts
│   │   │   ├── organizations.ts
│   │   │   ├── projects.ts
│   │   │   ├── videos.ts
│   │   │   ├── campaigns.ts
│   │   │   ├── audit-logs.ts
│   │   │   └── ...
│   │   ├── src/client.ts       # Database connection singleton
│   │   └── drizzle.config.ts   # Drizzle Kit configuration
│   │
│   ├── ui/                     # Shared React components
│   │   └── src/
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       └── ...
│   │
│   └── config/                 # Shared configuration
│       ├── eslint.config.mjs   # Shared ESLint config
│       ├── tsconfig.base.json  # Base TypeScript config
│       ├── tsconfig.node.json  # Node.js apps config
│       └── tsconfig.react.json # React apps config
│
├── docker/                     # Docker configuration
│   ├── postgres/init.sql       # DB initialization
│   └── grafana/provisioning/   # Monitoring (optional)
│
├── docker-compose.yml          # Services: PostgreSQL, Redis, MailHog
├── turbo.json                  # Turborepo pipeline config
├── pnpm-workspace.yaml         # pnpm workspace definition
└── docs/                       # Documentation
    ├── ARCHITECTURE.md         # Detailed architecture
    ├── TOTO_SPEC_V1.md         # Product specification
    └── TOTO_AI_Comprehensive_Playbook.md
```

---

## Prerequisites

- **Node.js**: 20.0.0 or higher
- **Package Manager**: pnpm (`npm install -g pnpm`)
- **Docker**: For PostgreSQL and Redis
- **OS**: macOS, Linux, or WSL2 on Windows

---

## Build and Development Commands

### Installation
```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys (OpenAI, etc.)
```

### Database Setup
```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Push database schema
pnpm db:push

# Generate migrations (if schema changes)
pnpm db:generate

# Open Drizzle Studio (database GUI)
pnpm db:studio
```

### Development
```bash
# Start all apps in development mode
pnpm dev

# Start individual apps
pnpm --filter @market-launch/api dev      # API only
pnpm --filter @market-launch/web dev      # Web only

# Services will be available at:
# - Frontend: http://localhost:3001
# - API: http://localhost:4000
# - Swagger Docs: http://localhost:4000/api/docs
# - MailHog: http://localhost:8025 (email testing)
```

### Building
```bash
# Build all apps and packages
pnpm build

# Build specific package
pnpm --filter @market-launch/db build
```

---

## Testing Commands

### Unit & Integration Tests
```bash
# Run all tests
pnpm test

# Run tests with coverage
pnpm test:coverage

# Run tests in watch mode
pnpm --filter @market-launch/api test:watch
```

### Test Configuration
- **API Tests**: Vitest with Node environment (`apps/api/vitest.config.ts`)
- **Coverage Thresholds**: 80% for branches, functions, lines, statements
- **Test Files**: `*.spec.ts` or `*.test.ts` in `src/` directories
- **Setup File**: `apps/api/src/test/setup.ts`

### E2E Tests
Located in `apps/api/test/`. Run via:
```bash
pnpm --filter @market-launch/api test:e2e
```

---

## Code Style Guidelines

### ESLint Configuration
The project uses a shared ESLint configuration (`packages/config/eslint.config.mjs`) with:

- **TypeScript Strict Rules**:
  - `no-explicit-any`: Error
  - `explicit-function-return-type`: Required
  - `no-floating-promises`: Error
  - `strict-boolean-expressions`: Error

- **Code Quality**:
  - `no-console`: Warn (only allow `console.warn` and `console.error`)
  - `eqeqeq`: Error (always use strict equality)
  - `no-var`: Error (use `const` or `let`)
  - `curly`: Error (always use braces)

- **Import Organization**:
  - `sort-imports`: Error (sorted imports)

### Running Linting
```bash
# Lint all packages
pnpm lint

# Fix auto-fixable issues
pnpm lint:fix

# Format with Prettier
pnpm format

# Check formatting
pnpm format:check
```

### Pre-commit Hooks
Husky and lint-staged are configured to:
- Run ESLint --fix on `*.{ts,tsx,js,jsx}`
- Run Prettier on all staged files

---

## Key Architecture Patterns

### Backend (NestJS)

#### Module Structure
Each module follows this structure:
```
modules/feature/
├── feature.module.ts      # Module definition
├── feature.controller.ts  # HTTP route handlers
├── feature.service.ts     # Business logic
├── dto/                   # Data Transfer Objects
└── (guards, decorators)   # Related utilities
```

#### Dependency Injection
The API uses NestJS's DI container. Key services:
- `DatabaseModule`: Provides Drizzle client globally
- `AuditService`: Automatic audit logging
- `ErrorHandlerService`: Centralized error handling

#### Security Patterns
- **Auth**: JWT tokens with refresh token rotation
- **Authorization**: RBAC with `@Roles()` decorator
- **Rate Limiting**: `@nestjs/throttler` (short/medium/long windows)
- **CORS**: Configured in `main.ts`
- **Helmet**: Security headers

### Database (Drizzle ORM)

#### Schema Pattern
```typescript
// packages/db/src/schema/feature.ts
export const tableName = pgTable('table_name', {
    id: uuid('id').primaryKey().default(sql`gen_random_uuid()`),
    // ... columns
}, (table) => [
    // indexes
]);
```

#### Database Access Pattern
```typescript
// Always use the singleton pattern
import { getDb } from '@market-launch/db';

const db = getDb();
const result = await db.select().from(users).where(eq(users.id, id));
```

### Frontend (Next.js)

#### State Management
- **Server State**: TanStack React Query (`hooks/`)
- **Client State**: Zustand (`lib/stores/`)
- **Auth**: JWT stored in memory + localStorage (refresh token)

#### API Communication
```typescript
// Use the centralized API client
import { apiClient } from '@/lib/api/client';

const data = await apiClient.projects.list();
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

### Required
```bash
# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/marketlaunch"

# Redis
REDIS_URL="redis://localhost:6379"

# Auth
JWT_SECRET="your-super-secret-jwt-key-min-32-chars"
SESSION_SECRET="your-session-secret"

# API
API_PORT=4000
WEB_PORT=3001
NODE_ENV=development
```

### Optional (for specific features)
```bash
# OpenAI (for AI features)
OPENAI_API_KEY="sk-..."

# Stripe (for billing)
STRIPE_SECRET_KEY="sk_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# OAuth
GOOGLE_CLIENT_ID="..."
GITHUB_CLIENT_ID="..."

# Email (SendGrid)
SENDGRID_API_KEY="..."

# Observability
SENTRY_DSN="..."
```

---

## Security Considerations

### Authentication & Authorization
- JWT access tokens (15 min expiry)
- Refresh tokens (7 day expiry) with rotation
- MFA support (TOTP)
- Account lockout after failed login attempts
- OAuth (Google, GitHub) integration

### Data Protection
- Passwords hashed with Argon2
- MFA secrets encrypted
- PII handling per GDPR requirements
- Audit logs for all sensitive operations

### API Security
- Rate limiting per endpoint
- Input validation with `class-validator`
- SQL injection prevention (Drizzle ORM)
- CORS configuration
- Security headers via Helmet

---

## Common Tasks

### Adding a New API Module
1. Create folder in `apps/api/src/modules/new-feature/`
2. Create `new-feature.module.ts`, `.controller.ts`, `.service.ts`
3. Add module to `app.module.ts` imports
4. Create DTOs in `dto/` folder
5. Add tests in `test/` folder

### Adding a Database Table
1. Create schema file in `packages/db/src/schema/`
2. Export from `packages/db/src/schema/index.ts`
3. Run `pnpm db:generate` to create migration
4. Run `pnpm db:push` to apply migration

### Adding a Shared UI Component
1. Create component in `packages/ui/src/`
2. Export from `packages/ui/src/index.ts`
3. Use in apps: `import { Button } from '@market-launch/ui'`

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 3001 in use | Change `WEB_PORT` in `.env` |
| Port 4000 in use | Change `API_PORT` in `.env` |
| Database connection failed | Run `docker-compose up -d` |
| Type errors | Run `pnpm typecheck` to identify issues |
| Module not found | Run `pnpm install` to sync dependencies |

### Debug Mode
```bash
# API debug mode
pnpm --filter @market-launch/api start:debug

# Web debug mode (source maps enabled by default in dev)
pnpm --filter @market-launch/web dev
```

---

## Documentation References

- **Architecture**: `ARCHITECTURE.md` - Detailed system design
- **API Docs**: Run API and visit `http://localhost:4000/api/docs`
- **Product Spec**: `docs/TOTO_SPEC_V1.md` - Feature specifications
- **AI Playbook**: `docs/TOTO_AI_Comprehensive_Playbook.md` - AI integration guide

---

## Package Registry

All internal packages are scoped under `@market-launch/`:
- `@market-launch/api` - NestJS backend
- `@market-launch/web` - Next.js frontend
- `@market-launch/db` - Database schema and client
- `@market-launch/ui` - Shared UI components
- `@market-launch/config` - Shared configurations

---

**Last Updated**: February 2026
**Maintainer**: TOTO Development Team

FROM node:26-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm install

FROM node:26-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL=/api/v1
ENV NEXT_TELEMETRY_DISABLED=1 NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN mkdir -p public && npm run build

FROM node:26-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1

# Use a fixed numeric identity so Kubernetes can verify runAsNonRoot.
RUN addgroup -S -g 10001 nodejs \
    && adduser -S -D -H -u 10001 -G nodejs nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=10001:10001 /app/.next/standalone ./
COPY --from=builder --chown=10001:10001 /app/.next/static ./.next/static

# Next.js may write runtime cache files.
RUN mkdir -p /app/.next/cache \
    && chown -R 10001:10001 /app

USER 10001:10001
EXPOSE 3000
ENV PORT=3000 HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]

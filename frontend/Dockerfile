FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev=false

FROM node:22-alpine AS builder
WORKDIR /app
# Render automatically forwards a Docker service's environment variables as
# build args with matching keys, but only for names declared with ARG here.
# NEXT_PUBLIC_* variables are inlined into the client bundle by Next.js at
# `next build` time, so without this the browser bundle always falls back to
# calling its own origin (relative URLs), producing 404s on every API call.
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]

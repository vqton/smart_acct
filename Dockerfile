FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY prisma/schema.prisma prisma/
COPY prisma.config.ts ./
RUN npx prisma generate
COPY tsconfig.json ./
COPY src/ src/
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY prisma/schema.prisma prisma/
COPY prisma.config.ts ./
COPY --from=builder /app/dist/ dist/
COPY --from=builder /app/src/generated/prisma/ src/generated/prisma/
RUN npx prisma generate
EXPOSE 8080
CMD ["node", "dist/main.js"]

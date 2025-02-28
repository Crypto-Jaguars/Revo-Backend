# Stage 1: Build dependencies
FROM node:20-alpine as build-stage

WORKDIR /app

# Install NestJS CLI globally
RUN npm install -g @nestjs/cli

COPY package*.json ./

# Use npm ci for reproducible builds
RUN npm ci

# Copy app source code
COPY . .

# Build the app
RUN npm run build

# Remove development dependencies
RUN npm prune --production

# Stage 2: Production
FROM node:20-alpine as production-stage

WORKDIR /app

# Copy built files and production dependencies
COPY --from=build-stage /app /app

# Set environment
ENV NODE_ENV=production

EXPOSE 3000

# Run the app directly with Node
CMD ["node", "dist/main.js"]

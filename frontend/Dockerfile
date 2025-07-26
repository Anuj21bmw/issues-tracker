FROM node:18-alpine as builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Clear npm cache and install dependencies
RUN npm cache clean --force && npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
# Stage 1 – Build the frontend with Vite
FROM node:18 AS builder
WORKDIR /app

# Copy only the frontend folder
COPY frontend/package*.json frontend/
RUN cd frontend && npm install

# Now copy the rest
COPY frontend/ frontend/
RUN cd frontend && npm run build

# Stage 2 – Serve it
FROM node:18
WORKDIR /app
RUN npm install -g serve

# Copy the build output from previous stage
COPY --from=builder /app/frontend/dist ./dist

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]

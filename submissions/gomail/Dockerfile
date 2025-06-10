# Build stage
FROM golang:1.24.2-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev sqlite-dev

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=1 GOOS=linux go build -ldflags="-s -w" -o gomail .

# Runtime stage
FROM alpine:latest

# Install runtime dependencies
RUN apk add --no-cache ca-certificates sqlite

WORKDIR /root/

# Copy the binary from builder stage
COPY --from=builder /app/gomail .

# Create a non-root user
RUN addgroup -g 1001 -S gomail && \
    adduser -S gomail -u 1001 -G gomail

USER gomail

# Expose port if your app serves HTTP (adjust if needed)
# EXPOSE 8080

# Run the binary
ENTRYPOINT ["./gomail"]

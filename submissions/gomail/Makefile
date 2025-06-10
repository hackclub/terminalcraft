# GoMail Makefile

.PHONY: build test clean install dev release docker help

# Variables
BINARY_NAME := gomail
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BUILD_DIR := dist
GO_VERSION := 1.24.2

# Default target
help: ## Show this help message
	@echo "GoMail Build System"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the binary for current platform
	@echo "Building $(BINARY_NAME) version $(VERSION)..."
	go build -ldflags="-s -w -X main.version=$(VERSION)" -o $(BINARY_NAME) .

test: ## Run tests
	go test -v ./...

clean: ## Clean build artifacts
	rm -rf $(BUILD_DIR)
	rm -f $(BINARY_NAME)
	rm -f $(BINARY_NAME).exe

install: ## Install dependencies
	go mod download
	go mod verify

dev: ## Run in development mode
	go run . --help

release: ## Build cross-platform binaries
	@echo "Building release version $(VERSION)..."
	./scripts/build.sh $(VERSION)

docker-build: ## Build Docker image
	docker build -t gomail:$(VERSION) .
	docker tag gomail:$(VERSION) gomail:latest

docker-run: ## Run Docker container
	docker run --rm -it gomail:$(VERSION)

lint: ## Run linter
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run; \
	else \
		echo "golangci-lint not installed. Install with: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"; \
	fi

fmt: ## Format code
	go fmt ./...

vet: ## Run go vet
	go vet ./...

mod-tidy: ## Tidy go modules
	go mod tidy

check: test vet fmt ## Run all checks

# Development helpers
run-help: ## Show application help
	go run . --help

run-version: ## Show application version
	go run . version

# Git helpers
tag: ## Create a new tag (usage: make tag VERSION=v1.0.0)
	@if [ -z "$(VERSION)" ]; then \
		echo "Please specify VERSION: make tag VERSION=v1.0.0"; \
		exit 1; \
	fi
	git tag $(VERSION)
	git push origin $(VERSION)
	@echo "Tag $(VERSION) created and pushed. GitHub Actions will create a release."

# Show current version
version: ## Show current version
	@echo $(VERSION)

# Quick development cycle
quick: clean build test ## Quick build and test cycle

all: clean install test build ## Full build pipeline

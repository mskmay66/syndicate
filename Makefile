.PHONY: init-kimi
init-kimi: ## Initialize Kimi API key as environment variable
	@echo "placing kimi api key as env variable"
	@export KIMI_API_KEY=$(security find-generic-password -a "default" -s "kimi" -w)

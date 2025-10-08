package main

import (
	"manager-service/pkg/api"
)

func main() {
	// Todo: Add scheduler


	// Todo: add graceful shutdown
	// Start HTTP server
	httpHandler := api.NewHandler()
	httpHandler.RegisterRoutes()
	httpHandler.StartServer()


}
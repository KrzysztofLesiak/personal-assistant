package api

import (
	"net/http"

	log "github.com/sirupsen/logrus"
)

// GET /v1/health
func handleHealth(r *http.Request) HTTPResponse {
	return HTTPResponse{
		Status: http.StatusOK,
		Data: map[string]string{"status": "ok"},
	}
}

// POST /v1/chat
func handleChat(r *http.Request) HTTPResponse {
	log.Info("Received chat request")

	return HTTPResponse{
		Status: http.StatusNotImplemented,
		Data: map[string]interface{}{
			"message": "Chat endpoint not implemented yet",
		},
	}
}

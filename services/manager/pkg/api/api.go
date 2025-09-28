package api

import (
	"manager-service/pkg/config"
	"net/http"
	"os"

	log "github.com/sirupsen/logrus"
)

type HTTPHandler struct {
	config *config.Config
}

func NewHandler() *HTTPHandler {	
	return &HTTPHandler{
		config: config.DefaultConfig(),
	}
}

// Define HTTPHandlerFunc as a non-generic type or use interface{} if needed
func (h *HTTPHandler) addRoute(pattern string, method string, handler HTTPHandlerFunc) {
	http.Handle(pattern, h.corsMiddleware(httpMiddleware(handler, method)))
}

func (h *HTTPHandler) RegisterRoutes() {
	h.addRoute("/v1/health", "GET", handleHealth)
	h.addRoute("/v1/chat", "POST", handleChat)
}

func (h *HTTPHandler) StartServer() error {
	http_host, set := os.LookupEnv("HTTP_HOST")
	if !set || http_host == "" {
		http_host = "localhost"
	}
	http_port, set := os.LookupEnv("HTTP_PORT")
	if !set || http_port == "" {
		http_port = "8090"
	}

	log.WithField("Config", map[string]interface{}{
		"AllowedOrigins":   h.config.AllowedOrigins,
		"AllowedMethods":   h.config.AllowedMethods,
		"AllowedHeaders":   h.config.AllowedHeaders,
		"AllowCredentials": h.config.AllowCredentials,
	}  ).Info("CORS configuration applied")

	address := http_host + ":" + http_port

	log.Info("Starting HTTP servers...")
	log.Infof("Starting listening on http://%s", address)
	return http.ListenAndServe(address, nil)
}
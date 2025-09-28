package api

import (
	"encoding/json"
	"net/http"
	"strings"

	log "github.com/sirupsen/logrus"
)

type ErrorDetail struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}	

type HTTPErrorResponse struct {
	Error ErrorDetail `json:"error"`
}

type HTTPResponse struct {
	Status int         			`json:"status"`
	Data interface{}  `json:"data,omitempty"`
}

type HTTPHandlerFunc func(request *http.Request) HTTPResponse

func (h *HTTPHandler) corsMiddleware(next http.Handler) http.Handler {
	config := h.config
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", strings.Join(config.AllowedOrigins, ", "))
		w.Header().Set("Access-Control-Allow-Methods", strings.Join(config.AllowedMethods, ", "))
		w.Header().Set("Access-Control-Allow-Headers", strings.Join(config.AllowedHeaders, ", "))
		if config.AllowCredentials {
			w.Header().Set("Access-Control-Allow-Credentials", "true")
		}

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func httpMiddleware(handler HTTPHandlerFunc, method string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusInternalServerError)

				resp := HTTPErrorResponse{
					Error: ErrorDetail{
						Code:    http.StatusInternalServerError,
						Message: "Internal Server Error",
					},
				}
				json.NewEncoder(w).Encode(resp)

				logRequest(r, http.StatusInternalServerError)
			}
		}()

		if r.Method != method {

			w.Header().Set("Content-Type", "application/json")
			w.Header().Set("Allow", method)
			w.WriteHeader(http.StatusMethodNotAllowed)

			resp := HTTPErrorResponse{
				Error: ErrorDetail{
					Code:    http.StatusMethodNotAllowed,
					Message: "Method Not Allowed",
				},
			}
			json.NewEncoder(w).Encode(resp)
			logRequest(r, http.StatusMethodNotAllowed)
			return
		}

		response := handler(r)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(response.Status)
		json.NewEncoder(w).Encode(map[string]interface{}{"data": response.Data})
		logRequest(r, response.Status)
	})
}

func logRequest(r *http.Request, statusCode int) {
	statusText := http.StatusText(statusCode)
	log.Infof("%s %s %s %d %s", r.Method, r.URL.Path, r.Proto, statusCode, statusText)
}
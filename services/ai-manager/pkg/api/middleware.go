package api

import (
	"context"
	"encoding/json"
	"net/http"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
)

type ErrorDetail struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}	

type HTTPResponse struct {
	Status int         	`json:"status,omitempty"`
	Data interface{}  	`json:"data,omitempty"`
	Error ErrorDetail 	`json:"error"`
}

type HTTPHandlerFunc func(request *http.Request) HTTPResponse

func (h *HTTPHandler) corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", strings.Join(h.config.AllowedOrigins, ", "))
		w.Header().Set("Access-Control-Allow-Methods", strings.Join(h.config.AllowedMethods, ", "))
		w.Header().Set("Access-Control-Allow-Headers", strings.Join(h.config.AllowedHeaders, ", "))
		if h.config.AllowCredentials {
			w.Header().Set("Access-Control-Allow-Credentials", "true")
		}

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func httpMiddleware(handler HTTPHandlerFunc, methods []string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				handleRecover(w, r)
			}
		}()

		ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
		defer cancel()

		r = r.WithContext(ctx)
		allowed := checkMethod(w, r, methods)
		if !allowed {
			return
		}

		select {
		case <-ctx.Done():
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusRequestTimeout)
			resp := HTTPResponse{
				Error: ErrorDetail{
					Code:    http.StatusRequestTimeout,
					Message: "Request Timeout",
				},
			}
			json.NewEncoder(w).Encode(resp)
			logRequest(r, http.StatusRequestTimeout)
			return
		default:
		}
		
		response := handler(r)
		handleResponse(w, r, response)
	})
}

func handleRecover(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusInternalServerError)

	resp := HTTPResponse{
		Error: ErrorDetail{
			Code:    http.StatusInternalServerError,
			Message: "Internal Server Error",
		},
	}
	json.NewEncoder(w).Encode(resp)

	logRequest(r, http.StatusInternalServerError)
}

func checkMethod(w http.ResponseWriter, r *http.Request, allowedMethods []string) bool {
	methodAllowed := false
	for _, m := range allowedMethods {
		if strings.EqualFold(r.Method, m) {
			methodAllowed = true
			break
		}
	}

	if !methodAllowed {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Allow", strings.Join(allowedMethods, ", "))
		w.WriteHeader(http.StatusMethodNotAllowed)

		resp := HTTPResponse{
			Error: ErrorDetail{
				Code:    http.StatusMethodNotAllowed,
				Message: "Method Not Allowed",
			},
		}
		json.NewEncoder(w).Encode(resp)
		logRequest(r, http.StatusMethodNotAllowed)
		return false 
	}

	return methodAllowed
}

func handleResponse(w http.ResponseWriter, r *http.Request, response HTTPResponse) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(response.Status)
	if response.Data != nil {
		json.NewEncoder(w).Encode(response.Data)
		logRequest(r, response.Status)
		return
	}

	if response.Error.Message != "" {
		json.NewEncoder(w).Encode(response.Error)
		logRequest(r, response.Status)
		return
	}
}

func logRequest(r *http.Request, statusCode int) {
	statusText := http.StatusText(statusCode)
	log.Infof("%s %s %s %d %s", r.Method, r.URL.Path, r.Proto, statusCode, statusText)
}
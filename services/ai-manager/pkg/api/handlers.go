package api

import (
	"net/http"
)

//Todo: Implement actual logic for each handler

// GET /v1/health
func handleHealth(r *http.Request) HTTPResponse {
	return HTTPResponse{
		Status: http.StatusOK,
		Data: map[string]string{"status": "ok"},
	}
}

// GET /v1/tasks/
func handleTasks(r *http.Request) HTTPResponse {
	return HTTPResponse{
		Status: http.StatusNotImplemented,
		Error: ErrorDetail{
			Code:    http.StatusNotImplemented,
			Message: "List tasks endpoint not implemented yet",
		},
	}
}

// GET, POST, PUT, DELETE /v1/tasks/{id}
func handleTask(r *http.Request) HTTPResponse {
	if r.Method == "GET" {
		return HTTPResponse{
			Status: http.StatusOK,
			Data: map[string]interface{}{
				"message": "Get task endpoint not implemented yet",
			},
		}
	}

	if r.Method == "POST" {
		return HTTPResponse{
			Status: http.StatusOK,
			Data: map[string]interface{}{
				"message": "Create task endpoint not implemented yet",
			},
		}
	}

	if r.Method == "PUT" {
		return HTTPResponse{
			Status: http.StatusOK,
			Data: map[string]interface{}{
				"message": "Update task endpoint not implemented yet",
			},
		}
	}

	if r.Method == "DELETE" {
		return HTTPResponse{
			Status: http.StatusOK,
			Data: map[string]interface{}{
				"message": "Delete task endpoint not implemented yet",
			},
		}
	}

	return HTTPResponse{
		Status: http.StatusMethodNotAllowed,
		Error: ErrorDetail{
			Code:    http.StatusMethodNotAllowed,
			Message: "Method not allowed",
		},
	}
}



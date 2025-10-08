package config

type Config struct {
	AllowedOrigins   []string
	AllowedMethods   []string
	AllowedHeaders   []string
	AllowCredentials bool
	InterpreterURL   string
	LLMServiceURL    string
}

func DefaultConfig() *Config {
	return &Config{
		AllowedOrigins:   []string{"http://localhost:3000", "http://localhost:8000"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "Authorization"},
		AllowCredentials: true,
		InterpreterURL:   "http://localhost:8181",
		LLMServiceURL:    "http://localhost:8000",
	}
}
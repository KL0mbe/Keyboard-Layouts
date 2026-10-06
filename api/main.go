package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type ComboResponse struct {
	Singles      []map[string]any `json:"single"`
	Compositions []map[string]any `json:"compositions"`
}

func main() {
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		log.Fatal("DATABASE_URL not set")
	}
	pool, err := pgxpool.New(context.Background(), dbURL)
	if err != nil {
		log.Fatalf("Unable to connect to database: %v\n", err)
	}
	defer pool.Close()

	mux := http.NewServeMux()
	mux.HandleFunc("GET /", getChar(pool))
	mux.HandleFunc("GET /countries", getCountries(pool))
	log.Fatal(http.ListenAndServe(":8080", withCORS(mux)))
}

func getCountries(pool *pgxpool.Pool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		rows, err := pool.Query(context.Background(), "SELECT * FROM countries")
		if err != nil {
			log.Println("countries query:", err)
			http.Error(w, "Countries Query failed", http.StatusInternalServerError)
			return
		}
		results, err := pgx.CollectRows(rows, pgx.RowToMap)
		if err != nil {
			log.Println("countries collect rows:", err)
			http.Error(w, "Countries: CollectRows failed", http.StatusInternalServerError)
			return
		}
		json.NewEncoder(w).Encode(results)
	}
}

func getChar(pool *pgxpool.Pool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		char := r.URL.Query().Get("char")
		country := r.URL.Query().Get("country")
		if char == "" || country == "" {
			errorMessage := "Missing Parameters:"
			if char == "" {
				errorMessage += " char"
			}
			if country == "" {
				errorMessage += " country"
			}
			http.Error(w, errorMessage, http.StatusBadRequest)
			return
		}
		singleRows, err := pool.Query(context.Background(), `
		SELECT layout.id, base.character, combo.modify_opt_alt, 
		combo.modify_shift, combo.modify_ctrl, combo.modify_altgr, 
		layout.native_name AS display_name
		FROM key_combos AS combo 
		JOIN characters AS out ON out.id = combo.output_char_id 
		JOIN keyboard_layouts AS layout ON layout.id = combo.keyboard_id 
		JOIN characters AS base ON base.id = combo.base_key_id 
		JOIN countries as c ON c.id = layout.country_id 
		WHERE out.character = $1 AND c.native_name = $2;`, char, country)
		if err != nil {
			http.Error(w, "Key Combo Query failed", http.StatusInternalServerError)
			return
		}
		singleResults, err := pgx.CollectRows(singleRows, pgx.RowToMap)
		if err != nil {
			http.Error(w, "Key Combo: CollectRows failed", http.StatusInternalServerError)
			return
		}
		compositions, err := pool.Query(context.Background(), `
		SELECT comp.id AS composition_id, layout.id AS layout_id, out.character AS output_char, 
		base.character AS base_char, combo.modify_shift, combo.modify_opt_alt, steps.step, 
		layout.native_name AS display_name
		FROM key_combos AS combo 
		JOIN composition_steps AS steps ON steps.combo_id = combo.id 
		JOIN standard_keys AS skey ON skey.id = combo.key_code_id 
		JOIN compositions AS comp ON comp.id = steps.composition_id 
		JOIN characters AS out ON out.id = comp.output_char_id 
		JOIN characters AS base ON base.id = combo.base_key_id 
		JOIN keyboard_layouts AS layout ON layout.id = comp.keyboard_id 
		JOIN countries AS c ON c.id = layout.country_id
		WHERE out.character = $1 AND c.native_name = $2;`, char, country)
		if err != nil {
			http.Error(w, "Key Combo Query failed", http.StatusInternalServerError)
			return
		}
		compositionResults, err := pgx.CollectRows(compositions, pgx.RowToMap)
		if err != nil {
			http.Error(w, "Key Composition Combo: CollectRows failed", http.StatusInternalServerError)
			return
		}

		response := ComboResponse{
			Singles:      singleResults,
			Compositions: compositionResults,
		}

		if err := json.NewEncoder(w).Encode(response); err != nil {
			log.Println(err)
			return
		}
	}
}

func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "*")
		w.Header().Set("Content-type", "application/json")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)

	})
}

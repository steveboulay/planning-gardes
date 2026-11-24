/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // En développement, les appels à /api partent vers le serveur Django
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/setupTests.ts"],
    restoreMocks: true,
    // Fuseau fixe : les tests de changement d'heure ne dépendent pas du poste ni de la CI
    env: { TZ: "Europe/Paris" },
  },
});

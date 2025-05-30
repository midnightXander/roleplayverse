import React, { useState } from "react";
import axios from "../../../services/api"; // ← ton fichier api.js

export default function SignInAndRegister() {
  const [isSignIn, setIsSignIn] = useState(true);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const payload = isSignIn
        ? { email, password }
        : { email, password, username };

      const endpoint = isSignIn ? "auth/login/" : "auth/register/";
      const response = await axios.post(endpoint, payload);

      setMessage("✅ Succès !");
      console.log("Réponse :", response.data);

      // Tu peux stocker le token ici si besoin
      // localStorage.setItem("token", response.data.token);
    } catch (error) {
      console.error(error);
      setMessage("❌ Une erreur est survenue.");
    }
  };

  return (
    <div className="min-h-screen bg-dark text-white flex items-center justify-center p-6">
      <div className="w-full max-w-md bg-gray-900 p-8 rounded-xl shadow-lg">
        <h1 className="text-2xl font-bold text-center text-primary mb-6">
          {isSignIn ? "Connexion" : "Inscription"} à RoleplayVerse
        </h1>

        <form className="space-y-5" onSubmit={handleSubmit}>
          {!isSignIn && (
            <div>
              <label className="block text-sm mb-1">Nom d'utilisateur</label>
              <input value={username} onChange={(e) => setUsername(e.target.value)}
                     type="text" className="w-full px-4 py-2 bg-gray-800 rounded border border-gray-700" />
            </div>
          )}

          <div>
            <label className="block text-sm mb-1">Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)}
                   type="email" className="w-full px-4 py-2 bg-gray-800 rounded border border-gray-700" />
          </div>

          <div>
            <label className="block text-sm mb-1">Mot de passe</label>
            <input value={password} onChange={(e) => setPassword(e.target.value)}
                   type="password" className="w-full px-4 py-2 bg-gray-800 rounded border border-gray-700" />
          </div>

          <button type="submit"
                  className="w-full py-2 bg-primary hover:bg-orange-700 rounded text-white font-semibold">
            {isSignIn ? "Se connecter" : "Créer un compte"}
          </button>
        </form>

        {message && <p className="mt-4 text-center text-sm">{message}</p>}

        <p className="mt-4 text-sm text-center">
          {isSignIn ? "Pas encore inscrit ?" : "Déjà un compte ?"}{" "}
          <button onClick={() => setIsSignIn(!isSignIn)} className="text-primary hover:underline">
            {isSignIn ? "Créer un compte" : "Se connecter"}
          </button>
        </p>
      </div>
    </div>
  );
}

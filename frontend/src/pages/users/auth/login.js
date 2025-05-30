import React from "react";

export default function Login() {
  return (
    <div className="min-h-screen bg-dark flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-900 p-8 rounded-xl shadow-xl">
        <h2 className="text-2xl font-bold text-orange-500 mb-6 text-center">Connexion</h2>
        <form className="space-y-5">
          <input type="text" placeholder="Nom d'utilisateur ou email" className="w-full p-3 rounded bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-orange-500" />
          <input type="password" placeholder="Mot de passe" className="w-full p-3 rounded bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-orange-500" />
          <button type="submit" className="w-full py-3 bg-orange-600 hover:bg-orange-700 text-white rounded font-semibold">Se connecter</button>
        </form>
        <p className="text-sm text-center text-gray-400 mt-4">Pas encore de compte ? <a href="/register" className="text-orange-400 hover:underline">Créer un compte</a></p>
      </div>
    </div>
  );
}

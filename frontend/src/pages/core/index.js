import {useEffect, useState} from 'react'
import React from 'react';

function Index(){

    return(
        <div className="bg-dark text-white min-h-screen">
      {/* Hero section */}
      <header className="flex flex-col items-center justify-center text-center p-8 bg-gradient-to-b from-black via-dark to-dark">
        <h1 className="text-4xl sm:text-5xl font-bold mb-4 text-primary">RoleplayVerse</h1>
        <p className="text-lg max-w-xl text-gray-300">
          Une nouvelle ère du RP Naruto commence. Incarne ton propre ninja, progresse, combats, écris ton histoire… et gagne des récompenses.
        </p>
        <a href="/register" className="mt-6 px-6 py-3 bg-primary hover:bg-orange-700 text-white rounded-full text-lg font-medium">
          Créer mon personnage
        </a>
      </header>

      {/* Sections principales */}
      <section className="py-16 px-6 max-w-5xl mx-auto text-center">
        <h2 className="text-2xl font-semibold mb-6">🌌 Ce que tu peux faire</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-xl font-bold mb-2">👤 Incarne un ninja</h3>
            <p>Crée ton propre personnage avec ses capacités, affinités et équipements.</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-xl font-bold mb-2">⚔️ Combats RP</h3>
            <p>Affronte d'autres joueurs ou l'IA dans des combats scénarisés avec des arbitres.</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-xl font-bold mb-2">💰 Gagne des récompenses</h3>
            <p>Accumule des Crédits RP pour monétiser ton activité et ta créativité.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 text-center text-sm text-gray-400">
        © {new Date().getFullYear()} RoleplayVerse — Tous droits réservés
      </footer>
    </div>
    );
}

export default Index
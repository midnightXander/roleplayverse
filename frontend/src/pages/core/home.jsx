// Home.jsx
import React, { useEffect, useState } from "react";
import api from "../../services/api";



export default function Home() {

  const getPosts = async () =>{
    const res = await api.get('feed')
    console.log(res.data.username)
  } 

  

  


  return (
    <div className="bg-dark text-white min-h-screen flex flex-col md:flex-row">

      {/* Left Sidebar */}
      <aside className="hidden md:block md:w-64 bg-gray-900 p-4 border-r border-gray-800">
        <h2 className="text-xl font-bold mb-4">📚 Navigation</h2>
        <nav className="space-y-3">
          <a href="/families" className="block text-gray-300 hover:text-primary">👪 Familles</a>
          <a href="/ranking" className="block text-gray-300 hover:text-primary">🏆 Classement</a>
          <a href="/events" className="block text-gray-300 hover:text-primary">📅 Événements</a>
          <a href="/adventure" className="block text-gray-300 hover:text-primary">🗺️ Mode Aventure</a>
        </nav>
      </aside>

      {/* Mobile Menu Toggle */}
      <div className="md:hidden fixed top-0 left-0 w-full z-50">
        <details className="bg-gray-900 border-b border-gray-800">
          <summary className="p-4 cursor-pointer font-bold text-primary">📚 Menu</summary>
          <nav className="flex flex-col gap-3 p-4">
            <a href="/families" className="text-gray-300 hover:text-primary">👪 Familles</a>
            <a href="/ranking" className="text-gray-300 hover:text-primary">🏆 Classement</a>
            <a href="/events" className="text-gray-300 hover:text-primary">📅 Événements</a>
            <a href="/adventure" className="text-gray-300 hover:text-primary">🗺️ Mode Aventure</a>
          </nav>
        </details>
      </div>

      {/* Feed Section */}
      <main className="flex-1 mt-16 md:mt-0 p-4">
        <h1 className="text-2xl font-bold mb-4 text-primary">📰 Fil d'actualité</h1>
        {/* Simulated Feed Item */}
        <div className="bg-gray-800 rounded-xl p-4 mb-4">
          <p className="text-white">Naruto a défié Sasuke dans la vallée de la fin ! ⚔️🔥</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 mb-4">
          <p className="text-white">Un nouveau tournoi a été lancé, participe maintenant ! 🏆</p>
        </div>

        <div className="bg-gray-800 rounded-xl p-4 mb-4">
          <button onClick={getPosts} className="text-white">get posts</button>
        </div>

      </main>

      {/* Right Sidebar */}
      <aside className="hidden lg:block lg:w-72 bg-gray-900 p-4 border-l border-gray-800">
        <h2 className="text-xl font-bold mb-4">🥇 Top Joueurs</h2>
        <ul className="text-sm space-y-2">
          <li>1. ItachiUchiwa</li>
          <li>2. SakuraStorm</li>
          <li>3. KakashiHunt</li>
        </ul>

        <h2 className="text-xl font-bold mt-6 mb-4">🏅 Top Familles</h2>
        <ul className="text-sm space-y-2">
          <li>1. Clan Uchiha</li>
          <li>2. Clan Hyuga</li>
          <li>3. Clan Nara</li>
        </ul>

        <div className="mt-6">
          <a href="/family-chat" className="inline-block bg-primary hover:bg-orange-700 text-white px-4 py-2 rounded-full text-sm font-semibold">💬 Accéder au chat familial</a>
        </div>
      </aside>

      {/* Mobile Bottom Floating Right Panel */}
      <div className="fixed bottom-4 right-4 lg:hidden">
        <details className="bg-gray-900 rounded-xl shadow-lg">
          <summary className="px-4 py-2 text-sm font-bold text-primary cursor-pointer">📊 Infos</summary>
          <div className="p-3 text-sm space-y-3">
            <div>
              <h4 className="font-bold text-white">Top Joueurs</h4>
              <ul className="text-gray-400">
                <li>1. ItachiUchiwa</li>
                <li>2. SakuraStorm</li>
                <li>3. KakashiHunt</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white">Top Familles</h4>
              <ul className="text-gray-400">
                <li>1. Clan Uchiha</li>
                <li>2. Clan Hyuga</li>
                <li>3. Clan Nara</li>
              </ul>
            </div>
            <div>
              <a href="/family-chat" className="text-primary hover:underline">💬 Chat familial</a>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}

import React from "react";

export default function TopNav() {
    return (
        <nav className="top-nav bg-gray-950 relative bg-opacity-50 w-full z-10 py-2" >
        <div className="max-w-7xl mx-auto px-2 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
                <div className="flex items-center">
                    <a href="/home" className="logo-container flex-shrink-0">    
                    <img className="h-20 w-auto" src="http://localhost:8000/static/images/logo/logo_1_nobg.png" alt="Roleplay Verse Logo" />
                    </a>
                    <div id="mobile-search" className="hidden md:block ml-4 ">
                        <div className="relative">
                            <input type="text" id="searchInput" className="bg-gray-900 border border-gray-700 w-64 text-white px-4 py-2 rounded-full  focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="recherche..." />
                            <button  className="absolute right-3 top-2 text-gray-400 hover:text-white">
                                
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" width="24" height="24" viewBox="0 0 512 512"><path fill="currentColor" d="m479.6 399.716l-81.084-81.084l-62.368-25.767A175.014 175.014 0 0 0 368 192c0-97.047-78.953-176-176-176S16 94.953 16 192s78.953 176 176 176a175.034 175.034 0 0 0 101.619-32.377l25.7 62.2l81.081 81.088a56 56 0 1 0 79.2-79.195ZM48 192c0-79.4 64.6-144 144-144s144 64.6 144 144s-64.6 144-144 144S48 271.4 48 192Zm408.971 264.284a24.028 24.028 0 0 1-33.942 0l-76.572-76.572l-23.894-57.835l57.837 23.894l76.573 76.572a24.028 24.028 0 0 1-.002 33.941Z"/></svg>
                            </button>
                            <button id="hide-search-btn" className="absolute right-3 top-2 text-gray-400 hover:text-white hidden">
                                
                                <svg  className="w-6 h-6 text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18 17.94 6M18 18 6.06 6"/>
                                </svg>
                                
                            </button>
                            <div id="searchResults" data-scope="global" className="searchResults absolute left-0 right-0 text-white mt-2 mx-0 p-3 bg-gray-900 rounded-lg shadow-lg z-10 overflow-y-auto hidden" >
                                <h2 className="font-bold">Résultat de la recherche</h2>
                                <div id="results">

                                </div>
                                
                                    <div id="searchLoader" className="text-center py-4 hidden">
                                        <i  className="fas fa-spinner fa-spin text-orange-500"></i> 
                                    </div> 
                                
                           </div>
                        </div>
                    </div>
                    <div className="md:hidden ml-4 flex items-center">
                        <button id="mobile-search-btn" className="text-gray-400 hover:text-white">
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" width="24" height="24" viewBox="0 0 512 512"><path fill="currentColor" d="m479.6 399.716l-81.084-81.084l-62.368-25.767A175.014 175.014 0 0 0 368 192c0-97.047-78.953-176-176-176S16 94.953 16 192s78.953 176 176 176a175.034 175.034 0 0 0 101.619-32.377l25.7 62.2l81.081 81.088a56 56 0 1 0 79.2-79.195ZM48 192c0-79.4 64.6-144 144-144s144 64.6 144 144s-64.6 144-144 144S48 271.4 48 192Zm408.971 264.284a24.028 24.028 0 0 1-33.942 0l-76.572-76.572l-23.894-57.835l57.837 23.894l76.573 76.572a24.028 24.028 0 0 1-.002 33.941Z"/></svg>
                                
                        </button>
                    </div>
                </div>
    
                
                <div className="hidden md:flex items-center space-x-8">
                    <a href="/home" className="flex items-center text-gray-300 hover:text-white">
                        <svg className="h-8 w-8" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m4 12 8-8 8 8M6 10.5V19a1 1 0 0 0 1 1h3v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h3a1 1 0 0 0 1-1v-8.5"/>
                        </svg> Accueil</a>
                    <a href="/chats" className="text-gray-300 flex items-center hover:text-white"><svg className="w-8 h-8" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 10.5h.01m-4.01 0h.01M8 10.5h.01M5 5h14a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-6.6a1 1 0 0 0-.69.275l-2.866 2.723A.5.5 0 0 1 8 18.635V17a1 1 0 0 0-1-1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z"/>
                    </svg> Inbox</a>
                    <a href="/combats" className="flex items-center text-gray-300 hover:text-white"><svg className="w-8 h-8" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M16 20c3.72-2 6-4.73 6-8c0-2.66-1.54-5.1-4.11-7h-.07a7.533 7.533 0 0 1 1.86 5c0 3-1.68 5-4.18 6.83c0 .01-1.12.71-2.5 1.58v-1.08L15 16s-.2-.6-.42-1.54C16.6 13.58 18 11.69 18 9.5c0-2.16-1.36-4.03-3.35-4.93C14.84 3.63 15 3 15 3l-3-2l-3 2s.16.63.35 1.57C7.37 5.47 6 7.34 6 9.5c0 2.19 1.4 4.08 3.42 4.96C9.2 15.4 9 16 9 16l2 1.33v1.08c-1.38-.87-2.5-1.57-2.5-1.58C6 15 4.32 13 4.32 10c0-1.91.68-3.65 1.86-5h-.06C3.54 6.9 2 9.34 2 12c0 3.27 2.29 6 6 8l1-1.5l1.92 1.23L7.34 22L8 23l3-1.93V23h2v-1.93L16 23l.66-1l-3.58-2.27L15 18.5l1 1.5m.75-10.5c0 1.59-.99 2.96-2.44 3.69c-.17-.96-.31-2.07-.31-3.19c0-1.33.2-2.85.42-4.14c1.39.74 2.33 2.09 2.33 3.64m-9.5 0c0-1.55.94-2.9 2.34-3.64C9.8 7.15 10 8.67 10 10c0 1.12-.14 2.23-.31 3.19c-1.45-.73-2.44-2.1-2.44-3.69Z"/></svg> Combats </a>
                </div>
    
                
                <div className="flex items-center">
                    <div className="flex space-x-1 items-center">
                        <a onclick="showOverlay()" href="/notifications">
                            <button className="text-gray-300 flex items-center hover:text-white relative r-4">
                            
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" d="M4 19V9a8 8 0 0 1 16 0v10M1 19h22m-8 0v1a3 3 0 1 1-6 0v-1"/></svg>
                                <div id="notifier" className="notifier absolute top-[-10px] right-0  translate-middle bg-red-500 text-gray-200  rounded-full w-6 h-6 flex items-center justify-center"> 0</div>
                               
                            
                            
                        </button>
                        </a>
                        
                        <div className="relative" id="profileDropdown">
                            <button className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white">
                                <img className="h-8 w-8 rounded-full" src="{{player.profile_picture.url}}" alt="{{player}} profile" />
                            </button>
                            <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 hidden" id="profileMenu">
                                <a href="{% url 'users:player' player.user.username %}" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"><i className="fas fa-user mr-2"></i>  Profile</a>
                                
                                <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"><i className="fas fa-gear mr-2"></i>Settings</a> 
                                <a href="{% url 'users:logout' %}" className="block px-4 py-2 text-sm text-orange-600 hover:bg-gray-100"><i className="fas fa-sign-out mr-2"></i>Se déconnecter</a>
                            </div>
                        </div>
                    </div>
                    <div className="ml-4 flex items-center bg-gray-900 border border-gray-700 rounded-full px-2 py-1">
                        <span className="text-orange-500 text-sm font-bold mr-2">100 JC</span>
                        <a href="{% url 'core:battle_points' %}">
                            <button className="bg-orange-500 text-white rounded-full px-2 py-1 text-xs hover:bg-orange-600 transition duration-300">
                            <i className="fas fa-plus text-xs"></i>
                        </button>
                        </a>
                        
                    </div>
                </div>
    
                
            </div>
        </div>

        
        <div className="md:hidden hidden" id="mobileMenu">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                
                <a href="{% url 'core:home' %}" className="text-gray-300 text-xl hover:text-white block px-3 py-2"><i className="fas fa-home mr-2"></i>Home</a>
                <a href="{% url 'chats:all' %}" className="text-gray-300 text-xl hover:text-white block px-3 py-2"><i className="fas fa-comments mr-2"></i>Chats</a>
                <a href="{% url 'battles:index' %}" className="text-gray-300 text-xl hover:text-white block px-3 py-2"><i className="fas fa-khanda mr-2"></i>Battles</a>
            </div>
        </div>
    </nav>
    );
    }
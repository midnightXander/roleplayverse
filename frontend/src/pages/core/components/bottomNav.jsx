import React from "react";

export default function BottomNav() {
    return (
        <div className="bottom-nav border-t border-gray-700 bg-gray-950 flex justify-center  space-x-6 bg-opacity-90 fixed bottom-0 w-full z-10 py-2 md:hidden animate-scaleIn">
            <a onclick="showOverlay()" href="{% url 'core:home' %}" className="bottom-nav-link text-gray-300 px-4 py-2 rounded-full hover:bg-gray-700 bg-opacity-50 ">
                <svg className=" text-orange-500 text-4xl" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m4 12 8-8 8 8M6 10.5V19a1 1 0 0 0 1 1h3v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h3a1 1 0 0 0 1-1v-8.5"/>
                </svg>
            </a>
            <a onclick="showOverlay()" href="{% url 'chats:all' %}" className="bottom-nav-link text-gray-300 px-4 py-2 rounded-full hover:bg-gray-700 bg-opacity-50">
                <svg className=" text-orange-500 text-4xl" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 10.5h.01m-4.01 0h.01M8 10.5h.01M5 5h14a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-6.6a1 1 0 0 0-.69.275l-2.866 2.723A.5.5 0 0 1 8 18.635V17a1 1 0 0 0-1-1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z"/>
                </svg>
            </a>
            <a onclick="showOverlay()" href="{% url 'battles:index' %}" className="bottom-nav-link text-orange-500 px-4 py-2 rounded-full hover:bg-gray-700 bg-opacity-50">
                <svg className=" text-orange-500 text-4xl" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M16 20c3.72-2 6-4.73 6-8c0-2.66-1.54-5.1-4.11-7h-.07a7.533 7.533 0 0 1 1.86 5c0 3-1.68 5-4.18 6.83c0 .01-1.12.71-2.5 1.58v-1.08L15 16s-.2-.6-.42-1.54C16.6 13.58 18 11.69 18 9.5c0-2.16-1.36-4.03-3.35-4.93C14.84 3.63 15 3 15 3l-3-2l-3 2s.16.63.35 1.57C7.37 5.47 6 7.34 6 9.5c0 2.19 1.4 4.08 3.42 4.96C9.2 15.4 9 16 9 16l2 1.33v1.08c-1.38-.87-2.5-1.57-2.5-1.58C6 15 4.32 13 4.32 10c0-1.91.68-3.65 1.86-5h-.06C3.54 6.9 2 9.34 2 12c0 3.27 2.29 6 6 8l1-1.5l1.92 1.23L7.34 22L8 23l3-1.93V23h2v-1.93L16 23l.66-1l-3.58-2.27L15 18.5l1 1.5m.75-10.5c0 1.59-.99 2.96-2.44 3.69c-.17-.96-.31-2.07-.31-3.19c0-1.33.2-2.85.42-4.14c1.39.74 2.33 2.09 2.33 3.64m-9.5 0c0-1.55.94-2.9 2.34-3.64C9.8 7.15 10 8.67 10 10c0 1.12-.14 2.23-.31 3.19c-1.45-.73-2.44-2.1-2.44-3.69Z"/></svg>
            </a>
            <a onclick="showOverlay()" href="{% url 'users:player' player.user.username %}" className="bottom-nav-link text-gray-300 bottom-nav-link px-4 py-2 rounded-full hover:bg-gray-700 bg-opacity-50">
                <svg className=" text-orange-500 text-4xl" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0 0a8.949 8.949 0 0 0 4.951-1.488A3.987 3.987 0 0 0 13 16h-2a3.987 3.987 0 0 0-3.951 3.512A8.948 8.948 0 0 0 12 21Zm3-11a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
                </svg>
            </a>
    
        </div>  
    );
    }
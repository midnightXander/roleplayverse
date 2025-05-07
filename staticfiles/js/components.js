
// Function to create a post element
// // Function to create a post element
function createPostElement(post) {
    const postElement = document.createElement('div');
    postElement.className = 'post bg-gray-700 rounded-lg p-4';
    const postElement2 = document.createElement('div');
    postElement2.className = 'post bg-gray-900 rounded-2xl shadow-sm p-4 border border-gray-800';
    //postElement.className = 'post-gradient rounded-xl p-6 border border-gray-700 hover-scale'
    // <span class='ellipsed-text body'>${comment.body}<span>
    //     <span class = 'full-text hidden body'>${comment.body}</span>

    
    //imgModalListener()
    
    //return postElement;
    
    postElement2.innerHTML = `
    <div class="flex items-start  gap-4">
            <img src="${post.author.profile_picture}" alt="${post.author.player}" class="myImg w-10 h-10 rounded-full" />
            <div class="flex-1">
              <div class="flex justify-between text-sm text-gray-400">
                <div>
                  <a onlick = 'showOverlay()' href = "/users/${post.author.name}" class="inline-block font-semibold hover:text-orange-600 text-white">${post.author.player}</a> @${post.author.nickname}
                </div>
                
    
                 <div class="relative flex space-x-2 ">
                  <span>${post.time_posted}</span>
                  <button onclick = 'togglePostDropdown(this)'  class="text-gray-300 hover:text-white focus:outline-none post-dropdown-toggle" data-post-id="${post.id}">
                      <i class="fas fa-ellipsis-v"></i>
                  </button>
                  <div class="post-dropdown-menu rounded-xl bg-opacity-80 bg-gray-900 border border-gray-700 w-48 py-2">
                        
                        <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="toggleToFavorites('${post.id}')">
                        ${post.is_favorite ? "<i class = 'fas fa-bookmark mr-2'></i>retirer des favoris":"<i class = 'far fa-bookmark mr-2'></i>ajouter aux favoris"}
                        </div>
                        
                        <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="socialShare(this,'https://roleplayverse.live/posts/${post.id}')"><i class = 'fas fa-share-alt mr-2'></i>Partager</div>
                        <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="copyLink('https://roleplayverse.live/posts/${post.id}')"><i class = 'fas fa-copy mr-2'></i>copier le lien</div>
                        ${post.author.name == currentPlayerData.username? 
                        `
                        <!--
                        <a href="#" class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600"><i class = 'fas fa-pencil-square-o mr-2'></i> Edit</a>
                        -->
                        <div class="block px-4 py-2 cursor-pointer text-red-500 text-sm text-gray-300 hover:bg-gray-600"  onclick="deletePost(this,'${post.id}')"><i class = 'fas fa-trash  mr-2'></i> Supprimer</div>
                        `:`
                      `}
                       
                    </div>
                </div>
              </div>
              
              <p onclick = 'toggleExpand(this)' class="body text-base text-gray-100 mt-1" data-expandable>
                
              </p>
             
                ${post.image ? `
                <div class="mt-3">
                <img  src='/static/images/loaders/img-loader.gif' onload = "replacePlaceholder(this, '${post.image}')" alt="${post.author.player} image de publication" class="w-full myImg rounded-xl border-1 border-gray-700 object-cover h-auto max-h-96" />
              </div>
                ` : ''}
              
              <div class="flex justify-between mt-4 text-gray-400 text-sm">
                <button class="like-button flex items-center space-x-1 hover:text-orange-500 ${post.liked ? 'liked' : ''}" data-post-id="${post.id}">
                <i class="far fa-heart"></i>
                <span class="like-count">${post.likes}</span>
                </button>
                <button class="comment-button flex items-center space-x-1 hover:text-blue-500">            
                <i class="far fa-comment"></i>
                <span class = 'comment-count'>${post.n_comments}</span>
                </button>

                
                <button class="flex items-center space-x-1 hover:text-orange-500" onclick="toggleToFavorites('${post.id}')">
                  <i class = 'far fa-bookmark'></i>
                </button>
                
                <button class="flex items-center space-x-1 hover:text-green-500" onclick="socialShare(this,'https://roleplayverse.live/posts/${post.id}')">
                  <i class = 'fas fa-share-alt'></i><span>partager</span>
                </button>
              </div>
    
               
    
              <div class="mt-4 space-y-3 comments max-h-64 overflow-y-auto" style='max-height:300px'>
                 ${post.comments.map(comment =>createComment(comment)).join('')}
              </div>
    
               <form onsubmit='sendComment(this, event)' class="comment-form mt-4" data-post-id = ${post.id}>
                    <input type="text" class="bg-gray-800 text-white p-2 rounded w-full  border-0  focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="ajoute un commentaire...">
                </form>
    
              
        
            </div>
          </div>
    `

    // Escape the post body and set it as text content
    const postBodyElement = postElement2.querySelector('p[data-expandable]');
    postBodyElement.textContent = post.body;
    postBodyElement.setAttribute('data-full', post.body_full);
    return postElement2
    }

    function createComment(comment){
      var c_player = {
          'username': '{{player.user.username}}',
          'player':'{{player}}',
      }

  return `
  
                      <div class="flex comment rounded-xl items-start space-x-3" data-toggle="tooltip" data-placement='top' title = '${comment.body}'>
                          <a class = "font-semibold inline-block  hover:text-orange-500" href='/users/${comment.author.username}'>
                                   <img src="${comment.author.profile_picture}"  alt="${comment.author.username}" class="w-8 h-8 rounded-full"> 
                          </a>
                          <div class="flex-1  rounded-lg p-1">
                              <div class="flex items-center justify-between mb-1 relative">
                                  <div class="flex items-center space-x-2">
                                      <a href='/users/${comment.author.username}' class="text-orange-500 text-sm font-semibold inline-block hover:text-orange-600 ">${comment.author.player}</a>
                                      <!--
                                      <span class="text-xs text-gray-400">${comment.timestamp}</span>
                                      -->
                                  </div>
                                  <div class="absolute top-0 right-2">
                                      <button onclick = 'toggleDropdown(this)' class="text-gray-400 hover:text-white post-dropdown-toggle">
                                          <i class="fas fa-ellipsis-h"></i>
                                      </button>

                                      <div class="post-dropdown-menu bg-gray-800 w-48 py-2">
                                          <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="copyLink('${comment.body}')"><i class = 'fas fa-copy mr-2'></i>copier</div>
                                          <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick=""><i class = 'fas fa-flag mr-2'></i> signaler</div>
                                          
                                          ${comment.author.username == c_player.username ?  `
                                          
                                          <div class="block px-4 py-2 cursor-pointer text-red-500 text-sm text-gray-300 hover:bg-gray-600"  onclick="deleteComment(this,'${comment.id}')"><i class = 'fas fa-trash  mr-2'></i> Supprimer</div>
                                          `:``}
                                      </div>
                                  </div>    
                          </div>
                          
                          <p onclick = 'toggleExpand(this)' class="body text-sm text-gray-300" data-expandable data-full='${comment.body_full}'>${comment.body}</p>
                          
                          
                          <div class="flex items-center space-x-4 mt-2 text-sm">
                                  
                                  <span class="text-xs text-gray-400">${comment.timestamp}</span>
                                  <button data-comment-id="${comment.id}" class='text-xs comment-like-button  rounded-full ${comment.liked ? 'liked' : ''}'>
                                      <i class="far fa-heart  mr-1"></i>
                                      <span class='comment-likes-count'>${comment.likes}</span>
                                  </button>
                                  <button data-comment-id="${comment.id}" class="reply-button text-gray-400 text-xs hover:text-orange-500">Reply</button>
                                  <!--
                                  <span class="text-gray-400">5 likes</span>
                                  -->
                              </div>
                          </div>
                      </div>
  `
  
}
    
function battleStatusToFrench(status){
    if(status == 'not_started') return "pas commencé"
    if(status == 'ongoing') return "en cours"
    if(status == 'waiting_refree') return "en attente d'arbitrage"

    return status
}

function battleTypeToFrench(type){
    if(type == 'friendly') return "Amicale"
    if(type == 'stake') return "Enjeu"

    return type
}


function  createBattleElement(battle){
  const battleElement = document.createElement('div')
  battleElement.className = 'battle-card  bg-gray-900 border border-gray-700 rounded-2xl p-6 flex flex-col';
  const status = battleStatusToFrench(battle.status)
  const type = battleTypeToFrench(battle.type)

  battleElement.innerHTML = `
                              <div class="flex justify-between items-center mb-4">
                                  <h3 class="text-xl font-bold">${status}</h3>
                                  <span class="bg-blue-500 text-white px-2 py-1 rounded-full text-sm">${type}</span>
                              </div>
                              <div class="flex justify-between items-center mb-4 flex-col">
                                  <div class="flex items-start">
                                      <img src="${battle.initiator.profile_picture}" alt="${battle.initiator.player}" class="w-12 h-12 rounded-full mr-4">
                                      <div>
                                          <a href="/users/${battle.initiator.username}" class="font-bold hover:text-orange-500 ">
                                              ${battle.initiator.player}<span class ='text-sm text-semibold text-gray-600'>@${battle.initiator.nickname}</span> ${ battle.winner ? (battle.winner.id == battle.initiator.id ? "<span class='text-green-500'>W</span>": ''):''}
                                          </a>
                                          <p class="text-sm text-gray-400">Rank: ${battle.initiator.rank}</p>
                                      </div>
                                  </div>
                                  <i class="fas fa-bolt text-yellow-500 text-2xl"></i>
                                  <div class="flex items-end">
                                      <div class="text-right mr-4">
                                          <a href="/users/${battle.opponent.username}" class="font-bold hover:text-orange-500 ">
                                              ${battle.opponent.player}<span class ='text-sm text-semibold text-gray-600'>@${battle.opponent.nickname}</span> ${ battle.winner ? (battle.winner.id == battle.opponent.id ? "<span class='text-green-500'>W</span>": ''):''}
                                          </a>
                                          <p class="text-sm text-gray-400">Rank: ${battle.opponent.rank}</p>
                                      </div>
                                      <img src="${battle.opponent.profile_picture}" alt="${battle.opponent.player}" class="w-12 h-12 rounded-full">
                                  </div>
                              </div>
                              ${battle.can_refree ? `<button data-battle_id="${battle.id}" class= "proposal-btn border border-purple-500 text-purple-500 px-4 py-2 rounded-lg hover:bg-purple-600 transition duration-300 mt-auto">
                                  <i class="fas fa-gavel mr-2"></i>Arbitrer le combat
                              </button>`:`
                              <div class='flex justify-between items-center' > 
                              <a onclick = 'showOverlay()' href="/battles/battle_room/${battle.id}" class="inline-block bg-transparent border border-orange-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition duration-300 mt-auto">
                                      voir le combat 
                              </a>

                              <div><i class="fas fa-eye mr-2"></i>: <span  class='text-orange-500' >${battle.spectators}</span></div>
                              <div>
                              
                              ` }
                          `
  
  return battleElement
}


function toggleSection(id) {
    const section = document.getElementById(id);
    const list = section.querySelector('.request-list');
    const arrow = section.querySelector('.arrow');
    const isOpen = list.classList.toggle('hidden');
    arrow.classList.toggle('rotate-90', !isOpen);
}
      
function createCollapsedRequest(request){

    return `
    <div class="battle-card p-4 flex justify-between items-center">
        <span>avec <span class="text-yellow-500">${request.character}</span> — ${request.type}</span>
        <button data-url="{% url 'battles:accept' ${request.id} %}" data-requesttype="${request.type}" data-character="${request.character}" data-requestsender="${request.sender}" 
        class="accept-button bg-green-600 hover:bg-green-700 text-white text-sm px-3 py-1 rounded">Accepter</button>
    </div>
    `
}

function createCollapsedRequests(requestData){
    const requestElement = document.createElement('div')
    requestElement.className = 'border border-gray-700 mb-4 rounded-2xl bg-opacity-90 bg-gray-900'
    requestElement.setAttribute('id', `${requestData.sender}-requests`)

    requestElement.innerHTML = `
            <div 
                class="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-700 rounded-xl transition" 
                onclick="toggleSection('${requestData.sender}-requests')"
              >
                <div class="text-lg flex font-semibold"><img src="{{data.sender.profile_picture.url}}" class="w-8 h-8 border border-orange-500 rounded-full mr-2"> {{data.sender}} - <span class="text-orange-500" >{{data.sender.rank}} </span> ({{data.length}} Requêtes)</div>
                <svg 
                  class="w-4 h-4 transition-transform transform arrow" 
                  fill="none" stroke="currentColor" stroke-width="2" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </div>
    
              <div class="request-list hidden divide-y divide-gray-700">
              ${requestData.requests.map(request => createCollapsedRequest(request)).join('')}
            </div>
    
    `

    return requestElement
    

    // return `
    
    // <div class="border border-gray-700 mb-4 rounded-2xl bg-opacity-90 bg-gray-900" id="{{data.sender}}-requests">
    //           <div 
    //             class="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-700 rounded-xl transition" 
    //             onclick="toggleSection('{{data.sender}}-requests')"
    //           >
    //             <div class="text-lg flex font-semibold"><img src="{{data.sender.profile_picture.url}}" class="w-8 h-8 border border-orange-500 rounded-full mr-2"> {{data.sender}} - <span class="text-orange-500" >{{data.sender.rank}} </span> ({{data.length}} Requêtes)</div>
    //             <svg 
    //               class="w-4 h-4 transition-transform transform arrow" 
    //               fill="none" stroke="currentColor" stroke-width="2" 
    //               viewBox="0 0 24 24"
    //             >
    //               <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
    //             </svg>
    //           </div>
    
    //           <div class="request-list hidden divide-y divide-gray-700">
    //             {% for request in  data.requests %}
    //             <div class="battle-card p-4 flex justify-between items-center">
    //               <span>avec <span class="text-yellow-500">{{request.character}}</span> — {{request.type}}</span>
    //               <button data-url="{% url 'battles:accept' request.id %}" data-requesttype="{{request.type}}" data-character="{{request.character}}" data-requestsender="{{request.sender}}" 
    //                class="accept-button bg-green-600 hover:bg-green-700 text-white text-sm px-3 py-1 rounded">Accepter</button>
    //             </div>
    //             {% endfor %}
        
    //           </div>
    //         </div>
    
    // `
}

function createRequest(request){

  return `
   <div class="battle-card border border-gray-600 shadow-md rounded-lg p-6 flex flex-col">
                      <div class="flex justify-between items-center mb-4">
                          <h3 class="text-xl font-bold">RDC</h3>
                          <span class="bg-yellow-500 text-gray-800 px-2 py-1 rounded-full text-sm">${request.type}</span>
                      </div>
                      <div class="flex justify-between items-center mb-4">
                          <div class="flex items-center">
                              <a href="/users/${request.sender.username}">
                                  <img src="${request.sender.profile_picture}" alt="Challenger" class="w-12 h-12 rounded-full mr-4">
                              </a>
                              <div>
                                  
                                  <a href="/users/${request.sender.username}" class="font-bold">${request.sender.player}</a>
                                  <p class="font-bold ">avec <span class="text-yellow-500">${request.character}</span></p>
                                  <p class="text-sm text-gray-400">Rang: ${request.sender.rank}</p>

                                  <small class=" font-bold text-sm text-gray-400">${request.date_sent}</small>
                              </div>
                          </div>
                          <i class="fas fa-bolt text-yellow-500 text-2xl"></i>
                          
                      </div>
                      <button class="accept-button border border-green-500 text-green-500 px-4 py-2 rounded-lg hover:bg-green-600 transition duration-300" data-url="/battles/accept/${request.id}" data-requesttype="${request.type}" data-character="${request.character}" data-requestsender="${request.sender.player}">
                          <i class="fas fa-check mr-2"></i>Accepter
                      </button>

              </div>
                        
  
  `

}

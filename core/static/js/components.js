function likePost(likeButton, postId, reaction = "🔥"){
        $(likeButton).toggleClass('animate__animated animate__heartBeat')
        $.ajax({
            url:  `/post/react/${postId}`,
            type:'POST',
            data: { reaction : reaction },
            beforeSend: function(){
                
            },
            success: function(res){
                
                document.querySelector(`#like-count-${postId}`).textContent = res.likes
                if(res.message == 'liked'){
                    // if(!document.querySelector(`#like-button-${postId}`).classList.contains('liked')){
                    //     document.querySelector(`#like-button-${postId}`).classList.add('liked');
                    // }

                }else if(res.message == 'unliked'){
                    likeButton.classList.remove('liked');
                }
            },
            complete: function(){
                
            },
            error: function(jqXHR, textstatus, errorThrown){
                
                showMyToast('an error occured please try again', 'error')
            }
            
        })
    }

function openCommentPopup(postId) {

    const popup = document.getElementById('commentPopup');
    popup.classList.remove('hidden');
    popup.classList.remove('fade-out-down');
    popup.classList.add('fade-in-up');

    

    getPostData(postId)

  }


  function closeCommentPopup() {
    const popup = document.getElementById('commentPopup');
    popup.classList.remove('fade-in-up');
    popup.classList.add('fade-out-down');
    setTimeout(() => {
      popup.classList.add('hidden');
    }, 300);
  }

  document.addEventListener('click', (e) => {
    const popup = document.getElementById('commentPopup');
    const content = document.getElementById('popupContent');
    if (!popup.classList.contains('hidden') && !content.contains(e.target) && !e.target.closest('button[onclick^="loginDecorator"]') && !e.target.closest('button[onclick^="openCommentPopup"]')) {
      closeCommentPopup();
    }
  });

  function getPostData(postId){
    const popupContent = document.getElementById('popupContent');
    const commentForm = popupContent.querySelector('#sendCommentForm');
    commentForm.setAttribute('data-post-id', postId)

    const commentsContainer = document.getElementById('comments-space')
    const loader = document.createElement("div")
            loader.classname = 'text-center flex space-x-2 w-full justify-center items-center'
            loader.innerHTML = `
            <i class="fas fa-spinner fa-spin text-orange-500"></i> 
            <span class="text-gray-400 text-sm "> Loading...</span>
            `
    $.ajax({
        url: `/post/${postId}/comments`,
        type: 'GET',
        data: {
            'Content-Type': 'application/json'
        },
        beforeSend: function(){
            commentsContainer.innerHTML = ''
            commentsContainer.append(loader);
        },
        success: function(res){
            const comments = res.comments
            if(comments.length > 0){
                comments.forEach(comment => {
                commentsContainer.append(createComment2(comment))
            });
            }else{
                commentsContainer.innerHTML = `
                    <p class = 'text-gray-500 text-center px-4 py-8'>
                        Soit le premier a commenter
                    </p>
                `
            }
        },
        complete: function(){
            loader.remove()
        },
        error: function(jqXHR, textstatus, errorThrown){
            showMyToast('An Error occurred, please try again','error')
        }
    })
}

    function showCommentReplyForm(commentId) {
    console.log($(`#comment-replies-${commentId}`).siblings('.reply-form').toggleClass('hidden'))
    //document.getElementById(`replies-${commentId}`).nextSibling('.reply-form').classList.toggle('hidden');
    }
    const showCommentReplies = (commentId) => {
        //document.getElementById(`comment-replies-${commentId}`).classList.toggle('hidden')
        const repliesSection = document.getElementById(`comment-replies-${commentId}`) 
        repliesSection.classList.toggle('hidden')
        const replies = repliesSection.querySelectorAll('.comment')
        //repliesSection.innerHTML = ''
        replies.forEach(commentElement => {
            repliesSection.appendChild(commentElement)
        });
    }
    

  function createComment2(comment){

    var c_player = {
        'username': '{{player.user.username}}',
        'player':'{{player}}',
    }

    
    
    const commentElement = document.createElement('div');
    commentElement.className = `comment ${comment.parent ? '' : `parent-comment`} flex items-start mb-4 gap-3`;
    commentElement.id = `${comment.parent ? '' : `parent-comment-${comment.id}`}`
    commentElement.setAttribute('data-id', comment.id)
    commentElement.innerHTML = `
                <a class = "inline-block" href='/users/${comment.author.username}'>
                <img src="${comment.author.profile_picture}" alt="avatar" class="rounded-full border border-orange-500 w-10 h-10" />
                </a>
                
                <div class="flex-1">
                        <a href='/users/${comment.author.username}' onclick = 'showOverlay();' class="text-sm font-semibold hover:text-orange-500 ">${comment.author.player} ${comment.parent ? ` <i class='fas fa-caret-right text-orange-500' ></i> <span class = 'text-gray-400'>${comment.parent.author.player}</span>`: ''}</a>
                        <p onclick = 'toggleExpand(this)' class="body text-sm text-gray-300" data-expandable data-full='${comment.body_full}'>${comment.body}</p>
                            <div class="absolute top-0 right-2">
                                <button onclick = 'toggleDropdown(this);' class="text-gray-400 hover:text-white post-dropdown-toggle">
                                    <i class="fas fa-ellipsis-h"></i>
                                </button>
    
                                <div class="post-dropdown-menu hidden rounded-xl border border-gray-700 bg-gray-800 w-48 py-2">
                                    <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="copyLink('${comment.body}')"><i class = 'fas fa-copy mr-2'></i>copier</div>
                                    <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick=""><i class = 'fas fa-flag mr-2'></i> signaler</div>
                                    
                                    ${comment.author.username == currentPlayerData.username ?  `
                                    
                                    <div class="block px-4 py-2 cursor-pointer text-red-500 text-sm text-gray-300 hover:bg-gray-600"  onclick="deleteComment(this,'${comment.id}')"><i class = 'fas fa-trash  mr-2'></i> Supprimer</div>
                                    `:``}
                            </div>
                            </div>    
                        <div class="flex items-center gap-4 mt-1 text-xs text-gray-500">
                        <span>${comment.timestamp}</span>
                        <button data-comment-id="${comment.id}" class='text-xs comment-like-button  rounded-full ' class="comment-like-button hover:text-orange-500 ${comment.liked ? 'liked' : ''}">
                            <i class="fa-regular fa-thumbs-up mr-1"></i> 
                            <span class='comment-likes-count'>${comment.likes}</span>
                        </button>
                        <button onclick = "showCommentReplyForm('${comment.id}')" class="hover:underline">Répondre</button>
                    </div>
                       
                    ${comment.replies.length > 0 && comment.parent == null  ? `
                        <button onclick="showCommentReplies('${comment.id}')" class="ml-4 mt-2 mb-4 text-sm text-gray-600 hover:text-orange-500 dark:text-gray-400">voir les reponses</button>
                        ` : ''}

                         <div class='reply-form flex flex-col space-y-2 my-2 hidden'>
                            <textarea id="comment-reply-${comment.id}" class='w-full bg-transparent text-white placeholder-gray-400 border-b border-gray-700 focus:outline-none resize-none' placeholder="Repondre a ${comment.author.username} ..."></textarea>
                            <button onclick="addCommentReply(this,'${comment.id}', '${comment.post_id}')">Soumettre</button>
                        </div>

                        <div class='mb-2 max-h-96 overflow-y-auto hidden' id="comment-replies-${comment.id}">
                        ${comment.replies
                            .map(
                                (reply) => `
                            <!--
                                <div class='text-sm mb-2 flex space-x-2'>
                                    <img src = '${reply.author.profile_picture}' class='w-8 h-8 rounded-full inline-block' />
                                    <div>
                                    <p><a href='/users/${reply.author.username}' onclick='showOverlay()' >${reply.author.username}</a> ${reply.parent ? ` <i class='fas fa-caret-right text-orange-500' ></i> <span class = 'text-gray-400'>${reply.parent.author.player}</span>`: ''} </p>
                                    <p>${reply.body_full}</p>
                                    <small class='text-sm text-gray-400'>${reply.timestamp}</small>
                                    </div>   
                            </div>
                            -->
                        `

                            )
                            .join("")}
                            </div>
                  <div></div>
                </div>
    `;

    comment.replies.forEach(reply => 
    commentElement.querySelector(`#comment-replies-${comment.id}`).appendChild(createComment2(reply)) )

    return commentElement;
    
    }

//Function to create comment element
function createComment(comment){

    var c_player = {
        'username': '{{player.user.username}}',
        'player':'{{player}}',
    }
    const commentElement = document.createElement('div');
    commentElement.className = 'flex comment rounded-xl items-start space-x-3';
    commentElement.innerHTML = `
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

                                    <div class="post-dropdown-menu rounded-xl border border-gray-700 bg-gray-800 w-48 py-2">
                                        <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="copyLink('${comment.body}')"><i class = 'fas fa-copy mr-2'></i>copier</div>
                                        <div class="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick=""><i class = 'fas fa-flag mr-2'></i> signaler</div>
                                        
                                        ${comment.author.username == currentPlayerData.username ?  `
                                        
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
    
    `;
    return commentElement;
}

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
            <img src="${post.author.profile_picture}" alt="${post.author.name}" class="myImg w-10 h-10 rounded-full" />
            <div class="flex-1">
              <div class="flex justify-between relative text-sm text-gray-400">
                <div class="sm:truncate inline-block">
                  <a onclick = 'showOverlay()' href = "/users/${post.author.name}" class="inline-block  font-semibold hover:text-orange-600 text-white">${post.author.name}</a> @${post.author.nickname}
                </div>
                
    
                 <div class="relative flex space-x-2 ">
                 <span class="text-xs">${post.time_posted}</span>   
                 <span class="px-2 py-1 bg-gray-800 text-gray-200 text-xs rounded-full border border-gray-700 font-semibold shadow">${ post.category }</span>
                  
                  <button onclick = 'togglePostDropdown(this)'  class="text-gray-300 hover:text-white focus:outline-none post-dropdown-toggle" data-post-id="${post.id}">
                      <i class="fas fa-ellipsis-v"></i>
                  </button>
                  <div class="post-dropdown-menu fade-in rounded-xl bg-opacity-80 bg-gray-900 border border-gray-700 w-48 py-2">
                        
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
              
              <p onclick = 'toggleExpand(this)' class="body  text-gray-100 mt-1" data-expandable>
                
              </p>
             
                ${post.image ? `
                <div class="mt-3">
                <img  src='/static/images/loaders/img-loader.gif' onload = "replacePlaceholder(this, '${post.image}')" alt="${post.author.player} image de publication" class="w-full myImg rounded-xl border-1 border-gray-700 object-cover h-auto max-h-[500px]" />
              </div>
                ` : ''}
              
              <div class="flex relative justify-between mt-4 text-gray-400 text-sm">
                <div id = "${post.id}-post-reactions" class="reactions bg-gray-800 fade-in-up absolute left-0 top-0 hidden flex space-x-2  mx-2 right-0  border border-gray-700 text-gray-300 text-sm p-2 rounded-3xl shadow-lg">
                    <button class='hover:scale-105 text-xl reaction-button' onclick = "loginDecorator(likePost,null,this, ${post.id},'🔥')">🔥</button>
                    <button class='hover:scale-105 text-xl reaction-button' onclick = "loginDecorator(likePost,null,this, ${post.id},'😂')" >😂</button>
                    <button class='hover:scale-105 text-xl reaction-button' onclick = "loginDecorator(likePost,null,this, ${post.id},'😲')" >😲</button>
                    <button class='hover:scale-105 text-xl reaction-button' onclick = "loginDecorator(likePost,null,this, ${post.id},'☹️')" >☹️</button>
                </div>
                <div  class="flex items-center space-x-1 hover:text-orange-500 ${post.liked ? 'liked' : ''}" data-post-id="${post.id}">
                <button onclick = "toggleElement(this,'${post.id}-post-reactions')" class = "" >${post.most_reaction}</button>
                <button onclick="openReactorsPopup('/posts/reactors/${post.id}')" class="like-count" id="like-count-${post.id}">${post.likes}</button>
                </div>
                <button onclick = "loginDecorator(openCommentPopup,null,'${post.id}')" class="comment-button flex items-center space-x-1 hover:text-blue-500">            
                <i class="far fa-comment"></i>
                <span class = 'comment-count'>${post.n_comments}</span>
                </button>

                
                <button class="flex items-center space-x-1 hover:text-orange-500" onclick="loginDecorator(toggleToFavorites,null,'${post.id}')">
                  <i class = 'far fa-bookmark'></i>
                </button>
                
                <button class="flex items-center space-x-1 hover:text-green-500" onclick="socialShare(this,'https://roleplayverse.live/posts/${post.id}')">
                  <i class = 'fas fa-share-alt'></i><span>partager</span>
                </button>
              </div>
    
               
            <!--
              <div class="mt-4 space-y-3 comments max-h-64 overflow-y-auto" style='max-height:300px'>
                 ${post.comments.map(comment =>createComment(comment)).join('')}
              </div>
            -->  
            <!--
               <form onsubmit='sendComment(this, event)' class="comment-form mt-4" data-post-id = ${post.id}>
                    <input type="text" class="bg-gray-800 text-white p-2 rounded w-full  border-0  focus:outline-none focus:ring-2 focus:ring-orange-500" placeholder="ajoute un commentaire...">
                </form>
            -->    
    
              
        
            </div>
          </div>
    `

    // Escape the post body and set it as text content
    const postBodyElement = postElement2.querySelector('p[data-expandable]');
    postBodyElement.textContent = post.body;
    postBodyElement.setAttribute('data-full', post.body_full);
    return postElement2
    }


//Make referee proposal function
function makeProposal(battleId){

    $.ajax({
        url : `/battles/refree/send_proposal/${battleId}`,
        type: "POST",
        data: { csrfmiddlewaretoken:"{{csrf_token}}" },
        beforeSend: function(){
            $('#loading-overlay').toggleClass('active')
        },
        success: function(res){
            if(res.status == "success"){
               showMyToast(res.message, 'success')
            }else{
                showMyToast(res.message, 'info', 5000);
            }
            
        },
        complete: function(){
            $('#loading-overlay').toggleClass('active')
        },
        error: function(jqXHR, textstatus, errorThrown){
            showMyToast("Une erreur s'est produite", 'error')
            console.log(textstatus, errorThrown)
        }
    })
    
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
    if(type == 'tournament') return "Tournoi"

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
                                          <a href="/users/${battle.initiator.username}" class="font-bold truncate hover:text-orange-500 ">
                                              ${battle.initiator.player}<span class ='text-sm text-semibold text-gray-600'>@${battle.initiator.nickname}</span> ${ battle.winner ? (battle.winner.id == battle.initiator.id ? "<span class='text-green-500'>W</span>": ''):''}
                                          </a>
                                          <p class="text-sm text-gray-400">Rang: <span class='text-orange-500' >${battle.initiator.rank}</span></p>
                                      </div>
                                  </div>
                                  <i class="fas fa-bolt text-yellow-500 text-2xl"></i>
                                  <div class="flex items-end">
                                      <div class="text-right mr-4">
                                          <a href="/users/${battle.opponent.username}" class="font-bold truncate hover:text-orange-500 ">
                                              ${battle.opponent.player}<span class ='text-sm text-semibold text-gray-600'>@${battle.opponent.nickname}</span> ${ battle.winner ? (battle.winner.id == battle.opponent.id ? "<span class='text-green-500'>W</span>": ''):''}
                                          </a>
                                          <p class="text-sm text-gray-400">Rang: <span class='text-orange-500' >${battle.opponent.rank}</span></p>
                                      </div>
                                      <img src="${battle.opponent.profile_picture}" alt="${battle.opponent.player}" class="w-12 h-12 rounded-full">
                                  </div>
                              </div>
                              ${battle.isReferee ? `
                                <span class = 'mb-2 text-green-500 mx-auto rounded-2xl border border-green-800 bg-green-500 bg-opacity-50 px-3 py-1 text-xs'>Tu arbitres ce combat</span>`:``}
                                
                              ${battle.can_refree ? `<button data-battle_id="${battle.id}" onclick ='makeProposal(${battle.id})' class= "proposal-btn border border-purple-500 text-purple-500 px-4 py-2 rounded-lg  transition duration-300 mt-auto">
                                  <i class="fas fa-gavel mr-2"></i>Proposer d'arbitrer le combat
                              </button>`:`
                              <div class='flex justify-between items-center' > 
                              <a onclick = 'showOverlay()' href="/battles/battle_room/${battle.id}" class="inline-block bg-transparent border border-orange-500 text-white px-4 py-2 rounded-2xl  transition duration-300 mt-auto">
                                      voir le combat 
                              </a>

                              <div>
                              

                              <i class="fas fa-eye mr-2"></i>: <span  class='text-orange-500' >${battle.spectators}</span>
                              </div>
                              </div>
                              
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

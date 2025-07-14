

function createNotificationCard(notification) {
    
    const card = document.createElement('div');
    card.className = `notification-card p-2 ${notification.clicked ? '': 'bg-gray-800'}`;
    card.innerHTML = `
        <div class = 'bg-gray-900 rounded-2xl border border-gray-700 p-4 shadow-md relative'>
        <a href="${notification.url}" onclick='showOverlay();markAsRead(${notification.id});' class="block px-2">
            <div class = 'flex space-x-2' >
              ${notification.image ? `<img src = '${notification.image}' class='min-w-12 h-12 rounded-full' />` : ''}
            <div>  
            <p class="text-gray-300  mb-2">${notification.content}</p>
            <p class="text-sm text-gray-400">${notification.timestamp}</p>
            <div>
            </div>
        </a>
        <div class="absolute top-2 right-2">
            <button class="text-gray-300 hover:text-white focus:outline-none dropdown-toggle" data-notification-id="${notification.id}">
                <i class="fas fa-ellipsis-v"></i>
            </button>
            <div class="dropdown-menu w-48 py-2">
                <a href="#" class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600" onclick="markAsRead(${notification.id})"><i class = 'fas fa-circle-thin mr-2'></i> Mark as read</a>
                <a href="#" class="block px-4 py-2 text-sm text-red-600 hover:bg-gray-600"  onclick="deleteNotification(${notification.id},'${notification.type}')"><i class = 'fas fa-trash mr-2'></i>Delete</a>
            </div>
        </div>
        </div>
    `;
    return card;
}
function deleteNotification(id,type) {
      console.log(`Deleting notification ${id}, ${type}`);
          $.ajax({
            url: `/users/notification/${id}/${type}`,
            type: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': '{{csrf_token}}' // Include CSRF token in headers
              },
              data:{ 
                csrfmiddlewaretoken : "{{ csrf_token }}",

              },
              beforeSend: function(){
                $('#loading-overlay').toggleClass('active')
              },
              success: function(res){
                if(res.status == 'success'){
                  showMyToast('Deleted','success')
                }
              },
              complete: function(){
                $('#loading-overlay').toggleClass('active')
                
                renderNotifications();
              },
              error: function(jqXHR, textstatus, errorThrown){
                console.log('error', errorThrown)
                showMyToast('An error occured please try again','error')
              }
          })
          
      
  }
  function markAllAsRead() {
      // Implement your logic here
      $.ajax({
            url: `/notifications/mark_as_read/all`,
            type: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': '{{csrf_token}}' // Include CSRF token in headers
              },
              data:{ 
                csrfmiddlewaretoken : "{{ csrf_token }}",

              },
              beforeSend: function(){
                showMyToast("Lu","success")
              },
              success: function(res){
                renderNotifications()
              },
              complete: function(){
                
              },
              error: function(jqXHR, textstatus, errorThrown){
                console.log('error', errorThrown)
                showMyToast('An error occured please try again','error')
              }
          })
  }

//   function answerChallenge(element, challengeId, answer){
//   const card = document.getElementById(`challenge-card-${challengeId}`)
//   const character = $(card).find("select").val()
//   console.log('{{csrf_token}}')
//   if(answer == "accept"){
//     if(character){
//       $.ajax({
//                 url: `/battles/challenge/answer/${challengeId}`,
//                 type : "POST",
//                 data:{csrfmiddlewaretoken:"{{ csrf_token }}", character: character, response: answer},
//                 beforeSend: function(){
//                   $('#loading-overlay').toggleClass('active')
//                 },
//                 success: function(res){
//                     if(res.status == "success"){
//                       showMyToast(res.message, 'success')
                      
//                       $(card).hide(300)
//                     //   card.classList.add('opacity-0', 'scale-95');
//                     //   card.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                      
//                     }else{
//                         showMyToast(res.message)
//                     }
//                 },
//                 complete: function(){
//                   $('#loading-overlay').toggleClass('active')
//                 },
//                 error: function(jqXHR, textstatus, errorThrown){
//                   showMyToast("An error occured", 'error')
//                 }
//             })
//   }else{
//     showMyToast('choisi un personnage pour accepter le challenge')
//   }
//   }else{
//     $.ajax({
//                 url: `/battles/challenge/answer/${challengeId}`,
//                 type : "POST",
//                 data:{csrfmiddlewaretoken:"{{ csrf_token }}", character: character, response: answer},
//                 beforeSend: function(){
//                   $('#loading-overlay').toggleClass('active')
//                 },
//                 success: function(res){
//                     if(res.status == "success"){
//                       showMyToast(res.message, 'success')
                      
//                       $(card).hide(300)
//                     //   card.classList.add('opacity-0', 'scale-95');
//                     //   card.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                      
//                     }else{
//                         showMyToast(res.message)
//                     }
//                 },
//                 complete: function(){
//                   $('#loading-overlay').toggleClass('active')
//                 },
//                 error: function(jqXHR, textstatus, errorThrown){
//                   showMyToast("An error occured", 'error')
//                 }
//             })
//   }
 
// }

function handleInvite(btn,inviteId, action) {
            // Simulated API call (replace with actual API call)
            const inviteCard = btn.closest('.invite-card')
            if(action == 'accept'){
              $.ajax({
                url: `/users/join_family/${inviteId}`,
                type : "POST",
                data:{csrfmiddlewaretoken:"{{ csrf_token }}"},
                beforeSend: function(){
                  $('#loading-overlay').toggleClass('active')
                },
                success: function(res){
                    if(res.status == "success"){
                      showMyToast(res.message, 'success')
                      
                      $(inviteCard).hide()
                      // inviteCard.classList.add('opacity-0', 'scale-95');
                      // inviteCard.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                      
                    }else{
                        showMyToast(res.message)
                    }
                },
                complete: function(){
                  $('#loading-overlay').toggleClass('active')
                },
                error: function(jqXHR, textstatus, errorThrown){
                  showMyToast("An error occured", 'error')
                }
            })
            }else if(action == 'decline'){
              $.ajax({
                url: `/users/notification/${inviteId}/game`,
                type : "DELETE",
                data:{csrfmiddlewaretoken:"{{ csrf_token }}"},
                beforeSend: function(){
                  $('#loading-overlay').toggleClass('active')
                },
                success: function(res){
                    if(res.status == "success"){
                      showMyToast(res.message, 'success')
                     
                      $(inviteCard).hide(300)
                    //   inviteCard.classList.add('opacity-0', 'scale-95');
                    //   inviteCard.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                      
                    }else{
                        showMyToast(res.message)
                    }
                },
                complete: function(){
                  $('#loading-overlay').toggleClass('active')
                  
                },
                error: function(jqXHR, textstatus, errorThrown){
                  showMyToast("An error occured", 'error')
                }
            })
            }
           
           
      }

function handleRequest(btn,requestId, action) {
            // Simulated API call (replace with actual API call)
            if(action == 'accept'){
              $.ajax({
                url: `/users/accept_request/${requestId}`,
                type : "POST",
                data:{csrfmiddlewaretoken:"{{ csrf_token }}"},
                beforeSend: function(){
                  $('#loading-overlay').toggleClass('active')
                },
                success: function(res){
                    if(res.status == "success"){
                      showMyToast(res.message, 'success')
                      const requestCard = btn.closest('.request-card')
                      $(requestCard).hide(300)
                    //   requestCard.classList.add('opacity-0', 'scale-95');
                    //   requestCard.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                      
                    }else{
                        showMyToast(res.message)
                    }
                },
                complete: function(){
                  
                  $('#loading-overlay').toggleClass('active')
                },
                error: function(jqXHR, textstatus, errorThrown){
                  showMyToast("An error occured", 'error')
                }
            })
            }else if(action == 'refuse'){
              $.ajax({
                url: `/users/notification/${requestId}/game`,
                type : "DELETE",
                data:{csrfmiddlewaretoken:"{{ csrf_token }}"},
                beforeSend: function(){
                  $('#loading-overlay').toggleClass('active')
                },
                success: function(res){
                    if(res.status == "success"){
                      showMyToast(res.message, 'success')
                      const requestCard = btn.closest('.request-card')
                      //$(requestCard).hide(300)
                      requestCard.classList.add('opacity-0', 'scale-95');
                      requestCard.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
                      
                    }else{
                        showMyToast(res.message)
                    }
                },
                complete: function(){
                  $('#loading-overlay').toggleClass('active')
                  
                },
                error: function(jqXHR, textstatus, errorThrown){
                  showMyToast("An error occured", 'error')
                }
            })
            }
            
      }


function renderNotifications() {
    $.ajax({
      url: '/notifications/all',
      type:'GET',
      data: {csrfmiddlewaretoken:'{{csrf_token}}'},
      beforeSend: function(){
        $('#notificationsList').html(`
          <div id='notifLoader' class="flex justify-center items-center h-full">
            <i class="fas fa-spinner fa-spin text-orange-500 text-3xl"></i>
          </div>
        `);
      },
      success: function(res){
        updateNotificationCount(0)
        if(res.status == 'success'){
            const characters = res.characters
            const notifications = res.notifications
            const container = document.getElementById('notificationsList');
            container.innerHTML = '';
            if(notifications.length > 0){
              notifications.forEach(notification => {
                container.appendChild(createNotificationCard(notification));
      });
            }else{
              // <svg class="m-auto w-[48px] h-[48px] dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
              //   <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="m10.827 5.465-.435-2.324m.435 2.324a5.338 5.338 0 0 1 6.033 4.333l.331 1.769c.44 2.345 2.383 2.588 2.6 3.761.11.586.22 1.171-.31 1.271l-12.7 2.377c-.529.099-.639-.488-.749-1.074C5.813 16.73 7.538 15.8 7.1 13.455c-.219-1.169.218 1.162-.33-1.769a5.338 5.338 0 0 1 4.058-6.221Zm-7.046 4.41c.143-1.877.822-3.461 2.086-4.856m2.646 13.633a3.472 3.472 0 0 0 6.728-.777l.09-.5-6.818 1.277Z"/>
              //   </svg>
              $(container).append(`
              <div id="no-notifications" class="">
              <div class="no-notifications rounded-lg p-8 text-center">
                <p class="text-xl text-gray-400">No personal notifications</p>
               <i class = 'fas fa-bell-slash text-3xl'></i>
                <p class="text-sm text-gray-500 mt-2">You're all caught up!</p>
              </div>
            </div>
              `)
            }

            const challenges = res.challenges
            const invites = res.invites
            const requests = res.requests

            const pContainer = document.getElementById('pNotificationsList');
            pContainer.innerHTML = '';
            if(challenges.length > 0){
              challenges.forEach(challenge => {
                pContainer.appendChild(createChallengeCard(challenge, characters));
            });
            }
            if(invites.length > 0){
              invites.forEach(invite => {
                pContainer.appendChild(createInviteCard(invite));
            });
            }
            if(requests.length > 0){
              requests.forEach(request => {
                pContainer.appendChild(createRequestCard(request));
            });
            }
            
      addNotifDropdownListeners();
    
          }
      },
      complete: function(){
        document.getElementById('notifLoader')?.remove();
      },
      error: function(jqXHR, textstatus, errorThrown){
        console.log('Error: ',errorThrown)
        showMyToast('An error occured','error')
      }
    })  
    
  }

  function addNotifDropdownListeners() {
      document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
          toggle.addEventListener('click', (e) => {
              e.stopPropagation();
              const dropdown = toggle.nextElementSibling;
              dropdown.classList.toggle('active');
          });
      });

      document.addEventListener('click', () => {
          document.querySelectorAll('.dropdown-menu').forEach(menu => {
              menu.classList.remove('active');
          });
      });
  }

        

    function openNotificationsScreen() {
      const screen = document.getElementById('notificationsScreen');
      const content = document.querySelector('.notifications-content');
      screen.classList.remove('hidden');
      content.classList.add('active');
      renderNotifications()
    }
  
    function closeNotificationsScreen() {
      const screen = document.getElementById('notificationsScreen');
      const content = document.querySelector('.notifications-content');
      content.classList.remove('active');
      setTimeout(() => {
        screen.classList.add('hidden');
      }, 300); // Match the CSS transition duration
    }

    function createChallengeCard(challenge,characters){
        
    const card = document.createElement('div');
    card.className = `challenge-card bg-gray-900 rounded-2xl shadow-lg p-6 my-2 mx-auto max-w-md w-full mb-4`;
    
    card.id = `challenge-card-${challenge.id}`
    
    card.innerHTML = `
        <div class="text-center mb-4">
          <i class="fas fa-fire text-4xl text-orange-600 mb-4"></i>
          <h2 class="text-2xl font-semibold">On t'as lancé un challenge!</h2>
      </div>

      
      <div class="bg-gray-900 rounded-2xl p-4 mb-6">
          <div class="flex items-center mb-4">
            <a onclick = 'showOverlay()' href="/users/${challenge.sender.username}">
              <img src="${challenge.sender.profile_picture}" alt="${challenge.sender.username} profile picture" class="w-16 h-16 rounded-full mr-4">
            </a>  
              <div>
                  <a href="${challenge.sender.profile_picture}" class="font-semibold text-xl text-lg">${challenge.sender.username}</a>
                  <p class="text-gray-400">Perso: <a href="#" class="font-semibold text-orange-500" >${challenge.sender_character}</a></p>
              </div>
          </div>
          <p class="text-gray-300">${challenge.sender.player} t'as lancé un challenge</p>
      </div>

      <div class="mb-4">
        <label for="character" class="block mb-2">Choisis ton perso:</label>
        <select id="character" name="character" class="character-select w-full border border-orange-500 bg-gray-900 text-white p-2 rounded-2xl">
            <option value="">Choisis ton perso</option>
              ${characters.map((character)=>
              `
                <option value="${character.name}">
                ${character.name}
                </option>
              `).join('')
              }
        </select>
    </div>
      <div class="flex flex-col space-y-3">
        <button onclick="answerChallenge(this,'${challenge.id}', 'accept')" class="bg-green-600 mb-2 hover:bg-green-700 text-white py-3 px-4 rounded-full transition duration-300 pulse-animation">
            <i class="fas fa-check mr-2"></i>Accepter le Challenge
        </button>
        <button onclick="answerChallenge(this,'${challenge.id}', 'decline')" class="bg-red-600 hover:bg-red-700 text-white py-3 px-4 rounded-full transition duration-300">
            <i class="fas fa-times mr-2"></i>Refuser le Challenge
        </button>
    </div>
    `;
    
    return card;

    }

    function createRequestCard(notif){
        
        const card = document.createElement('div');
        card.className = `request-card bg-gray-900 rounded-2xl p-4 mb-4 flex flex-col md:flex-row items-center justify-between`;
        
        card.innerHTML = `
        <div class="text-center flex mb-6">
            <h2 class="text-2xl font-semibold">Un joueur veut rejoindre ta famille !</h2>
        </div>
           <div class="flex items-center mb-4 md:mb-0">
        <a href="/users/${notif.sender.username}"> 
          <img src="${notif.sender.profile_picture.url}" alt="User Avatar" class="w-12 h-12 rounded-full mr-4">
        </a>  
       
          <div>
              <a href="/users/${notif.sender.username}" class="font-semibold">${notif.sender.player}</a>
              <p class="text-gray-400 text-sm">Rank: ${notif.sender.rank} | Progress: ${notif.sender.progression}%</p>
          </div>
      </div>
      <div class="flex space-x-2">
          <button  onclick="handleRequest(this,'${notif.id}', 'accept')" class="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-full transition duration-300">
              <i class="fas fa-check mr-2"></i>Accept
          </button>
          <button onclick="handleRequest(this,'${notif.id}', 'refuse')" class="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-full transition duration-300">
              <i class="fas fa-times mr-2"></i>Refuse
          </button>
      </div>
          
        `;
        
        return card;
    
        }
        function createInviteCard(notif){
        
        const card = document.createElement('div');
        card.className = `invite-card bg-gray-900 rounded-lg shadow-2xl p-6 my-2 mx-auto max-w-md w-full mb-4`;
        
        card.innerHTML = `
           <div class="text-center mb-6">
          <i class="fas fa-users text-4xl text-blue-500 mb-4"></i>
          <h2 class="text-2xl font-semibold">Tu as été invité!</h2>
      </div>
      
      <div class="bg-gray-900 rounded-2xl p-4 mb-6">
          <div class="flex items-center mb-4">
            <a href="/users/family/65744${notif.family.id}">
              <img src="${notif.family.profile_picture}" alt="Family Leader Avatar" class="w-16 h-16 rounded-full mr-4">
            </a>  
            
              <div>
                  <a href="/users/family/65744${notif.family.id}" class="font-semibold text-xl text-lg">${notif.family.name}</a>
                  <p class="text-gray-400">Parrain: <a href="/users/${notif.family.god_father.username}" class="font-semibold" >${notif.family.god_father.username}</a></p>
              </div>
          </div>
          <p class="text-gray-300">Tu as été invité a rejoindre la famille ${notif.family.name} . Vas tu accepter leurs invitations?</p>
      </div>
      
      <div class="flex flex-col space-y-3">
        <button onclick="handleInvite(this,'${notif.id}', 'accept')" class="bg-green-600 mb-2 hover:bg-green-700 text-white py-3 px-4 rounded-full transition duration-300 pulse-animation">
            <i class="fas fa-check mr-2"></i>Accepter
        </button>
        <button onclick="handleInvite(this,'${notif.id}', 'decline')" class="bg-red-600 hover:bg-red-700 text-white py-3 px-4 rounded-full transition duration-300">
            <i class="fas fa-times mr-2"></i>Decliner
        </button>
    </div>
        `;
        
        return card;
    
        }

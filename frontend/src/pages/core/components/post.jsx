import React from 'react';


function Post({ post }) {
    return (
          
        <div key={post.id} classNameName = 'post bg-gray-900 rounded-2xl shadow-sm p-4 border border-gray-800'>
          <div className="flex items-start  gap-4">
                  <img src={"http://localhost:8000"+post.author.profile_picture} alt={post.author.player} className="myImg w-10 h-10 rounded-full" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm text-gray-400">
                      <div>
                        <a onlick = 'showOverlay()' href = "/users/{post.author.name}" className="inline-block font-semibold hover:text-orange-600 text-white">{post.author.player}</a> @{post.author.nickname}
                      </div>
                      
          
                       <div className="relative flex space-x-2 ">
                        <span>{post.time_posted}</span>
                        <button onclick = 'togglePostDropdown(this)'  className="text-gray-300 hover:text-white focus:outline-none post-dropdown-toggle" data-post-id="{post.id}">
                            <i className="fas fa-ellipsis-v"></i>
                        </button>
                        {/* <div className="post-dropdown-menu rounded-xl bg-opacity-80 bg-gray-900 border border-gray-700 w-48 py-2">
                              
                              <div className="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="toggleToFavorites('{post.id}')">
                              {post.is_favorite ? "<i className = 'fas fa-bookmark mr-2'></i>retirer des favoris":"<i className = 'far fa-bookmark mr-2'></i>ajouter aux favoris"}
                              </div>
                              
                              <div className="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="socialShare(this,'https://roleplayverse.live/posts/{post.id}')"><i className = 'fas fa-share-alt mr-2'></i>Partager</div>
                              <div className="block px-4 py-2 text-sm text-gray-300 cursor-pointer hover:bg-gray-600" onclick="copyLink('https://roleplayverse.live/posts/{post.id}')"><i className = 'fas fa-copy mr-2'></i>copier le lien</div>
                              {post.author.name == currentPlayerData.username? 
                              `
                              <!--
                              <a href="#" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-600"><i className = 'fas fa-pencil-square-o mr-2'></i> Edit</a>
                              -->
                              <div className="block px-4 py-2 cursor-pointer text-red-500 text-sm text-gray-300 hover:bg-gray-600"  onclick="deletePost(this,'{post.id}')"><i className = 'fas fa-trash  mr-2'></i> Supprimer</div>
                              `:`
                            `}
                             
                          </div> */}
                      </div>
                    </div>
                    
                    <p data-full = {post.body_full} onclick = 'toggleExpand(this)' className="body text-base text-gray-100 mt-1" data-expandable>
                     {post.body}
                    </p>
                   
                      {post.image ? 
                        <div className="mt-3">
                            <img  src={"http://localhost:8000"+ post.image} onload = "replacePlaceholder(this, '{post.image}')" alt = '{post.author.player + "image de publication" }'  className="w-full myImg rounded-xl border-1 border-gray-700 object-cover h-auto max-h-[500px]" />
                        </div>
                       : ''}
                    
                    <div className="flex justify-between mt-4 text-gray-400 text-sm">
                      <button className="like-button flex items-center space-x-1 hover:text-orange-500 {post.liked ? 'liked' : ''}" data-post-id={post.id}>
                      <i className="far fa-heart"></i>
                      <span className="like-count">{post.likes}</span>
                      </button>
                      <button onclick = 'openCommentPopup({post.id});' className="comment-button flex items-center space-x-1 hover:text-blue-500">            
                      <i className="far fa-comment"></i>
                      <span className = 'comment-count'>{post.n_comments}</span>
                      </button>
      
                      
                      <button className="flex items-center space-x-1 hover:text-orange-500" onclick="toggleToFavorites('{post.id}')">
                        <i className = 'far fa-bookmark'></i>
                      </button>
                      
                      <button className="flex items-center space-x-1 hover:text-green-500" onclick="socialShare(this,'https://roleplayverse.live/posts/{post.id}')">
                        <i className = 'fas fa-share-alt'></i><span>partager</span>
                      </button>
                    </div>
          
                     
                  
                    {/* <div className="mt-4 space-y-3 comments max-h-64 overflow-y-auto" style='max-height:300px'>
                       {post.comments.map(comment =>createComment(comment)).join('')}
                    </div> */}
                     
                  </div>
                </div>
                </div>    
      
    );
  }

export default Post;
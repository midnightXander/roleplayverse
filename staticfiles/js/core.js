function imgModalListener(){
    var modal = document.getElementById('imgModal');

// Get the image and insert it inside the modal - use its "alt" text as a caption
// var img = document.getElementById('myImg');

$('.myImg').on('click',(e)=>{

    var modalImg = document.getElementById("img01");
    modal.style.display = "block";
    modalImg.src = e.target.src;
    
})
// Get the <span> element that closes the modal
var close = document.getElementsByClassName("close")[0];

// When the user clicks on <span> (x), close the modal
close.onclick = function() { 
  modal.style.display = "none";
}

}    
function disableSubmitButton(button){
    button.disabled = true
}
function showOverlay(){
    $('#loading-overlay').addClass('active')
}

//imgModalListener()
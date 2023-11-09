var el = document.getElementById('topNav');

var  hiddenDiv = document.getElementById('list');

// ✅ Show hidden DIV on hover
el.addEventListener('mouseover', function handleMouseOver() {
  hiddenDiv.style.display = 'flex';

  // 👇️ if you used visibility property to hide the div
  // hiddenDiv.style.visibility = 'visible';
});

// ✅ (optionally) Hide DIV on mouse out
el.addEventListener('mouseout', function handleMouseOut() {
  hiddenDiv.style.display = 'none';

  // 👇️ if you used visibility property to hide the div
  // hiddenDiv.style.visibility = 'hidden';
});
        
var msg = document.getElementById("message");

// Set a timeout to hide the div after 5 seconds (5000 milliseconds)
setTimeout(function() {
  // Change the CSS style to hide the div
  if ( msg != null){
    msg.style.display = "none";
  }
}, 5000);

var id = document.getElementById('student_id')

/*
toggle.onclick = function handleMouseClick() {
	if (id.style.display === "inline") {
    		id.style.display = "none";
  	} 
	else {
    		id.style.display = "inline";
  	}

        console.log("click",id.style.display);
};
*/


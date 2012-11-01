// SliTaz Pizza Javascript functions.
//

// Check form to avoid empty values and bad email.
function checkForm() {
	if(document.forms["pizza"]["flavor"].value == "")
    {
        alert("Please enter SliTaz pizza flavor name");
        document.forms["pizza"]["flavor"].focus();
        return false;
    } else {
		var str = "!@#$%^&*()+=[]\\\';,./{}|\":<>?";
		for (var i = 0; i < document.forms["pizza"]["flavor"].value.length; i++) {
		  	if (str.indexOf(document.forms["pizza"]["flavor"].value.charAt(i)) != -1)
		  	{
			  	alert ("Invalid Flavor name.\n Please remove special characters.");
			  	document.forms["pizza"]["desc"].focus();
			  	return false;
		  	}
		}
	}
    if(document.forms["pizza"]["desc"].value == "")
    {
        alert("Please fill in the flavor description");
        document.forms["pizza"]["desc"].focus();
        return false;
    }
	var x=document.forms["pizza"]["mail"].value;
	var atpos=x.indexOf("@");
	var dotpos=x.lastIndexOf(".");
	if (atpos<1 || dotpos<atpos+2 || dotpos+2>=x.length)
	{
		alert("Missing or not a valid email address");
		return false;
	}
}

// Notification messages
function setOpacity(notifyId, opacityLevel) {
	var notifyStyle = document.getElementById(notifyId).style;
	notifyStyle.opacity = opacityLevel / 100;
	notifyStyle.filter = 'alpha(opacity='+opacityLevel+')';
}

function fadeNotify(notifyId, startOpacity, stopOpacity, duration) {
	var speed = Math.round(duration / 100);
	var timer = 2000;
	for (var i=startOpacity; i>=stopOpacity; i--) {
		setTimeout("setOpacity('"+notifyId+"',"+i+")", timer * speed);
		timer++;
	}
}

function hideNotify() {
	document.getElementById('notify').style.display = 'none';
}


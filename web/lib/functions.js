// SliTaz Pizza Javascript functions.
//

function charactersOK(field, name) {
	var str = "`!#$%^&*()+=[]\\\';,/{}|\":<>?";
	if(document.forms["pizza"][field].value == "") {
        	alert("Please enter"+name);
		document.forms["pizza"][field].focus();
		return false;
	}
	for (var i = 0; i < document.forms["pizza"][field].value.length; i++) {
		if (str.indexOf(document.forms["pizza"][field].value.charAt(i)) != -1) {
			alert ("Invalid "+name+".\n Please remove special characters.");
			document.forms["pizza"][field].focus();
			return false;
		}
	}
	return true;
}

// Check form to avoid empty values and bad email.
function checkForm() {
    if (!charactersOK("flavor", "pizza flavor name", 
    			"`!@#$%^&*()+=[]\\\';,./{}|\":<>?"))
	return false;
    if (!charactersOK("desc", "flavor description", 
    			"`!@#$%^&*()+=[]\\\';,./{}|\":<>?"))
	return false;
    if (!charactersOK("mail", "email address", "$`\\"))
	return false;
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


#!/bin/sh
#

[ -f "/etc/slitaz/pizza.conf" ] && . /etc/slitaz/pizza.conf
[ -f "../pizza.conf" ] && . ../pizza.conf
. $VHOST/db.conf
. /usr/lib/slitaz/httphelper
header

cat $VHOST/lib/header.html

# Content negotiation for Gettext
IFS=","
for lang in $HTTP_ACCEPT_LANGUAGE
do
	lang=${lang%;*} lang=${lang# } lang=${lang%-*}
	[ -d "$lang" ] &&  break
	case "$lang" in
		en) lang="C" ;;
		fr) lang="fr_FR" ;;
	esac
done
unset IFS
export LANG=$lang LC_ALL=$lang

# Internationalization: $(gettext "")
. /usr/bin/gettext.sh
TEXTDOMAIN='pizza'
export TEXTDOMAIN

inqueue=$(ls $queue | wc -l)
builds=$(cat $builds)
pubiso=$(ls -1 $public | wc -l)
[ "$builds" ] || builds=0

		cat << EOT
<h2>$(gettext "Public flavors")</h2>
<p>
$(gettext "")
</p>
<pre>
Flavors: $inqueue in queue - $builds builds - $pubiso public</a>
</pre>
EOT

for dir in $public/*
do
	if [ -f $dir/receipt ] && (grep -q '^FLAVOR' $dir/receipt ]); then
		flavor=$(grep '^FLAVOR' $dir/receipt | cut -d '=' -f 2 | sed 's/\"//g' )
		uri="$(basename $dir)"
		desc=$(grep '^SHORT_DESC'  $dir/receipt| cut -d '=' -f 2 | sed 's/\"//g')
cat <<EOT
<a href="/?id=${uri#slitaz-}">$flavor</a><br/>
Description: $desc<br />
<br />
EOT
	fi
done

# HTML footer.
cat $VHOST/lib/footer.html

exit 0

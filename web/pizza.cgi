#!/bin/sh
#
# SliTaz Pizza CGI/web interface - Let's have a pizza :-) 
# Please KISS, it is important and keep speed in mind. Thanks, Pankso.
#

# Output a RSS feed of latest build isos.
if [ "$QUERY_STRING" == "rss" ]; then
	. /etc/slitaz/pizza.conf
	pubdate=$(date "+%a, %d %b %Y %X")
	cat << EOT
Content-Type: text/xml

<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0">
<channel>
	<title>SliTaz Pizza</title>
	<description>The SliTaz Pizza cooker feed</description>
	<link>$PIZZA_URL</link>
	<lastBuildDate>$pubdate GMT</lastBuildDate>
	<pubDate>$pubdate GMT</pubDate>
EOT
	for rss in $(ls -1t $PIZZA/chroot${SLITAZ}/xml/*.xml | head -n 12)
	do
		cat $rss
	done
	cat << EOT
</channel>
</rss>
EOT
	exit 0
fi

# Content negotiation for Gettext
IFS=","
for lang in $HTTP_ACCEPT_LANGUAGE
do
	lang=${lang%;*} lang=${lang# } lang=${lang%-*}
	case "$lang" in
		de) lang="de_DE" && break ;;
		el) lang="el_GR" && break ;;
		en) lang="C" && break ;;
		fr) lang="fr_FR" && break ;;
		pt) lang="pt_BR" && break ;;
		ru) lang="ru_RU" && break ;;
		sv) lang="sv_SE" && break ;;
		pl) lang="pl_PL" && break ;;
	esac
done
unset IFS
export LANG=$lang LC_ALL=$lang

# Internationalization: $(gettext "")
. /usr/bin/gettext.sh
TEXTDOMAIN='pizza'
export TEXTDOMAIN

. lib/libpizza

#
# Commands
#

case " $(GET) " in
	*\ start\ *)
		#
		# First step
		#
		date=$(date "+%Y%m%d")
		id=$date-$$
		cat << EOT
<h2>$(gettext "First step")</h2>
<p>
	$(gettext "Choose your distribution name and the one you want to use as \
base. We need your mail to notify you when your SliTaz Flavor is built \
and if anything goes wrong.")
</p>
<form method="get" action="pkgs.cgi" name="pizza" onsubmit="return checkForm();">
<table>
	<tbody>
		<tr>
			<td>$(gettext "Flavor name")</td>
			<td><input type="text" name="flavor" size="40" maxlength="25" /></td>
		</tr>
		<tr>
			<td>$(gettext "Short description")</td>
			<td><input type="text" name="desc" size="40" maxlength="60" /></td>
		</tr>
		<tr>
			<td>$(gettext "Email")</td>
			<td><input type="text" name="mail" size="40" /></td>
		</tr>
		<tr>
			<td>$(gettext "Based on")</td>
			<td>
				<select name="skel">
					<option value="base">
						Base - $(gettext "Text mode system")</option>
					<option value="justx">
						Justx - $(gettext "X without GTK or Qt")</option>
					<option value="gtkonly">
						Gtkonly - $(gettext "Clean GTK desktop")</option>
					<option value="core">
						Core - $(gettext "Default SliTaz desktop")</option>
				</select>
			</td>
		</tr>
	</tbody>
</table>
<pre>
Uniq ID : $id
</pre>
<div class="next">
	<input type="hidden" name="id" value="$id" />
	<input type="submit" value="$(gettext 'Continue')">
</div>
</form>
EOT
		;;
	*\ gen\ *)
		#
		# Generate step
		#
		id="$(GET id)"
		. $tmpdir/slitaz-$id/receipt
		addfiles=$(find $tmpdir/slitaz-$id/addfiles -type f | wc -l)
		[ "$addfiles" ] || addfiles=0
		packages=$(cat $tmpdir/slitaz-$id/packages.list | wc -l)
		cat << EOT
<h2>$(gettext "Generate")</h2>
<p>
	$(gettext "Last chance to stop process or start over. Next step will pack \
your flavor and add it to the build queue. Here you can also add a note to \
your receipt flavor, this will be displayed on your flavor ID page and \
can be used to give more info to other users and SliTaz developers.")
</p>

<pre>
Uniq ID    : $id
Flavor     : $FLAVOR
Short desc : $SHORT_DESC
Maintainer : $MAINTAINER
Packages   : $packages
Addfiles   : $addfiles
</pre>
<form method="get" action="./">
<div class="box">
	Note:
	<input type="text" name="note" style="width: 720px;" />
</div>
	<div class="next">
		<input type="submit" name="cancel" value="$(gettext 'Cancel')">
		<input type="hidden" name="addfiles" value="$addfiles" />
		<input type="hidden" name="id" value="$id" />
		<input type="submit" name="pack" value="$(gettext 'Build flavor')">
	</div>
</form>
EOT
		;;
	*\ cancel\ *)
		id="$(GET id)"
		echo "<p>$(eval_gettext 'Removing temporary files for: $id')</p>"
		[ -d "$tmpdir/slitaz-$id" ] && rm -rf $tmpdir/slitaz-$id/
		cat << EOT
<form method="get" action="./">
	<input type="submit" name="start" value="$(gettext 'Start over')">
</form>
EOT
		;;
	*\ pack\ *)
		#
		# Pack distro step
		#
		id="$(GET id)"
		receipt="$tmpdir/slitaz-$id/receipt"
		addfiles="$(GET addfiles)"
		log="$tmpdir/slitaz-$id/distro.log"
		note="$(GET note)"
		inqueue=$(ls $queue | wc -l)
		. $receipt
		cat << EOT
<h2>$(gettext 'Packing: $FLAVOR')</h2>
<pre>
EOT
		if ! fgrep ADDFILES $receipt; then
			echo "ADDFILES=\"$addfiles\"" >> $receipt
		fi
		if ! fgrep NOTE $receipt; then
			echo "NOTE=\"$note\"" | \
			sed 's/\\/\\\\/g;s/\$/\\$/g;s/`/\\`/g' >> $receipt
		fi
		
		# The rootcd README
		gettext "Creating SliTaz CD-ROM README..."
		date=$(date '+%Y-%m-%d %H:%M')
		mkdir -p $tmpdir/slitaz-$id/rootcd
		cp $DATA/README.distro $tmpdir/slitaz-$id/rootcd/README
		sed -i s"/_DATE_/$date/" $tmpdir/slitaz-$id/rootcd/README
		status
		
		gettext "Creating flavor tarball..."
		cd $tmpdir && tar cjf $FLAVOR.tar.bz2 slitaz-$id
		mkdir -p $public/slitaz-$id
		mv $FLAVOR.tar.bz2 $public/slitaz-$id
		status
		
		# Keep a public receipt copy and move everything from tmp to queue.
		echo "Flavor packed   : $(date '+%Y-%m-%d %H:%M')" | tee -a $log
		gettext "Moving $id to Pizza build queue..."
		mv -f $tmpdir/slitaz-$id/distro.log $public/slitaz-$id
		cp -f $tmpdir/slitaz-$id/receipt $public/slitaz-$id
		mv $tmpdir/slitaz-$id $queue
		status
		
		if [ "$inqueue" == "1" ]; then
			gettext "Your ISO will be built on next Pizza Bot run"
		else
			eval_ngettext \
				'There is $inqueue flavor in queue' \
				'There are $inqueue flavors in queue' $inqueue
		fi
		echo ""
		echo "New flavor added to queue: <a href='?id=$id'>$id</a> ($FLAVOR)" | log
		cat << EOT
</pre>
<div>
	<img src="images/archive.png" alt="[ tarball ]" />
	$(gettext "Download tarball:")
	<a href="public/slitaz-$id/$FLAVOR.tar.bz2">$FLAVOR.tar.bz2</a>
	- Browse <a href="public/slitaz-$id/">the flavor</a>
</div>
<div class="next">
	<form method="get" action="./">
		<input type="hidden" name="id" value="$id" />
		<input type="submit" value="$(gettext 'Status')">
	</form>
</div>
EOT
		;;
	*\ id\ *)
		#
		# ID Status page
		#
		id="$(GET id)"
		[ -f "$queue/slitaz-$id/receipt" ] && . $queue/slitaz-$id/receipt
		[ -f "public/slitaz-$id/receipt" ] && . public/slitaz-$id/receipt
		log="$public/slitaz-$id/distro.log"
		if [ ! -d "public/slitaz-$id" ]; then
			gettext "Sorry, can't find flavor ID: $id"
			cat lib/footer.html && exit 0
		fi
		if [ -f "$public/slitaz-$id/$FLAVOR.iso" ]; then
			dir="public/slitaz-$id"
			list="$dir/packages.list"
			iso="$dir/$FLAVOR.iso"
			msg="$(gettext 'Download ISO:') <a href=\"$dir/$FLAVOR.iso\">$FLAVOR.iso</a>
				[ <a href=\"$dir/$FLAVOR.md5\">md5</a> ]"
		else
			list="$queue/slitaz-$id/packages.list"
			msg="$(gettext 'Flavor is building or still in the build queue')"
		fi
		pkgslist=$(cat $list | wc -l)
		pkgsinst=$(cat $installed | wc -l)
		[ "$pkgsinst" ] || pkgsinst=0
		[ "$ISO_SIZE" ] || ISO_SIZE="N/A"
		[ "$ROOTFS_SIZE" ] || ROOTFS_SIZE="N/A"
		cat << EOT
<h2>$(gettext 'Status for: $FLAVOR')</h2>
<div>
	$(get_gravatar $MAINTAINER) $(gettext "Flavor description:") $SHORT_DESC
</div>
<pre>
Uniq ID     : $id
Flavor      : $FLAVOR
Packages    : $pkgslist in list - $pkgsinst installed
Rootfs size : $ROOTFS_SIZE
ISO size    : $ISO_SIZE
</pre>

<div>
	<img src="images/iso.png" alt="[ iso ]" /> $(echo $msg)
</div>
<div>
	<img src="images/archive.png" alt="[ tarball ]" />
	$(gettext "Download tarball:")
	<a href="public/slitaz-$id/$FLAVOR.tar.bz2">$FLAVOR.tar.bz2</a>
EOT
		if [ -f "$public/slitaz-$id/$FLAVOR.flavor" ]; then
			cat << EOT
	- Flavor file: <a href="public/slitaz-$id/$FLAVOR.flavor">$FLAVOR.flavor</a>
EOT
		fi
		cat << EOT
	- Browse <a href="public/slitaz-$id/">the flavor</a>
</div>
EOT
		if [ "$NOTE" ]; then
			echo "<div class="note">$NOTE</div>"
		fi
		if [ -f "$log" ]; then
			echo '<h2>Distro log</h2>'
			echo '<pre>'
			fgrep 'Build time' $log
			cat $log | highlighter log
			echo '</pre>'
		fi ;;
	*\ help\ *)
		echo "<h2>$(gettext 'Help')</h2>"
		cat /usr/share/doc/pizza/help.en.html
		cat /usr/share/doc/pizza/faq.en.html
		echo '<h3>README</h3>'
		echo '<pre>'
		cat /usr/share/doc/pizza/README
		echo '</pre>' ;;
	*\ info\ *)
		# English only :-)
		if mount | fgrep -q slitaz/public; then
			mounted="Public is mounted"
		else
			mounted="WARNING: Public is not mounted"
		fi
		echo '<h2><img src="images/monitor.png" alt="(i)" />Pizza Info</h2>'
		echo '<pre>'
		[ "$mounted" ] && echo "$mounted"
		echo -n "Public flavors : " && ls -1 public | wc -l
		echo -n "Public size    : " && du -sh public | awk '{print $1}'
		echo -n "Tmp size       : " && du -sh $tmpdir | awk '{print $1}'
		echo '</pre>' ;;
	*\ activity\ *)
		cat << EOT
<h2><img src="images/monitor.png" alt="" />$(gettext "Activity")</h2>

<pre>
$(tac $activity | highlighter activity)
</pre>

EOT
		;;
	*)
		#
		# Main page
		#
		inqueue=$(ls $queue | wc -l)
		builds=$(cat $builds)
		pubiso=$(ls -1 public | wc -l)
		[ "$builds" ] || builds=0
		cat << EOT
<h2>$(gettext "Welcome")</h2>
<form method="get" action="./">
<p>
	$(gettext "SliTaz Pizza lets you create your own SliTaz ISO flavor \
online. The ISO image can be burnt on a cdrom or installed on USB media. \
Please read the SliTaz Pizza <a href=\"?help\">Help</a> before starting \
a new flavor.")
</p>
<pre>
Flavors: $inqueue in queue - $builds builds - $pubiso <a href="/public">public</a>
</pre>

<div class="start">
		<input type="submit" name="start" value="$(gettext 'Create a new flavor')">
</div>

EOT
		echo "<h2>$(gettext 'Latest builds')</h2>"
		echo '<pre>'
		for flavor in $(ls -1t public | head -n 5)
		do
			if [ -f "public/$flavor/receipt" ]; then
				. ./public/$flavor/receipt
				[ -f "public/$flavor/$FLAVOR.iso" ] && \
					cat << EOT
$(get_gravatar $MAINTAINER 24) <a href="?id=$ID">$VERSION</a> : \
<a href="public/$flavor/$FLAVOR.iso">$FLAVOR.iso</a> ($ISO_SIZE)
EOT
			fi
		done 
		echo '</pre>' 
		cat << EOT
<h2>$(gettext "Activity")</h2>
<pre>
$(tac $activity | head -n 12 | highlighter activity)
</pre>
	<input type="submit" name="activity" value="$(gettext 'More activity')">
</form>
EOT
		;;
esac

# HTML footer.
cat lib/footer.html

exit 0

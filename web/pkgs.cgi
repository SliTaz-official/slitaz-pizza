#!/bin/sh
#
# SliTaz Pizza CGI/web interface - Let's have a pizza :-) 
# Packages step
#

. lib/libpizza

id="$(GET id)"
flavor="$(GET flavor)"
skel="$(GET skel)"
desc="$(GET desc)"
mail="$(GET mail)"
add="$(GET add)"
log="$tmpdir/slitaz-$id/distro.log"
list="$tmpdir/slitaz-$id/packages.list"

#
# Functions
#

list_pkgs() {
	# Pizza uses local packages synced with mirror each night.
	pkgsdesc="$SLITAZ/$SLITAZ_VERSION/packages/packages.desc"
	[ ! -f "$pkgsdesc" ] && echo "Missing: $pkgsdesc"
	for pkg in $(cat $list)
	do
		IFS="|"
		grep "^$pkg |" $pkgsdesc | cut -f 1,2,3 -d "|" | \
		while read PACKAGE VERSION SHORT_DESC
		do
			cat << EOT
<tr>
	<td><input type="checkbox" name="pkg" value="$PACKAGE" /></td>
	<td>$PACKAGE</td>
	<td>$VERSION</td>
	<td>$SHORT_DESC</td>
</tr>
EOT
		done
	done
}

# Gen an empty receipt for new flavor.
empty_receipt() {
	cat > $tmpdir/slitaz-$id/receipt << EOT
# SliTaz flavor receipt.

FLAVOR=""
SHORT_DESC=""
VERSION="$(date "+%Y%m%d")"
MAINTAINER=""

ID=""
SKEL=""

EOT
}

#
# Actions
#

case " $(GET) " in
	*\ add\ *)
		for pkg in $add
		do
			if ! grep -q ^${pkg}$ $list; then
				echo "$pkg" >> $list
			fi
		done ;;
	*\ rm\ *)
		cmdline=$(echo ${QUERY_STRING#pkg=} | sed s'/&/ /g')
		cmdline=${cmdline%id=*}
		pkgs=$(echo $cmdline | sed -e s'/+/ /g' -e s'/pkg=//g' -e s/$cmd//)
		for pkg in $pkgs
		do
			sed -i "/^${pkg}$/"d $list
		done ;;
	*)
		# No space in flavor name please.
		flavor=$(echo $flavor | sed s'/ //'g)
		# Javascript can be disable in browser.
		[ ! "$flavor" ] && echo "Missing flavor name" && exit 0
		[ ! "$mail" ] && echo "Missing email address" && exit 0
		[ ! "$skel" ] && echo "Missing SliTaz skeleton" && exit 0
		[ ! "$desc" ] && echo "Missing short desciption" && exit 0
		mkdir -p $tmpdir/slitaz-$id
		cp -f $cache/packages.$skel $list
		echo "Receipt created : $(date '+%Y-%m-%d %H:%M')" > $log
		empty_receipt
		sed -i \
			-e s"/FLAVOR=.*/FLAVOR=\"slitaz-$flavor\"/" \
			-e s"/MAINTAINER=.*/MAINTAINER=\"$mail\"/" \
			-e s"/SKEL=.*/SKEL=\"$skel\"/" \
			-e s"/SHORT_DESC=.*/SHORT_DESC=\"$desc\"/" \
			-e s"/ID=.*/ID=\"$id\"/" $tmpdir/slitaz-$id/receipt ;;
esac

#
# Source the receipt and display page.
#
. $tmpdir/slitaz-$id/receipt

nb=$(cat $list | wc -l)
cat << EOT
<h2>Packages ($nb)</h2>

<form method="get" action="pkgs.cgi">
	<table>
		<tbody>
			$(list_pkgs)
		</tbody>
	</table>
	<div>
	<input type="hidden" name="id" value="$id" />
	<input type="submit" name="rm" value="$(gettext "Remove package(s)")">
</form>

<form method="get" action="pkgs.cgi" style="float: right;">
	<input type="text" name="add" />
	<input type="hidden" name="id" value="$id" />
	<input type="submit" name="pkgs" value="$(gettext "Add package(s)")">
</form>

<pre>
Uniq ID    : $id
Flavor     : $FLAVOR
Short desc : $SHORT_DESC
</pre>
<div class="next">
		<form method="get" action="rootfs.cgi">
		<input type="hidden" name="id" value="$id" />
		<input type="submit" value="$(gettext "Continue")">
	</form>
</div>
EOT

# HTML footer.
cat lib/footer.html

exit 0

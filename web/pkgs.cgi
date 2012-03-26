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
log="$tmpdir/slitaz-$id/distro.log"
allpkgs="$SLITAZ/$SLITAZ_VERSION/packages/packages.desc"
# Flavor pkgs list format: pkgname version " short desc "
list="$tmpdir/slitaz-$id/packages.desc"

#
# Functions
#

# Pizza uses local packages synced with mirror each night.
list_pkgs() {
	[ ! -f "$list" ] && echo "Missing: $list"
	cat $list | while read PACKAGE VERSION SHORT_DESC
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

# Search packages or desc in the local packages.desc
# TODO: Html table with selection
search_pkgs() {
	echo '<pre>'
	for pkg in $search
	do
		fgrep $pkg $allpkgs | cut -d "|" -f 1,2,3
	done
	echo '</pre>'
}

#
# Actions
#

case " $(GET) " in
	*\ search\ *)
		search="$(GET search)"
		notify "Searching for: $search" ;;
	*\ add\ *)
		add="$(GET add)"
		notify "Adding packages: $add"
		for pkg in $add
		do
			# Add pkg only if not yep in Pizza flavor pkgs list
			if ! grep -Eq "^($pkg|get-$pkg) " $list; then
				pkginfo=$(grep -E "^($pkg|get-$pkg) " $allpkgs | cut -f 1,2,3 -d "|")
				name=$(echo $pkginfo | cut -d "|" -f 1)
				vers=$(echo $pkginfo | cut -d "|" -f 2)
				desc=$(echo $pkginfo | cut -d "|" -f 3)
				echo "$name $vers \" $desc \"" >> $list
			fi
		done ;;
	*\ rm\ *)
		cmdline=$(echo ${QUERY_STRING#pkg=} | sed s'/&/ /g')
		cmdline=${cmdline%id=*}
		pkgs=$(echo $cmdline | sed -e s'/+/ /g' -e s'/pkg=//g' -e s/$cmd//)
		for pkg in $pkgs
		do
			sed -i "/^${pkg} /"d $list
		done ;;
	*)
		# No space in flavor name please.
		flavor=$(echo $flavor | sed s'/ //'g)
		# Javascript can be disable in browser.
		[ ! "$flavor" ] && echo "Missing flavor name" && exit 0
		[ ! "$mail" ] && echo "Missing email address" && exit 0
		[ ! "$skel" ] && echo "Missing SliTaz skeleton" && exit 0
		[ ! "$desc" ] && echo "Missing short desciption" && exit 0
		notify "$(gettext "Creating receipt and packages list")"
		mkdir -p $tmpdir/slitaz-$id
		cp -f $hgflavors/$skel/packages.desc $list
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
	<div id="packages">
	<table>
		<tbody>
			$(list_pkgs)
		</tbody>
	</table>
	</div>
	<input type="hidden" name="id" value="$id" />
	<input type="submit" name="rm" value="$(gettext "Remove package(s)")" />
</form>

<form method="get" action="pkgs.cgi">
<div style="float: right;">
	<input type="text" name="add" style="width: 400px;" />
	<input type="hidden" name="id" value="$id" />
	<input type="submit" name="pkgs" value="$(gettext "Add package(s)")" />
</div>
</form>

<form method="get" action="pkgs.cgi">
<p>

$(gettext "Here you can add or remove some packages from your flavor. You
can also search for packages name and description to find a package name")

</p>
	<input type="text" name="search" style="width: 300px;" />
	<input type="hidden" name="id" value="$id" />
	<input type="submit" value="$(gettext "Search")" />
	<div id="pkgs-search">
		$([ "$search" ] && search_pkgs)
	</div>
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

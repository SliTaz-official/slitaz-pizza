#!/bin/sh
#
# SliTaz Pizza CGI/web interface - Let's have a pizza :-) 
# SliTaz rootfs step
#

. lib/libpizza
log="$tmpdir/slitaz-$id/distro.log"

# Internationalization: $(gettext "")
. /usr/bin/gettext.sh
TEXTDOMAIN='pizza'
export TEXTDOMAIN

# Handle rootfs.* file upload.
tarball_handler() {
	echo "<pre>"
	echo "File name : $tarball"
	echo "File size : $size Bytes"
	gettext "Moving rootfs tarball to slitaz-$id"
	upload=$tmpdir/slitaz-$id/upload-$$
	mkdir -p $upload && cd $upload
	mv $tmpname "$upload/$tarball" && rm -rf $(dirname $tmpname)
	chmod a+r $upload/$tarball
	status
	
	# Extract into the tmp upload dir.
	gettext "Extracting archive for sanity checks..."
	case "$tarball" in
		*.tar.gz) tar xzf $tarball && status ;;
		*.tar.bz2) tar xjf $tarball && status ;;
		*.tar.lzma) tar xaf $tarball && status ;;
		*) echo && error "Unsupported tarball format" && rm -rf $upload
	esac
	
	# Upload dir is removed if bad tarball so we stop here. Now be a bit
	# restrictive using only rootfs as archive name and check FSH in root.
	# Dont allow files in /dev /proc /sys /tmp /mnt
	if [ -d "$upload/rootfs" ]; then
		gettext "Checking Filesystem Standard..."
		for i in $(ls $upload/rootfs)
		do
			case "$i" in
				bin|boot|etc|home|init|lib|root|sbin|usr|var) continue ;;
				*) echo "Bad FSH path for: $i" && rm -rf $upload ;;
			esac
		done && status
		# Dont allow too big rootfs content.
		size=$(du -s $upload/rootfs | awk '{print $1}')
		gettext "Checking uploaded rootfs size..."
		if [ "$size" -lt "$MAX_UPLOAD" ]; then
			status
		else
			echo && error "Tarball is too big"
			rm -rf $upload
		fi
	fi
	
	# So now it time to move the addfile to flavor files.
	if [ -d "$upload/rootfs" ]; then
		echo "Additional rootfs: accepted" | tee -a $log
		mkdir -p $tmpdir/slitaz-$id
		mv $upload/rootfs $tmpdir/slitaz-$id
		rm -rf $tmpdir/slitaz-$id/upload-*
	fi
	echo "</pre>"
	rm -rf $upload
}

#
# Actions
#

case " $(FILE) " in
	*\ wallpaper\ *)
		id="$(POST id)"
		tmpname="$(FILE wallpaper tmpname)"
		wallpaper="$(FILE wallpaper name)"
		size="$(FILE wallpaper size)"
		if echo $wallpaper | fgrep -q .jpg; then
			images=$tmpdir/slitaz-$id/rootfs/usr/share/images
			mkdir -p $images
			mv $tmpname $images/slitaz-background.jpg
			chmod a+r $images/*.jpg
			notify "$(gettext "Added image:") $wallpaper ($size Bytes)" "info"
		else
			notify "$(gettext "Unsupported image format")" "error"
		fi ;;
	*\ tarball\ *)
		id="$(POST id)"
		tmpname="$(FILE tarball tmpname)"
		tarball="$(FILE tarball name)"
		size="$(FILE tarball size)" ;;
	*)
		id="$(GET id)" ;;
esac

#
# Source receipt and display page with additional rootfs or file upload.
#
. $tmpdir/slitaz-$id/receipt
cat << EOT
<h2>Rootfs</h2>
<form method="post" action="rootfs.cgi" enctype="multipart/form-data">

<p>
	SliTaz root filesystem modification can be done via an easy to use form,
	a single tarball or by uploading files one by one in the wanted directory.
</p>

<h3>$(gettext "Easy customization")</h3>

	$(gettext "Desktop Wallpaper"):
	<input type="file" name="wallpaper" size="40" />
	<input type="submit" value="Upload" />

<h3>$(gettext "Rootfs tarball")</h3>
<p>
	The files in the rootfs archive must have the same directory structure
	as any standard SliTaz or Linux system. For example if you wish to
	have a custom boot configuration file, you will have: rootfs/etc/rcS.conf.
	Accepted tarball formats are: <strong>tar.gz tar.bz2 tar.lzma</strong>
	and the archived directory must be named rootfs with a valid file system
	hierachy such as: /usr/bin /etc /var/www
</p>

	Rootfs tarball:
	<input type="file" name="tarball" size="40" />
	<input type="hidden" name="id" value="$id" />
	<input type="submit" value="Upload" />
</form>

$([ "$tarball" ] && tarball_handler)

<pre>
Uniq ID    : $id
Flavor     : $FLAVOR
Short desc : $SHORT_DESC
</pre>
<div class="next">
	<form method="get" action="./">
		<input type="hidden" name="id" value="$id" />
		<input type="submit" name="gen" value="$(gettext "Continue")">
	</form>
</div>
EOT

# HTML footer.
cat lib/footer.html

exit 0

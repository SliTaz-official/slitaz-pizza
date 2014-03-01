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
		mkdir -p $tmpdir/slitaz-$id/rootfs
		cp -a $upload/rootfs/* $tmpdir/slitaz-$id/rootfs
		rm -rf $tmpdir/slitaz-$id/upload-* $upload/rootfs
	fi
	echo "</pre>"
	rm -rf $upload
}

#
# Actions
#

case " $(FILE) " in
	*\ wallpaper\ *)
		tmpname="$(FILE wallpaper tmpname)"
		wallpaper="$(FILE wallpaper name)"
		size="$(FILE wallpaper size)"
		if echo $wallpaper | fgrep -q .jpg; then
			images=$tmpdir/slitaz-$id/rootfs/usr/share/images
			mkdir -p $images
			mv $tmpname $images/slitaz-background.jpg
			chmod a+r $images/*.jpg
			notify "$(gettext "Added image:") $wallpaper ($size Bytes)"
		else
			notify "$(gettext "Unsupported image format")" "error"
		fi ;;
	*\ desktop\ *)
		id="$(POST id)"
		tmpname="$(FILE desktop tmpname)"
		file="$(FILE desktop name)"
		size="$(FILE desktop size)"
		path="$tmpdir/slitaz-$id/rootfs/etc/skel/Desktop"
		mkdir -p $path
		case "$file" in
			*README*|*.desktop|*.html|*.png|*.jpg) 
				mv $tmpname $path/$file
				chmod a+r $path/$file
				notify "$(gettext "Added file:") $file ($size Bytes)" ;;
			*) 
				notify "$(gettext "Unsupported file type")" "error" ;;
		esac
		;;
	*\ tarball\ *)
		tmpname="$(FILE tarball tmpname)"
		tarball="$(FILE tarball name)"
		size="$(FILE tarball size)" ;;
	*)
		id="$(GET id)" ;;
esac

[ -n "$id" ] || id="$(POST id)"

if [ "$(POST fastboot)" != "" ]; then
	echo "Fast boot conversion" >> $log
	notify "$(gettext "Fast boot conversion")"
	mkdir -p $tmpdir/slitaz-$id/rootfs/etc/tazlito 2> /dev/null
	# lzo decompression crash with 2.6.37...
	false && cat > $tmpdir/slitaz-$id/rootfs/etc/tazlito/fastboot.iso <<EOT
[ -x /usr/bin/lzop ] || tazpkg get-install lzop
find * | cpio -o -H newc | lzop -9 > \$1/boot/rootfs.gz
EOT
	cat > $tmpdir/slitaz-$id/rootfs/etc/tazlito/fastboot.iso <<EOT
find * | cpio -o -H newc | gzip -9 > \$1/boot/rootfs.gz
[ -x /usr/bin/advdef ] || tazpkg get-install advancecomp
[ -x /usr/bin/advdef ] && advdef -z4 \$1/boot/rootfs.gz
EOT
	cat > $tmpdir/slitaz-$id/rootfs/etc/tazlito/fastboot.rootfs <<EOT
sed -i 's/FAST_BOOT_X="no"/FAST_BOOT_X="yes"/' etc/rcS.conf
EOT
fi

if [ "$(POST loram)" != "none" ] && [ "$(POST loram)" != "" ]; then
	echo "Low RAM conversion: $(POST loram)" >> $log
	notify "$(gettext "Low RAM conversion:") $(POST loram)"
	mkdir -p $tmpdir/slitaz-$id/rootfs/etc/tazlito 2> /dev/null
	rm -f $tmpdir/slitaz-$id/rootfs/etc/tazlito/fastboot.iso 2> /dev/null
	cat > $tmpdir/slitaz-$id/rootfs/etc/tazlito/loram.final <<EOT
cd \$1/..
iso=\$(ls *.iso)
if [ -s "\$iso" ]; then
	echo "Converting \$iso to low ram iso..."
	yes y | tazlito build-loram \$iso \$iso.\$\$ $(POST loram)
	mv -f \$iso.\$\$ \$iso
	md5sum \$iso > \${iso%.iso}.md5
	echo "================================================================================"
fi
cd - > /dev/null
EOT
fi

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

<p>
$(gettext "Desktop Wallpaper in JPG format"):
<p>

<div class="inputfile">
	<div class="inputhide">
		<input type="file" name="wallpaper" size="48" />
	</div>
</div>
<input type="submit" value="Upload Image" style="margin-left: 6px;" />

<p>
$(gettext "Files on user desktop such as README, desktop files or documentation.
The files will be copied in the Home directory of each new user. SliTaz creates
the default Live user at boot. Allowed files and extensions are:") README 
.desktop .html .png .jpg:
<p>

<div class="inputfile">
	<div class="inputhide">
		<input type="file" name="desktop" size="48" />
	</div>
</div>
<input type="submit" value="Upload File" style="margin-left: 6px;" />


<h3>$(gettext "Rootfs tarball")</h3>
<p>
	The files in the rootfs archive must have the same directory structure
	as any standard SliTaz or Linux system. For example if you wish to
	have a custom boot configuration file, you will have: rootfs/etc/rcS.conf.
	Accepted tarball formats are: <strong>tar.gz tar.bz2 tar.lzma</strong>
	and the archived directory must be named rootfs with a valid file system
	hierachy such as: /usr/bin /etc /var/www
</p>

<div class="inputfile">
	<div class="inputhide">
		<input type="file" name="tarball" size="48" />
	</div>
</div>
<input type="submit" value="Upload rootfs" style="margin-left: 6px;" />

<h3>$(gettext "ISO image conversion")</h3>

	<input type="checkbox" name="fastboot" />
	$(gettext "Fast boot") - 
	$(gettext "Low RAM support"):
	<select name="loram">
		<option value="none">$(gettext "No")</option>
		<option value="ram">$(gettext "In RAM only")</option>
		<option value="smallcdrom">$(gettext "Small CDROM or RAM")</option>
		<option value="cdrom">$(gettext "Large CDROM or RAM")</option>
	</select>
	<input type="submit" value="Convert" />

<input type="hidden" name="id" value="$id" />
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

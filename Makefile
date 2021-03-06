# Makefile for SliTaz Pizza.
#

PACKAGE="pizza"
PREFIX?=/usr
DESTDIR?=
LINGUAS?=el fa fr it ja pl pt_BR ru sv vi zh_CN

all:

# i18n

pot:
	xgettext -o po/pizza.pot -L Shell --package-name="SliTaz Pizza" \
		./web/pizza.cgi ./web/pkgs.cgi ./web/rootfs.cgi

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/$$l.po po/$(PACKAGE).pot; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/pizza.mo po/$$l.po; \
	done;

# Installation

install: msgfmt
	install -m 0755 -d $(DESTDIR)/etc/slitaz
	install -m 0755 -d $(DESTDIR)$(PREFIX)/bin
	install -m 0755 -d $(DESTDIR)$(PREFIX)/share/pizza/public
	install -m 0755 -d $(DESTDIR)$(PREFIX)/share/pizza/web
	install -m 0755 -d $(DESTDIR)$(PREFIX)/share/pizza/web/images
	install -m 0755 -d $(DESTDIR)$(PREFIX)/share/pizza/web/lib
	install -m 0755 -d $(DESTDIR)$(PREFIX)/share/doc/pizza
	install -m 0755 pizza $(DESTDIR)$(PREFIX)/bin
	install -m 0755 pizza-bot $(DESTDIR)$(PREFIX)/share/pizza
	install -m 0755 public/index.cgi $(DESTDIR)$(PREFIX)/share/pizza/public
	install -m 0755 data/* $(DESTDIR)$(PREFIX)/share/pizza
	install -m 0644 pizza.conf $(DESTDIR)/etc/slitaz
	install -m 0644 README $(DESTDIR)$(PREFIX)/share/doc/pizza
	cp -a doc/* $(DESTDIR)$(PREFIX)/share/doc/pizza
	cp -a po/mo $(DESTDIR)$(PREFIX)/share/locale
	cp -a web $(DESTDIR)$(PREFIX)/share/pizza
	chown -R root.root $(DESTDIR)$(PREFIX)/share/pizza
	chmod 755 $(DESTDIR)$(PREFIX)/share/pizza/web/*.cgi

uninstall:
	rm -rf \
		$(DESTDIR)$(PREFIX)/bin/pizza \
		$(DESTDIR)/etc/slitaz/pizza.conf \
		$(DESTDIR)$(PREFIX)/share/pizza \
		$(DESTDIR)$(PREFIX)/share/doc/pizza

clean:
	rm -rf po/*~
	rm -rf po/mo
	rm -rf po/*.mo

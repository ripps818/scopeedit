PREFIX ?= $(HOME)/.local
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share/scopeedit
APPDIR = $(PREFIX)/share/applications
DESKTOP = $(APPDIR)/local.scopeedit.Gui.desktop

.PHONY: install uninstall check

install:
	install -Dm755 scopeedit $(DESTDIR)$(DATADIR)/scopeedit
	install -Dm755 scopeedit-gui $(DESTDIR)$(DATADIR)/scopeedit-gui
	install -Dm644 scopeedit.py $(DESTDIR)$(DATADIR)/scopeedit.py
	install -Dm644 legends.py $(DESTDIR)$(DATADIR)/legends.py
	install -d $(DESTDIR)$(BINDIR) $(DESTDIR)$(APPDIR)
	ln -sf $(DATADIR)/scopeedit $(DESTDIR)$(BINDIR)/scopeedit
	ln -sf $(DATADIR)/scopeedit-gui $(DESTDIR)$(BINDIR)/scopeedit-gui
	sed 's|@BINDIR@|$(BINDIR)|' local.scopeedit.Gui.desktop > $(DESTDIR)$(DESKTOP)

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/scopeedit $(DESTDIR)$(BINDIR)/scopeedit-gui $(DESTDIR)$(DESKTOP)
	rm -rf $(DESTDIR)$(DATADIR)

check:
	python3 -m py_compile scopeedit scopeedit-gui scopeedit.py legends.py

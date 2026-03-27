PROJECT_DIR := $(shell pwd)
PLIST_NAME := com.productivitylog.dashboard
PLIST_SRC := $(PROJECT_DIR)/$(PLIST_NAME).plist
PLIST_DST := $(HOME)/Library/LaunchAgents/$(PLIST_NAME).plist
UV := uv

.PHONY: sync dev install uninstall start stop restart status logs

sync:
	$(UV) sync

dev:
	$(UV) run flask --app src.dashboard.app:create_app run --host 127.0.0.1 --port 5050 --reload

install: sync
	cp $(PLIST_SRC) $(PLIST_DST)
	launchctl load $(PLIST_DST)
	@echo "Dashboard service installed and started."

uninstall:
	-launchctl unload $(PLIST_DST)
	-rm -f $(PLIST_DST)
	@echo "Dashboard service uninstalled."

start:
	launchctl start $(PLIST_NAME)

stop:
	launchctl stop $(PLIST_NAME)

restart: stop start

status:
	@launchctl list | grep $(PLIST_NAME) || echo "Service not loaded."
	@curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:5050/ 2>/dev/null || echo "Dashboard not responding."

logs:
	@tail -f /tmp/productivitylog-dashboard.log /tmp/productivitylog-dashboard.err

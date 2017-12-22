# Defaults for site level variables 
# These can be overridden in site-settings.Makefile from the site directory.
export SITE_SRS =
export SITE_NAME = $(notdir $(CURDIR))
export SITE_PROCESSES = dem.tif

# DEM Options
export SITE_DEM_COLORS_FILE = $(CURDIR)/dem-colors.txt

SITE_SESSIONS_PREFIX = "sessions"
SITE_SESSIONS =
SESSION_MAKE = $(MAKE) -f $(VM_SCRIPTS)/makefiles/session.Makefile

-include site-settings.Makefile

.PHONY: all site-header

all: site-header $(foreach session,$(SITE_SESSIONS),.session-$(session))
		
site-header:
	@echo "Processing site: $(SITE_NAME)"
	@echo "-----------------------------"	
	@echo "Srs: $(SITE_SRS)"
	@echo "Processes: $(SITE_PROCESSES)"


.session-%:	
	$(SESSION_MAKE) -C $(SITE_SESSIONS_PREFIX)/$(subst .session-,,$*)

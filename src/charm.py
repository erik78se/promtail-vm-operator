#!/usr/bin/env python3
# Copyright 2022 Erik Lönroth
# See LICENSE file for licensing details.
#

""" The Promtail subordinate charm:

"""

import logging
import os
import subprocess
import base64

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
from promtail_ops_manager import PromtailOpsManager

# Log messages can be retrieved using juju debug-log
logger = logging.getLogger(__name__)

class PromtailCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.promtail_ops_manager = PromtailOpsManager()
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.update_status, self._update_status)
        self.framework.observe(self.on.set_config_action, self._on_set_config_action)

    def _on_install(self, event):
        """Handle install event."""
        logger.info("Installing promtail...")
        zip_resource = self.model.resources.fetch('promtail-zipfile')
        self.promtail_ops_manager.install(zip_resource) # Prepares OS, installs binary and unitfile

    def _on_config_changed(self, event):
        """Handle changed configuration."""
        logger.info("Configuring promtail...")
        pass

    def _on_start(self, event):
        """Handle start event."""
        logger.info("Starting promtail...")
        self.promtail_ops_manager.start_promtail()
        self._set_status()
    
    def _update_status(self, event):
        """Handle update-status event."""
        self._set_status()

    def _on_set_config_action(self,event):
        """
        This action allows a user to upload a completely new config.
        
        juju run-action promtail/0 set-config config="$(base64 /tmp/promtail.yaml)" --wait

        The config is checked for errors before getting installed.

        Service is restarted if the config is OK.

        """
        base64_cfg = event.params['config']
        base64_bytes = base64_cfg.encode('ascii')
        cfg_bytes = base64.b64decode(base64_bytes)
        cfg = cfg_bytes.decode('ascii')

        with open('/tmp/_tmp_promtail_cfg.yaml', 'w') as f:
            f.write(cfg)
        
        if self.promtail_ops_manager.verify_config(filename='/tmp/_tmp_promtail_cfg.yaml'):
            logger.info("Writing new config.")
            self.promtail_ops_manager.promtail_cfg.write_text(cfg)
            event.log("Successfully wrote new config.")
            os.remove("/tmp/_tmp_v_cfg.yaml")
            self.promtail_ops_manager.restart_promtail()
        else:
            event.fail("promtail -verify-config said config is bougs. No config was written")

    def _set_status(self):
        """
        Manage the status of the service.
        """
        stat = subprocess.call(["systemctl", "is-active", "--quiet", "promtail"])
        if(stat == 0):  # if 0 (active), print "Active"
            v = self.promtail_ops_manager.promtail_version()
            self.unit.set_workload_version(v)
            self.unit.status = ActiveStatus("Active")
        else:
            self.unit.status = WaitingStatus("promtail service inactive.")


if __name__ == "__main__":  # pragma: nocover
    main(PromtailCharm)

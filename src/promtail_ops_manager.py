"""PromtailOpsManager Class"""
import os
import re
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path


class PromtailOpsManager:
    """
    Mangages the promtail service, such as installing, configuring, etc.

    This class should work independently from juju, such as that it can
    be tested without lauching a full juju environment.
    """

    def __init__(self):
        self.promtail_home = Path('/opt/promtail')
        self.promtail = Path('/opt/promtail/promtail-linux-amd64')
        self.promtail_cfg = self.promtail_home.joinpath('promtail-local-config.yaml')
        self.promtail_unitfile = Path('/etc/systemd/system/promtail.service')
        
    def _prepareOS(self):
        """ sudo mkdir /opt/promtail """
        try:
            subprocess.run(['mkdir', '-p', self.promtail_home], check = True)
            print(f"Prepared OS for promtail installation {self.promtail_home}")
        except:
            print(f"Error preparing OS for promtail installation {self.promtail_home}")
            sys.exit(1)

    def _install_from_resource(self, resource_path):
        """
        Install from a resource.
        """
        # Remove the promtail home dir if exists
        if self.promtail_home.exists():
            shutil.rmtree(self.promtail_home)

        # Unzip the juju resource into the build dir
        with zipfile.ZipFile(resource_path,"r") as zip_ref:
            zip_ref.extractall(self.promtail_home)
        

        try:
            os.system(f"ls {self.promtail}")
            subprocess.run(['chmod','a+x',self.promtail], check = True) 
        except:
            print("Error installing promtail binary")
            sys.exit(1)

    def _install_config(self):
        """
        Install the config from template.
        """
        if self.promtail_cfg.exists():
            self.promtail_cfg.unlink()
        promtailconfig_tmpl = Path('templates/promtail-varlog-config.yaml.tmpl').read_text()
        self.promtail_cfg.write_text(promtailconfig_tmpl)

    def _install_systemd_unitfile(self):
        """ Install the systemd unit file."""
        if self.promtail_unitfile.exists():
            self.promtail_unitfile.unlink()
        systemdunitfile_tmpl = Path('templates/promtail.service.tmpl').read_text()
        self.promtail_unitfile.write_text(systemdunitfile_tmpl)

    def stop_promtail(self):
        """Stop promtail"""
        try:
            subprocess.run(['systemctl','stop','promtail'], check = True)
        except Exception as e:
            print("Error stopping promtail", str(e))

    def start_promtail(self):
        """Start promtail"""
        try:
            subprocess.run(['systemctl','start','promtail'], check = True)            
        except Exception as e:
            print("Error starting promtail", str(e))
    
    def restart_promtail(self):
        """Restart promtail"""
        try:
            subprocess.run(['systemctl','restart','promtail'], check = True)            
        except Exception as e:
            print("Error starting promtail", str(e))


    def install(self, resource_file):
        """ Installs from a supplied zip file resource """
        self._prepareOS()
        self._install_from_resource(resource_file)
        self._install_config()
        self._install_systemd_unitfile()

    def promtail_version(self):
        """ Return the version of promtail as a string or None"""
        try:
            r = subprocess.run(
                [
                    self.promtail.resolve(), 
                    '-config.file', self.promtail_cfg.resolve(),
                    '-version'
                ],capture_output=True
            ).stdout.decode()            
            ver = re.search(r'version\s*([\d.]+)', r).group(1)
            return ver
        except Exception as e:
            print("Error getting version from promtail", e)
            return None

    def verify_config(self, filename=None):
        """ Use promtail -version to verify the config is legit """
        if filename:
            filetocheck = Path(filename)
        else:
            filetocheck = self.promtail_cfg
        try:
            r = subprocess.run(
                [
                    self.promtail.resolve(), 
                    '-config.file', filetocheck.resolve(),
                    '-version'
                ],capture_output=True
            )
            s = r.stdout.decode()
            return re.search(r'promtail', s)

        except Exception as e:
            print("Error verifying config", e)
            return None

    def _purge(self):
        """ Whipes the installation and remove all traces of promtail """
        try:
            subprocess.run(['rm', self.promtail], check = True)
            print("Success removing promtail bin", self.promtail)
            subprocess.run(['rm', self.promtail_unitfile], check = True)
            print("Success removing promtail unitfile", self.promtail_unitfile)
            subprocess.run(['rm', '-rf', self.promtail_home], check = True)
            print("Success purging promtail home dir", self.promtail_home)
        except:
            print("Error purging promtail")
from pathlib import Path
from promtail_ops_manager import PromtailOpsManager

# The promtail release file.
resource = "./promtail.zip"

manager = PromtailOpsManager()
# manager.install(resource)

# Setup for local tests such that installation of binaries etc.
# will not mess up your local client.
manager.promtail_home = Path('/tmp/promtail')
manager.promtail = Path('/tmp/promtail/promtail-linux-amd64')
manager.promtail_cfg = manager.promtail_home.joinpath('promtail-local-config.yaml')
manager.promtail_unitfile = Path('/tmp/promtail.service')

# Run tests.
manager._prepareOS()
manager._install_from_resource(resource)
manager._install_config()
manager._install_systemd_unitfile()
if manager.verify_config():
    print("Config OK")
else:
    print("Config is error")

print("Version:", manager.promtail_version() )
# manager._purge()

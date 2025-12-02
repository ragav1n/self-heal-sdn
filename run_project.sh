#!/bin/bash

# --- CONFIGURATION: PATHS TO VIRTUAL ENVIRONMENTS ---

# 1. Environment for Ryu Controller (Python 3.8 usually)
RYU_VENV="$HOME/Projects/self-heal-sdn/ryu_venv_38/bin/activate"

# 2. Environment for Telemetry Agent (Your main .venv)
# NOTE: If this .venv is inside the 'monitoring_and_telemetry' folder, 
# change the line below to: .../monitoring_and_telemetry/.venv/bin/activate
AGENT_VENV="$HOME/Projects/self-heal-sdn/monitoring_and_telemetry/.venv/bin/activate"
# ----------------------------------------------------

# 1. Kill old processes to ensure a clean start
echo "[*] Cleaning up old processes..."
sudo mn -c
sudo fuser -k 6633/tcp
sudo fuser -k 8080/tcp
sudo fuser -k 8000/tcp  # Telemetry port
sudo killall python3

# 2. Start Ryu Controller (Uses RYU_VENV)
echo "[*] Starting Ryu Controller..."
gnome-terminal --tab --title="Controller" -- bash -c "source $RYU_VENV; cd controller_apps; ryu-manager sh_controller.py --verbose --ofp-tcp-listen-port 6633; exec bash"

# 3. Wait for Controller to initialize
sleep 5

# 4. Start Telemetry Agent (Uses AGENT_VENV)
echo "[*] Starting Telemetry Agent..."
gnome-terminal --tab --title="Telemetry" -- bash -c "source $AGENT_VENV; cd monitoring_and_telemetry; python3 telemetry_agent.py; exec bash"

# 5. Start Mininet (Uses System Python + Sudo)
echo "[*] Starting Mininet Topology..."
cd mininet_topology
sudo python3 topo_healing.py

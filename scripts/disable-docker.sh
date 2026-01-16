#!/bin/bash

# =============================================================================
# THE "I HATE DOCKER" SCRIPT
# =============================================================================
# Because sometimes you just want your RAM back.
# =============================================================================

echo "Stopping Docker services.... (Shhh, go to sleep now)"
sudo systemctl stop docker docker.socket containerd

echo "Disabling docker auto-start... (Stay down!)"
sudo systemctl disable docker docker.socket containerd

echo ""
echo "----------------------------------------"
echo "  Paranoia Check (Trust issues?)"
echo "----------------------------------------"

echo -n "docker enabled: "
systemctl is-enabled docker 2>/dev/null || echo "disabled (Good.)"

echo -n "docker.socket enabled: "
systemctl is-enabled docker.socket 2>/dev/null || echo "disabled (Excellent.)"

echo -n "containerd enabled: "
systemctl is-enabled containerd 2>/dev/null || echo "disabled (Perfection.)"

echo ""
echo "Current Status:"
systemctl status docker --no-pager | grep -E "Active | Loader"

echo ""
echo "Done. Docker has been banished to the shadow realm."
echo "Your system is now free."

cat << "EOF"
      .
     / \
    /   \
   /  |  \
  /   |   \
 /    |    \
/_____|_____\
    R.I.P
   DOCKER
EOF

echo "................................."
echo "BYE BYE"
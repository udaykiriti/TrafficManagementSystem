#!/bin/bash

echo "Stopping Docker services...."
sudo systemctl stop docker docker.socket containered

echo "Disabling docker auto-start..."
sudo systemctl disable docker docker.socket containered

echo "<!----------------------------------------!>"
echo "two step verification.... for ur satisfaction"

echo -n "docker enabled: "
systemctl is-enabled docker 2>/dev/null || echo "disabled"

echo -n "docker.socket enabled: "
systemctl is-enabled docker.socket 2>/dev/null || echo "disabled"

echo -n "containered enabled: "
systemctl is-enabled containered 2>/dev/null || echo "disabled"

echo ""
echo "docker status:"
systemctl status docker --no-pager | grep -E "Active | Loader"

echo " "
echo "Done... Docker is stopped and disabled"
echo "..........................."
echo "BYE BYE"

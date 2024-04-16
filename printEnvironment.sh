#!/bin/bash

# The function is used to obtain distribution information
get_distro_info() {
    local distro_id=$(lsb_release -i -s 2>/dev/null)
    local distro_version=$(lsb_release -r -s 2>/dev/null)
    local kernel_version=$(uname -r)

    # If lsd_release is not available, try parsing the/etc/* - release file
    if [ -z "$distro_id" ] || [ -z "$distro_version" ]; then
        distro_id=$(grep '^ID=' /etc/*-release | cut -d= -f2 | tr -d '"')
        distro_version=$(grep '^VERSION_ID=' /etc/*-release | cut -d= -f2 | tr -d '"')
    fi

    echo "$distro_id $distro_version (Kernel version: $kernel_version)"
}

# get Git repo name
git_repo_name=''
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    git_repo_name=$(basename "$(git rev-parse --show-toplevel)")
    if [ $? -ne 0 ]; then
        git_repo_name="(Can't get repo name)"
    fi
else
    git_repo_name="It NOT a Git repo"
fi

# get CPU type
cpu_model=$(uname -m)

# get memory size
memory_size=$(free -h | grep Mem | awk '{print $2}')

# get docker version
docker_version=''
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | cut -d ' ' -f3)
else
    docker_version="Docker not installed"
fi

# get python version
python_version=''
if command -v python &> /dev/null; then
    python_version=$(python --version | cut -d ' ' -f2)
else
    python_version="Python not installed"
fi

# Print all infomation
echo "Current Repo：$git_repo_name"
echo "Operating system: $(get_distro_info)"
echo "CPU Type：$cpu_model"
echo "Memory：$memory_size"
echo "Docker Version：$docker_version"
echo "Python Version：$python_version"

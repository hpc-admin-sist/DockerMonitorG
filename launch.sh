#!/bin/zsh

BASE="/p300/g_cluster/DockerMonitor"
cd $BASE

tmux start-server
tmux new-session -d -s G-ClusterMonitor -n main
tmux new-window -t G-ClusterMonitor:1 -n gpu
tmux new-window -t G-ClusterMonitor:2 -n container

tmux send-keys -t  G-ClusterMonitor:0 "cd $BASE; python main.py" C-m
tmux send-keys -t  G-ClusterMonitor:1 "cd $BASE; python gpu_tools/save_all_nodes_gpu_msg.py" C-m
tmux send-keys -t  G-ClusterMonitor:2 "cd $BASE; python docker_tools/save_all_nodes_container_status.py" C-m

tmux select-window -t G-ClusterMonitor:0
tmux attach-session -t G-ClusterMonitor
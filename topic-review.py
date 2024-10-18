#!/usr/bin/env python
import argparse
import sys
import subprocess
import json
import re

def label_patches(args):
    topic_list = re.split(',', args.topic)
    topic_list = list(dict.fromkeys(topic_list))  # remove duplications

    for topic in topic_list:
        command = ['ssh', '-p', str(args.port), args.server, args.remote, 'query', '--format=JSON', '--dependencies', '--current-patch-set', 'topic:' + topic]
        print(f"Querying topic '{topic}' with command: {' '.join(command)}")
        try:
            commits = subprocess.check_output(command).decode('utf-8').strip().splitlines()
            patches = []

            # Parse each line as JSON
            for line in commits:
                if line.strip():  # Skip empty lines
                    patches.append(json.loads(line))

            for patch in patches:
                if 'currentPatchSet' not in patch or 'project' not in patch or 'number' not in patch:
                    print("Warning: patch does not have 'currentPatchSet', 'project', or 'number' field, skipping...")
                    continue

                # Check the contents of currentPatchSet
                current_patch_set = patch['currentPatchSet']
                print(f"Current Patch Set: {current_patch_set}")  # Debugging line

                if 'revision' not in current_patch_set:
                    print("Warning: 'revision' field not found in currentPatchSet, skipping...")
                    continue

                project = patch['project']
                change_number = patch['number']
                patch_set_number = current_patch_set['number']

                # Construct the full patch identifier (change-id/patch-set-number)
                full_patch_id = f"{change_number},{patch_set_number}"

                review_command = [
                    'ssh', '-p', str(args.port), args.server,
                    'gerrit', 'review', '--project', project,
                    f'--label={args.label}={args.score}' if args.label else '',  # 仅在提供 label 时添加
                    full_patch_id
                ]

                # 添加消息参数，仅在提供时加入
                if args.message:
                    review_command.append(f'--message={args.message}')

                # 清理空字符串（如果 label 未提供）
                review_command = [arg for arg in review_command if arg]

                print(f"Preparing to label patch '{full_patch_id}' in project '{project}' with command: {' '.join(review_command)}")

                try:
                    subprocess.check_call(review_command)
                    print(f"Successfully labeled patch '{full_patch_id}'")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to label patch '{full_patch_id}'. Error: {e}")
                    print(f"Command that failed: {' '.join(review_command)}")
                    print(f"Return code: {e.returncode}")
                    print(f"Output: {e.output}")

        except subprocess.CalledProcessError as e:
            print(f"Error occurred while executing command: {' '.join(command)}")
            print(f"Error code: {e.returncode}")
            print(f"Output: {e.output}")
            sys.exit(1)

def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Label Gerrit patches')
    parser.add_argument('-t', '--topic', help='You can assign multiple topics by putting comma between them', required=True)
    parser.add_argument('-s', '--server', help='Gerrit server', required=True)
    parser.add_argument('-r', '--remote', help='Git remote name', default="gerrit")
    parser.add_argument('-p', '--port', help='SSH port', default=29418)
    parser.add_argument('--label', help='Label to apply (e.g., Code-Review, Verified)', required=False)
    parser.add_argument('--score', help='Score to apply (e.g., +1, +2, -1, -2, 0)', required=False)
    parser.add_argument('--message', help='Message for the review', required=False)  # 修改为可选参数
    return parser.parse_args(args)

if __name__ == '__main__':
    args = check_arg(sys.argv[1:])
    # Ensure score is provided when label is provided
    if args.label and args.score is None:
        print("Error: '--score' is required when '--label' is provided.")
        sys.exit(1)
    label_patches(args)

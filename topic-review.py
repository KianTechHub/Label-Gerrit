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
            # 获取所有commit，注意：这里分割时使用了strip()去除换行符
            commits = subprocess.check_output(command).decode('utf-8').strip().splitlines()
            print(f"Raw commit data received: {commits}")  # 输出原始数据供调试

            patches = []

            # 解析每一行，确保每一行是有效的JSON对象
            for line in commits:
                line = line.strip()  # 去除多余的空格或换行符
                if not line:
                    print("Skipping empty line.")  # 跳过空行
                    continue

                try:
                    patch = json.loads(line)

                    # 跳过 "type": "stats" 类型的行
                    if 'type' in patch and patch['type'] == 'stats':
                        print("Skipping stats information.")
                        continue

                    patches.append(patch)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line}")  # 跳过无效的JSON行
                    continue

            # 处理解析出的每个patch
            for patch in patches:
                if 'currentPatchSet' not in patch or 'project' not in patch or 'number' not in patch:
                    print("Warning: patch does not have 'currentPatchSet', 'project', or 'number' field, skipping...")
                    continue

                # 检查currentPatchSet内容
                current_patch_set = patch['currentPatchSet']
                print(f"Current Patch Set: {current_patch_set}")  # 调试输出当前Patch Set

                if 'revision' not in current_patch_set:
                    print("Warning: 'revision' field not found in currentPatchSet, skipping...")
                    continue

                project = patch['project']
                change_number = patch['number']
                patch_set_number = current_patch_set['number']

                # 构建完整的patch标识符 (change-id/patch-set-number)
                full_patch_id = f"{change_number},{patch_set_number}"

                review_command = [
                    'ssh', '-p', str(args.port), args.server,
                    'gerrit', 'review', '--project', project,
                    f'--label={args.label}={args.score}', full_patch_id
                ]

                # 如果提供了消息，则将其添加到命令中
                if args.message:
                    # 使用 -m '"message内容"' 格式
                    review_command.append(f'-m \'"{args.message}"\'')

                print(f"Preparing to label patch '{full_patch_id}' in project '{project}' with command: {' '.join(review_command)}")

                try:
                    subprocess.run(' '.join(review_command), shell=True, check=True)
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
    parser.add_argument('--message', help='Message for the review', required=False)  # Make message optional
    return parser.parse_args(args)

if __name__ == '__main__':
    args = check_arg(sys.argv[1:])
    # 确保在提供label时提供score
    if args.label and args.score is None:
        print("Error: '--score' is required when '--label' is provided.")
        sys.exit(1)
    label_patches(args)


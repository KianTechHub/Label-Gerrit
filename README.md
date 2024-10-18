# Label-Gerrit

```markdown
# Gerrit Patch Labeling Tool

This script allows users to label Gerrit patches associated with specific topics quickly. You can apply labels like `Code-Review` or `Verified` along with a specified score (`+1`, `+2`, `-1`, `-2`, or `0`) to the patches without downloading them, assuming that the patches are already verified.

## Features

- **Label Patches**: Easily label multiple patches based on specified Gerrit topics.
- **Customizable Labels and Scores**: Specify any label and score you want to apply.
- **Multi-topic Support**: Apply labels to patches related to multiple topics at once.

## Requirements

- Python 3.x
- Access to a Gerrit server
- SSH access to the Gerrit server with the necessary permissions to label patches.

## Usage

To run the script, use the following command:

```bash
python3 label_patches.py --topic <TOPIC> --server <SERVER> --label <LABEL> --score <SCORE> [--remote <REMOTE>] [--port <PORT>]
```

### Parameters

- `-t`, `--topic`: Comma-separated list of topics (e.g., `T-1234,T-5678`).
- `-s`, `--server`: The Gerrit server address.
- `-r`, `--remote`: (Optional) Git remote name. Defaults to `gerrit`.
- `-p`, `--port`: (Optional) SSH port for Gerrit. Defaults to `29418`.
- `--label`: The label to apply (e.g., `Code-Review`, `Verified`).
- `--score`: The score to apply (e.g., `+1`, `+2`, `-1`, `-2`, `0`).

### Example

To label patches associated with the topic `T-1234` on the server `gerrit.yourcompany.com`, applying a `Code-Review` label with a score of `+1`, use the following command:

```bash
python3 label_patches.py --topic T-1234 --server gerrit.yourcompany.com --label Code-Review --score +1
```

## Error Handling

- The script will output warnings if no patches are found for the specified topics.
- If there are issues executing the commands, the script will print the error messages and exit.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you would like to contribute to this project.
```


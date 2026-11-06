# OSS Release Check

A small, dependency-free command-line tool that checks a local repository for common open-source release basics: a README, license, contributor guidance, code of conduct, security policy, changelog, CI workflow, issue guidance, and (when present) a package license field.

It is intended as a practical checklist for maintainers preparing a first public release or reviewing an existing repository. It reads local files only; it does not contact GitHub or any other service.

## Requirements

- Python 3.10 or newer
- No third-party packages

## Use

Run from the repository root:

```console
python /path/to/oss_release_check.py .
```

Choose a machine-readable or copyable report:

```console
python /path/to/oss_release_check.py . --format json
python /path/to/oss_release_check.py . --format markdown > release-check.md
```

Or point it at another local directory:

```console
python /path/to/oss_release_check.py ../my-project
```

The report distinguishes missing recommendations from optional checks. A present file is only detected by common filename; the tool does not judge whether its contents are correct or sufficient. It is not legal, security, quality, impact, or funding-program advice.

## Checks

| Check | What it looks for |
|---|---|
| README | Common README filenames and non-empty content |
| LICENSE | Common license filenames and non-empty content |
| CONTRIBUTING | Contributor instructions |
| CODE_OF_CONDUCT | Community expectations |
| SECURITY | Vulnerability reporting guidance |
| CHANGELOG | A project change history |
| CI_WORKFLOW | At least one file in `.github/workflows/` |
| ISSUE_GUIDANCE | GitHub issue templates or guidance (optional) |
| PACKAGE_LICENSE_METADATA | A license field in common Python, Node.js, or Rust manifests (when found) |

## Limitations

- Filename checks can produce false positives; read the files yourself.
- CI workflow files are detected, not executed or evaluated.
- Package metadata parsing is intentionally lightweight.
- The tool makes no claim about project adoption or open-source program eligibility.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and focused improvements are welcome.

## License

MIT. See [LICENSE](LICENSE).

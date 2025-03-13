# Test Cases

## Thunderbird

## B2G

### Releases

Not currently supported

### Candidates

Not currently supported

## URL

## Retries

```bash
mozdownload -a firefox -t daily -p win32 --retry-attempts=2
mozdownload -a firefox -t daily -p win32 --retry-attempts=2 --retry-delay=0
```

## Errors

```bash
mozdownload -a firefox -t release -p win32 -v invalid
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2 --retry-delay=0
```

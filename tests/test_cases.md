# Test Cases

## Thunderbird

### Tinderbox

```
mozdownload -a thunderbird -t tinderbox -p linux --branch=comm-central --extension=txt
```

## B2G

### Releases
Not currently supported

### Candidates
Not currently supported

### Tinderbox
Not currently supported

## URL

## Retries
```
mozdownload -a firefox -t daily -p win32 --retry-attempts=2
mozdownload -a firefox -t daily -p win32 --retry-attempts=2 --retry-delay=0
```

## Errors
```
mozdownload -a firefox -t release -p win32 -v invalid
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2 --retry-delay=0
```

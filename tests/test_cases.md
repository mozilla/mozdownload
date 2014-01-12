# Test Cases

## Correct Choice of Scraper
```
mozdownload -t release -p win32 -v latest
mozdownload -t candidate -p win32 -v 21.0
mozdownload -t daily -p win32
mozdownload -t tinderbox -p win32
```

## Firefox

### Tinderbox

<!-- Issue #144 -->
```
mozdownload -a firefox -p mac64 --branch=mozilla-central
```

## Thunderbird

### Tinderbox

```
mozdownload -a thunderbird -t tinderbox -p linux --branch=mozilla-central --extension=txt
```

## B2G

### Releases
Not currently supported

### Candidates
Not currently supported

### Tinderbox
Not currently supported

## URL
* need test case for password protected URL resource [bug 895835](https://bugzilla.mozilla.org/show_bug.cgi?id=895835)

```
mozdownload --url=https://mozqa.com/index.html
mozdownload --url=https://mozqa.com/index.html -d url-downloads
mozdownload --url=https://mozqa.com/index.html --username=username --password=password
```

## Errors
```
mozdownload -a firefox -t daily -p win32 --branch=invalid
mozdownload -a firefox -t daily -p win32 --branch=invalid --retry-attempts=2
mozdownload -a firefox -t daily -p win32 --branch=invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p win32 -v invalid
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2 --retry-delay=0
```

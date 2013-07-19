# Test Cases

## Firefox

### Releases
```
mozdownload -p win32 -v latest
mozdownload -t release -p win32 -v latest
mozdownload -a firefox -p win32 -v latest
mozdownload -a firefox -t release -p linux -v latest
mozdownload -a firefox -t release -p linux64 -v latest
mozdownload -a firefox -t release -p mac -v latest
mozdownload -a firefox -t release -p win32 -v latest
mozdownload -a firefox -t release -p win32 -v latest -d firefox-release-builds
mozdownload -a firefox -t release -p win32 -v latest -l de
mozdownload -a firefox -t release -p win32 -v 21.0
mozdownload -a firefox -t release -p win32 -v 21.0 -l es-ES
```

### Candidates
* unable to find unsigned candidate builds #108

```
mozdownload -t candidate -p win32 -v 21.0
mozdownload -a firefox -t candidate -p linux -v 21.0
mozdownload -a firefox -t candidate -p linux64 -v 21.0
mozdownload -a firefox -t candidate -p mac -v 21.0
mozdownload -a firefox -t candidate -p win32 -v 21.0
mozdownload -a firefox -t candidate -p win32 -v 21.0 -d firefox-candidate-builds
mozdownload -a firefox -t candidate -p win32 -v 21.0 -l cs
mozdownload -a firefox -t candidate -p win32 -v 21.0 -l en-GB
mozdownload -a firefox -t candidate -p win32 -v 21.0 --build-number=1
```

### Daily
* some folders do not contain builds #11
* multiple matches are shown when specifying a unique build id #102

```
mozdownload -t daily -p win32
mozdownload -t daily -p win32 --branch=mozilla-central
mozdownload -a firefox -t daily -p win32
mozdownload -a firefox -t daily -p linux --branch=mozilla-central
mozdownload -a firefox -t daily -p linux64 --branch=mozilla-central
mozdownload -a firefox -t daily -p mac --branch=mozilla-central
mozdownload -a firefox -t daily -p win32 --branch=mozilla-central
mozdownload -a firefox -t daily -p win64 --branch=mozilla-central
mozdownload -a firefox -t daily -p linux --branch=mozilla-central --extension=txt
mozdownload -a firefox -t daily -p win32 --branch=mozilla-central -d firefox-daily-builds
mozdownload -a firefox -t daily -p win32 --branch=mozilla-central -l it
mozdownload -a firefox -t daily -p win32 --branch=mozilla-central -l sv-SE
mozdownload -a firefox -t daily -p win32 --branch=mozilla-central --build-id=20130706031213
mozdownload -a firefox -t daily -p win32 --branch=mozilla-central --date=2013-07-02
mozdownload -a firefox -t daily -p win32 --branch=mozilla-central --date=2013-07-02 --build-number=1
mozdownload -a firefox -t daily -p win32 --branch=mozilla-aurora
mozdownload -a firefox -t daily -p win32 --branch=ux
```

### Tinderbox
* unable to download tinderbox builds by timestamp #103

```
mozdownload -t tinderbox -p win32
mozdownload -t tinderbox -p win32 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win32
mozdownload -a firefox -t tinderbox -p linux --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p linux64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p mac64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win64 --branch=mozilla-central
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --extension=tests.zip
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --debug-build
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central -d firefox-tinderbox-builds
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central -l el
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central -l pt-PT
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --date=2013-07-17
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --date=2013-07-17 --build-number=1
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-central --date=1374141721
mozdownload -a firefox -t tinderbox -p win32 --branch=mozilla-inbound
```

## Thunderbird

### Releases
```
mozdownload -a thunderbird -p win32 -v latest
mozdownload -a thunderbird -t release -p linux -v latest
mozdownload -a thunderbird -t release -p linux64 -v latest
mozdownload -a thunderbird -t release -p mac -v latest
mozdownload -a thunderbird -t release -p win32 -v latest
mozdownload -a thunderbird -t release -p win32 -v latest -d thunderbird-release-builds
mozdownload -a thunderbird -t release -p win32 -v latest -l de
mozdownload -a thunderbird -t release -p win32 -v 16.0
mozdownload -a thunderbird -t release -p win32 -v 16.0 -l es-ES
```

### Candidates
* unable to find unsigned candidate builds #108

```
mozdownload -a thunderbird -t candidate -p linux -v 10.0.5esr
mozdownload -a thunderbird -t candidate -p linux64 -v 10.0.5esr
mozdownload -a thunderbird -t candidate -p mac -v 10.0.5esr
mozdownload -a thunderbird -t candidate -p win32 -v 10.0.5esr
mozdownload -a thunderbird -t candidate -p win32 -v 10.0.5esr -d thunderbird-candidate-builds
mozdownload -a thunderbird -t candidate -p win32 -v 10.0.5esr -l cs
mozdownload -a thunderbird -t candidate -p win32 -v 10.0.5esr -l en-GB
mozdownload -a thunderbird -t candidate -p win32 -v 10.0.5esr --build-number=1
```

### Daily
* multiple matches are shown when specifying a unique build id #102

```
mozdownload -a thunderbird -t daily -p linux --branch=comm-central
mozdownload -a thunderbird -t daily -p linux64 --branch=comm-central
mozdownload -a thunderbird -t daily -p mac --branch=comm-central
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central
mozdownload -a thunderbird -t daily -p win64 --branch=comm-central
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central --extension=tests.zip
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central -d thunderbird-daily-builds
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central -l it
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central -l sv-SE
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central --build-id=20130710030204
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central --date=2013-07-10
mozdownload -a thunderbird -t daily -p win32 --branch=comm-central --date=2013-07-10 --build-number=1
mozdownload -a thunderbird -t daily -p win32 --branch=comm-aurora
```

### Tinderbox
* some folders do not contain builds #11
* unable to download tinderbox builds by timestamp #103

```
mozdownload -a thunderbird -t tinderbox -p linux --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p linux64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p mac64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p win64 --branch=comm-central
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --extension=tests.zip
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --debug-build
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central -d thunderbird-tinderbox-builds
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central -l el
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central -l pt-PT
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --date=2013-07-17
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --date=2013-07-17 --build-number=1
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-central --date=1374084645
mozdownload -a thunderbird -t tinderbox -p win32 --branch=comm-aurora
```

## B2G

### Releases
Not currently supported

### Candidates
Not currently supported

### Daily
Not currently supported due to #104

<!--
```
mozdownload -a b2g -t daily -p linux --branch=mozilla-central
mozdownload -a b2g -t daily -p linux64 --branch=mozilla-central
mozdownload -a b2g -t daily -p mac64 --branch=mozilla-central
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central -d b2g-daily-builds
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central -l en-US
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central --date=2013-07-02
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central --date=2013-07-02 --build-number=1
mozdownload -a b2g -t daily -p win32 --branch=mozilla-central --build-id=20130702031336
```
-->

### Tinderbox
Not currently supported

## URL
* downloaded url resources are not placed in target directory #105
* need test case for password protected URL resource [bug 895835](https://bugzilla.mozilla.org/show_bug.cgi?id=895835)

```
mozdownload --url=https://mozqa.com/index.html
mozdownload --url=https://mozqa.com/index.html -d url-downloads
mozdownload --url=https://mozqa.com/index.html --username=username --password=password
```

## Errors
* first retry attempt does not pause for the retry delay #106

```
mozdownload -a firefox -t daily -p win32 --branch=invalid
mozdownload -a firefox -t daily -p win32 --branch=invalid --retry-attempts=2
mozdownload -a firefox -t daily -p win32 --branch=invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p win32 -v invalid
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v invalid --retry-attempts=2 --retry-delay=0
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-attempts=2
mozdownload -a firefox -t release -p win32 -v latest --timeout=0.1 --retry-delay=0
```

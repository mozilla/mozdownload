## How to contribute
So you want to write code and get it landed in the official mozdownload repository? Then first fork [our repository](https://github.com/mozilla/mozdownload) into your own Github account, and create a local clone of it as described in the [installation instructions](https://github.com/mozilla/mozdownload#installation). The latter will be used to get new features implemented or bugs fixed. Once done and you have the code locally on the disk, you can get started. We advice to not work directly on the master branch, but to create a separate branch for each issue you are working on. That way you can easily switch between different work, and you can update each one for latest changes on upstream master individually. Check also our [best practices for Git](http://ateam-bootcamp.readthedocs.org/en/latest/reference/git_github.html).

### Writing Code
For writing the code just follow our [Python style guide](http://ateam-bootcamp.readthedocs.org/en/latest/reference/python-style.html), and also test with [pylama](https://pypi.python.org/pypi/pylama). If there is something unclear of the style, just look at existing code which might help you to understand it better.

### Submitting Patches
When you think the code is ready for review a pull request should be created on Github. Owners of the repository will watch out for new PR's and review them in regular intervals. By default for each change in the PR we automatically run all the tests via [Github Actions](https://github.com/mozilla/mozdownload/actions). If tests are failing make sure to address the failures immediately. Otherwise you can wait for a review. If comments have been given in a review, they have to get integrated. For those changes a separate commit should be created and pushed to your remote development branch. Don't forget to add a comment in the PR afterward, so everyone gets notified by Github. Keep in mind that reviews can span multiple cycles until the owners are happy with the new code.

## Managing the Repository

### Merging Pull Requests
Once a PR is in its final state it needs to be merged into the upstream master branch. For that please **DO NOT** use the Github merge button! But merge it yourself on the command line. Reason is that we want to hvae a clean history. Before pushing the changes to upstream master make sure that all individual commits have been squashed into a single one with a commit message ending with the issue number, e.g. "Fix for broken download behavior (#45)". Also check with `git log` to not push merge commits. Only merge PRs where Github Actions does not report any failure!

### Versioning
In irregular intervals we are releasing new versions of mozdownload. Therefore we make use of milestones in the repository. For each implemented feature or fix the issue's milestone flag should be set to the next upcoming release. That way its easier to see what will be part of the next release.

When releasing a new version of mozdownload please ensure to also update the history.md file with all the landed features and bug fixes. You are advised to use the [following issue](https://github.com/mozilla/mozdownload/issues/303) as template for the new release issue which needs to be filed. Please also check the associated PR for the code changes to be made.

To build and upload the new package to PyPI follow the commands below. Keep in mind that you need [wheel](https://pypi.python.org/pypi/wheel) and [twine](https://pypi.python.org/pypi/twine) to be installed and the [~/.pypirc](https://docs.python.org/2/distutils/packageindex.html#the-pypirc-file) file updated.

* rm -rf dist/
* python setup.py sdist bdist_wheel
* twine upload dist/*

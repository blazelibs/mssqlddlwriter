# script should be run from package root if not being run in Jenkins
if [ -z "$WORKSPACE" ]; then
    VENVDIR="/tmp/mssqlddlwriter-jenkins-venv"
else
    VENVDIR="$WORKSPACE/.venv-install"
    cd "$WORKSPACE"
fi

# remove the install venv so we start from scratch
rm -rf "$VENVDIR"

# create a new virtualenv
virtualenv "$VENVDIR" --no-site-packages -q

# activate virtualenv
source "$VENVDIR/bin/activate"

# install from pypi
pip install "https://bitbucket.org/rsyring/mssqlddlwriter/get/tip.zip#egg=mssqlddlwriter"

# import it
python -c 'import mssqlddlwriter'

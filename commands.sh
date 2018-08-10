# usage from clean slate:

# git clone https://github.com/melhof/Badulina-control-system.git
# cd Badulina-control-system
# source commands.sh
# badulina-development

badulina-development() {
    agua-build
    agua-init
    ./app.py
}
badulina-server() {
    agua-install
    agua-build
    ln -s /usr/lib/python3/dist-packages/widgetlords lib/python3.5/site-packages/
    agua-init
    agua-startup
}
agua-build() {
    # install python packages and init db
    python3 -m venv .
    source bin/activate

    pip install --upgrade pip
    pip install -r requirements.txt 
}
agua-init() {
    flask db upgrade # create db
    flask agua_init # populate db
}
agua-install() {
    # install system packages
    wget https://github.com/widgetlords/libwidgetlords/releases/download/v1.0.2/libwidgetlords_1.0.2_armhf.deb
    sudo dpkg -i libwidgetlords_1.0.2_armhf.deb
    rm libwidgetlords_1.0.2_armhf.deb 
}
agua-uninstall() {
    # uninstall system packages
    sudo apt remove libwidgetlords
}
agua-startup() {
    sudo cp daemons/agua.service /etc/systemd/system/
    sudo systemctl enable agua.service
    sudo service agua restart

    systemctl status agua.service
}
agua-shutdown() {
    sudo service agua stop
    sudo systemctl disable agua.service
    sudo rm /etc/systemd/system/agua.service
}
agua-deploy() {
    # restart agua service
    sudo service agua stop
    source bin/activate

    flask db upgrade

    sudo service agua start
}

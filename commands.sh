# usage from clean slate:

# git clone gitserver/agua/
# cd agua/
# source commands
# agua-install
# agua-build

agua-install() {
    # install system packages and start services
    wget https://github.com/widgetlords/libwidgetlords/releases/download/v1.0.2/libwidgetlords_1.0.2_armhf.deb
    sudo dpkg -i libwidgetlords_1.0.2_armhf.deb
    rm libwidgetlords_1.0.2_armhf.deb 
}

agua-uninstall() {
    # uninstall system packages and stop services
    sudo service agua stop
    sudo systemctl disable agua.service

    sudo rm /etc/systemd/system/agua.service

    sudo apt remove libwidgetlords
}

agua-build() {
    # clone repo, build & start agua app
    python3 -m venv .
    source bin/activate

    pip install -r requirements.txt 
    ln -s /usr/lib/python3/dist-packages/widgetlords lib/python3.5/site-packages/
    
    flask db init
    flask db migrate
    flask db upgrade

    flask agua_init

    sudo cp daemons/agua.service /etc/systemd/system/
    sudo systemctl enable agua.service
    sudo service agua restart

    systemctl status agua.service
}

agua-deploy() {
    # restart agua service
    sudo service agua stop
    source bin/activate

    flask db migrate
    flask db upgrade

    sudo service agua start

}

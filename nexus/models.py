from app import db

class Device(db.Model):
    __tablename__ = "device"
    id = db.Column(db.Integer, primary_key=True)
    # area for tags:
    # area = db.Column(db.String(20))
    hostname = db.Column(db.String(40), unique=True, index=True, nullable=False)
    IP = db.Column(db.String(20), unique=True)
    platform = db.Column(db.String(40))
    SW_type = db.Column(db.String(200))
    SW_version = db.Column(db.String(200))
    bootflask_free_size = db.Column(db.Float())
    memory_size = db.Column(db.Float())
    target_image_existing = db.Column(db.Boolean())
    location = db.Column(db.String(80))
    uptime = db.Column(db.DateTime())
    number_servers = db.Column(db.Integer())
    tags = db.Column(db.String(120))
    updated_by = db.Column(db.DateTime())

    #Defining One to Many relationships with the relationship function on the Parent Table
    interfaces = db.relationship('Interfaces', backref="device", lazy='dynamic')

    def __init__(self, hostname, IP, platform, SW_type, SW_version, uptime, memory_size, updated_by):
        self.hostname = hostname
        self.IP = IP
        self.platform = platform
        self.SW_type = SW_type
        self.SW_version = SW_version
        self.memory_size = memory_size
        self.uptime = uptime
        self.updated_by = updated_by

    def __repr__(self):
        return '<Hostname %r>' % self.hostname

class Interfaces(db.Model):
    __tablename__ = "interfaces"
    id = db.Column(db.Integer, primary_key=True)
    interface = db.Column(db.String(120), nullable=False)
    desc = db.Column(db.String(255))
    status = db.Column(db.String(40))
    operate_mode = db.Column(db.String(20))
    stp_edge = db.Column(db.Boolean())
    rx_transceiver = db.Column(db.Float())
    Last_link_flapped = db.Column(db.DateTime())
    #Defining the Foreign Key on the Child Table
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    #Defining One to Many relationships with the relationship function on the Parent Table
    cdp_interface = db.relationship('CDP', backref="interface", lazy='dynamic')

    def __init__(self, interface, desc, status, operate_mode):
        self.interface = interface
        self.desc = desc
        self.status = status
        self.operate_mode = operate_mode

    def __repr__(self):
        return '<interface %r>' % self.interface

class CDP(db.Model):
    __tablename__ = "cdp"
    id = db.Column(db.Integer, primary_key=True)
    peer_interface = db.Column(db.String(120))
    peer_hostname = db.Column(db.String(40))
    #Defining the Foreign Key on the Child Table
    interface_id = db.Column(db.Integer, db.ForeignKey('interfaces.id'))

    def __init__(self, peer_interface, peer_hostname):
        self.peer_interface = peer_interface
        self.peer_hostname = peer_hostname

    def __repr__(self):
        return '<interface %r>' % self.interface

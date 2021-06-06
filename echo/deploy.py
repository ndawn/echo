import os
from ipaddress import IPv4Address, IPv4Network

from fabric import Config as FabricConfig, Connection
from scapy.layers.inet import IP, TCP, sr1, traceroute as scapy_traceroute
from scapy.volatile import RandShort
import json

from echo.config import SERVER_HOST
from echo.models.db import Agent, Device, DeviceTypeEnum
from echo.models.pydantic import PyDeviceTraced


class TemporaryAgentConfig:
    def __init__(self, agent: Agent):
        self.__agent = agent
        self.__agent_config = None
        self.__temp_file_name = f'.tmp.agent.{self.__agent.pk}.json'

    def _make_config(self):
        self.__agent_config['server_hostname'] = SERVER_HOST
        self.__agent_config['subnet'] = self.__agent.subnet.cidr
        self.__agent_config['token'] = self.__agent.token

    def __enter__(self):
        with open('agent_config.json') as config_file:
            self.__agent_config = json.load(config_file)

        self._make_config()

        with open(self.__temp_file_name, 'w') as temp_file:
            json.dump(self.__agent_config, temp_file)

        return self.__temp_file_name

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.__temp_file_name)


def traceroute(ip: IPv4Address) -> list[IPv4Address]:
    ip_string = str(ip)

    ans, unans = scapy_traceroute(ip_string)

    nodes = []

    for snd, rcv in ans:
        nodes.append((snd.ttl, rcv.src))

        if rcv.src == ip_string:
            break

    nodes.sort(key=lambda node: node[0])

    return list(map(lambda node: node[1], nodes))


def scan_address(ip: IPv4Address) -> PyDeviceTraced:
    ip_string = str(ip)

    with open('agent_config.json') as config:
        ports = json.load(config)['ports']

    available_ports = []
    source_port = RandShort()

    for port_ in ports:
        port = int(port_)

        answer = sr1(
            IP(dst=ip_string) / TCP(sport=source_port, dport=port, flags='S'),
            verbose=0,
            timeout=0.5,
        )

        if (answer is not None) and (answer.haslayer(TCP)) and (answer.getlayer(TCP).flags == 0x12):
            available_ports.append((ports[str(port)], port))

            sr1(
                IP(dst=ip_string) / TCP(sport=source_port, dport=port, flags='R'),
                verbose=0,
                timeout=0,
            )

    return PyDeviceTraced(ip=ip, ports=available_ports)


async def create_non_existent_devices(device_list: list[PyDeviceTraced], agent: Agent):
    if not device_list:
        return

    db_devices = []

    for traced_device in device_list:
        device = await Device.get_or_none(address=str(traced_device.ip))

        if device is None:
            device = await Device.create(
                address=str(traced_device.ip),
                subnet=agent.subnet if traced_device.ip in IPv4Network(agent.subnet.cidr) else None,
                type=DeviceTypeEnum.ECHO if str(traced_device.ip) == agent.address else DeviceTypeEnum.UNKNOWN,
                connected_with=[],
                connection_options=traced_device.ports,
            )

        db_devices.append(device)

    for i in range(len(db_devices)):
        neighbours = []

        if i != 0:
            neighbours.append(db_devices[i - 1].pk)

        if i != len(db_devices) - 1:
            neighbours.append(db_devices[i + 1].pk)

        db_devices[i].connected_with.extend(neighbours)

        db_devices[i].connected_with = list(set(db_devices[i].connected_with))

        await db_devices[i].save()


def deploy_agent(agent: Agent):
    config = None

    if agent.username != 'root':
        config = FabricConfig(overrides={'sudo': {'password': agent.password}})

    connection = Connection(
        host=agent.address,
        port=22,
        user=agent.username,
        config=config,
    )

    connection.connect_kwargs.password = agent.password

    with TemporaryAgentConfig(agent) as config_file:
        connection.put(config_file, 'echo_agent/config.json')

    connection.put('deploy.sh', '.')
    connection.sudo('/bin/sh deploy.sh')

    connection.close()


async def deploy(agent: Agent):
    traced_devices = [scan_address(ip) for ip in traceroute(agent.address)]
    await create_non_existent_devices(traced_devices, agent)
    deploy_agent(agent)


def destroy(agent: Agent):
    config = None

    if agent.username != 'root':
        config = FabricConfig(overrides={'sudo': {'password': agent.password}})

    connection = Connection(
        host=agent.address,
        port=22,
        user=agent.username,
        config=config,
    )

    connection.connect_kwargs.password = agent.password

    connection.put('destroy.sh', '.')
    connection.sudo('/bin/sh destroy.sh')

    connection.close()

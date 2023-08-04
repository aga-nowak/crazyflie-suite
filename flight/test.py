import natnetclient as natnet
client = natnet.NatClient
flapper = client.rigid_bodies['flapper']
print(flapper.position)
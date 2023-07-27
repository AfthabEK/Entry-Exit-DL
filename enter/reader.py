#!/usr/bin/python3
import socket


def readData():
	readerIP='192.168.230.16'
	readerPort=100
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
		s.connect((readerIP, readerPort))
	except:
		raise Exception('NetworkError: Socket creation failed.')

	#print("Sending Read request.")
	cmd = bytearray([10, 255, 2, 128, 117])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	cnt = out[5]
	#print("Response: " + " ".join("%02x" % b for b in out))

	#print("Sending get tag data request.")
	cmd = bytearray([10, 255, 3, 65, 16, 163])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	#print("Response: " + " ".join("%02x" % b for b in out))
	if out[4] > 1:
		raise Exception("WARNING: More than one tags in range!!!")
	elif out[4] == 0:
		raise Exception("WARNING: No tags in range!!!")
	out = out[7:7+12][::-1]
	if out[1] == 0x9e:
		raise Exception("WARNING: Attempted to read empty tag.")
	out = out.decode()
	out = ''.join([c if ord(c) != 0 else '' for c in out])

	#print(out)
	return out

print(readData())
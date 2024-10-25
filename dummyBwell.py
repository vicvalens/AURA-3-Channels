from pylsl import StreamInfo, StreamOutlet
from getpass import getpass
import keyboard

# Create a new StreamInfo
info = StreamInfo('NeuroVR', 'triggers', 1, 0, 'string', 'myuidw43536')

# Create a new outlet
outlet = StreamOutlet(info)


def leer_teclado(event):
	tecla = event.name
	#outlet.push_sample([tecla])
	#print("Tecla presionada: " + tecla)
	#if tecla in [string(i) for i in range(1, 10)]:
	#	tecla="Trial_"+tecla
	mytrigger=0.0
	if tecla=="s":
		mytrigger=1.0


	#outlet.push_sample([mytrigger])
	#outlet.push_sample(mytrigger)

def main():
	print("NeuroVR stream Started")	
	keyboard.on_press(leer_teclado)

	while True:
		keyboard.wait('esc')
		break

main()
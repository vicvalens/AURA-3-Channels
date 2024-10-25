import pylsl
import csv
import os
from datetime import datetime


stream_markers = None
inlet_markers = None
markers = None   

def is_colon_trigger(string):
    # Check if ':' is in the string
    return ':' in string
def initialize_bWell_stream():
    global inlet_markers
    global stream_markers

    print("Connecting to NeuroVR stream")
    stream_markers = pylsl.resolve_stream('name', 'NeuroVR')
    
    if len(stream_markers) == 0:
        print("No se encontró el stream 'NeuroVR'. Asegúrate de que esté siendo enviado por otro programa.")
        return
    inlet_markers=pylsl.StreamInlet(stream_markers[0])
    print("Connected!")

def esperar_stream():
    global markers   

    
    # Resolver el stream "AURA_Power"
    canales = pylsl.resolve_stream('name', 'AURAKalmanFilteredEEG')
    canales_EEG= pylsl.resolve_stream('name', 'AURAPSD')

    print("Resolviendo Streams")
#    canales = pylsl.resolve_stream('name', 'AURA')
    canales_triggers = pylsl.resolve_stream('name', 'neuro_vr_triggers')


    if len(canales) == 0:
        print("No se encontró el stream 'AURA_Power'. Asegúrate de que esté siendo enviado por otro programa.")
        return

    if len(canales_EEG) == 0:
        print("No se encontró el stream 'AURA_Filtered'. Asegúrate de que esté siendo enviado por otro programa.")
        return

    if len(canales_triggers) == 0:
        print("No se encontró el stream 'neuro_vr_triggers'. Asegúrate de que esté siendo enviado por otro programa.")
        return


    # Crear un objeto de entrada para el stream "AURA_Power"
    entrada = pylsl.StreamInlet(canales[0])
    entrada_EEG= pylsl.StreamInlet(canales_EEG[0])
    entrada_triggers = pylsl.StreamInlet(canales_triggers[0])
 
    print("Esperando datos desde el stream 'AURA_Power', Triggers...")

    grabando = False
    archivo_csv = None
    writer = None
    participant_id=""
    folder_path="participants"
    session_name=""
    archivo_csv=None
    
    archivo_eeg_csv=None
    writer_eeg=None


    while True:
        sample, timestamp = entrada.pull_sample()
        sample_EEG, timestamp_EEG = entrada_EEG.pull_sample()        
        triggers, _ = entrada_triggers.pull_sample(0)

        if inlet_markers!=None:
            markers, _ = inlet_markers.pull_sample(0)
            if markers==None:
                marker_label="0"
            else: 
                marker_label=markers

        if triggers==None:
            trigger_label="0"
           
        elif is_colon_trigger(str(triggers[0])):
            trigger_entry = str(triggers[0]).split(":")
            if trigger_entry[0]=="participant_id":
                participant_id=trigger_entry[1]
                print("Id: "+participant_id)
                folder_path=os.path.join(folder_path, participant_id)
                if not os.path.isdir(folder_path):
                    os.makedirs(folder_path)
                    print("Directory: "+participant_id+" created")
                else:
                    print("Directory: "+participant_id+" found")
                initialize_bWell_stream()
            elif trigger_entry[0]=="start_session":
                print("Start Session: "+trigger_entry[1])
                session_name=trigger_entry[1] 
                if not grabando:
                    trigger_label="start_session_"+session_name
                    grabando=True
                    now = datetime.now()
                    now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
                    my_filename=session_name+"_"+now_str
                    csv_path = os.path.join(folder_path, f'{my_filename}.csv')
                    archivo_csv = open(csv_path, "w", newline="")
                    writer = csv.writer(archivo_csv)
                    print("Recording started...")
                    my_filename_eeg=session_name+"_eeg_"+now_str
                    csv_path_eeg = os.path.join(folder_path, f'{my_filename_eeg}.csv')
                    archivo_eeg_csv = open(csv_path_eeg, "w", newline="")
                    writer_eeg = csv.writer(archivo_eeg_csv)                                

            elif trigger_entry[0]=="end_session":
                print("End Session: "+trigger_entry[1])
                if grabando: 
                    trigger_label="end_session_"+session_name
                    writer.writerow([timestamp] + sample+[trigger_label])
                    writer_eeg.writerow([timestamp] + sample_EEG+[trigger_label])
                    grabando=False
                    archivo_csv.close()
                    archivo_eeg_csv.close()
                    print(trigger_label)
                    print("Recording finished...") 
                    folder_path="participants"
                    folder_path=os.path.join(folder_path, participant_id)

        elif str(triggers[0])=="exit":
            print("Finished")
            break

        else:
            trigger_label=triggers
            print(str(triggers[0]))



        if grabando:
#            writer.writerow([timestamp] + sample+[trigger_label])
            writer.writerow([timestamp] + sample+[trigger_label]+[marker_label[0]])
            writer_eeg.writerow([timestamp] + sample_EEG+[trigger_label]+[marker_label[0]])

esperar_stream()

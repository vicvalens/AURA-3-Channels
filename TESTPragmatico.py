import time
from pylsl import StreamInfo, StreamOutlet
from getpass import getpass
import keyboard
import random
import pylsl
import numpy as np
import pandas as pd
import joblib

info = StreamInfo('neuro_vr_triggers', 'triggers', 1, 0, 'string', 'myuidw43536')
outlet = StreamOutlet(info)
reading_keyboard=False
backspace_num=0
directory = 'participants/'
participation_id=""
script_path = 'BMI_Control_Sender.py'
model = joblib.load('zensync_random_forest.pkl') 
#canales = pylsl.resolve_stream('name', 'AURA_Power_Power')
canales = pylsl.resolve_stream('name', 'AURAPSD')

print("Resolviendo Streams")

if not canales:
    print("No se encontró el stream 'AURA_Power'. Asegúrate de que esté siendo enviado por otro programa.")
else:
    entrada = pylsl.StreamInlet(canales[-1])
    #columnas_a_eliminar = list(range(8, 16)) + list(range(24, 39))

def calcular_features(sample_array, columnas_a_eliminar):
    sample_array = np.delete(sample_array, columnas_a_eliminar)
    std = np.std(sample_array)
    mean = np.mean(sample_array)
    asymmetry = pd.Series(sample_array).skew()
    return mean, std, asymmetry

def realizar_prediccion(features):
    feature_names = ['Mean', 'STD', 'Asymmetry']
    features_df = pd.DataFrame([features], columns=feature_names)
    prediction = model.predict(features_df)
    return prediction

def calcular_cognitive_engagement(df_real_time):
    #alphas = df_real_time.iloc[:, 17:20].mean(axis=1)
    #thetas = df_real_time.iloc[:, 9:12].mean(axis=1)
    alphas = df_real_time.iloc[:, 6:8].mean(axis=1)
    thetas = df_real_time.iloc[:, 3:5].mean(axis=1)
    df_real_time['CEng'] = thetas/alphas
    return df_real_time

# def calcular_cognitive_engagement2(df_real_time):
#     num_pares = 3
#     theta_alpha_ratios = []
#     for i in range(num_pares):
#         alpha = df_real_time.iloc[:, 17 + i]
#         theta = df_real_time.iloc[:, 9 + i]
#         ratio = theta / alpha
#         theta_alpha_ratios.append(ratio)
#     df_real_time['CEng'] = pd.concat(theta_alpha_ratios, axis=1).mean(axis=1)
#     return df_real_time

def read_keyboard(event):
    global backspace_num
    if reading_keyboard==True:
        tecla = event.name
        if tecla in [str(i) for i in range(1, 10)]:
            tecla="trigger_"+tecla        
        outlet.push_sample([tecla])
        print("Trigger sent: "+tecla)
        backspace_num=backspace_num+1

def delete_typed_keys():
    global backspace_num
    for _ in range(backspace_num):
        keyboard.press_and_release('backspace')
    backspace_num=0

def display_menu():
    print("***************** Cognitive Training Menu *****************")
    print("Select excercise")
    print("6. ZenSync: Relaxation Pod")
    print("7. Vending Machine: Cognitive Flexibility")
    print("8. Exit")
    print("****************************************")
    option = int(input("Option: "))
    return option

def zensync_video_carrousel_relaxation():
    #seconds = 10
    max_avg_engagement_value = -1
    max_avg_engagement_index = -1
    avg_engagements = []  # Lista para almacenar los promedios de cada video

    for i in range(7):
        if i == 0:
            video_duration = 38  # Duración de 40 segundos para el primer video
        elif i == 6:
            video_duration = 8  # Duración de 10 segundos para el último video
        else:
            video_duration = 25  # Duración de 30 segundos para los demás videos


        outlet.push_sample([f"Start_video_{i+1}"])
        print(f"sending: Start_video_{i+1}")
        time.sleep(1)
        outlet.push_sample(["fadein"])
        print("sending: fadein")
        start_time = time.time()
        df_real_time = pd.DataFrame() 
        engagement_values = []
        
        while time.time() - start_time < video_duration:
            sample, timestamp = entrada.pull_sample()
            df_real_time = pd.concat([df_real_time, pd.DataFrame([sample])], ignore_index=True)
            
            if time.time() - start_time >= 2:  # Calcular después de 2 segundos
                df_engagement = calcular_cognitive_engagement(df_real_time)
                current_engagement = df_engagement['CEng'].iloc[-1] 
                engagement_values.append(current_engagement)
                print("Current Relaxation: ", current_engagement)
        
        avg_engagement = sum(engagement_values) / len(engagement_values) if engagement_values else 0
        
        print(f"Average Relaxation for video {i+1}: ", avg_engagement)
        
        # Añadir al listado de promedios y actualizar el máximo solo si no es el primer ni el último video
        if i != 0 and i != 6:  # Excluir el primer y último video
            avg_engagements.append(avg_engagement)
            if avg_engagement > max_avg_engagement_value:
                max_avg_engagement_value = avg_engagement
                max_avg_engagement_index = i

        outlet.push_sample(["fadeout"])
        print("sending: fadeout")
        time.sleep(2)

    video_to_play = f"Start_video_{max_avg_engagement_index + 1}"
    print(f"sending: {video_to_play}")
    outlet.push_sample([video_to_play])
    outlet.push_sample(["fadein"])
    print("sending: fadein")
    outlet.push_sample(["end_session:zensync"])
    time.sleep(20)
    outlet.push_sample(["fadeout"])


    print("sending: end_trial")

    # Imprimir los promedios individuales de relajación para cada video
    for i, avg_engagement in enumerate(avg_engagements):
        print(f"Average Relaxation for video {i+1}: {avg_engagement:.2f}")

def zensync_relaxation():
    global directory
    print("**** Calibration Stage ****")
    trials = int(input("How many trials? "))
    print("Press Enter to start zensync Calibration session...")
    input()  
    outlet.push_sample(["start_session:zensync"])  
    print("sending: start_session:zensync")    
    for i in range(trials):
        outlet.push_sample(["fadeout"])
        print("sending: fadeout")
        time.sleep(2)
        print("----> Trial: " + str(i + 1))
        zensync_video_carrousel_relaxation()
    outlet.push_sample(["end_session:zensync"])  
    print("sending: end_session:zensync")
    print("End zensync Calibration routine")

def vending_machine_flexible():
    global directory
    print("Press Enter to start Vending Machine session...")
    input()
    outlet.push_sample(["start_session:vending_machine"])
    print("sending: start_session:vending_machine")    
    CEV = 0
    CEPoints = 0
    successes = 0
    failures = 0
    Threshold = 30
    while True:
        CEV = random.randint(0, 50)
        print(f"CEV actual: {CEV}")
        if CEV > Threshold:
            CEPoints += 1
            print(f"CEPoints incrementado a {CEPoints}")
    print("sending: end_session:vending_machine")
    print("End vending_machine routine")

def confirm_experiment():
    ans = input("Do you want start_experiment? (y/n): ")
    if ans.lower() == 'y':
        return ans.lower()
    elif ans.lower() == 'n':
        print("Terminating program...")
        return ans.lower()
    else:
        print("Invalid input, please enter 'y' for yes or 'n' for no.")

def get_send_participant_code():
    global participation_id
    while True:
        code = input("Type participant ID: ")
        participation_id=code
        code_trigger="participant_id:"+str(code)        
        print("ID entered:"+code_trigger)
        ans = input("is the ID correct? (y/n): ")
        if ans.lower() == 'y':
            outlet.push_sample([code_trigger])
            print(code_trigger+" sent")
            break
        elif ans.lower() == 'n':
            continue
        else:
            print("Invalid input, please enter 'y' for yes or 'n' for no.")

def break_rest():
    mins = 2
    print("********************Start Break ********************")    
    for i in range(mins):
        print("Break ----> Min "+str(i+1))
        time.sleep(60)
    print("********************End Break ********************")    

print("...Main Experiment LSL Server Started...")

get_send_participant_code()

while True:
    option=display_menu()
    if option == 6:
        print("You selected: Egg: Attention")
        confirmation=confirm_experiment()
        if confirmation=='y':
            zensync_relaxation()
            #break_rest()
        else:
            print("Going back to menu...")   
    elif option == 7:
        print("You selected: Vending Machine: Cognitive Flexibility")
        confirmation=confirm_experiment()
        if confirmation=='y':
            vending_machine_flexible()
            #break_rest()
    elif option == 8:
        print("Terminating program")
        outlet.push_sample(["exit"])
        time.sleep(2)
        break
    else:
        print("Invalid option. Please select a number between 1 and 8.")

import speech_recognition as sr #recognitize speech
import webbrowser #opens webbrowser as per voice command
import pyttsx3 as ttsx #for text to speech

recognizer=sr.Recognizer() #object to  recognize the speech as we use sr.method
tts=ttsx.init() #initialize pyttsx3   


def speak(txt):
    tts.say(txt)
    tts.runAndWait()


def processcommand(c):
    pass

if __name__=="__main__":
    speak("Initializing jarvis")

    while True:
        #wait for the wake word "Jarvis"
        # obtain audio from the microphone
        r = sr.Recognizer()

        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("Say something!")
                audio = r.listen(source,timeout=2,phrase_time_limit=1) 
            word= r.recognize_google(audio)
            print(f"heard:{word}")

            if(word.lower()=="jarvis"):
                speak("Ya")

                #listen for command
                with sr.Microphone() as source:
                    print("Jarvis activate")
                    audio = r.listen(source)
                    command=r.recognize_google(audio)
                    processcommand()
 
        except Exception as e:
            print("Error; {0}".format(e))
import os
import re
import music21
import sys
import random
import codecs
import os
from textblob import TextBlob
from collections import deque

script_dir = os.path.dirname(__file__)
text = codecs.open(os.path.join(script_dir,"static/test.txt"), encoding='utf-8', errors='ignore')
text_string = text.read()
text_arr = text_string.split()

#Removing punctuation
text_sentences = re.split('[?.!]', text_string)
num_sentences = len(text_sentences)


#How big the buffer size is
array_size = 10
running_array = [0]*array_size

sentiment_average = 0

def calculateAverageSentiment():
    sum = 0
    for num in running_array:
        sum+=num
    return sum/array_size


#Generates a list of rhythms based off of an array of text
#Uses the ASCII code of the last letter of the given word. (Shifts array over using rotate number )
def generateRhythm(rotate,rhythm_list):
    new_r = []
    for string in text_arr:
        new_r.append(float(rhythm_list[(ord(string[-1])+rotate)%len(rhythm_list)]))

    return new_r

time_sig_string = ""

def getPart(root,major_vec,minor_vec,char_of_string,other_rhythm):
    s = music21.stream.Part()
    current_sentiment_spot = 0


    denom = 0
    #Change denominator of time sig if number of words in corpus is even or odd
    if len(text_arr)%2 == 0:
    #even
        denom = 4
    else:
    #odd
        denom = 8

    #Numerator is 2, 3 or 4
    numerator = (num_sentences%3+1)*2

    if time_sig_string != "":
        time_sig_split = time_sig_string.split("/")
        numerator = time_sig_split[0]
        denom = time_sig_split[1]


    #Setting up xml
    meter = music21.meter.TimeSignature(str(numerator)+"/"+str(denom))
    calc_tempo = len(text_arr)%80+60
    tempo = music21.tempo.MetronomeMark(number=calc_tempo)
    s.append(tempo)
    s.append(meter)

    #root = 48
    #Default to major vector
    current_interval_vector = major_vec

    prev = root+current_interval_vector[random.randint(0, len(current_interval_vector)-1)]

    sd = 7

    prev = root

    range = 19



    index = 0
    for string in text_arr:

        word_stat = TextBlob(string)
        word_sent = TextBlob(string).sentiment.polarity
        running_array[current_sentiment_spot] = word_sent
        current_sentiment_spot = (current_sentiment_spot+1)%array_size
        average_sent = calculateAverageSentiment()

        lyric_to_add = string

        if word_sent > 0:
            lyric_to_add = "("+lyric_to_add+")"
        elif word_sent < 0:
            lyric_to_add = "<"+lyric_to_add+">"
        else:
            lyric_to_add = "["+lyric_to_add+"]"

        prev_vec = current_interval_vector

        if current_interval_vector == major_vec and word_sent < 0:
            current_interval_vector = minor_vec
        elif current_interval_vector == minor_vec and word_sent > 0:
            current_interval_vector = major_vec

        #if average_sent >= 0:
        #    current_interval_vector = major_vec
        #else:
        #    current_interval_vector = minor_vec

        if prev_vec != current_interval_vector:
            lyric_to_add = " |||| " + lyric_to_add



        #second line reverses rhythm line
        #start on second thing of strings
        note = (ord(string[char_of_string%len(string)]))%len(current_interval_vector)-1
        #rhythm = rhythms[(ord(string[-1]))%len(rhythms)]
        sd = current_interval_vector[note]

        if abs((root+sd)-prev) < abs((root-12+sd)-prev):
            prev = root+sd
        else:
            prev = root-12+sd

        append_note = music21.note.Note(prev)
        append_note.quarterLength = other_rhythm[index]



        append_note.lyric = lyric_to_add
        append_note.color = "#ff0000"
        s.append(append_note)

        index+=1

    return s

time_numerator = 2

#babby_stream = music21.stream.Part()
#f = music21.note.Note("F5")
#babby_stream.append(f)

def generateXML(major, minor, rhythm_list):
    first_rhythm = generateRhythm(0,rhythm_list)
    reversed_rhythm = list(reversed(first_rhythm))
    third_rhythm = deque(first_rhythm)
    third_rhythm.rotate(num_sentences)
    #(first_rhythm)
    #third_rhythm = generateRhythm(1,rhythm_list)

    root=48
    selected_major = major
    selected_minor = minor
    first_part = getPart(root,selected_major,selected_minor,0,first_rhythm)
    second_part = getPart(root+12, selected_major,selected_minor,1,reversed_rhythm)
    third_part = getPart(root+24, selected_major, selected_minor, 2, third_rhythm)

    #b = getPart(48,0)
    #c = getPart(48,1)

    #first_part.write('xml',os.path.join(script_dir,"part1.xml"))
    #first_part.write('midi',os.path.join(script_dir,"part1.midi"))
    #second_part.write('xml',os.path.join(script_dir,"part2.xml"))
    #second_part.write('midi',os.path.join(script_dir,"part2.midi"))
    #third_part.write('xml',os.path.join(script_dir,"part3.xml"))
    #third_part.write('midi',os.path.join(script_dir,"part3.midi"))

    #d = getPart(48,2)
    #d=getPart(48+7)
    #print(prev)
    master_stream = music21.stream.Stream([first_part,second_part,third_part])
    #master_stream.write('xml',os.path.join(script_dir,"all.xml") )
    master_stream.write('midi',os.path.join(script_dir,"static/test.midi"))

def printScaleChoices():
    for i in range(0,len(scales)):
        print(str(i)+")"+" "+scale_names[i]+": "+str(scales[i]))
    print("11) Custom")

def enterCustom():
    print("Enter a comma seperated list, for example:")
    print("1,2,3,4,5,6,7")
    in_str = input("Values: ")
    arr = [x.strip() for x in in_str.split(',')]
    new_arr = []
    for i in arr:
        new_arr.append(float(i))

    return new_arr

#result = input("in").split(",")
#print(result)
##print("====================")
##print("Welcome to the Music Generation Thingy!")
##print("This program will generate music based off of the general sentiment of the text")
##
##print("First, type in a time signature for the piece. (4/4, 6/8, 12/8, etc.)")
##print("Leave blank to automatically generate one!")
##
##while True:
##    time_sig_string = input("Time Sig: ")
##
##    if time_sig_string == "":
##        break
##
##    time_sig_split = time_sig_string.split("/")
##    denom = int(time_sig_split[1])
##    if denom == 2 or denom == 4 or denom == 8 or denom == 16:
##        break
##    else:
##        print("Denominator must be 2, 4, 8, or 16!")
##
##
##
##print("First, choose a scale for when the text's sentiment is positive. (Just type the number)")
##printScaleChoices()
##choice = int(input("Choice: "))
##
##positive_scale =[]
##
##if choice == 11:
##    positive_scale = enterCustom()
##else:
##    positive_scale = scales[choice]
##
##print("Now choose a scale for when the text's sentiment is negative.")
##printScaleChoices()
##choice = int(input("Choice: "))
##
##negative_scale = []
##if choice == 11:
##    negative_scale = enterCustom()
##else:
##    negative_scale = scales[choice]
##
##print("Finally, chose a library of possible rhythms to pick from.")
##print("This is based off of quarter note values, so 1 = Quarter Note, 0.5 = Eight Note, 2 = Half Note, etc)")
##print("So for example, if you want whole notes, half notes, and eight notes it would be: 4,2,0.5")
##
##custom_rhythm = enterCustom()
##
##print("Generating, please wait...")
##generateXML(positive_scale,negative_scale,custom_rhythm)
##print("Done!")
##

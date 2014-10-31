# -*- coding: utf-8 -*-
import math

import numpy as np
import scipy
from scipy.spatial.distance import euclidean

from flask import Flask, render_template, request

from dj_tiny_data import paths, lyrics_to_bow

app = Flask(__name__)

SAMPLE = u"""
Richi Peña
Chino y Nacho
Esta cancion nació de un pensamiento
Es Así
Y yo solo pienso en ti
Mi niña bonita
Mi amor
Oyee
Tu reconoces un hig cuando lo oyes

Lo que siento por ti
Es ternura y pasión
Tú me has hecho sentir
Que hay en mi corazón
Tanto amoooor
Tanto amoor

Yo nací para ti
Y tú también para mí
Y ahora sé que morir es tratar de vivir
Sin tu amoor
Sin tu amoor

Mi niña bonita mi dulce princesa
Me siento en las nubes cuando tú me besas
Y siento que vuelo más alto que el cielo
Si tengo de cerca el olor de tú pelo

Mi niña bonita brillante lucero
Te queda pequeña la frase Te Quiero
Por eso mis labios te dicen te amo
Cuando estamos juntos más nos enamoramos

Aquí hay amoor
Aquí hay amoor
Aquí hay amoor amor
Aquí hay amoor amor
Aquí hay hay hay hay hay hay amor

Este amor que como espuma sube
Que cuando te tomo de la mano por el parque
Camino en las nubes
Parece mentira que ya no recuerdo nada
Cuando solo estuve
Nada se podrá comparar
Con algo tan especial

Nada se compara con lo nuestro mi vida

Le agradezco al tiempo
Que me ha demostrado que las cosas buenas llegan
En cualquier momento
Yo no imaginaba que conocería
Algún día este sentimiento
Un amor puro y natural
Digno de admirar
(Digno de admirar princesa)

Un amor de fantasía, lleno de romance y alegría
De bello detalle cada día
Nena quién lo diría
Que algún día yo me enamoraría
Y que sin tu amor no viviría
Como sabia que esto pasaría
Que ibas a ser mía
Y que yo querría
Amarte por siempre mi niña bonita

Mi niña bonita mi dulce princesa
Me siento en las nubes cuando tú me besas
Y siento que vuelo más alto que el cielo
Si tengo de cerca el olor de tú pelo

Mi niña bonita brillante lucero
Te queda pequeña la frase Te Quiero
Por eso mis labios te dicen te amo
Cuando estamos juntos más nos enamoramos
Aquí hay amoor
(Mi niña bonita)
Aquí hay amoor
(Mi niña bonita)
Aquí hay amoor amor
Aquí hay amoor amor
Aquí hay hay hay hay hay hay amor

Desde este momento no podrás sacarte esta canción de tú cabeza

Chino Y Nacho
Mi Niña Bonita
Tú y únicamente tú
Mi Niñaa Boniiitaa!
Más nah
"""

SAMPLE_2 = u"""
You say one for the trebble, two for the time
Come on y'all let's rock this!
You say one for the trebble, two for the time
Come on!

Speech is my hammer, bang the world into shape
Now let it fall... (Hungh!!)
My restlessness is my nemesis
It's hard to really chill and sit still
Committed to page, I write rhymes
Sometimes won't finish for days
Scrutinize my literature, from the large to the miniature
I mathematically add-minister
Subtract the wack
Selector, wheel it back, I'm feeling that
(Ha ha ha) From the core to the perimeter black,
You know the motto
Stay fluid even in staccato
(Mos Def) Full blooded, full throttle
Breathe deep inside the trunk hollow
There's the hum, young man where you from
Brooklyn number one
Native son, speaking in the native tongue
I got my eyes on tomorrow (there it is)
While you still try to follow where it is
I'm on the Ave where it lives and dies
Violently, silently
Shine so vibrantly that eyes squint to catch a glimpse
Embrace the bass with my dark ink fingertips
Used to speak the king's English
But caught a rash on my lips
So now my chat just like dis
Long range from the base-line (switch)
Move like an apparition
Float to the ground with ammuntion (chi-chi-chi-POW)
Move from the gate, voice cued on your tape
Putting food on your plate
Many crews can relate
Who choosing your fate (yo)
We went from picking cotton
To chain gang line chopping
To Be-Bopping
To Hip-Hopping
Blues people got the blue chip stock option
Invisible man, got the whole world watching
(where ya at) I'm high, low, east, west,
All over your map
I'm getting big props, with this thing called hip hop
Where you can either get paid or get shot
When your product in stock
The fair-weather friends flock
When your chart position drop
Then the phone calls....
Chill for a minute
Let's see whoelse tops
Snatch your shelf spot
Don't gas yourself ock
The industry just a better built cell block
A long way from the shell tops
And the bells that L rocked (rock, rock, rock, rock...)

[scratching]

Hip Hop is prosecution evidence
The out of court settlement
Ad space for liquor
Sick without benefits (hungh!)
Luxury tenements choking the skyline
It's low life getting tree-top high
Here there's a back water remedy
Bitter intent to memory
A class E felony
Facing the death penalty (hungh!)
Stimulant and sedative, original repetitive
Violently competitive, a school unacredited
The break beats you get broken with
on time and inappropriate
Hip Hop went from selling crack to smoking it
Medicine for loneliness
Remind me of Thelonius and Dizzy
Propers to B-Boys getting busy
The war-time snap shot
The working man's jack-pot
A two dollar snack box
Sold beneath the crack spot
Olympic spnosor of the black glock
Gold medalist in the back shot
From the sovereign state of the have-nots
Where farmers have trouble with cash crops (woooo)
It's all city like phase two
Hip Hop will simply amaze you
Craze you, pay you
Do whatever you say do
But black, it can't save you
"""


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/genre', methods=['POST'])
def genre():
    with open(paths.CLUSTER_GENRES, 'r') as fgenres,\
            open(paths.K_MEANS_CLUSTERS, 'r') as fcenters,\
            open(paths.WORD_LIST_PATH, 'r') as fwords:
        data = request.get_json()
        print data
        lyrics = data['lyrics']
        #lyrics = SAMPLE_2
        bow = lyrics_to_bow.lyrics_to_bow(lyrics)
        if bow is None:
            raise Exception
        word_list = fwords.read().split('\n')[:-1]
        occurence_array = np.zeros(len(word_list))
        for idx, word_df in enumerate(word_list):
            word = word_df.split(',')[0]
            df = float(word_df.split(',')[1])
            tf = 0.0
            idf = 1
            if word in bow:
                tf = math.sqrt(float(bow[word]))
                idf = 1 + math.log(1425.0 / (df + 2))
            occurence_array[idx] = tf*idf
        occurence_array /= scipy.linalg.norm(occurence_array)
        centers = np.loadtxt(fcenters, delimiter=',')
        min_distance = -1
        index = None
        for idx, center in enumerate(centers):
            distance = euclidean(center, occurence_array)
            if index is None or distance < min_distance:
                min_distance = distance
                index = idx
        genres = fgenres.read().split('\n')
        return genres[index]

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')

import base64
import io
import matplotlib.pyplot as plt
import random
from flask import Flask, Response, request, render_template
import math
from matplotlib import pyplot as plt
import pandas as pd

class Autko:
    def __init__(self,v_0,v_zad,alfa):
        #parametry związane z samochodem
        self.v_0 = float(v_0)/3.6                   #prędkość początkowa km/h
        self.v_zad = float(v_zad)/3.6              #prądkość zadana w km/h
        self.m = 600.0                         #masa autka w kg skoda 1147kg opel astra 1300kg
        self.F_max = 30_000.0                    #max moc silnika w N

        #parametry do siły oporu
        self.A = 2.87                         #powierzchnia czołowa pojazdu 2.54 [m^2] opel astra 2,850886[m^2] skoda fabia 4
        self.C = 0.28                           #stała do oporu opel 0.26 skoda 0.28
        self.p = 1.1255                          #gęstość powietrza
        self.g = 9.81                           #przyspieszenie ziemskie
        self.alfa = alfa                       #kąt nachylenia podłoża
        self.op = 0.03                          #opór opon o asfalt

        #stałe do symulacji
        self.T_p = 0.1                          #czas próbkowania
        self.t_sim = 500                        #czas symulacji [s]
        self.k_p = 0.0008                    #wzmocnienie regulatora
        self.N = int(self.t_sim / self.T_p) + 1 #ilość iteracji
        self.T_d = 0.006                    #czas wyprzedzania
        self.T_i = 1.9                    #czas zdwojenia [s]
        self.u_max = 30.0                        #max zmienna sterująca
        self.u_min = -30.0                       #min zmienna sterująca
        # wzrost kp ozacza zmniejszenie uchybu regulacji w stanbie ustalonym
        #wzrost przeregulowania
        #wzrost Ti oznacza likwidacje uchybu regulacji w stanie ustalonym
        # zwiększenie czasu regulacji
        #wzrost Td skrucenie czasu regulacji
        #listy
        self.poz_pedal = float(1/self.u_max)
        self.u = [0.0, ]
        self.e = [0.0, ]
        self.v = [self.v_0, ]
        self.t = [0.0, ]
        self.droga = [0, ]
        self.x = [0.0, ]                        #lista do pedału gazu
        self.u_zogr = [0.0, ]
        self.F_ciagu = [0.0, ]
        self.F_opor_powietrza = [0.0, ]
        self.F_opor = [0.0, ]
        self.F_toczenia = [0.0, ]
a = Autko(50.0,110.0,-2.0)
#symulacja
def sim(a):
    for i in range(a.N):
        a.t.append(i * a.T_p)
        e = a.v_zad - a.v[-1]
        a.e.append(e)
        # algorytm pozycyjny
        u_v2 = a.k_p * (a.e[-1] + (a.T_p / a.T_i) * sum(a.e) + (a.T_d / a.T_p) * (a.e[-1] - a.e[-2]))
        a.u.append(u_v2)
        if u_v2 <= a.u_min:
            u_v2 = a.u_min
        elif u_v2 >= a.u_max:
            u_v2 = a.u_max
        a.u_zogr.append(u_v2)
        a.x.append(a.u_zogr[-1] * a.poz_pedal)


        F_oporow = a.op * a.m * a.g
        F_toczenia = a.m * a.g * math.sin((math.radians(a.alfa)))
        F_oporow_powietrza = 0.5 * a.p * a.v[-1] * a.v[-1] * a.A * a.C
        F_ciagu = a.F_max * a.x[-1]

        # branie pod uwage nachylenia podłaoza
        # w zalezności od tego cz np jedziemy do czy do przodu czy staczamy sie z góry
        # czy pod góre to siły oporu mogą nam defakto pomagać bardziej niz przeszkadzać
        # jak angle mniejsze niż 0 to jedziemy z górki albo cofamy sie pod górke
        wsp_T_op_pow = -1
        al = 1
        if a.alfa < 0:
            al= -1
            if a.v[-1] > 0:
                wsp_T_op_pow = -1
            else:
                wsp_T_op_pow = 1
        elif a.alfa > 0:
            al = -1
            if a.v[-1] > 0:
                wsp_T_op_pow = -1
            else:
                wsp_T_op_pow = 1
        else:
            if a.v[-1] > 0:
                wsp_T_op_pow = -1
            elif a.v[-1] < 0:
                wsp_T_op_pow = 1



        fop = F_oporow_powietrza * wsp_T_op_pow
        a.F_ciagu.append(F_ciagu)
        a.F_opor.append(F_oporow)
        a.F_opor_powietrza.append(fop)
        a.F_toczenia.append(F_toczenia*al)
        v = (a.T_p / a.m) * (F_ciagu - F_toczenia + fop) + a.v[-1]
        a.droga.append(v * a.T_p + a.droga[-1])
        a.v.append(v)

    v_km_h = [3.6*x for x in a.v]
        #wskażniki jakości jeszce
        #na prez zanalazłem wieck mogą sie przydac do czegoś
        #przeregulowanie
    v_zad = a.v_zad*3.6
    if v_zad > 0:
        print(max(v_km_h))
        print(v_zad)
        kappa = ((max(v_km_h) - v_zad) / v_zad) * 100 # to ma być w procenrach pokazane
    else:
        kappa = (abs(min(v_km_h)) - (abs(v_zad)) / abs(v_zad)) * 100 # to ma byc w procentach pokazane
    Ie = 0
        #całkowe wskażniki dokładności regulacji
    for i in range(len(a.e)):
        x = abs(a.e[i])
        Ie = Ie + x
    Ie = Ie*a.T_p
        #całkowe wskazniki kosztów regulacji
    Iu = 0
    for i in range(len(a.u)):
        x = abs(a.u[i])
        Iu = Iu + x
    Iu = Iu*a.T_p
        #czas regulacji
    nr = 0
    print(a.N)
    print(len(a.v))
    for i in range(a.N, 1, -1):
        if abs(v_km_h[i]) <= abs(v_zad*0.94) or abs(v_km_h[i]) >= abs(v_zad*1.06):
            nr = i
            break
    tr = nr*a.T_p

    return a.u_zogr, a.u, a.droga, v_km_h, a.F_toczenia, a.F_opor_powietrza, a.F_ciagu, a.x, a.t, kappa, Iu, Ie, tr



app = Flask(__name__)


@app.route('/')
def index():
    # domyślne wartości suwaków
    V0 = 50
    Vz = 60
    al = -1
    # pobierz wartości suwaków z żądania
    if request.args.get('V0'):
        V0 = int(request.args.get('V0'))
    if request.args.get('Vz'):
        Vz = int(request.args.get('Vz'))
    if request.args.get('al'):
        al = int(request.args.get('al'))
    # rysuj wykres za pomocą Matplotlib
    a = (sim(Autko(V0, Vz, al)))
    fig, ax_1 = plt.subplots()
    ax_1.plot(a[8], a[3])
    ax_1.set_title("Prędkość")
    ax_1.set_xlabel("t[s]")
    ax_1.set_ylabel("v[km/h]")
    ax_1.legend(title="Przeregulowanie: {}%\nCzas regulacji: {}s\nKoszt regulacji: {}\nDokładność regulacji: {}".format(round(a[9],2), round(a[12],2), round(a[10],2), round(a[11],2)))
    # zapisz wykres do bufora
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    # zamień bufor na obrazek base64
    buf1.seek(0)
    image_base64_1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    # wyświetl szablon z wykresem i suwakami
    fig, ax_2 = plt.subplots()
    ax_2.plot((sim(Autko(V0, Vz, al)))[8], (sim(Autko(V0, Vz, al)))[0])
    ax_2.set_title("Zmienna sterująca")
    ax_2.set_xlabel("t[s]")
    ax_2.set_ylabel("u")
    # zapisz wykres do bufora
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    # zamień bufor na obrazek base64
    buf2.seek(0)
    image_base64_2 = base64.b64encode(buf2.getvalue()).decode('utf-8')



    return render_template('index.html', V0=V0, Vz=Vz, al=al, image_base64_1=image_base64_1, image_base64_2=image_base64_2)


if __name__ == '__main__':
    app.run(debug=True)

import math
from matplotlib import pyplot as plt
import pandas as pd
class Autko:
    def __init__(self,v_0,v_zad,alfa):
        #parametry związane z samochodem
        self.v_0 = float(v_0)/3.6                   #prędkość początkowa km/h
        self.v_zad = float(v_zad)/3.6              #prądkość zadana w km/h
        self.m = 1147.0                         #masa autka w kg skoda 1147kg opel astra 1300kg
        self.F_max = 5_900.0                    #max moc silnika w N

        #parametry do siły oporu
        self.A = 2.850886                            #powierzchnia czołowa pojazdu 2.54 [m^2] opel astra 2,850886[m^2] skoda fabia 4
        self.C = 0.28                           #stała do oporu opel 0.26 skoda 0.28
        self.p = 1.1255                          #gęstość powietrza
        self.g = 9.81                           #przyspieszenie ziemskie
        self.alfa = alfa                       #kąt nachylenia podłoża
        self.op = 0.03                          #opór opon o asfalt

        #stałe do symulacji
        self.T_p = 0.1                          #czas próbkowania
        self.t_sim = 500                        #czas symulacji [s]
        self.k_p = 0.0025                      #wzmocnienie regulatora
        self.N = int(self.t_sim / self.T_p) + 1 #ilość iteracji
        self.T_d = 0.09                        #czas wyprzedzania
        self.T_i = 2.0                        #czas zdwojenia [s]
        self.u_max = 10.0                        #max zmienna sterująca
        self.u_min = -5.0                       #min zmienna sterująca
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
a = Autko(60.0,110.0,0.0)
#symulacja
def sim(a):
    for i in range(a.N):
        a.t.append(i * a.T_p)
        a.e.append(a.v_zad - a.v[-1])
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
        # na prezentacji były jakieś wskazniki jakości ale nie pamietam za bardzo żeby mówił
        # o nich na lekcji wiec idk w sm
        v_km_h = [3.6*x for x in a.v]
    return a.u_zogr, a.u, a.droga, v_km_h, a.F_toczenia, a.F_opor_powietrza, a.F_ciagu, a.x, a.t

u_ograniczone, u, droga, v, F_opor, F_opor_powietrza, F_ciagu, x, t = sim(a)
print(v)

def plots(u_ograniczone, u, droga, v, F_opor, F_opor_powietrza, F_ciagu, x, t ):
    x_axis = t
    y_axis_1 = u
    y_axis_2 = u_ograniczone
    y_axis_3 = v
    y_axis_4 = droga
    y_axis_5 = F_opor
    y_axis_6 = F_ciagu
    y_axis_7 = F_opor_powietrza
    y_axis_8 = x

    plt.style.use("seaborn")
    fig, axs = plt.subplots(2, 2)

    axs[0, 0].plot(x_axis, y_axis_3, label="Prędkość samochodu")
    axs[0, 0].legend()
    axs[0, 0].set_title("Zmiana prędkości samochdu w czasie")
    axs[0, 0].set_xlabel("Czas t[s]")
    axs[0, 0].set_ylabel("Prędkość v[km/h]")

    axs[0, 1].plot(x_axis, y_axis_2, label="Zmienna sterująca")
    axs[0, 1].legend()
    axs[0, 1].set_title("Wykres zmiany zmiennej sterującej w czasie")
    axs[0, 1].set_xlabel("Czas t[s]")
    axs[0, 1].set_ylabel("Zmienna sterująca u")

    axs[1, 0].plot(x_axis, y_axis_4, label="Droga przebyta przez samochó")
    axs[1, 0].legend()
    axs[1, 0].set_title("Wykres drogi przejechanej przez samochód")
    axs[1, 0].set_xlabel("Czas t[s]")
    axs[1, 0].set_ylabel("Droga s[m]")

    axs[1, 1].plot(x_axis[1:], y_axis_5[1:], label="Siła toczenia")
    axs[1, 1].plot(x_axis[1:], y_axis_6[1:], label="Siła ciągu silnika")
    axs[1, 1].plot(x_axis[1:], y_axis_7[1:], label="Siła oporu powietrza")
    axs[1, 1].legend()
    axs[1, 1].set_title("Wykres sił działających na samochód")
    axs[1, 1].set_xlabel("Czas t[s]")
    axs[1, 1].set_ylabel("Siła F[N]")
    return plt.show()

plots(u_ograniczone, u, droga, v, F_opor, F_opor_powietrza, F_ciagu, x, t )






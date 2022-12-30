import math
from matplotlib import pyplot as plt
import pandas as pd
class Autko:
    def __init__(self,v_0,v_zad):
        #parametry związane z samochodem
        self.v_0 = float(v_0)     #prędkość początkowa m/s
        self.v_zad = float(v_zad) #prądkość zadana w m/s
        self.m = 500.0           #masa autka w kg
        self.F_max = 2100.0     #max moc silnika w N

        #parametry do siły oporu
        self.A = 7.0              #stała do oporu
        self.C = 0.24             #stała do oporu
        self.p = 1.225            #gęstość powietrza
        self.g = 9.81             #przyspieszenie ziemskie
        self.alfa = -1.0          #kąt nachylenia podłoża
        self.op = 0.0032  # opór opon o asfalt

        #stałe do symulacji
        self.T_p = 0.1              #czas próbkowania
        self.t_sim = 200            #czas symulacji [s]
        self.kp = 0.0007            #wzmocnienie regulatora
        self.N = int(self.t_sim / self.T_p) + 1 #ilość iteracji
        self.T_d = 0.009            #czas wyprzedzania
        self.T_i = 0.4              #czas zdwojenia [s]
        self.u_max = 15             #max zmienna sterująca
        self.u_min = -15            #min zmienna sterująca



        #listy
        self.poz_pedal = float(1/self.u_max)
        self.u = [0.0, ]
        self.e = [0.0, ]
        self.v = [v_0, ]
        self.t = [0.0, ]
        self.droga = [0, ]
        self.x = [0.0, ] #lista do pedału gazu
        self.u_zogr = [0.0, ]
        self.F_ciagu = [0.0, ]
        self.F_opor_powietrza = [0.0, ]
        self.F_opor = [0.0, ]
a = Autko(40.0,50.0)
#symulacja
def sim(a):
    for i in range(a.N):
        a.t.append(i * a.T_p)
        a.e.append(a.v_zad - a.v[-1])
        # algorytm pozycyjny
        u_v2 = a.kp * (a.e[-1] + (a.T_p / a.T_i) * sum(a.e) + (a.T_d / a.T_p) * (a.e[-1] - a.e[-2]))
        a.u.append(u_v2)
        if a.u[-1] <= a.u_min:
            u_v2 = a.u_min
        elif a.u[-1] >= a.u_max:
            u_v2 = a.u_max
        a.u_zogr.append(u_v2)
        a.x.append(a.u_zogr[-1] * a.poz_pedal)

        angle = abs(math.radians(a.alfa))
        F_oporow = a.op * a.m * a.g * math.sin(angle)
        F_oporow_powietrza = 0.5 * a.p * a.v[-1] * a.v[-1] * a.A * a.C
        F_ciagu = a.F_max * a.x[-1]

        # branie pod uwage nachylenia podłaoza
        # w zalezności od tego cz np jedziemy do czy do przodu czy staczamy sie z góry
        # czy pod góre to siły oporu mogą nam defakto pomagać bardziej niz przeszkadzać
        wsp_T_op_pow = 1
        wsp_T_op = 1
        # jak angle mniejsze niż 0 to jedziemy z górki albo cofamy sie pod górke
        if angle < 0:
            if a.v[-1] > 0:
                wsp_T_op_pow = 1
                wsp_T_op = -1
            else:
                wsp_T_op_pow = -1
                wsp_T_op = -1
        else:
            if a.v[-1] > 0:
                wsp_T_op_pow = 1
                wsp_T_op = 1
            else:
                wsp_T_op_pow = -1
                wsp_T_op = 1

        fop = F_oporow_powietrza * wsp_T_op_pow
        fo = F_oporow * wsp_T_op
        a.F_ciagu.append(F_ciagu)
        a.F_opor.append(fo)
        a.F_opor_powietrza.append(fop)
        a.v.append((a.T_p / a.m) * (F_ciagu - (fo + fop)) + a.v[-1])
        # na prezentacji były jakieś wskazniki jakości ale nie pamietam za bardzo żeby mówił
        # o nich na lekcji wiec idk w sm
        a.droga.append(a.v[-1]*a.T_p + a.droga[-1])
    return a.u_zogr, a.u, a.droga, a.v, a.F_opor, a.F_opor_powietrza, a.F_ciagu, a.x, a.t

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
    axs[0, 0].set_ylabel("Prędkość v[m/s]")

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

    axs[1, 1].plot(x_axis, y_axis_5, label="Siła oporu podłoża")
    axs[1, 1].plot(x_axis, y_axis_6, label="Siła ciągu silnika")
    axs[1, 1].plot(x_axis, y_axis_7, label="Siła oporu powietrza")
    axs[1, 1].legend()
    axs[1, 1].set_title("Wykres sił działających na samochód")
    axs[1, 1].set_xlabel("Czas t[s]")
    axs[1, 1].set_ylabel("Siła F[N]")

    return plt.show()

plots(u_ograniczone, u, droga, v, F_opor, F_opor_powietrza, F_ciagu, x, t )





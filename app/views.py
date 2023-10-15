from app import app
from time import time
from flask import render_template, url_for , request, jsonify
import pandas as pd
import json
import plotly
import plotly.express as px
from datetime import datetime


def toStrArray(cells):

    cells_values = cells.split( '"},{"val":"')
    cells_values[0] = cells_values[0][9:len(cells_values[0])]
    cells_values[len(cells_values) - 1] = cells_values[len(cells_values) - 1][0:len(cells_values[len(cells_values) - 1]) - 3]

    return cells_values

def findBad(cells_values):
    bad_values = []
    i = 0

    #поиск ячеек с неудовлетворяющими значениями
    while i < len(cells_values):
        count = 0

        for j in range(len(cells_values[i])):
            if cells_values[i][j] >= '0' and cells_values[i][j] <= '9':
                count += 1
            else:
                break

        if count < len(cells_values[i]) or len(cells_values[i]) == 0:
            bad_values.append(str(i))
            
        i += 1

    return bad_values


def countTStart(n, start_values):
    sum_t = [0, 0, 0, 0, 0, 0, 0]
    sum_dt = [0, 0, 0, 0, 0, 0]
    T = 0

    dt_str = []
    dt = []

    '''for i in range(0, n, 7):
        dt.append([])
        for j in range(7):
            sum_t[j] += start_values[i // 7][j + 1]
            dt[i].append(max(sum_a - sum_x - sum_b, 0))
        xs.append(max(sum_a - sum_x - sum_b, 0))
        sum_x += xs[i // step]
        sum_b += start_values[i // step][2]
        if (three):
            ys.append(max(sum_x + sum_b - sum_y - sum_c, 0))
            sum_y += ys[i // step]
            sum_c += start_values[i // step][3]

    for i in range(len(xs)):
        mas_x.append(str(xs[i]))
        if (three):
            mas_y.append(str(ys[i]))

        
    if (three):
        T = sum_y + sum_c
    else:
        T = sum_x + sum_b

    return (T, mas_dt)'''


def countT(n, values, type):
    return (countTStart(n, type + 2, values))

def countTseq(values, seq):
    sum_a = 0
    sum_b = 0
    sum_c = 0
    sum_x = 0
    sum_y = 0

    mas_x = []
    mas_y = []

    xs = []
    ys = []
    for i in range(len(seq)):
        sum_a += values[seq[i]][1]
        xs.append(max(sum_a - sum_x - sum_b, 0))
        sum_x += xs[i]
        sum_b += values[seq[i]][2]
        ys.append(max(sum_x + sum_b - sum_y - sum_c, 0))
        sum_y += ys[i]
        sum_c += values[seq[i]][3]

    for i in range(len(xs)):
        mas_x.append(str(xs[i]))
        mas_y.append(str(ys[i]))

    T = sum_y + sum_c

    return (T, mas_x, mas_y)


def JohnsonAlgorithm(start_values):
    mas_a = []
    mas_b = []

    k = len(start_values)
    for i in range(k):
        m = start_values[0][1]
        row = 0
        ind = 0
        for j in range(len(start_values)):
            for t in range(2):
                if (start_values[j][t + 1] < m):
                    m = start_values[j][t + 1]
                    row = j
                    ind = t
        
        if (ind == 0):
            mas_a.append(start_values[row])
        else:
            mas_b.append(start_values[row])

        start_values.pop(row)

    mas_b.reverse()
    result_values = mas_a + mas_b

    return result_values

def TableMethod(values, t_str, T_str, dt_str, Tpr_str, Tozh_str):
    t = []
    T = []
    dt = []

    Tpr = []
    Tozh = []

    for i in range(7):
        t.append([])
        T.append([])
        dt.append([])
        for j in range(7):
            t[i].append(values[i][j + 1])

            T_up = 0
            T_left = 0

            for k in range(i - 1, -1, -1):
                if (T[k][j] != 0):
                    T_up = T[k][j]
                    break

            for k in range(j - 1, -1, -1):
                if (T[i][k] != 0):
                    T_left = T[i][k]
                    break

            if (t[i][j] == 0):
                T[i].append(0)
                dt[i].append(0)
            else:
                T[i].append(t[i][j] + max(T_up, T_left))
                dt[i].append(max(T_up, T_left) - T_up)

            t_str.append(str(t[i][j]))
            T_str.append(str(T[i][j]))
            dt_str.append(str(dt[i][j]))

    s1 = 0
    s2 = 0

    for i in range(7):

        T_up = 0
        T_left = 0

        for k in range(6, -1, -1):
            if (T[k][i] != 0):
                T_up = T[k][i]
                break

        for k in range(6, -1, -1):
            if (T[i][k] != 0):
                T_left = T[i][k]
                break

        Tpr.append(T_up)
        Tozh.append(T_left)
        for j in range(7):
            Tpr[i] -= t[j][i]
            Tozh[i] -= t[i][j]

        s1 += Tpr[i]
        s2 += Tozh[i]

        Tpr_str.append(str(Tpr[i]))
        Tozh_str.append(str(Tozh[i]))

    Tpr_str.append(str(s1))
    Tozh_str.append(str(s2))


def SortAsc(params, seq, param_number):

    seq = seq.copy()

    n = len(seq)

    for i in range(n - 1):
        for j in range(n - i - 1):
            if params[seq[j]][param_number] > params[seq[j + 1]][param_number]:
                seq[j], seq[j + 1] = seq[j + 1], seq[j]
    
    return seq

def SortDesc(params, seq, param_number):

    seq = seq.copy()

    n = len(seq)

    for i in range(n - 1):
        for j in range(n - i - 1):
            if params[seq[j]][param_number] < params[seq[j + 1]][param_number]:
                seq[j], seq[j + 1] = seq[j + 1], seq[j]
    
    return seq

def Rule1(params, D10, D2):

    #сортировка D10 в порядке возрастания P1
    seq = SortAsc(params, D10, 1)

    #сортировка D2 в порядке убывания P2
    seq += SortDesc(params, D2, 2)

    return seq


def Rule2(params):

    D = params.copy()

    n = len(D)

    #сортировка D в порядке убывания лямбда
    for i in range(n - 1):
        for j in range(n - i - 1):
            if D[j][3] < D[j + 1][3]:
                D[j], D[j + 1] = D[j + 1], D[j]

    seq = []

    for i in range(n):
        seq.append(D[i][0])
        
    return seq

def Rule3(params, D1, D0, D2):

    #сортировка D1 в порядке возрастания P1
    seq = SortAsc(params, D1, 1)

    #сортировка D0 в порядке возрастания P1
    seq += SortAsc(params, D0, 1)

    #сортировка D2 в порядке убывания P2
    seq += SortDesc(params, D2, 2)

    return seq

def Pairs(params, d):
    seq = []

    n = len(d) // 2

    for i in range(n):
        m = params[d[0]][2]
        k = 0

        for j in range(len(d)):
            if params[d[j]][2] > m:
                m = params[d[j]][2]
                k = j
        
        seq.append(d[k])
        d.pop(k)

        m = params[d[0]][1]
        k = 0

        for j in range(len(d)):
            if params[d[j]][1] < m:
                m = params[d[j]][1]
                k = j

        seq.append(d[k])
        d.pop(k)

    return seq

def Dx(params, seq, dx):

    n = len(seq)
    lx = params[dx][3]

    placed = False

    for i in range(0, n - 2, 2):
        m1 = max(params[seq[i]][3], params[seq[i + 1]][3])
        m2 = min(params[seq[i + 2]][3], params[seq[i + 3]][3])

        if (m1 >= lx >= m2):
            placed = True
            seq.insert(i + 2, dx)
            break

    if not placed and lx >= min(params[seq[0]][3], params[seq[1]][3]):
        placed = True
        seq.insert(0, dx)

    if not placed and lx <= max(params[seq[n - 2]][3], params[seq[n - 1]][3]):
        placed = True
        seq.append(dx)
        
    return seq

def Rule4(params, D1, D0, D2):
    d1 = D1.copy()
    d0 = D0.copy()
    d2 = D2.copy()

    seq = Pairs(params, d1)

    if (len(d1) != 0):
        if (len(d0) == 0 and len(d2) == 0):
            Dx(params, seq, d1[0])
        else:
            seq.append(d1[0])

            if (len(d0) != 0):
                dn = d0
            else:
                dn = d2
            
            m = params[dn[0]][1]
            k = 0

            for j in range(len(dn)):
                if params[dn[j]][1] < m:
                    m = params[dn[j]][1]
                    k = j

            seq.append(dn[k])
            dn.pop(k)

    
    seq += Pairs(params, d0)

    if (len(d0) != 0):
        if (len(d2) == 0):
            Dx(params, seq, d0[0])
        else:
            seq.append(d0[0])

            m = params[d2[0]][1]
            k = 0

            for j in range(len(d2)):
                if params[d2[j]][1] < m:
                    m = params[d2[j]][1]
                    k = j

            seq.append(d2[k])
            d2.pop(k)

    seq += Pairs(params, d2)

    if (len(d2) != 0):
        Dx(params, seq, d2[0])

    return seq

@app.route('/')
@app.route('/index')
def index():
    if request.is_json:
        cells_values = toStrArray(request.args.get('cells_values'))
        bad_values = findBad(cells_values)
        start_values = []

        if (len(bad_values) == 0):
            for i in range(0, len(cells_values), 7):
                v = [i // 7]
                for j in range(7):
                    v.append(int(cells_values[i + j]))

                start_values.append(v)



            P1 = []
            P2 = []
            lamb = []

            params = []

            for i in range(7):
                sum1 = 0
                sum2 = 0

                for j in range(4):
                    sum1 += start_values[i][j + 1]
                    sum2 += start_values[i][j + 4]

                P1.append(str(sum1))
                P2.append(str(sum2))
                lamb.append(str(sum2 - sum1))

                params.append([i, sum1, sum2, sum2 - sum1])

            D1 = []
            D0 = []
            D10 = []
            D2 = []

            for i in range(7):
                if params[i][3] >= 0:
                    if params[i][3] > 0:
                        D1.append(params[i][0])
                    else:
                        D0.append(params[i][0])
                    D10.append(params[i][0])
                else:
                    D2.append(params[i][0])

            sequences = [Rule1(params, D10, D2), Rule2(params), Rule3(params, D1, D0, D2), Rule4(params, D1, D0, D2)]

            seq_str = []

            for i in range(7):
                for j in range(4):
                    seq_str.append(str(sequences[j][i] + 1))

            if (request.args.get('action') == 'countPS'):

                return jsonify({'P1s': (' ').join(P1), 'P2s': (' ').join(P2), 'lambdas': (' ').join(lamb), 'seq_str': (' ').join(seq_str)})

            #Прорисовка графика по исходным значениям
            elif (request.args.get('action') == 'draw'):

                t = []
                T = []
                dt = []

                TableMethod(start_values, t, T, dt, [], [])
                return jsonify({'t_str': (' ').join(t), 'T_str': (' ').join(T), 'dt_str': (' ').join(dt)})

            #Поиск решения
            elif (request.args.get('action') == 'find'):
                t_res = []
                T_res = []
                dt_res = []
                Tpr_res = []
                Tozh_res = []

                values = []

                print(start_values)

                i = 0

                for seq in sequences:
                    print('seq ', seq)
                    values.append([])
                    for elem in seq:
                        print('elem', elem)
                        values[i].append(start_values[elem].copy())
                    i += 1

                print(values)

                for i in range(4):
                    TableMethod(values[i], t_res, T_res, dt_res, Tpr_res, Tozh_res)
                return jsonify({'seq_str': (' ').join(seq_str), 't_str': (' ').join(t_res), 'T_str': (' ').join(T_res), 'dt_str': (' ').join(dt_res), 'Tpr_str': (' ').join(Tpr_res), 'Tozh_str': (' ').join(Tozh_res)})

                
        return jsonify({'bad': (' ').join(bad_values)})
    else:
        return render_template("index.html", type = 2)
